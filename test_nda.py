import requests
import json
import time

url = "https://web-production-d0182.up.railway.app"

with open("保密协议_测试.docx", "rb") as f:
    files = {"file": ("保密协议_测试.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    data = {
        "corridor": "CN_SG",
        "doc_type": "non_disclosure_agreement",
        "company_name": "Test Company Pte. Ltd."
    }
    print("Submitting NDA...")
    response = requests.post(f"{url}/adapt", files=files, data=data, timeout=30)

print(f"Status: {response.status_code}")
result = response.json()
print(json.dumps(result, indent=2))
job_id = result["job_id"]
print(f"Job ID: {job_id}")
print("Polling...")

for i in range(80):
    time.sleep(8)
    r = requests.get(f"{url}/status/{job_id}", timeout=30)
    print(f"Poll {i+1}: {r.text[:150]}")
    s = r.json()
    if s.get("status") == "complete":
        print("COMPLETE")
        print(json.dumps(s, indent=2))
        break
    elif s.get("status") == "error":
        print(f"ERROR: {s.get('error')}")
        break