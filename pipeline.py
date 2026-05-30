import json
import os
import re
import threading
import time
from pathlib import Path

import anthropic
import httpx
from docx import Document as DocxDocument
from PyPDF2 import PdfReader

from airtable_loader import load_lcm_records

PROMPTS_DIR = Path(__file__).parent / "prompts"

OUTPUT_HEADERS = [
    "=== OUTPUT 1: CLEAN ===",
    "=== OUTPUT 2: REDLINE ===",
    "=== OUTPUT 3: COMMENTARY ===",
]

# (output_num, keyword) pairs that map 1-to-1 to OUTPUT_HEADERS
_HEADER_KEYWORDS = [(1, "CLEAN"), (2, "REDLINE"), (3, "COMMENTARY")]


def _find_header_span(text: str, output_num: int, keyword: str):
    """Return (start_of_line, end_after_newline) for the header line of OUTPUT N: KEYWORD.

    Always returns full-line boundaries so content extracted between two header
    spans starts and ends cleanly, even when the header carries surrounding
    markdown decoration such as **=== OUTPUT 1: CLEAN ===**.

    Tries exact match first (fast O(n) scan), then falls back to a flexible
    regex that tolerates:
      - Varying numbers of '=' signs or none at all
      - Extra spaces / tabs around the parts
      - Case differences  (Output 1 / output 1 / OUTPUT 1)
      - Alternative separators between number and keyword  (: / - / space)
      - Surrounding decoration  (**  ==  …  ==  **)
    Returns (-1, -1) if the header cannot be located by either method.
    """
    def _line_span(pos: int):
        """Given a character position inside `text`, return (line_start, line_end)
        where line_end is the index just after the terminating '\\n' (or len(text))."""
        ls = text.rfind('\n', 0, pos)
        ls = 0 if ls == -1 else ls + 1
        le = text.find('\n', pos)
        le = len(text) if le == -1 else le + 1
        return ls, le

    exact = f"=== OUTPUT {output_num}: {keyword} ==="
    idx = text.find(exact)
    if idx != -1:
        return _line_span(idx)

    pat = re.compile(
        rf'(?im)^[^\n]*\boutput[ \t]+{output_num}\b[^\n]*\b{re.escape(keyword)}\b[^\n]*$'
    )
    m = pat.search(text)
    if m:
        return _line_span(m.start())
    return -1, -1


def _header_missing(text: str, output_num: int, keyword: str) -> bool:
    """True when the header for OUTPUT N: KEYWORD cannot be found (flexible match)."""
    return _find_header_span(text, output_num, keyword)[0] == -1


def _missing_headers(text: str) -> list:
    """Return the OUTPUT_HEADERS strings that are absent from text (flexible match)."""
    return [
        OUTPUT_HEADERS[i]
        for i, (n, kw) in enumerate(_HEADER_KEYWORDS)
        if _header_missing(text, n, kw)
    ]


# block1 part number that contains doc-type-specific drafting rules
DOC_TYPE_PART_MAP = {
    # CN-SG doc-type-specific parts (only used when no corridor part is loaded)
    "mou":                                   7,
    "memorandum_of_understanding":           7,
    "jv_agreement":                          8,
    "joint_venture":                         8,
    "jv":                                    8,
    "exclusive_distribution":                9,
    "exclusive_distribution_agreement":      9,
    "non_exclusive_distribution":            9,
    "non_exclusive_distribution_agreement":  9,
    # SG-MY-exclusive doc types (not present in CN_SG; Part 11 is their corridor part)
    "ip_licence":                            11,
    "ip_license":                            11,
    "franchise":                             11,
    "franchise_agreement":                   11,
    "sha":                                   11,
    "shareholders_agreement":                11,
    "employment":                            11,
    "employment_contract":                   11,
    "service_agreement":                     11,
}

# block1 part number that contains corridor-level adaptation rules
CORRIDOR_PART_MAP = {
    "SG_ID": 10,
    "CN_ID": 10,
    "SG_MY": 11,
}

PROMPT_SIZE_WARN = 180_000   # chars — log a warning above this threshold


def _extract_text_docx(file_bytes: bytes) -> str:
    import io
    doc = DocxDocument(io.BytesIO(file_bytes))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    if not paragraphs:
        raise ValueError("The .docx file contains no extractable text.")
    return "\n\n".join(f"{i+1}. {text}" for i, text in enumerate(paragraphs))


def _extract_text_pdf(file_bytes: bytes) -> str:
    import io
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text.strip())
    if not pages:
        raise ValueError("The .pdf file contains no extractable text.")
    full_text = "\n\n".join(pages)
    paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]
    return "\n\n".join(f"{i+1}. {text}" for i, text in enumerate(paragraphs))


def _strip_markdown_tables(text: str) -> str:
    """Convert markdown table rows to plain text to reduce token count."""
    lines = []
    for line in text.split("\n"):
        s = line.strip()
        if not (s.startswith("|") and s.endswith("|")):
            lines.append(line)
            continue
        # Skip separator rows: |---|---|
        if re.match(r"^\|[\s\-:|]+\|$", s):
            continue
        # Convert table data row: | A | B | C | → "A | B | C"
        cells = [c.strip() for c in s.strip("|").split("|") if c.strip()]
        if cells:
            lines.append("  " + " | ".join(cells))
    return "\n".join(lines)


def _extract_part(text: str, part_num: int) -> str:
    """Extract a numbered part section from block1 text using its === markers."""
    match = re.search(
        rf'=== PART {part_num}:.*?=== END PART {part_num} ===',
        text,
        re.DOTALL,
    )
    return match.group(0).strip() if match else ""


def _load_system_prompt(corridor: str = "CN_SG", doc_type: str = "") -> str:
    """Load system prompt, selecting block1 parts based on corridor and doc_type.

    CN_SG  → full block1 (Parts 1-6 + any doc-type parts present).
    Other  → Part 6 (deal profile modulation)
             + corridor-specific part (e.g. Part 10 for SG_ID)
             + doc-type-specific part (Part 7/8/9 where applicable).

    block2 (PDPA) and block3 (certainty hierarchy) are always included in full.
    """
    b1_path = PROMPTS_DIR / "block1_style_guide.txt"
    if not b1_path.exists():
        raise ValueError(f"Prompt file not found: {b1_path}")
    b1_raw = _strip_markdown_tables(b1_path.read_text(encoding="utf-8"))

    corr = corridor.upper()
    if corr == "CN_SG":
        # Slim path: Parts 1–6 extracted individually via markers.
        # Falls back to full block1 if any part is missing (zero regression risk).
        cn_sg_parts = []
        cn_sg_loaded = []
        for n in [1, 2, 3, 4, 5, 6]:
            p = _extract_part(b1_raw, n)
            if p:
                cn_sg_parts.append(p)
                cn_sg_loaded.append(f"Part{n}")
        if len(cn_sg_parts) == 6:
            b1_content = "\n\n".join(cn_sg_parts)
            print(f"[pipeline] block1: slim (CN_SG) — loaded {cn_sg_loaded} ({len(b1_content):,} chars, was {len(b1_raw):,} full)")
        else:
            b1_content = b1_raw   # fallback: extraction incomplete
            print(f"[pipeline] block1: full fallback (CN_SG) — only extracted {cn_sg_loaded}, using full {len(b1_raw):,} chars")
    else:
        selected = []
        loaded_parts = []

        # Part 6 — deal profile / clause modulation rules (universal)
        part6 = _extract_part(b1_raw, 6)
        if part6:
            selected.append(part6)
            loaded_parts.append("Part6")
        else:
            print(f"[pipeline] WARNING: could not extract Part 6 from block1 — using full block1")
            selected.append(b1_raw)
            loaded_parts.append("block1-FULL(fallback)")

        # Corridor-level rules (e.g. Part 10 for SG_ID)
        corr_part_num = CORRIDOR_PART_MAP.get(corr)
        if corr_part_num:
            cp = _extract_part(b1_raw, corr_part_num)
            if cp:
                selected.append(cp)
                loaded_parts.append(f"Part{corr_part_num}")
            else:
                print(f"[pipeline] WARNING: Part {corr_part_num} not found for corridor {corr}")

        # Doc-type-specific rules (Part 7 MOU / Part 8 JV / Part 9 Distribution).
        # Skipped when a corridor part is already loaded (corr_part_num is not None),
        # because corridor parts (Part 10 SG_ID, Part 11 SG_MY) are self-contained
        # and include doc-type rules — loading Part 7/8/9 alongside would be
        # contradictory, wasteful, and risks pushing the prompt over the token limit.
        doc_part_num = DOC_TYPE_PART_MAP.get(doc_type.lower())
        if doc_part_num and corr_part_num is None:
            dp = _extract_part(b1_raw, doc_part_num)
            if dp:
                selected.append(dp)
                loaded_parts.append(f"Part{doc_part_num}")
            else:
                print(f"[pipeline] WARNING: Part {doc_part_num} not found for doc_type {doc_type}")

        b1_content = "\n\n".join(selected)
        print(
            f"[pipeline] block1: slim ({corr}) — loaded {loaded_parts} "
            f"({len(b1_content):,} chars, was {len(b1_raw):,} full)"
        )

    blocks = ["=== BLOCK1 STYLE GUIDE ===\n\n" + b1_content]

    for filename in ("block2_pdpa_enforcement.txt", "block3_certainty_hierarchy.txt"):
        path = PROMPTS_DIR / filename
        if not path.exists():
            raise ValueError(f"Prompt file not found: {path}")
        raw = _strip_markdown_tables(path.read_text(encoding="utf-8"))
        section_name = filename.replace(".txt", "").replace("_", " ").upper()
        blocks.append(f"=== {section_name} ===\n\n{raw}")

    return "\n\n".join(blocks)


def _parse_response(response_text: str) -> dict:
    """Split Claude response into clean / redline / commentary sections.

    Uses _find_header_span for each section, which tries an exact string match
    first then falls back to a flexible regex that tolerates variations in = count,
    case, whitespace, and minor wording differences.  Raises ValueError only when
    a section truly cannot be located by either method.
    """
    h1s, h1e = _find_header_span(response_text, 1, "CLEAN")
    h2s, h2e = _find_header_span(response_text, 2, "REDLINE")
    h3s, h3e = _find_header_span(response_text, 3, "COMMENTARY")

    missing = []
    if h1s == -1: missing.append("OUTPUT 1: CLEAN")
    if h2s == -1: missing.append("OUTPUT 2: REDLINE")
    if h3s == -1: missing.append("OUTPUT 3: COMMENTARY")

    if missing:
        raise ValueError(
            f"Output headers not found after exact + flexible matching. "
            f"Missing: {missing}\n"
            f"Raw response (first 500 chars):\n{response_text[:500]}"
        )

    return {
        "clean":      response_text[h1e:h2s].strip(),
        "redline":    response_text[h2e:h3s].strip(),
        "commentary": response_text[h3e:].strip(),
    }



def build_deal_profile_block(deal_profile: dict) -> str:
    """Build an inline calibration block from the deal profile.
    Rules are injected directly — not referenced — so Claude acts on them immediately."""
    if not deal_profile:
        return ""

    size_labels = {
        "under_50K":  "Under SGD 50,000",
        "50K_300K":   "SGD 50,000 – 300,000",
        "300K_1M":    "SGD 300,000 – 1,000,000",
        "1M_5M":      "SGD 1,000,000 – 5,000,000",
        "5M_10M":     "SGD 5,000,000 – 10,000,000",
        "10M_50M":    "SGD 10,000,000 – 50,000,000",
        "50M_100M":   "SGD 50,000,000 – 100,000,000",
        "over_100M":  "Over SGD 100,000,000",
    }
    leverage_labels = {
        "we_seek_access":   "We seek access to something they control",
        "they_seek_access": "They seek access to something we control",
        "balanced":         "Both parties bring something the other needs",
        "exploratory":      "Exploratory — neither party fully committed",
    }
    importance_labels = {
        "pilot":           "Pilot — under 12 months",
        "medium_term":     "Medium-term — 1 to 3 years",
        "long_term":       "Long-term — 3 years or more",
        "strategic_entry": "Strategic market entry",
    }
    timeline_labels = {
        "urgent":   "Urgent — within 30 days",
        "normal":   "Standard — 1 to 3 months",
        "flexible": "Flexible — no deadline",
    }

    instructions = []
    size     = deal_profile.get("deal_size", "")
    leverage = deal_profile.get("leverage", "")
    ip_types = deal_profile.get("ip_types", [])
    importance = deal_profile.get("strategic_importance", "")
    timeline   = deal_profile.get("timeline_urgency", "")
    currency   = deal_profile.get("payment_currency", "")

    # ── LIABILITY CAP & DEAL-SIZE RULES ──────────────────────────────────────
    if size == "under_50K":
        instructions += [
            "LIABILITY CAP: 100% of total fees paid. Use Singapore courts, not SIAC.",
            "NON-COMPETE: Maximum 6 months if included.",
            "LAWYER_REVIEW: Minimal flags — lightweight document.",
            "COMMENTARY NOTE: 'Low-value arrangement — lightweight protections applied throughout.'",
        ]
    elif size == "50K_300K":
        instructions += [
            "LIABILITY CAP: Total fees paid in preceding 12 months.",
            "SIAC: 1 arbitrator.",
            "NON-COMPETE: 6–12 months.",
            "COMMENTARY NOTE: 'Mid-value arrangement — standard balanced protections applied.'",
        ]
    elif size == "300K_1M":
        instructions += [
            "LIABILITY CAP: 12 months fees + IP breach carved out as uncapped.",
            "SIAC: 1 arbitrator.",
            "NON-COMPETE: 12 months.",
            "PDPA: Apply full mandatory baseline.",
            "COMMENTARY NOTE: 'Significant-value arrangement — strengthened protections applied. IP breach liability uncapped.'",
        ]
    elif size == "1M_5M":
        instructions += [
            "LIABILITY CAP: 24 months fees + IP breach uncapped + flag insurance requirement.",
            "SIAC: 3-arbitrator panel.",
            "NON-COMPETE: 12–24 months.",
            "PDPA: Full baseline + PIPL dual compliance flag.",
            "LAWYER_REVIEW: Flag all PARAMETERIZED clauses.",
            "COMMENTARY NOTE: 'High-value arrangement — comprehensive protections. All PARAMETERIZED clauses require lawyer confirmation.'",
        ]
    elif size == "5M_10M":
        instructions += [
            "LIABILITY CAP: Fixed SGD cap — LAWYER_REVIEW mandatory, no default. IP breach uncapped. Flag PI insurance minimum SGD 5M.",
            "SIAC: 3-arbitrator panel mandatory.",
            "NON-COMPETE: 24 months mandatory. Lawyer review required.",
            "JV GOVERNANCE: Unanimous consent for all reserved matters. No chairman casting vote.",
            "ANTI-DILUTION: Flag as mandatory.",
            "LAWYER_REVIEW: Every single PARAMETERIZED field — no exceptions.",
            "COMMENTARY NOTE: 'Large-value arrangement. Every PARAMETERIZED clause requires lawyer confirmation. Do not execute without full legal review.'",
        ]
    elif size == "10M_50M":
        instructions += [
            "LIABILITY CAP: LAWYER_REVIEW MANDATORY — do not insert any default cap. Flag ICC as SIAC alternative.",
            "SIAC: 3-arbitrator panel mandatory.",
            "NON-COMPETE: 24 months mandatory. Full geographic scope. 3% passive investment carve-out.",
            "SANCTIONS: Flag mandatory sanctions screening — CN party and all beneficial owners against OFAC, EU, UN, MAS lists.",
            "IRAS: Flag transfer pricing documentation requirement — 6th Edition guidelines.",
            "LAWYER_REVIEW: Apply to EVERY PARAMETERIZED field without exception. Do not auto-fill any default.",
            "COMMENTARY NOTE: 'Major transaction — SGD 10M–50M range. This document requires full legal review by Singapore-qualified counsel before execution. Qarta has structured the document and identified all material issues. Estimated lawyer review: 8–15 hours.'",
        ]
    elif size in ("50M_100M", "over_100M"):
        instructions += [
            "LIABILITY CAP: Do not insert any cap — LAWYER_REVIEW only. Explain market practice at this tier in commentary.",
            "SIAC: 3-arbitrator mandatory. Flag ICC, LCIA, HKIAC as alternatives.",
            "EMERGENCY ARBITRATION: Flag SIAC Rule 30 Emergency Arbitrator.",
            "CCCS: Flag merger review consideration.",
            "SANCTIONS: Enhanced due diligence flag — beneficial ownership verification mandatory.",
            "LAWYER_REVIEW: Apply to every clause — no defaults anywhere.",
            "COMMENTARY NOTE: 'Flagship transaction — SGD 50M+ range. Full legal team review required. Recommend engaging Singapore counsel (HSF, Linklaters, or equivalent). Estimated lawyer review: 20–40 hours. This document is not execution-ready without legal sign-off.'",
        ]

    # ── LEVERAGE / COMMERCIAL POSITION ────────────────────────────────────────
    if leverage == "we_seek_access":
        instructions.append(
            "COMMERCIAL POSITION: We seek access — apply protective provisions in our favour. "
            "Longer termination notice before we can be terminated. "
            "Narrower non-compete scope post-termination. "
            "More reserved matters requiring their consent."
        )
    elif leverage == "they_seek_access":
        instructions.append(
            "COMMERCIAL POSITION: They seek access — we have leverage. "
            "Shorter termination notice for us. Broader non-compete scope. "
            "Fewer reserved matters requiring their consent."
        )
    elif leverage == "exploratory":
        instructions.append(
            "COMMERCIAL POSITION: Exploratory — apply pilot framing. "
            "Short terms, easy exit, minimal commitments, no long-tail non-competes."
        )

    # ── IP / DATA TYPES ───────────────────────────────────────────────────────
    if ip_types and "none" not in ip_types:
        if "manufacturing_process" in ip_types:
            instructions.append(
                "IP — MANUFACTURING PROCESS: Licence strongly preferred over assignment. "
                "Flag IRAS transfer pricing. Non-compete scope includes directly competitive manufacturing. "
                "Trade secrets: indefinite protection. Insert IP indemnity clause."
            )
        if "software" in ip_types:
            instructions.append(
                "IP — SOFTWARE: Flag work product ownership for input. "
                "PDPA elevated if software processes personal data. "
                "Flag source code escrow. Trade secrets: indefinite protection."
            )
        if "trademark" in ip_types:
            instructions.append(
                "IP — TRADEMARK: Insert quality control clause. "
                "All goodwill accrues to Principal — insert expressly. "
                "Flag IPOS registration status in commentary. "
                "Post-termination: immediate cessation of all mark use."
            )
        if "personal_data" in ip_types or "data" in " ".join(ip_types).lower():
            instructions.append(
                "IP — PERSONAL DATA: Apply full PDPA mandatory baseline. "
                "Flag PIPL dual compliance. Flag DPO appointment. "
                "Insert 24-hour internal + 3-day PDPC breach notification. "
                "Recommend separate DPA."
            )
    else:
        instructions.append(
            "IP/DATA: None involved — standard boilerplate only. "
            "No elevated IP or PDPA provisions."
        )

    # ── STRATEGIC IMPORTANCE / TERM ───────────────────────────────────────────
    if importance == "pilot":
        instructions.append(
            "TERM: 6–12 months initial term. Easy exit. No marketing commitments. "
            "No minimum purchase. Non-compete: omit or 6 months maximum."
        )
    elif importance == "medium_term":
        instructions.append(
            "TERM: 2 years initial. 1-year renewal with 60-day notice. "
            "Non-compete: 6–12 months. Commercially reasonable efforts standard."
        )
    elif importance == "long_term":
        instructions.append(
            "TERM: 3 years initial. 1-year renewal with 90-day notice. "
            "Non-compete: 12 months. 60–90 day post-termination transition."
        )
    elif importance == "strategic_entry":
        instructions.append(
            "TERM: 3–5 years initial. Performance-reviewed renewal. "
            "Non-compete: 12–24 months. 90-day post-termination transition. "
            "Flag regulatory approvals."
        )

    # ── TIMELINE ──────────────────────────────────────────────────────────────
    if timeline == "urgent":
        instructions.append(
            "TIMELINE URGENT: Auto-fill ALL PARAMETERIZED fields with market-standard Singapore defaults. "
            "Add commentary note on every defaulted field: 'Default applied for speed — review before execution.' "
            "Reduce LAWYER_REVIEW to critical items only."
        )
    elif timeline == "flexible":
        instructions.append(
            "TIMELINE FLEXIBLE: Flag every PARAMETERIZED field with full commentary explaining options "
            "and trade-offs. Apply LAWYER_REVIEW generously. Maximum depth throughout."
        )

    # ── PAYMENT CURRENCY ──────────────────────────────────────────────────────
    currency_map = {
        "SGD": "Singapore Dollars (SGD). Late interest: SORA + 2% per annum.",
        "USD": "United States Dollars (USD). Note: USD selected as neutral currency — avoids CNY convertibility restrictions.",
        "CNY": "Chinese Renminbi (CNY). MANDATORY FLAG: CNY is not freely convertible. Cross-border CNY payments require SAFE approval and MAS FX compliance. Lawyer review of payment mechanics required.",
        "IDR": "Indonesian Rupiah (IDR). FLAG: IDR subject to Bank Indonesia FX regulations. USD recommended as alternative.",
        "MYR": "Malaysian Ringgit (MYR). FLAG: Subject to Bank Negara Malaysia FX administration rules.",
        "VND": "Vietnamese Dong (VND). MANDATORY FLAG: VND subject to State Bank of Vietnam FX controls. USD strongly recommended.",
        "THB": "Thai Baht (THB). FLAG: Subject to Bank of Thailand FX regulations.",
        "PHP": "Philippine Peso (PHP). FLAG: Subject to Bangko Sentral ng Pilipinas FX regulations. USD recommended.",
        "EUR": "Euros (EUR).",
        "GBP": "British Pounds Sterling (GBP).",
    }
    if currency in currency_map:
        instructions.append(f"PAYMENT CURRENCY: {currency_map[currency]}")

    # ── ASSEMBLE BLOCK ────────────────────────────────────────────────────────
    lines = [
        "╔══════════════════════════════════════════════════╗",
        "║  DEAL PROFILE — MANDATORY CALIBRATION RULES      ║",
        "║  READ AND APPLY BEFORE DRAFTING ANY CLAUSE        ║",
        "╚══════════════════════════════════════════════════╝",
        "",
        "The following instructions OVERRIDE all generic defaults",
        "in the style guide. Apply every rule below without exception.",
        "",
    ]

    if size:
        lines.append(f"CONTRACT VALUE:        {size_labels.get(size, size)}")
    if leverage:
        lines.append(f"COMMERCIAL POSITION:   {leverage_labels.get(leverage, leverage)}")
    if ip_types:
        lines.append(f"IP / DATA:             {', '.join(ip_types)}")
    if importance:
        lines.append(f"STRATEGIC IMPORTANCE:  {importance_labels.get(importance, importance)}")
    if timeline:
        lines.append(f"TIMELINE:              {timeline_labels.get(timeline, timeline)}")
    if currency:
        lines.append(f"PAYMENT CURRENCY:      {currency}")

    lines += ["", "── CALIBRATION INSTRUCTIONS ──"]
    lines += [f"• {instr}" for instr in instructions]
    lines += [
        "",
        "╔══════════════════════════════════════════════════╗",
        "║  END DEAL PROFILE — NOW PROCEED TO DRAFT         ║",
        "╚══════════════════════════════════════════════════╝",
        "",
    ]
    return "\n".join(lines)


def adapt_contract(
    file_bytes: bytes,
    file_ext: str,
    corridor: str,
    doc_type: str,
    company_name: str,
    deal_profile: dict = None,
) -> dict:
    """
    Adapt a Chinese-law contract to Singapore-law compliance.

    Args:
        file_bytes:    Raw bytes of the uploaded contract file.
        file_ext:      File extension — 'docx' or 'pdf' (without dot).
        corridor:      Localisation corridor, e.g. 'CN_SG'.
        doc_type:      Document type key, e.g. 'employment_contract'.
        company_name:  Client company name for contract header.
        deal_profile:  Optional dict of deal context fields for clause modulation.

    Returns:
        dict with keys 'clean', 'redline', 'commentary' (all str).
    """
    # Step 1 — Extract contract text
    print("[pipeline] Extracting contract text...")
    ext = file_ext.lower().lstrip(".")
    if ext == "docx":
        contract_text = _extract_text_docx(file_bytes)
    elif ext == "pdf":
        contract_text = _extract_text_pdf(file_bytes)
    else:
        raise ValueError(f"Unsupported file format '.{ext}'. Only .docx and .pdf are accepted.")
    print(f"[pipeline] Extracted {len(contract_text)} chars from .{ext} file.")

    # Step 2 — Load system prompt blocks + deal profile (corridor-aware)
    print("[pipeline] Loading prompts...")
    system_prompt = _load_system_prompt(corridor=corridor, doc_type=doc_type)
    print(f"[pipeline] Prompts loaded ({len(system_prompt):,} chars).")

    deal_profile_block = build_deal_profile_block(deal_profile or {})
    if deal_profile_block:
        print(f"[pipeline] Deal profile injected ({len(deal_profile_block)} chars).")

    # Step 3 — Load LCM + strategy records from Airtable
    print("[pipeline] Loading LCM records from Airtable...")
    airtable_data = load_lcm_records(corridor=corridor, doc_type=doc_type)
    lcm_records = airtable_data["lcm_records"]
    strategy_records = airtable_data["strategy_records"]
    print(f"[pipeline] Loaded {len(lcm_records)} LCM records, {len(strategy_records)} strategy records.")

    lcm_json = json.dumps(lcm_records, indent=2, ensure_ascii=False)
    strategy_json = json.dumps(strategy_records, indent=2, ensure_ascii=False)

    # Step 4 — Build user message
    user_message = f"""=== LCM RECORDS ===
{lcm_json}

=== STRATEGIES ===
{strategy_json}

=== CONTRACT TO ADAPT ===
Company: {company_name}
Corridor: {corridor}
Document type: {doc_type}

{contract_text}

Please adapt this contract and produce exactly three outputs separated by these exact headers:

=== OUTPUT 1: CLEAN ===
[complete clean adapted contract]

=== OUTPUT 2: REDLINE ===
[redline showing all changes]

=== OUTPUT 3: COMMENTARY ===
[full commentary with four-field format per clause]"""

    # Step 5 — Call Claude API (streaming) with prompt caching on the static system prompt
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        timeout=httpx.Timeout(600.0, connect=10.0),
    )

    # Static style guide is cached; dynamic deal profile appended without cache
    system_block = [
        {
            "type": "text",
            "text": system_prompt,
            "cache_control": {"type": "ephemeral"},
        }
    ]
    if deal_profile_block:
        system_block.append({"type": "text", "text": deal_profile_block})

    def _call_claude_streaming(messages: list) -> str:
        """Stream a Claude response, printing a dot every 5 seconds as a heartbeat.
        Returns whatever was received — caller checks for completeness."""
        result_parts = []
        stop_event = threading.Event()

        def _heartbeat():
            while not stop_event.is_set():
                stop_event.wait(5)
                if not stop_event.is_set():
                    print(".", end="", flush=True)

        dot_thread = threading.Thread(target=_heartbeat, daemon=True)
        dot_thread.start()
        try:
            with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=32000,
                system=system_block,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    result_parts.append(text)
        except Exception as e:
            # Connection dropped mid-stream — return whatever arrived
            print(f"\n[pipeline] Stream interrupted: {type(e).__name__}: {e}")
        finally:
            stop_event.set()
            dot_thread.join(timeout=1)
            print()  # newline after dots

        return "".join(result_parts)

    def _continuation(partial: str) -> str:
        """Ask Claude to continue from where it left off.
        Uses a targeted prompt when only OUTPUT 3 (COMMENTARY) is missing."""
        present = [h for h in OUTPUT_HEADERS if h in partial]
        missing = [h for h in OUTPUT_HEADERS if h not in partial]
        print(f"[pipeline] Continuation: have {present}, need {missing}")

        if missing == [OUTPUT_HEADERS[2]]:
            # Only COMMENTARY missing — targeted request so Claude doesn't re-draft CLEAN/REDLINE
            prompt = (
                "You completed OUTPUT 1 (CLEAN) and OUTPUT 2 (REDLINE) but did not produce "
                "OUTPUT 3 (COMMENTARY). Please produce the full commentary section now, "
                "starting with this exact header on its own line:\n\n"
                "=== OUTPUT 3: COMMENTARY ===\n\n"
                "Provide the complete four-field commentary for every adapted clause. "
                "Do not repeat OUTPUT 1 or OUTPUT 2."
            )
        else:
            prompt = (
                f"Your previous response was cut off. You produced {present} but stopped "
                f"before completing {missing}. Please continue exactly from where you left off "
                f"and generate the remaining sections, starting with the next missing header."
            )

        result = _call_claude_streaming([
            {"role": "user",      "content": user_message},
            {"role": "assistant", "content": partial},
            {"role": "user",      "content": prompt},
        ])
        return partial + "\n\n" + result

    # Step 6 — Log total prompt size then call Claude
    total_chars = (
        len(system_prompt)
        + len(deal_profile_block)
        + len(user_message)
    )
    print(
        f"[pipeline] Prompt size: {total_chars:,} chars total "
        f"(system={len(system_prompt):,}, deal_profile={len(deal_profile_block):,}, "
        f"user={len(user_message):,})"
    )
    if total_chars > PROMPT_SIZE_WARN:
        print(
            f"[pipeline] WARNING: prompt exceeds {PROMPT_SIZE_WARN:,} char threshold "
            f"({total_chars:,} chars). Corridor-aware loading applied: "
            f"corridor={corridor}, doc_type={doc_type}."
        )

    print(
        f"[pipeline] Job config: corridor={corridor}, doc_type={doc_type}, "
        f"lcm_records={len(lcm_records)}, strategy_records={len(strategy_records)}"
    )
    print("[pipeline] Calling Claude API... (this may take 2-3 minutes for full output)")
    response_text = _call_claude_streaming([{"role": "user", "content": user_message}])
    print(f"[pipeline] Received {len(response_text):,} chars.")
    print(f"[pipeline] Response preview: {response_text[:200]!r}")

    missing = _missing_headers(response_text)

    if missing:
        has_any = not (len(missing) == len(OUTPUT_HEADERS))

        if not has_any:
            # Connection dropped before any output — retry the full call once
            print("[pipeline] No output received. Retrying full call...")
            response_text = _call_claude_streaming([{"role": "user", "content": user_message}])
            print(f"[pipeline] Retry received {len(response_text):,} chars.")
            print(f"[pipeline] Retry preview: {response_text[:200]!r}")
            missing = _missing_headers(response_text)

        if missing:
            # Partial output — targeted continuation (commentary-aware or generic)
            print(f"[pipeline] Missing sections {missing}. Running continuation 1...")
            response_text = _continuation(response_text)

        # Check again — second continuation if still incomplete
        still_missing = _missing_headers(response_text)
        if still_missing:
            print(f"[pipeline] Still missing {still_missing}. Running continuation 2...")
            response_text = _continuation(response_text)

        # Final check — third pass if commentary specifically still absent
        still_missing = _missing_headers(response_text)
        if still_missing == [OUTPUT_HEADERS[2]]:
            print("[pipeline] Commentary still absent. Running targeted commentary continuation...")
            response_text = _continuation(response_text)

    print("[pipeline] All sections present, parsing...")

    # Step 7 — Parse (flexible header matching); ONE automatic retry if headers are
    # present in the text but formatted in a way the flexible matcher still can't
    # resolve — re-asks the model to re-emit with exact headers.
    try:
        parsed = _parse_response(response_text)
    except ValueError as parse_err:
        print(f"[pipeline] Header parse failed after flexible matching: {parse_err!r}")
        print("[pipeline] Retrying with explicit header-format instruction...")
        header_fix_prompt = (
            "Your previous response could not be parsed because the output section "
            "headers were not in the expected format. Please re-output all three "
            "sections now using EXACTLY these headers, each on its own line with no "
            "variation whatsoever:\n\n"
            "=== OUTPUT 1: CLEAN ===\n"
            "(full clean document)\n\n"
            "=== OUTPUT 2: REDLINE ===\n"
            "(full redline document)\n\n"
            "=== OUTPUT 3: COMMENTARY ===\n"
            "(full commentary)\n\n"
            "Begin immediately with === OUTPUT 1: CLEAN === — no preamble."
        )
        retry_response = _call_claude_streaming([
            {"role": "user",      "content": user_message},
            {"role": "assistant", "content": response_text},
            {"role": "user",      "content": header_fix_prompt},
        ])
        parsed = _parse_response(retry_response)   # raises if still broken

    parsed["records_loaded"] = len(lcm_records)
    return parsed
