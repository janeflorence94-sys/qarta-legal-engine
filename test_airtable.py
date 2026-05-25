import os
import requests
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("AIRTABLE_API_KEY")
base = os.getenv("AIRTABLE_BASE_ID")

tables = [
    "Service Agreement Clauses",
    "PDPA Data Protection Clauses",
    "Employment Contract Clauses",
    "NDA Clauses (Demo Tier)",
    "Rewrite Strategies"
]

for table in tables:
    url = f"https://api.airtable.com/v0/{base}/{table.replace(' ', '%20').replace('(', '%28').replace(')', '%29')}?maxRecords=1"
    r = requests.get(url, headers={"Authorization": f"Bearer {key}"})
    print(f"{table}: {r.status_code} ({'OK' if r.status_code == 200 else 'FAIL'})")
