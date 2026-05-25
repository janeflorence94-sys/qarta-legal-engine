import requests, json, time, sys

url = "https://web-production-d0182.up.railway.app"

tests = [
    {
        "file": "SG_ID_NDA_Test.docx",
        "doc_type": "non_disclosure_agreement",
        "label": "SG→ID NDA",
        "deal_profile": {"deal_size": "50K_300K", "leverage": "balanced",
                        "strategic_importance": "medium_term", "timeline_urgency": "normal",
                        "payment_currency": "USD"}
    },
    {
        "file": "SG_ID_MOU_Test.docx",
        "doc_type": "mou",
        "label": "SG→ID MOU",
        "deal_profile": {"deal_size": "1M_5M", "leverage": "we_seek_access",
                        "strategic_importance": "strategic_entry", "timeline_urgency": "normal",
                        "mou_transaction_type": "Setting up a joint venture company together",
                        "due_diligence": "Yes — formal due diligence required",
                        "payment_currency": "USD"}
    },
    {
        "file": "SG_ID_ServiceAgreement_Test.docx",
        "doc_type": "service_agreement",
        "label": "SG→ID Service Agreement",
        "deal_profile": {"deal_size": "300K_1M", "leverage": "they_seek_access",
                        "strategic_importance": "long_term", "timeline_urgency": "normal",
                        "ip_types": ["software"],
                        "data_involved": "true",
                        "payment_currency": "USD"}
    },
    {
        "file": "SG_ID_JV_Test.docx",
        "doc_type": "jv_agreement",
        "label": "SG→ID JV Agreement",
        "deal_profile": {"deal_size": "10M_50M", "leverage": "we_seek_access",
                        "strategic_importance": "strategic_entry", "timeline_urgency": "normal",
                        "ip_types": ["manufacturing_process"],
                        "equity_split": "We hold the majority (more than 50%)",
                        "ceo_control": "We appoint the CEO and manage operations",
                        "ip_mechanism": "We contribute IP — we want to licence it",
                        "industry_sector": "Manufacturing / Industrial / Hardware",
                        "payment_currency": "USD"}
    },
    {
        "file": "SG_ID_NEDA_Test.docx",
        "doc_type": "non_exclusive_distribution",
        "label": "SG→ID Non-Exclusive Distribution",
        "deal_profile": {"deal_size": "300K_1M", "leverage": "they_seek_access",
                        "strategic_importance": "medium_term", "timeline_urgency": "normal",
                        "ip_types": ["trademark"],
                        "territory": "All of Southeast Asia",
                        "product_type": "Consumer goods (food, cosmetics, personal care)",
                        "payment_currency": "USD"}
    },
]

idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
t = tests[idx]

print(f"\nTesting: {t['label']}")
print(f"Corridor: SG_ID\n")

with open(t["file"], "rb") as f:
    files = {"file": (t["file"], f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    data = {
        "corridor": "SG_ID",
        "doc_type": t["doc_type"],
        "company_name": "Test Co.",
        "deal_profile": json.dumps(t["deal_profile"])
    }
    r = requests.post(f"{url}/adapt", files=files, data=data, timeout=30)

print(f"Status: {r.status_code}")
result = r.json()
job_id = result["job_id"]
print(f"Job ID: {job_id}")

for i in range(80):
    time.sleep(8)
    s = requests.get(f"{url}/status/{job_id}", timeout=30).json()
    print(f"Poll {i+1}: {s.get('status')}")
    if s.get("status") == "complete":
        print(f"\nCOMPLETE — {t['label']}")
        print(f"Records loaded: {s['metadata'].get('records_loaded')}")
        for k in ["clean", "commentary", "redline"]:
            print(f"  {k}: {url}/outputs/{job_id}_{k}.docx")
        break
    elif s.get("status") == "error":
        print(f"ERROR: {s.get('error')}")
        break