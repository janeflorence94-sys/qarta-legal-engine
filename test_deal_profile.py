import requests
import json
import time

url = "https://web-production-d0182.up.railway.app"

deal_profile = json.dumps({
    "deal_size": "10M_50M",
    "leverage": "balanced",
    "ip_types": ["manufacturing_process", "trademark"],
    "strategic_importance": "strategic_entry",
    "timeline_urgency": "normal",
    "payment_currency": "SGD"
})

with open("05_test_contract_CN.docx", "rb") as f:
    files = {"file": ("05_test_contract_CN.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    data = {
        "corridor": "CN_SG",
        "doc_type": "employment_contract",
        "company_name": "Test JV Co. Pte. Ltd.",
        "deal_profile": deal_profile
    }
    print("Submitting with SGD 10M–50M deal profile...")
    response = requests.post(f"{url}/adapt", files=files, data=data, timeout=30)

print(f"Status: {response.status_code}")
result = response.json()
job_id = result["job_id"]
print(f"Job ID: {job_id}")

for i in range(80):
    time.sleep(8)
    r = requests.get(f"{url}/status/{job_id}", timeout=30)
    s = r.json()
    print(f"Poll {i+1}: {s.get('status')}")
    if s.get("status") == "complete":
        print(json.dumps(s, indent=2))
        break
    elif s.get("status") == "error":
        print(f"ERROR: {s.get('error')}")
        break