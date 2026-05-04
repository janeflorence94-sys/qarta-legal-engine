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
PROMPT_FILES = [
    "block1_style_guide.txt",
    "block2_pdpa_enforcement.txt",
    "block3_certainty_hierarchy.txt",
]

OUTPUT_HEADERS = [
    "=== OUTPUT 1: CLEAN ===",
    "=== OUTPUT 2: REDLINE ===",
    "=== OUTPUT 3: COMMENTARY ===",
]


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


def _load_system_prompt() -> str:
    blocks = []
    for filename in PROMPT_FILES:
        path = PROMPTS_DIR / filename
        if not path.exists():
            raise ValueError(f"Prompt file not found: {path}")
        raw = path.read_text(encoding="utf-8")
        cleaned = _strip_markdown_tables(raw)
        section_name = filename.replace(".txt", "").replace("_", " ").upper()
        blocks.append(f"=== {section_name} ===\n\n{cleaned}")
    return "\n\n".join(blocks)


def _parse_response(response_text: str) -> dict:
    """Split Claude response into clean / redline / commentary sections."""
    missing = [h for h in OUTPUT_HEADERS if h not in response_text]
    if missing:
        raise ValueError(
            f"Claude response is missing required output headers: {missing}\n"
            "Raw response (first 500 chars):\n" + response_text[:500]
        )

    parts = {}
    positions = {h: response_text.index(h) for h in OUTPUT_HEADERS}

    clean_start = positions[OUTPUT_HEADERS[0]] + len(OUTPUT_HEADERS[0])
    redline_start = positions[OUTPUT_HEADERS[1]] + len(OUTPUT_HEADERS[1])
    commentary_start = positions[OUTPUT_HEADERS[2]] + len(OUTPUT_HEADERS[2])

    parts["clean"] = response_text[clean_start:positions[OUTPUT_HEADERS[1]]].strip()
    parts["redline"] = response_text[redline_start:positions[OUTPUT_HEADERS[2]]].strip()
    parts["commentary"] = response_text[commentary_start:].strip()

    return parts



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

    # Step 2 — Load system prompt blocks + deal profile
    print("[pipeline] Loading prompts...")
    system_prompt = _load_system_prompt()
    print(f"[pipeline] Prompts loaded ({len(system_prompt)} chars).")

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
            print(f"\n[pipeline] Stream interrupted: {e}")
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

    # Step 6 — First call; retry/continue on drop or truncation
    print("[pipeline] Calling Claude API... (this may take 2-3 minutes for full output)")
    response_text = _call_claude_streaming([{"role": "user", "content": user_message}])
    print(f"[pipeline] Received {len(response_text)} chars.")

    missing = [h for h in OUTPUT_HEADERS if h not in response_text]

    if missing:
        has_any = any(h in response_text for h in OUTPUT_HEADERS)

        if not has_any:
            # Connection dropped before any output — retry the full call once
            print("[pipeline] No output received. Retrying full call...")
            response_text = _call_claude_streaming([{"role": "user", "content": user_message}])
            missing = [h for h in OUTPUT_HEADERS if h not in response_text]

        if missing:
            # Partial output — targeted continuation (commentary-aware or generic)
            print(f"[pipeline] Missing sections {missing}. Running continuation 1...")
            response_text = _continuation(response_text)

        # Check again — second continuation if still incomplete
        still_missing = [h for h in OUTPUT_HEADERS if h not in response_text]
        if still_missing:
            print(f"[pipeline] Still missing {still_missing}. Running continuation 2...")
            response_text = _continuation(response_text)

        # Final check — third pass if commentary specifically still absent
        still_missing = [h for h in OUTPUT_HEADERS if h not in response_text]
        if still_missing == [OUTPUT_HEADERS[2]]:
            print("[pipeline] Commentary still absent. Running targeted commentary continuation...")
            response_text = _continuation(response_text)

    print("[pipeline] All sections present, parsing...")

    # Step 7 — Parse and return (include record count for API metadata)
    parsed = _parse_response(response_text)
    parsed["records_loaded"] = len(lcm_records)
    return parsed
