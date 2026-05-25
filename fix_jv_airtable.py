import os, requests

TOKEN     = os.environ["AIRTABLE_API_KEY"]
BASE_ID   = "appwmBfW20jnFo64x"
TABLE_NAME = "JV Agreement Clauses (SG-MY)"

headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

records = [
    {"fields": {"Concept ID": "JV-MY-NL01", "Label": "National Language Act - Bahasa Malaysia",
                "Requires Human Review": True,
                "Statutory Reference": "National Language Act 1963/67 (Act 32); Courts of Judicature Act 1964 s.8",
                "Notes": "PARAMETERIZED — set Automation Type manually in Airtable"}},
    {"fields": {"Concept ID": "JV-MY-P01", "Label": "MY PDPA 2010 - personal data protection",
                "Requires Human Review": True,
                "Statutory Reference": "Personal Data Protection Act 2010 (Act 709)",
                "Notes": "FULL_AUTO — set Automation Type manually in Airtable"}},
    {"fields": {"Concept ID": "JV-MY-L01", "Label": "Labuan IBFC - cross-border structuring",
                "Requires Human Review": True,
                "Statutory Reference": "Labuan Companies Act 1990 (Act 441); Labuan Business Activity Tax Act 1990 (Act 445)",
                "Notes": "REFERENCE_ONLY — set Automation Type manually in Airtable"}},
]

url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME.replace(' ', '%20')}"
r = requests.post(url, headers=headers, json={"records": records})
print(f"Upload: {r.status_code}")
if r.status_code in (200, 201):
    for rec in r.json().get("records", []):
        print(f"  {rec['id']} — {rec['fields'].get('Concept ID')}")
else:
    print(r.text[:300])
