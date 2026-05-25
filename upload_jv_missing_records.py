"""
Upload 3 missing JV Agreement Clauses (SG-MY) records to Airtable.
Records: JV-MY-NL01, JV-MY-P01, JV-MY-L01

Usage:
    python upload_jv_missing_records.py
"""

import os
import sys
import requests

BASE_ID    = "appwmBfW20jnFo64x"
TABLE_NAME = "JV Agreement Clauses (SG-MY)"

TOKEN_ENV_VARS = ["AIRTABLE_API_KEY", "AIRTABLE_TOKEN", "AIRTABLE_PAT"]

def get_token():
    for env in TOKEN_ENV_VARS:
        t = os.environ.get(env)
        if t:
            print(f"✅ Token found in ${env}")
            return t
    print("❌ No Airtable token found.")
    print("   Set it with: $env:AIRTABLE_API_KEY = 'patXXXXXX...'")
    sys.exit(1)

RECORDS = [
    {
        "Concept ID": "JV-MY-NL01",
        "Label": "National Language Act — Bahasa Malaysia",
        "SG Behavior": "No language requirement for commercial agreements in Singapore — English only is valid",
        "MY Requirement": "National Language Act 1963/67 (Act 32): Bahasa Malaysia is the official language; certain documents may require Bahasa Malaysia; dual-language approach recommended for enforceability and regulatory compliance",
        "Operation": "INSERT",
        "Template Clause": "[DUAL LANGUAGE RECOMMENDED]: This Agreement may be executed in both Bahasa Malaysia and English. In the event of any inconsistency between the Bahasa Malaysia and English versions, the [PREVAILING VERSION: select — English / Bahasa Malaysia] version shall prevail.\n\n[ALTERNATIVE — ENGLISH ONLY WITH ACKNOWLEDGMENT]: The Parties agree that this Agreement shall be in the English language. The Parties acknowledge that the National Language Act 1963/67 (Act 32) designates Bahasa Malaysia as the official language of Malaysia and that certain regulatory filings or court proceedings may require certified translation into Bahasa Malaysia. Each Party shall bear the cost of any translation required for its own regulatory or legal purposes.",
        "Statutory Reference": "National Language Act 1963/67 (Act 32); Courts of Judicature Act 1964 s.8 (court proceedings in Bahasa Malaysia)",
        "Statutory Detail": "KEY DIFFERENCE FROM INDONESIA: The National Language Act 1963/67 situation in Malaysia is meaningfully less strict than Indonesia's UU Bahasa (Law No. 24/2009). Malaysian courts regularly adjudicate English-language commercial contracts. However: (a) court proceedings in Malaysia are conducted in Bahasa Malaysia (Courts of Judicature Act 1964 s.8); (b) certain regulatory submissions may require Bahasa Malaysia documentation; (c) for government/GLC contracts, Bahasa Malaysia may be contractually required. For arbitration (AIAC/SIAC): English is the agreed language — no Bahasa Malaysia issue.",
        "Risk Level": "Medium",
        "Requires Human Review": True,
        "Notes": "MATERIAL DIFFERENCE FROM INDONESIA: English-only agreements are enforceable in Malaysian courts for B2B commercial matters — less strict than Indonesia's UU Bahasa. However: (1) court proceedings require Bahasa Malaysia — budget for certified translation if dispute is anticipated; (2) government/GLC contracts typically require Bahasa Malaysia; (3) SSM and regulatory filings may require Bahasa Malaysia versions. PARAMETERIZED — user selects: (a) English only; (b) dual-language with English prevailing; (c) dual-language with Bahasa Malaysia prevailing (for government contracts).",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Joint Venture Agreement (SG→MY)",
    },
    {
        "Concept ID": "JV-MY-P01",
        "Label": "MY PDPA 2010 — personal data protection",
        "SG Behavior": "SG PDPA 2012; PDPC; 3-day breach notification; 11 data protection provisions",
        "MY Requirement": "Personal Data Protection Act 2010 (Act 709); PDPD Commissioner; 7 data protection principles; no mandatory breach notification timeline yet (amendment pending); Singapore IS on MY cross-border whitelist",
        "Operation": "INSERT",
        "Template Clause": "Each Party shall process personal data of the other Party's personnel, clients, and counterparties in compliance with the Personal Data Protection Act 2010 (Act 709) ('MY PDPA') and its Regulations. In particular:\n(a) General Principle: personal data shall not be processed without the data subject's consent unless processing is permitted under MY PDPA;\n(b) Notice and Choice: data subjects shall be notified of the purposes of processing before or at the time of collection (MY PDPA s.7);\n(c) Disclosure Limitation: personal data shall not be disclosed without consent except as permitted under MY PDPA;\n(d) Security: each Party shall implement reasonable security measures to protect personal data against loss, misuse, modification, or unauthorised disclosure (MY PDPA s.9);\n(e) Retention: personal data shall not be retained longer than necessary for the purposes for which it was collected;\n(f) Data Integrity: personal data shall be accurate, complete, not misleading, and kept up-to-date;\n(g) Access and Correction: data subjects have the right to access and correct their personal data (MY PDPA ss.30-34);\n(h) Cross-Border Transfer: personal data shall not be transferred outside Malaysia except to countries in the prescribed whitelist or with adequate safeguards. [NOTE: Singapore is on the MY PDPA cross-border whitelist — SG to MY data transfers are permitted with appropriate safeguards];\n(i) Data Breach: in the event of a personal data breach, the affected Party shall notify the PDPD Commissioner and take remedial action in accordance with the MY PDPA and any applicable regulations [NOTE: no mandatory notification timeline currently prescribed — monitor MY PDPA Amendment Bill for changes, expected to introduce mandatory 72-hour notification].",
        "Statutory Reference": "Personal Data Protection Act 2010 (Act 709); Personal Data Protection Regulations 2013; Personal Data Protection Standards 2015; PDPD Commissioner (pdp.gov.my); MY PDPA Amendment Bill (pending)",
        "Statutory Detail": "MY PDPA 2010 vs SG PDPA 2012 key differences: 1. BREACH NOTIFICATION: MY PDPA has no mandatory breach notification timeline currently — SG PDPA requires 3-day notification. Amendment bill pending — likely to introduce mandatory 72-hour notification when enacted. Monitor pdp.gov.my. 2. SEVEN PRINCIPLES: General, Notice and Choice, Disclosure, Security, Retention, Data Integrity, Access (vs SG's 11 provisions). 3. CROSS-BORDER WHITELIST: Singapore IS on Malaysia's prescribed list — SG to MY data transfers permitted with appropriate safeguards. 4. SECTORAL APPLICATION: MY PDPA does not apply to Federal and State Governments; applies only to private sector data users. 5. SENSITIVE PERSONAL DATA: health, political opinions, religious beliefs, criminal records — require explicit consent under MY PDPA s.40. 6. ENFORCEMENT: PDPD Commissioner can impose fines; criminal penalties for serious breaches (up to MYR 500,000 and/or imprisonment up to 3 years).",
        "Risk Level": "High",
        "Requires Human Review": True,
        "Notes": "FULL_AUTO — mandatory for all SG-MY documents. SG is on MY cross-border whitelist — SG to MY data flows are less restricted than SG to ID flows. No mandatory breach notification timeline YET — monitor MY PDPA Amendment Bill. Sensitive personal data (health, criminal records) requires explicit consent under MY PDPA s.40. PDPA does not apply to government entities — relevant where either party is a GLC.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Joint Venture Agreement (SG→MY)",
    },
    {
        "Concept ID": "JV-MY-L01",
        "Label": "Labuan IBFC — cross-border structuring consideration",
        "SG Behavior": "No equivalent offshore financial centre structuring in SG context; Variable Capital Companies (VCC) as SG fund vehicle",
        "MY Requirement": "Labuan International Business and Financial Centre (Labuan IBFC) — Malaysia's offshore financial jurisdiction; frequently used for SG to MY cross-border holding structures, treasury, IP holding, and regional headquarters",
        "Operation": "REFERENCE_ONLY",
        "Template Clause": "STRUCTURING NOTE — LAWYER REVIEW REQUIRED\n\nThis Agreement has been drafted on the basis that the parties are contracting directly under Malaysian onshore law. Where the transaction involves a cross-border holding structure, treasury function, IP ownership, or regional headquarters arrangement between Singapore and Malaysia, the use of a Labuan entity (incorporated under the Labuan Companies Act 1990 in the Labuan International Business and Financial Centre) may offer material tax and structuring advantages.\n\nLabuan entities relevant to SG-MY structures:\n(a) Labuan company: 3% corporate tax on audited net profits from Labuan business activity (vs Malaysia onshore 24%); no WHT on dividends or royalties paid by Labuan entity to foreign shareholders;\n(b) Labuan Holding Company: holds shares in Malaysian Sdn Bhd; dividends from Sdn Bhd to Labuan holding are exempt from Malaysian WHT under Labuan regime;\n(c) Labuan IP Holding: holds IP licensed to operating entities in Malaysia and the region; royalties received subject to 3% Labuan corporate tax;\n(d) Malaysia-Singapore DTA: Labuan entities may access reduced DTA withholding rates — subject to LHDN substance requirements and anti-treaty-shopping rules.\n\nIf a Labuan structure is being considered for this transaction, obtain specific tax and legal advice from qualified Malaysian and Singapore advisers before executing any agreements.",
        "Statutory Reference": "Labuan Companies Act 1990 (Act 441); Labuan Business Activity Tax Act 1990 (Act 445); Labuan Financial Services Authority (LFSA) — labuanibfc.my; Malaysia-Singapore DTA (anti-treaty-shopping provisions); Income Tax Act 1967 s.3A (Labuan provisions)",
        "Statutory Detail": "Labuan IBFC is Malaysia's offshore financial jurisdiction on Labuan island (Federal Territory). Key features: 1. TAX RATE: 3% on audited net profits from Labuan business activity (vs 24% onshore Malaysian corporate tax). 2. NO WHT ON DISTRIBUTIONS: no withholding tax on dividends or interest paid by Labuan entities to non-residents. 3. DTA ACCESS: Labuan entities can access Malaysia's DTA network subject to substance requirements. 4. SUBSTANCE REQUIREMENTS: LHDN requires genuine economic substance in Labuan — management and control must be exercised in Labuan; nominee arrangements without genuine substance risk DTA access being denied. 5. COMMON SG-MY STRUCTURES: (a) SG HoldCo to Labuan Holding to Malaysian Sdn Bhd; (b) SG to Labuan IP Co; (c) SG to Labuan Treasury Co. 6. POST-BEPS: OECD BEPS requirements have tightened Labuan substance rules — structures must have genuine economic substance.",
        "Risk Level": "Medium",
        "Requires Human Review": True,
        "Notes": "REFERENCE_ONLY — Labuan is a structuring consideration, not a governing law clause. Include in JV and SHA where investment/holding structure is being designed. NOT applicable to Employment Contracts. Lawyer and tax adviser review mandatory before implementing any Labuan structure. Post-BEPS substance requirements are real — nominee structures without genuine activity in Labuan will not withstand LHDN scrutiny.",
        "Automation Type": "REFERENCE_ONLY",
        "Document Type": "Joint Venture Agreement (SG→MY)",
    },
]

def upload_records(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    table_encoded = TABLE_NAME.replace(" ", "%20")
    url = f"https://api.airtable.com/v0/{BASE_ID}/{table_encoded}"

    payload = {"records": [{"fields": r} for r in RECORDS]}
    resp = requests.post(url, headers=headers, json=payload)

    if resp.status_code not in (200, 201):
        print(f"❌ Upload failed {resp.status_code}: {resp.text[:500]}")
        sys.exit(1)

    data = resp.json()
    created = data.get("records", [])
    print(f"\n✅ Uploaded {len(created)} records to '{TABLE_NAME}':")
    for r in created:
        print(f"   {r['id']}  →  {r['fields'].get('Concept ID', '?')} | {r['fields'].get('Label', '?')}")

def main():
    token = get_token()
    print(f"\n📋 Uploading 3 missing JV records to Airtable...")
    print(f"   Base: {BASE_ID}")
    print(f"   Table: {TABLE_NAME}\n")
    upload_records(token)
    print(f"\n✅ Done. JV Agreement Clauses (SG-MY) now has all 8 records.")
    print("   Next JV adaptation will load records=8.")

if __name__ == "__main__":
    main()
