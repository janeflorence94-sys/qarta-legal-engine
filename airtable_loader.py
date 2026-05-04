import os

import requests


def _encode_table(name: str) -> str:
    """Encode a table name for use in an Airtable URL path.
    Airtable accepts literal parentheses but requires spaces as %20.
    Over-encoding parentheses as %28/%29 causes 403 errors."""
    return name.replace(" ", "%20")

AIRTABLE_API_URL = "https://api.airtable.com/v0"

# Maps (corridor, doc_type) → Airtable table name
CORRIDOR_TABLE_MAP = {
    # ── CN-SG corridor ────────────────────────────────────────────────────────
    ("CN_SG", "employment_contract"):               "Employment Contract Clauses",
    ("CN_SG", "service_agreement"):                 "Service Agreement Clauses",
    ("CN_SG", "nda"):                               "NDA Clauses (Demo Tier)",
    ("CN_SG", "non_disclosure_agreement"):          "NDA Clauses (Demo Tier)",
    ("CN_SG", "pdpa"):                              "PDPA Data Protection Clauses",
    ("CN_SG", "mou"):                               "MOU Clauses (CN-SG)",
    ("CN_SG", "memorandum_of_understanding"):       "MOU Clauses (CN-SG)",
    ("CN_SG", "jv_agreement"):                      "JV Agreement Clauses (CN-SG)",
    ("CN_SG", "joint_venture"):                     "JV Agreement Clauses (CN-SG)",
    ("CN_SG", "jv"):                                "JV Agreement Clauses (CN-SG)",
    ("CN_SG", "exclusive_distribution"):            "Exclusive Distribution Clauses (CN-SG)",
    ("CN_SG", "exclusive_distribution_agreement"):  "Exclusive Distribution Clauses (CN-SG)",
    ("CN_SG", "non_exclusive_distribution"):        "Non-Exclusive Distribution Clauses (CN-SG)",
    ("CN_SG", "non_exclusive_distribution_agreement"): "Non-Exclusive Distribution Clauses (CN-SG)",

    # ── SG-ID corridor ────────────────────────────────────────────────────────
    ("SG_ID", "nda"):                               "NDA Clauses (SG-ID)",
    ("SG_ID", "non_disclosure_agreement"):          "NDA Clauses (SG-ID)",
    ("SG_ID", "mou"):                               "MOU Clauses (SG-ID)",
    ("SG_ID", "memorandum_of_understanding"):       "MOU Clauses (SG-ID)",
    ("SG_ID", "service_agreement"):                 "Service Agreement Clauses (SG-ID)",
    ("SG_ID", "jv_agreement"):                      "JV Agreement Clauses (SG-ID)",
    ("SG_ID", "joint_venture"):                     "JV Agreement Clauses (SG-ID)",
    ("SG_ID", "jv"):                                "JV Agreement Clauses (SG-ID)",
    ("SG_ID", "non_exclusive_distribution"):        "Non-Exclusive Distribution Clauses (SG-ID)",
    ("SG_ID", "non_exclusive_distribution_agreement"): "Non-Exclusive Distribution Clauses (SG-ID)",
}

STRATEGIES_TABLE = "Rewrite Strategies"


def get_table_name(corridor: str, doc_type: str) -> str:
    """Resolve (corridor, doc_type) → Airtable table name.
    Falls back to CN_SG table if no corridor-specific entry exists."""
    key = (corridor.upper(), doc_type.lower())
    if key in CORRIDOR_TABLE_MAP:
        return CORRIDOR_TABLE_MAP[key]
    # CN_SG fallback — keeps existing doc types working for any corridor
    fallback = ("CN_SG", doc_type.lower())
    if fallback in CORRIDOR_TABLE_MAP:
        return CORRIDOR_TABLE_MAP[fallback]
    raise ValueError(
        f"No Airtable table configured for corridor='{corridor}', doc_type='{doc_type}'. "
        "Add an entry to CORRIDOR_TABLE_MAP in airtable_loader.py."
    )


def _get_headers():
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    if not api_key:
        raise ValueError("AIRTABLE_API_KEY is not set in environment variables.")
    if not base_id:
        raise ValueError("AIRTABLE_BASE_ID is not set in environment variables.")
    return {"Authorization": f"Bearer {api_key}"}


def _fetch_all_records(table_name: str) -> list[dict]:
    """Fetch all records from a table, handling Airtable's 100-record pagination."""
    headers = _get_headers()
    base_id = os.getenv("AIRTABLE_BASE_ID")
    url = f"{AIRTABLE_API_URL}/{base_id}/{_encode_table(table_name)}"

    records = []
    params = {}

    while True:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 401:
            raise ValueError("Invalid AIRTABLE_API_KEY — authentication failed.")
        if response.status_code == 404:
            raise ValueError(
                f"Table '{table_name}' not found in base '{base_id}'. "
                "Check that the table name matches exactly."
            )
        if response.status_code != 200:
            raise ValueError(
                f"Airtable API error {response.status_code}: {response.text}"
            )

        data = response.json()
        records.extend(
            {"id": r["id"], **r.get("fields", {})} for r in data.get("records", [])
        )

        offset = data.get("offset")
        if not offset:
            break
        params = {"offset": offset}

    return records


def load_lcm_records(corridor: str, doc_type: str) -> dict:
    """
    Load all LCM records for the given corridor + doc_type, plus Rewrite Strategies.

    Args:
        corridor:  Localisation corridor, e.g. 'CN_SG' or 'SG_ID'.
        doc_type:  Document type key, e.g. 'nda', 'jv_agreement'.

    Returns:
        dict with keys 'lcm_records' and 'strategy_records'.
    """
    resolved_table = get_table_name(corridor, doc_type)

    lcm_records = _fetch_all_records(resolved_table)

    if not lcm_records:
        raise ValueError(
            f"No records found in table '{resolved_table}'. "
            "Check that the table has data in your Airtable base."
        )

    strategy_records = _fetch_all_records(STRATEGIES_TABLE)

    return {
        "lcm_records": lcm_records,
        "strategy_records": strategy_records,
    }
