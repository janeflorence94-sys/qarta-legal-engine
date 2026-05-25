import requests
import json
import time

url = "https://web-production-d0182.up.railway.app"

with open("05_test_contract_CN.docx", "rb") as f:
    files = {"file": ("05_test_contract_CN.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    data = {
        "corridor": "CN_SG",
        "doc_type": "employment_contract",
        "company_name": "Test Company Pte. Ltd."
    }
    print("Sending request to /adapt endpoint...")
    response = requests.post(f"{url}/adapt", files=files, data=data, timeout=30)

print(f"Status code: {response.status_code}")
result = response.json()
job_id = result["job_id"]
print(f"Job ID: {job_id}")
print("Polling for completion...")

while True:
    time.sleep(5)
    status_response = requests.get(f"{url}/status/{job_id}", timeout=30)
print(f"Raw: {status_response.text[:200]}")
status = status_response.json()
print(f"Status: {status.get('status', 'NO STATUS KEY')}")
    if status["status"] == "complete":
        print(json.dumps(status, indent=2))
        break
    elif status["status"] == "error":
        print(f"Error: {status.get('error')}")
        break