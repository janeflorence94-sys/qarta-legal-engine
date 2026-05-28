"""Quick sanity-check for get_table_name corridor suffix logic."""
from airtable_loader import get_table_name

cases = [
    ("CN_SG", "employment_contract", "Employment Contract Clauses (CN-SG)"),
    ("CN_SG", "nda",                 "NDA Clauses (Demo Tier) (CN-SG)"),
    ("SG_MY", "employment_contract", "Employment Contract Clauses (SG-MY)"),
    ("SG_MY", "franchise",           "Franchise Agreement Clauses (SG-MY)"),
    ("SG_ID", "nda",                 "NDA Clauses (SG-ID)"),
    ("SG_MY", "mou",                 "MOU Clauses (SG-MY)"),
]

all_ok = True
for corridor, doc_type, expected in cases:
    result = get_table_name(corridor, doc_type)
    status = "OK" if result == expected else "FAIL"
    if result != expected:
        all_ok = False
    print(f"  [{status}]  {corridor}/{doc_type}  ->  {result}")
    if result != expected:
        print(f"         expected: {expected}")

print()
print("All checks passed." if all_ok else "FAILURES — see above.")
