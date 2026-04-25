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


def adapt_contract(
    file_bytes: bytes,
    file_ext: str,
    corridor: str,
    doc_type: str,
    company_name: str,
) -> dict:
    """
    Adapt a Chinese-law contract to Singapore-law compliance.

    Args:
        file_bytes:   Raw bytes of the uploaded contract file.
        file_ext:     File extension — 'docx' or 'pdf' (without dot).
        corridor:     Localisation corridor, e.g. 'CN_SG'.
        doc_type:     Document type key, e.g. 'employment_contract'.
        company_name: Client company name for contract header.

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

    # Step 2 — Load system prompt blocks
    print("[pipeline] Loading prompts...")
    system_prompt = _load_system_prompt()
    print(f"[pipeline] Prompts loaded ({len(system_prompt)} chars).")

    # Step 3 — Load LCM + strategy records from Airtable
    print("[pipeline] Loading LCM records from Airtable...")
    airtable_data = load_lcm_records(doc_type)
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

    system_block = [
        {
            "type": "text",
            "text": system_prompt,
            "cache_control": {"type": "ephemeral"},
        }
    ]

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
                max_tokens=16000,
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
        """Ask Claude to continue from where it left off."""
        present = [h for h in OUTPUT_HEADERS if h in partial]
        missing = [h for h in OUTPUT_HEADERS if h not in partial]
        print(f"[pipeline] Continuation: have {present}, need {missing}")
        prompt = (
            f"Your previous response was cut off. You generated {present} but stopped "
            f"before {missing}. Please continue exactly from where you left off and "
            f"generate the remaining sections, starting with the next missing header."
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
            # Partial output — continue from what we have
            print(f"[pipeline] Missing sections {missing}. Running continuation...")
            response_text = _continuation(response_text)

        # Final check — second continuation if still incomplete
        still_missing = [h for h in OUTPUT_HEADERS if h not in response_text]
        if still_missing:
            print(f"[pipeline] Still missing {still_missing}. Running second continuation...")
            response_text = _continuation(response_text)

    print("[pipeline] All sections present, parsing...")

    # Step 7 — Parse and return (include record count for API metadata)
    parsed = _parse_response(response_text)
    parsed["records_loaded"] = len(lcm_records)
    return parsed
