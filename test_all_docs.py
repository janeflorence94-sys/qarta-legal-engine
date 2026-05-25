import requests, json, time, sys

url = "https://web-production-d0182.up.railway.app"

tests = [
    {
        "file": "合作意向书_测试.docx",
        "doc_type": "mou",
        "label": "MOU",
        "deal_profile": {"deal_size": "1M_5M", "leverage": "balanced", 
                        "strategic_importance": "long_term", "timeline_urgency": "normal",
                        "mou_transaction_type": "Distribution arrangement — we supply, they sell",
                        "exclusivity": "Yes — neither party can negotiate with others",
                        "due_diligence": "Yes — formal due diligence required"}
    },
    {
        "file": "合资经营协议_测试.docx",
        "doc_type": "jv_agreement", 
        "label": "JV Agreement",
        "deal_profile": {"deal_size": "10M_50M", "leverage": "balanced",
                        "strategic_importance": "strategic_entry", "timeline_urgency": "normal",
                        "ip_types": ["manufacturing_process"],
                        "equity_split": "50:50 — equal ownership",
                        "ceo_control": "We appoint the CEO and manage operations",
                        "ip_mechanism": "We contribute IP — we want to licence it",
                        "industry_sector": "Manufacturing / Industrial / Hardware",
                        "payment_currency": "SGD"}
    },
    {
        "file": "独家经销协议_测试.docx",
        "doc_type": "exclusive_distribution",
        "label": "Exclusive Distribution",
        "deal_profile": {"deal_size": "1M_5M", "leverage": "they_seek_access",
                        "strategic_importance": "long_term", "timeline_urgency": "normal",
                        "ip_types": ["trademark"],
                        "territory": "Singapore only",
                        "product_type": "Consumer goods (food, cosmetics, personal care)",
                        "minimum_purchase": "Yes — with consequences if target is missed",
                        "payment_currency": "SGD"}
    },
    {
        "file": "非独家经销协议_测试.docx",
        "doc_type": "non_exclusive_distribution",
        "label": "Non-Exclusive Distribution",
        "deal_profile": {"deal_size": "50K_300K", "leverage": "balanced",
                        "strategic_importance": "medium_term", "timeline_urgency": "normal",
                        "territory": "Singapore only",
                        "product_type": "Electronics or electrical goods",
                        "payment_currency": "SGD"}
    },
]

# Run one test at a time — pass index as argument
# python test_all_docs.py 0  (MOU)
# python test_all_docs.py 1  (JV)
# python test_all_docs.py 2  (Exclusive Dist)
# python test_all_docs.py 3  (Non-Exclusive Dist)

idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
t = tests[idx]

print(f"\nTesting: {t['label']}")
print(f"File: {t['file']}")
print(f"Doc type: {t['doc_type']}\n")

with open(t["file"], "rb") as f:
    files = {"file": (t["file"], f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    data = {
        "corridor": "CN_SG",
        "doc_type": t["doc_type"],
        "company_name": "Test Co. Pte. Ltd.",
        "deal_profile": json.dumps(t["deal_profile"])
    }
    r = requests.post(f"{url}/adapt", files=files, data=data, timeout=30)

print(f"Status: {r.status_code}")
result = r.json()
job_id = result["job_id"]
print(f"Job ID: {job_id}")
print("Polling...")

for i in range(80):
    time.sleep(8)
    s = requests.get(f"{url}/status/{job_id}", timeout=30).json()
    print(f"Poll {i+1}: {s.get('status')}")
    if s.get("status") == "complete":
        print(f"\nCOMPLETE — {t['label']}")
        print(f"Records loaded: {s['metadata'].get('records_loaded', 'unknown')}")
        files_out = s.get("files", {})
        for k, v in files_out.items():
            job_short = job_id.split("-")[0]
            print(f"  {k}: {url}/outputs/{job_id}_{k}.docx")
        break
    elif s.get("status") == "error":
        print(f"ERROR: {s.get('error')}")
        break