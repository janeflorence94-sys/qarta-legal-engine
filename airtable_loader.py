import os
import requests
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_API_URL = "https://api.airtable.com/v0"

# Maps doc_type identifiers to Airtable table names
DOC_TYPE_TABLE_MAP = {
    "employment_contract": "Employment Contract Clauses",
    "service_agreement": "Service Agreement Clauses",
    "nda": "NDA Clauses (Demo Tier)",
    "pdpa": "PDPA Data Protection Clauses",
    "document_types": "Document Types",
    "automation_types": "Automation Types",
}

STRATEGIES_TABLE = "Rewrite Strategies"


def _get_headers():
    if not AIRTABLE_API_KEY:
        raise ValueError("AIRTABLE_API_KEY is not set in .env")
    if not AIRTABLE_BASE_ID:
        raise ValueError("AIRTABLE_BASE_ID is not set in .env")
    return {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}


def _fetch_all_records(table_name: str) -> list[dict]:
    """Fetch all records from a table, handling Airtable's 100-record pagination."""
    headers = _get_headers()
    url = f"{AIRTABLE_API_URL}/{AIRTABLE_BASE_ID}/{requests.utils.quote(table_name)}"

    records = []
    params = {}

    while True:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 401:
            raise ValueError("Invalid AIRTABLE_API_KEY — authentication failed.")
        if response.status_code == 404:
            raise ValueError(
                f"Table '{table_name}' not found in base '{AIRTABLE_BASE_ID}'. "
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


def load_lcm_records(table_name: str, corridor: str = None, doc_type: str = None) -> dict:
    """
    Load all records from the specified table plus Rewrite Strategies.

    Args:
        table_name: doc_type key (e.g. 'employment_contract') or exact Airtable table name.
        corridor:   Accepted but unused — tables are already separated by doc type.
        doc_type:   Accepted but unused — kept for API compatibility.

    Returns:
        dict with keys 'lcm_records' and 'strategy_records'.
    """
    resolved_table = DOC_TYPE_TABLE_MAP.get(table_name, table_name)

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
