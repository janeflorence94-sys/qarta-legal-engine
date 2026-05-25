"""
Qarta SG-ID LCM Upload Script
Run: python upload_sgid_lcm.py
Requirements: pip install requests
"""
import requests
import json
import time

API_KEY = "pataU1CHASPyWivFC.906b7535e4754d1a9715bd12c5150216a5e7035e1367f344086465b08aed5a2f"
BASE_ID = "appwmBfW20jnFo64x"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

ALL_DATA = {
  "NDA Clauses (SG-ID)": {
    "headers": [
      "Concept ID",
      "Label",
      "SG Behavior",
      "ID Requirement",
      "Operation",
      "Template Clause",
      "Statutory Reference",
      "Statutory Detail",
      "Risk Level",
      "Requires Human Review",
      "Notes",
      "Automation Type",
      "Document Type"
    ],
    "records": [
      {
        "Concept ID": "NDA-ID-001",
        "Label": "Governing law",
        "SG Behavior": "Singapore law governs NDA; SIAC or Singapore courts as dispute forum",
        "ID Requirement": "Indonesian law (Hukum Indonesia) as governing law for Indonesian parties; domestic disputes under Indonesian courts or BANI",
        "Operation": "REPLACE",
        "Template Clause": "This Agreement shall be governed by and construed in accordance with the laws of the Republic of Indonesia.",
        "Statutory Reference": "Indonesian Civil Code (Burgerlijk Wetboek / KUHPerdata); Law No. 30/1999 on Arbitration and Alternative Dispute Resolution",
        "Statutory Detail": "Indonesian law applies to contracts executed or performed in Indonesia. For cross-border NDAs between SG and ID parties, Indonesian courts will often apply Indonesian law regardless of governing law clause if performance is in Indonesia. For enforceability of confidentiality obligations against Indonesian parties, Indonesian law governing clauses are strongly recommended.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "Indonesian law governing clause strongly recommended when Indonesian party is the recipient of confidential information — Indonesian courts are far more willing to enforce obligations under Indonesian law.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Non-Disclosure Agreement"
      },
      {
        "Concept ID": "NDA-ID-002",
        "Label": "Dispute resolution",
        "SG Behavior": "SIAC arbitration or Singapore courts",
        "ID Requirement": "BANI (Badan Arbitrase Nasional Indonesia) or SIAC with Indonesian seat; Indonesian courts for domestic enforcement",
        "Operation": "REPLACE",
        "Template Clause": "Any dispute arising out of or in connection with this Agreement shall be referred to and finally resolved by arbitration administered by the Singapore International Arbitration Centre (SIAC) in accordance with its Arbitration Rules, with the seat of arbitration in Singapore. The tribunal shall consist of one (1) arbitrator. The language of arbitration shall be English.",
        "Statutory Reference": "Law No. 30/1999 on Arbitration; New York Convention (ratified by Indonesia via Presidential Decree No. 34/1981)",
        "Statutory Detail": "Indonesia is a New York Convention signatory. SIAC awards are enforceable in Indonesia through the Central Jakarta District Court. Indonesian courts have occasionally refused enforcement on public policy grounds — SIAC is generally preferred over BANI for Singapore parties due to international enforceability and procedural certainty.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "SIAC strongly recommended over Indonesian courts for SG→ID NDAs. Indonesian court proceedings are slow and unpredictable for foreign parties. BANI is acceptable if Indonesian party insists on local arbitration.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Non-Disclosure Agreement"
      },
      {
        "Concept ID": "NDA-ID-003",
        "Label": "Confidential Information definition",
        "SG Behavior": "Broad definition covering all business, technical, financial information disclosed in any form",
        "ID Requirement": "Indonesian law recognises trade secrets (rahasia dagang) under Law No. 30/2000 on Trade Secrets; definition must align with statutory categories for court enforcement",
        "Operation": "REWRITE",
        "Template Clause": "\"Confidential Information\" means all information disclosed by the Disclosing Party to the Receiving Party, in any form or medium, whether oral, written, electronic, or visual, that is designated as confidential or that reasonably should be understood to be confidential given the nature of the information and the circumstances of disclosure, including but not limited to: technical data, trade secrets (rahasia dagang), know-how, research, product plans, products, services, customers, markets, software, developments, inventions, processes, formulas, technology, designs, drawings, engineering, financial data, personnel data, and business plans.",
        "Statutory Reference": "Law No. 30/2000 on Trade Secrets (Rahasia Dagang); Indonesian Civil Code Art. 1233",
        "Statutory Detail": "Indonesian Law No. 30/2000 defines trade secrets (rahasia dagang) as business information that is not publicly known in the relevant business sector, has economic value, and is maintained as secret by the owner through reasonable steps. Including the Indonesian term \"rahasia dagang\" in the definition strengthens enforceability in Indonesian courts.",
        "Risk Level": "Medium",
        "Requires Human Review": "No",
        "Notes": "Include Indonesian term rahasia dagang alongside English definition for dual enforceability. Indonesian courts respond better to Indonesian-language statutory references.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Disclosure Agreement"
      },
      {
        "Concept ID": "NDA-ID-004",
        "Label": "Permitted disclosure — Representatives",
        "SG Behavior": "Disclosure permitted to employees, directors, legal advisers, and professional advisers on need-to-know basis",
        "ID Requirement": "Same principle applies; add Indonesian notaris (notary) and konsultan hukum (legal consultant) as recognised categories",
        "Operation": "REWRITE",
        "Template Clause": "The Receiving Party may disclose Confidential Information to its directors, officers, employees, notaries (notaris), legal consultants (konsultan hukum), and professional advisers who: (a) have a need to know such information for the purpose of evaluating the Proposed Transaction; and (b) are bound by confidentiality obligations no less restrictive than those in this Agreement.",
        "Statutory Reference": "Law No. 30/2000 Art. 5; Indonesian Notary Law (Law No. 2/2014)",
        "Statutory Detail": "Indonesian notaries (notaris) play a mandatory role in many commercial transactions — they must authenticate certain documents and may need access to confidential information. Excluding notaries from permitted disclosure could make the NDA unworkable in practice. Indonesian legal consultants (konsultan hukum) are distinct from advocates (advokat) under Indonesian law.",
        "Risk Level": "Low",
        "Requires Human Review": "No",
        "Notes": "Indonesian commercial practice requires notary involvement in company formations, land transactions, and certain agreements. Always include notaris as a permitted disclosure category.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Disclosure Agreement"
      },
      {
        "Concept ID": "NDA-ID-005",
        "Label": "Standard carve-outs",
        "SG Behavior": "Public domain, prior knowledge, independent development, legally required disclosure",
        "ID Requirement": "Same four carve-outs apply; add government regulatory disclosure requirement specific to Indonesian licensing authorities (BKPM/OSS, OJK for financial services)",
        "Operation": "REWRITE",
        "Template Clause": "The obligations in this Agreement do not apply to information that: (a) is or becomes publicly available through no act or omission of the Receiving Party; (b) was already known to the Receiving Party without restriction prior to disclosure; (c) is independently developed by the Receiving Party without use of the Confidential Information; (d) is required to be disclosed by applicable law, court order, or regulatory authority including the Indonesian Investment Coordinating Board (BKPM/OSS) or other Indonesian government authority, provided that the Receiving Party gives prior written notice to the Disclosing Party to the extent permitted by law.",
        "Statutory Reference": "Law No. 30/2000 Art. 5; Law No. 25/2007 on Capital Investment",
        "Statutory Detail": "BKPM (now integrated into OSS) may require disclosure of investment documents as part of licensing requirements. The Indonesian Financial Services Authority (OJK) may require disclosure for regulated entities. These are legitimate regulatory carve-outs that must be explicitly included.",
        "Risk Level": "Low",
        "Requires Human Review": "No",
        "Notes": "Indonesian regulatory bodies including BKPM/OSS, OJK, and Bank Indonesia may require document disclosure as part of licensing or supervisory processes.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Disclosure Agreement"
      },
      {
        "Concept ID": "NDA-ID-006",
        "Label": "Confidentiality obligation duration",
        "SG Behavior": "Typically 3 years for general information; indefinite for trade secrets",
        "ID Requirement": "Same principle; Law No. 30/2000 does not limit trade secret protection duration — indefinite protection available for qualifying trade secrets",
        "Operation": "REWRITE",
        "Template Clause": "The Receiving Party shall maintain the confidentiality of Confidential Information for a period of [DURATION: recommend three (3) years] from the date of disclosure, except that trade secrets (rahasia dagang) shall be maintained in confidence indefinitely for as long as they retain their status as trade secrets under Law No. 30/2000.",
        "Statutory Reference": "Law No. 30/2000 on Trade Secrets Art. 1, 2, 5",
        "Statutory Detail": "Indonesian Law No. 30/2000 provides indefinite protection for qualifying trade secrets (rahasia dagang) — those that: (a) are not publicly known in the relevant business sector; (b) have economic value; and (c) are maintained as secret through reasonable steps. A time-limited confidentiality clause may inadvertently strip trade secrets of their statutory protection after the contractual period expires.",
        "Risk Level": "Medium",
        "Requires Human Review": "No",
        "Notes": "Dual duration structure — 3 years general, indefinite for rahasia dagang — maximises protection under Indonesian law.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Non-Disclosure Agreement"
      },
      {
        "Concept ID": "NDA-ID-007",
        "Label": "Purpose limitation",
        "SG Behavior": "Information used only for evaluating the proposed transaction",
        "ID Requirement": "Same principle; specify the Proposed Transaction clearly — Indonesian courts apply purpose limitation strictly",
        "Operation": "REWRITE",
        "Template Clause": "The Receiving Party shall use the Confidential Information solely for the purpose of evaluating, negotiating, and implementing [PROPOSED TRANSACTION: describe the contemplated business arrangement] (the \"Proposed Transaction\") and for no other purpose.",
        "Statutory Reference": "Indonesian Civil Code Art. 1338 (freedom of contract); Law No. 30/2000 Art. 13",
        "Statutory Detail": "Indonesian courts apply contractual purpose limitations literally. If confidential information is used outside the stated purpose, the Disclosing Party can seek injunctive relief and damages under both contract law and Law No. 30/2000.",
        "Risk Level": "Medium",
        "Requires Human Review": "No",
        "Notes": "Describe the Proposed Transaction specifically — vague purpose clauses are harder to enforce in Indonesian courts.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Non-Disclosure Agreement"
      },
      {
        "Concept ID": "NDA-ID-008",
        "Label": "Personal data protection (UU PDP)",
        "SG Behavior": "PDPA compliance clause for personal data shared under NDA",
        "ID Requirement": "UU PDP (Law No. 27/2022) — Indonesia's Personal Data Protection Law; mandatory compliance clause for any NDA involving personal data",
        "Operation": "INSERT",
        "Template Clause": "To the extent any Confidential Information constitutes personal data as defined under Law No. 27/2022 on Personal Data Protection (UU PDP), each Party shall process such personal data in accordance with UU PDP and shall: (a) process personal data only for the purpose specified in this Agreement; (b) implement appropriate technical and organisational security measures; (c) not transfer personal data outside Indonesia except in compliance with UU PDP Chapter VII; and (d) promptly notify the other Party of any personal data breach involving the other Party's personal data.",
        "Statutory Reference": "Law No. 27/2022 (UU PDP); Government Regulation No. 71/2019 on Electronic Systems and Transactions",
        "Statutory Detail": "UU PDP came into force in October 2022 with a 2-year transition period ending October 2024. As of 2024, UU PDP is fully in force. Cross-border personal data transfers from Indonesia require adequate protection in the receiving country. Singapore's PDPA is generally considered adequate but this should be confirmed with Indonesian counsel.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "UU PDP is now fully enforceable. Any NDA involving personal data of Indonesian citizens or residents must include UU PDP compliance obligations. Singapore entities receiving Indonesian personal data must ensure PDPA adequacy.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Disclosure Agreement"
      },
      {
        "Concept ID": "NDA-ID-009",
        "Label": "Return or destruction of information",
        "SG Behavior": "Return or certify destruction on request or termination",
        "ID Requirement": "Same principle; Indonesian courts expect specific return/destruction obligations for trade secrets (rahasia dagang) enforcement",
        "Operation": "REWRITE",
        "Template Clause": "Upon the Disclosing Party's written request or upon termination of this Agreement, the Receiving Party shall promptly (and in any event within [TIMEFRAME: recommend fourteen (14) calendar days]): (a) return all Confidential Information in tangible form to the Disclosing Party; or (b) destroy all Confidential Information and certify such destruction in writing. The Receiving Party may retain copies required by applicable Indonesian law or regulation, subject to continuing confidentiality obligations.",
        "Statutory Reference": "Law No. 30/2000 Art. 5; Indonesian Civil Code Art. 1265",
        "Statutory Detail": "Indonesian trade secret law (Law No. 30/2000) supports injunctive relief for failure to return or destroy trade secrets. The 14-day timeframe is consistent with Indonesian commercial practice.",
        "Risk Level": "Low",
        "Requires Human Review": "No",
        "Notes": "Include Indonesian regulatory retention carve-out — certain documents must be retained under Indonesian tax law (10 years) and company law.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Disclosure Agreement"
      },
      {
        "Concept ID": "NDA-ID-010",
        "Label": "Remedies — injunctive relief",
        "SG Behavior": "Acknowledge monetary damages may be inadequate; right to seek injunctive relief",
        "ID Requirement": "Indonesian courts can grant provisional injunctions (putusan sela / penetapan sementara); specify Indonesian court jurisdiction for interim relief",
        "Operation": "INSERT",
        "Template Clause": "The Receiving Party acknowledges that breach of this Agreement would cause irreparable harm to the Disclosing Party for which monetary damages would be an inadequate remedy. Accordingly, the Disclosing Party shall be entitled to seek injunctive relief (penetapan sementara) or other equitable relief from any competent Indonesian court or the arbitral tribunal, without the need to post bond or other security, in addition to any other remedies available at law or in equity.",
        "Statutory Reference": "Law No. 30/1999 Art. 32 (arbitral interim measures); Indonesian Civil Procedural Law (HIR/RBg)",
        "Statutory Detail": "Indonesian courts can grant provisional injunctions under HIR Art. 180 and RBg Art. 191. Indonesian arbitrators can grant interim measures under Law No. 30/1999 Art. 32. The Indonesian term \"penetapan sementara\" for provisional injunction should be included for court clarity.",
        "Risk Level": "Medium",
        "Requires Human Review": "No",
        "Notes": "Including the Indonesian legal term penetapan sementara makes this clause directly actionable in Indonesian courts without translation argument.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Disclosure Agreement"
      },
      {
        "Concept ID": "NDA-ID-011",
        "Label": "No licence or partnership",
        "SG Behavior": "No IP licence, no partnership, no obligation to proceed",
        "ID Requirement": "Same; Indonesian law does not require specific disclaimers but express negation prevents implied partnership (persekutuan) claims under Indonesian Civil Code",
        "Operation": "INSERT",
        "Template Clause": "Nothing in this Agreement shall be construed as: (a) granting any licence, right, or interest in any Confidential Information or intellectual property of the Disclosing Party; (b) creating any partnership (persekutuan), joint venture, agency, or employment relationship between the Parties; or (c) obligating either Party to enter into any further agreement or to proceed with the Proposed Transaction.",
        "Statutory Reference": "Indonesian Civil Code Art. 1618-1652 (partnership); Law No. 40/2007 on Limited Liability Companies",
        "Statutory Detail": "Indonesian Civil Code recognises implied partnership (maatschap/persekutuan) where parties jointly pursue a common economic goal. An NDA that involves sharing of proprietary information for a common purpose could inadvertently imply a partnership absent an express disclaimer.",
        "Risk Level": "Low",
        "Requires Human Review": "No",
        "Notes": "Include Indonesian term persekutuan to prevent implied partnership arguments under Indonesian Civil Code.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Disclosure Agreement"
      },
      {
        "Concept ID": "NDA-ID-012",
        "Label": "Language and translation",
        "SG Behavior": "English as governing language; no Indonesian language requirement",
        "ID Requirement": "Law No. 24/2009 on Flag, Language, State Emblem, and National Anthem (UU Bahasa) requires Indonesian language for agreements involving Indonesian government entities or Indonesian private parties in certain contexts",
        "Operation": "INSERT",
        "Template Clause": "This Agreement is executed in the English language. [PARAMETERIZED — If Indonesian party requires dual language]: This Agreement shall also be executed in Bahasa Indonesia. In the event of any conflict between the English version and the Bahasa Indonesia version, the [English / Bahasa Indonesia] version shall prevail.",
        "Statutory Reference": "Law No. 24/2009 (UU Bahasa) Art. 31; Supreme Court Circular Letter No. 3/2010",
        "Statutory Detail": "Law No. 24/2009 Art. 31 requires Indonesian language for agreements involving Indonesian government entities. For private party agreements, the Cipta Kerja (Omnibus) Law partially relaxed this requirement. However, Indonesian courts have invalidated contracts not in Bahasa Indonesia in certain cases (PT Bangun Karya Pratama Lestari v Nine AM Ltd, 2013). Best practice: dual-language with English prevailing for SG→ID commercial NDAs.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "CRITICAL: Law No. 24/2009 language requirement has caused contract invalidation in Indonesian courts. Always advise dual-language execution for significant SG→ID agreements. The 2013 Nine AM case is the leading precedent.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Non-Disclosure Agreement"
      },
      {
        "Concept ID": "NDA-ID-013",
        "Label": "Stamp duty (Bea Materai)",
        "SG Behavior": "No stamp duty requirement for NDAs in Singapore",
        "ID Requirement": "Indonesian Stamp Duty Law (UU Bea Materai No. 10/2020) — IDR 10,000 stamp duty required for agreements executed in Indonesia",
        "Operation": "INSERT",
        "Template Clause": "[INSERTED NOTICE — NOT A CONTRACTUAL CLAUSE] STAMP DUTY NOTE: Under Indonesian Law No. 10/2020 on Stamp Duty (Bea Materai), agreements executed in Indonesia or intended for use in Indonesian legal proceedings require affixing of a Bea Materai stamp of IDR 10,000 per original copy. Failure to affix Bea Materai does not void the contract but may affect admissibility in Indonesian courts until the duty is paid (nazegeling). The Indonesian party should ensure all original copies are properly stamped before execution.",
        "Statutory Reference": "Law No. 10/2020 on Stamp Duty (Bea Materai); Government Regulation No. 86/2021",
        "Statutory Detail": "Bea Materai of IDR 10,000 is required for: (a) documents used as evidence in court; (b) civil documents; (c) documents with a nominal value exceeding IDR 5,000,000. An unstamped agreement can be retroactively stamped (nazegeling) before use in court upon payment of the outstanding duty. Electronic Bea Materai is now available via Peruri (government printing authority).",
        "Risk Level": "Medium",
        "Requires Human Review": "No",
        "Notes": "Bea Materai does not void contracts but affects Indonesian court admissibility. Always flag this for Indonesian parties — Singapore parties are often unaware of this requirement.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Disclosure Agreement"
      },
      {
        "Concept ID": "NDA-ID-014",
        "Label": "Entire agreement and variation",
        "SG Behavior": "Entire agreement supersedes prior negotiations; written variation required",
        "ID Requirement": "Same principle; Indonesian Civil Code Art. 1338 recognises freedom of contract; written variation recommended to prevent implied modification arguments",
        "Operation": "INSERT",
        "Template Clause": "This Agreement constitutes the entire agreement between the Parties relating to the subject matter hereof and supersedes all prior agreements, representations, and understandings. No amendment or modification of this Agreement shall be valid unless made in writing and signed by authorised representatives of both Parties.",
        "Statutory Reference": "Indonesian Civil Code Art. 1338, 1320, 1321",
        "Statutory Detail": "Indonesian law recognises the principle of pacta sunt servanda (Art. 1338) — agreements must be performed. However, Indonesian courts can imply modification from conduct (itikad baik / good faith principle). An entire agreement clause prevents such implied modification arguments.",
        "Risk Level": "Low",
        "Requires Human Review": "No",
        "Notes": "Standard clause; Indonesian courts generally respect entire agreement clauses.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Disclosure Agreement"
      },
      {
        "Concept ID": "NDA-ID-015",
        "Label": "Notarisation requirement flag",
        "SG Behavior": "No notarisation required for NDAs in Singapore",
        "ID Requirement": "Notarisation (akta notaris) not legally required for NDAs but strengthens enforceability in Indonesian courts; strongly recommended for high-value arrangements",
        "Operation": "INSERT",
        "Template Clause": "[INSERTED NOTICE — NOT A CONTRACTUAL CLAUSE] NOTARISATION NOTE: Indonesian law does not require notarisation (akta notaris) for non-disclosure agreements. However, notarised agreements carry a stronger presumption of authenticity and are more readily enforceable in Indonesian courts. For arrangements involving significant commercial value or trade secrets, the Parties should consider executing this Agreement before an Indonesian notaris. A notarised akta notaris has the evidentiary status of an authentic deed (akta otentik) under Indonesian law.",
        "Statutory Reference": "Indonesian Notary Law (Law No. 2/2014); Indonesian Civil Procedure Law (HIR Art. 165)",
        "Statutory Detail": "An akta otentik (authentic notarial deed) has the highest evidentiary value in Indonesian courts and creates a rebuttable presumption of the truth of its contents. A private agreement (akta di bawah tangan) can be challenged on signature authenticity. For SG→ID NDAs involving significant trade secrets, notarisation is commercially advisable.",
        "Risk Level": "Low",
        "Requires Human Review": "No",
        "Notes": "Recommend notarisation for any SG→ID NDA where the underlying arrangement involves trade secrets worth more than USD 100,000.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Disclosure Agreement"
      }
    ]
  },
  "MOU Clauses (SG-ID)": {
    "headers": [
      "Concept ID",
      "Label",
      "SG Behavior",
      "ID Requirement",
      "Operation",
      "Template Clause",
      "Statutory Reference",
      "Statutory Detail",
      "Risk Level",
      "Requires Human Review",
      "Notes",
      "Automation Type",
      "Document Type"
    ],
    "records": [
      {
        "Concept ID": "MOU-ID-001",
        "Label": "Governing law",
        "SG Behavior": "Singapore law as governing law",
        "ID Requirement": "Indonesian law recommended for enforceability of binding provisions against Indonesian party; dual-law approach possible for SG→ID MOUs",
        "Operation": "PARAMETERIZED",
        "Template Clause": "This Memorandum of Understanding shall be governed by and construed in accordance with the laws of [GOVERNING LAW: recommend Indonesian law (Hukum Indonesia) for binding provisions; Singapore law acceptable if SIAC arbitration agreed].",
        "Statutory Reference": "Indonesian Civil Code Art. 1338; Law No. 30/1999 on Arbitration",
        "Statutory Detail": "For SG→ID MOUs, Indonesian law governing clauses make the binding carve-out provisions (confidentiality, exclusivity) more enforceable against Indonesian parties. However, Singapore law with SIAC arbitration is commercially standard for Singapore companies and provides procedural certainty.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "Key decision for SG→ID MOUs: Indonesian law is more enforceable locally but Singapore law provides procedural familiarity for SG party. PARAMETERIZED for user input.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Memorandum of Understanding"
      },
      {
        "Concept ID": "MOU-ID-002",
        "Label": "Dispute resolution",
        "SG Behavior": "SIAC arbitration or Singapore courts",
        "ID Requirement": "SIAC (Singapore-seated) strongly recommended over BANI or Indonesian courts for SG→ID commercial disputes; New York Convention enforcement available",
        "Operation": "REPLACE",
        "Template Clause": "Any dispute arising out of or in connection with this Memorandum of Understanding, including any question regarding its existence, validity, or termination, shall be referred to and finally resolved by arbitration administered by the Singapore International Arbitration Centre (SIAC) in accordance with the Arbitration Rules of the Singapore International Arbitration Centre for the time being in force. The seat of arbitration shall be Singapore. The tribunal shall consist of one (1) arbitrator. The language of the arbitration shall be English.",
        "Statutory Reference": "Law No. 30/1999; Presidential Decree No. 34/1981 (New York Convention ratification)",
        "Statutory Detail": "SIAC awards are enforceable in Indonesia through the Central Jakarta District Court under Presidential Decree No. 34/1981. BANI awards are only enforceable domestically. For SG→ID MOUs, SIAC is the clear preference for Singapore parties.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "SIAC over BANI is strongly recommended. Indonesian court proceedings are slow and expensive for foreign parties.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Memorandum of Understanding"
      },
      {
        "Concept ID": "MOU-ID-003",
        "Label": "Non-binding statement with binding carve-outs",
        "SG Behavior": "Non-binding statement with explicit list of binding carve-out clauses",
        "ID Requirement": "Same architecture required; Indonesian courts examine non-binding statements carefully — must be clear and comprehensive",
        "Operation": "INSERT",
        "Template Clause": "Except for clauses [LIST BINDING CLAUSES: confidentiality, exclusivity, governing law, dispute resolution, costs, announcements, no partnership, term/termination], which the Parties expressly agree are legally binding and enforceable, the remaining provisions of this Memorandum of Understanding are non-binding statements of the Parties' intentions and do not constitute a legally binding agreement. Neither Party shall have any legal obligation to enter into the Definitive Agreement or to complete the Proposed Transaction.",
        "Statutory Reference": "Indonesian Civil Code Art. 1320 (contract formation requirements); Art. 1338",
        "Statutory Detail": "Indonesian contract law requires four elements for a binding contract: agreement (sepakat), capacity (kecakapan), specific subject matter (hal tertentu), and lawful cause (sebab yang halal). A non-binding MOU deliberately lacks the \"sepakat\" (agreement/intention to be bound) element for its commercial terms. The non-binding statement clause makes this explicit.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "Most critical clause in any SG→ID MOU. Indonesian courts have found MOUs binding where language was ambiguous — comprehensive non-binding statement is essential.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Memorandum of Understanding"
      },
      {
        "Concept ID": "MOU-ID-004",
        "Label": "Purpose and contemplated transaction",
        "SG Behavior": "Non-binding description of proposed arrangement using intention language",
        "ID Requirement": "Use Indonesian \"bermaksud\" (intends) and \"berencana\" (plans) rather than \"menyetujui\" (agrees) or \"akan\" (shall) in non-binding sections",
        "Operation": "REWRITE",
        "Template Clause": "The Parties have entered into this Memorandum of Understanding to record their mutual understanding and non-binding intentions with respect to the Proposed Transaction. The Parties intend (bermaksud) to negotiate in good faith toward the execution of a definitive agreement on the terms contemplated herein. Nothing in this Memorandum of Understanding shall be construed as a binding commitment to complete the Proposed Transaction.",
        "Statutory Reference": "Indonesian Civil Code Art. 1338 (itikad baik / good faith)",
        "Statutory Detail": "Indonesian law recognises a general obligation of good faith (itikad baik) in contractual negotiations under Art. 1338. Unlike Singapore law (which does not impose a general duty to negotiate in good faith), Indonesian law may imply good faith obligations during the MOU period — this should be expressly limited to the specific matters agreed as binding.",
        "Risk Level": "Medium",
        "Requires Human Review": "No",
        "Notes": "Indonesian concept of itikad baik (good faith) is broader than Singapore law. The MOU should not rely on good faith obligations as a substitute for clear binding commitments.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Memorandum of Understanding"
      },
      {
        "Concept ID": "MOU-ID-005",
        "Label": "Exclusivity of negotiations",
        "SG Behavior": "Mutual or one-sided exclusivity for defined period; legally binding",
        "ID Requirement": "Same principle; Indonesian law supports exclusivity clauses; include Indonesian term \"eksklusivitas\" for clarity",
        "Operation": "PARAMETERIZED",
        "Template Clause": "[If exclusivity agreed]: During the Exclusivity Period of [DURATION: recommend 60 calendar days], each Party agrees exclusively (secara eksklusif) not to negotiate, discuss, or enter into any agreement with any third party with respect to any arrangement that is substantially similar to the Proposed Transaction. Breach of this clause shall entitle the non-breaching Party to seek injunctive relief and damages.",
        "Statutory Reference": "Indonesian Civil Code Art. 1338; Law No. 5/1999 on Prohibition of Monopoly Practices (if market power relevant)",
        "Statutory Detail": "Indonesian law supports exclusivity clauses as a matter of freedom of contract (Art. 1338). However, exclusivity clauses that restrict competition may attract scrutiny under Law No. 5/1999 (Competition Law) if the parties have significant market power in the relevant market.",
        "Risk Level": "Medium",
        "Requires Human Review": "Yes",
        "Notes": "Check KPPU (Komisi Pengawas Persaingan Usaha — Indonesian Competition Authority) implications if parties have significant market power.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Memorandum of Understanding"
      },
      {
        "Concept ID": "MOU-ID-006",
        "Label": "Confidentiality",
        "SG Behavior": "Binding confidentiality clause with standard carve-outs",
        "ID Requirement": "Same structure; align with Law No. 30/2000 (Trade Secrets) and UU PDP for personal data; include Indonesian terms for enforceability",
        "Operation": "REWRITE",
        "Template Clause": "Each Party agrees that the terms of this Memorandum of Understanding and all information disclosed in connection with the Proposed Transaction shall be treated as confidential (rahasia) and shall not be disclosed to any third party without the prior written consent of the other Party, except to the extent required by applicable Indonesian law or regulation. This clause is legally BINDING notwithstanding any other provision of this Memorandum of Understanding.",
        "Statutory Reference": "Law No. 30/2000 on Trade Secrets; UU PDP (Law No. 27/2022)",
        "Statutory Detail": "Indonesian courts enforce contractual confidentiality obligations under general contract law principles and Law No. 30/2000 for trade secrets. The express statement \"THIS CLAUSE IS BINDING\" is essential for SG→ID MOUs to ensure enforceability.",
        "Risk Level": "High",
        "Requires Human Review": "No",
        "Notes": "Always mark confidentiality as BINDING explicitly. Indonesian courts have found MOU confidentiality provisions unenforceable where the non-binding wrapper was not clearly limited.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Memorandum of Understanding"
      },
      {
        "Concept ID": "MOU-ID-007",
        "Label": "PT PMA structure flag",
        "SG Behavior": "No equivalent — Singapore companies can operate directly",
        "ID Requirement": "Foreign investment in Indonesia requires PT PMA structure; MOU should reference intended investment vehicle and BKPM/OSS approval requirement",
        "Operation": "INSERT",
        "Template Clause": "[INSERTED — APPLICABLE WHERE CONTEMPLATED TRANSACTION INVOLVES FOREIGN INVESTMENT IN INDONESIA]: The Parties acknowledge that the Proposed Transaction may require: (a) establishment of a foreign investment company (Perusahaan Penanaman Modal Asing / PT PMA) incorporated under Indonesian law; (b) investment licensing through the Online Single Submission (OSS) system administered by the Indonesian Investment Coordinating Board (BKPM); and (c) compliance with the Indonesian Positive Investment List under Government Regulation No. 5/2021. The Parties intend to address these regulatory requirements in the Definitive Agreement.",
        "Statutory Reference": "Law No. 25/2007 on Capital Investment; Government Regulation No. 5/2021 (Positive Investment List); OSS Regulation (BKPM Regulation No. 4/2021)",
        "Statutory Detail": "Foreign companies cannot directly operate in Indonesia without a local investment vehicle. PT PMA is the standard vehicle for foreign direct investment. The Positive Investment List (replacing the former Negative Investment List) specifies sectors open to foreign investment and maximum foreign ownership percentages. Minimum capital for PT PMA is IDR 10 billion (approximately USD 650,000).",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "CRITICAL for any SG→ID MOU involving business operations in Indonesia. PT PMA establishment takes 2-4 months. Minimum capital requirement IDR 10 billion must be flagged early.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Memorandum of Understanding"
      },
      {
        "Concept ID": "MOU-ID-008",
        "Label": "Costs and expenses",
        "SG Behavior": "Each party bears own costs",
        "ID Requirement": "Same; Indonesian commercial practice accepts costs provisions in MOUs",
        "Operation": "INSERT",
        "Template Clause": "Each Party shall bear its own costs and expenses (including legal fees, due diligence costs, and advisory fees) incurred in connection with this Memorandum of Understanding and the negotiation of the Proposed Transaction, regardless of whether the Proposed Transaction is completed.",
        "Statutory Reference": "Indonesian Civil Code Art. 1338",
        "Statutory Detail": "Indonesian law does not impose pre-contractual cost liability absent an express agreement. The costs clause prevents either party from claiming reimbursement of negotiation costs if the transaction fails.",
        "Risk Level": "Low",
        "Requires Human Review": "No",
        "Notes": "Standard clause; Indonesian courts respect express costs provisions.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Memorandum of Understanding"
      },
      {
        "Concept ID": "MOU-ID-009",
        "Label": "No partnership or agency",
        "SG Behavior": "Express disclaimer of partnership, agency, employment",
        "ID Requirement": "Same; include Indonesian terms persekutuan (partnership) and kuasa (agency) for enforceability",
        "Operation": "INSERT",
        "Template Clause": "Nothing in this Memorandum of Understanding shall be construed as creating any partnership (persekutuan), joint venture, agency (kuasa), or employment relationship between the Parties. Neither Party has authority to bind the other Party to any obligation.",
        "Statutory Reference": "Indonesian Civil Code Art. 1618 (partnership); Art. 1792 (agency/kuasa)",
        "Statutory Detail": "Indonesian Civil Code recognises implied partnerships and agency relationships from conduct. Express disclaimer using Indonesian legal terms prevents such arguments.",
        "Risk Level": "Low",
        "Requires Human Review": "No",
        "Notes": "Include Indonesian terms persekutuan and kuasa — Indonesian courts respond to Indonesian legal terminology.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Memorandum of Understanding"
      },
      {
        "Concept ID": "MOU-ID-010",
        "Label": "Term and termination",
        "SG Behavior": "6-month term with unilateral termination right on 14 days notice",
        "ID Requirement": "Same structure; Indonesian courts accept unilateral termination rights in non-binding MOUs",
        "Operation": "REWRITE",
        "Template Clause": "This Memorandum of Understanding shall be valid for a period of [TERM: recommend six (6) months] from the date of execution, unless earlier terminated. Either Party may terminate this Memorandum of Understanding by giving [NOTICE: recommend fourteen (14) calendar days] prior written notice to the other Party. This Memorandum of Understanding shall automatically terminate upon execution of the Definitive Agreement.",
        "Statutory Reference": "Indonesian Civil Code Art. 1266, 1267 (termination of agreements)",
        "Statutory Detail": "Indonesian Civil Code Art. 1266 requires court approval for termination of bilateral agreements unless the parties have expressly agreed to out-of-court termination. For MOUs with express unilateral termination rights, court approval is not required. The automatic termination on Definitive Agreement execution should be express to avoid uncertainty.",
        "Risk Level": "Medium",
        "Requires Human Review": "No",
        "Notes": "Indonesian Civil Code Art. 1266 court approval for termination is waived by express unilateral termination rights. Always include this waiver expressly.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Memorandum of Understanding"
      },
      {
        "Concept ID": "MOU-ID-011",
        "Label": "Language requirement (UU Bahasa)",
        "SG Behavior": "English as governing language",
        "ID Requirement": "Law No. 24/2009 (UU Bahasa) may require Bahasa Indonesia for agreements with Indonesian parties; dual-language strongly recommended",
        "Operation": "INSERT",
        "Template Clause": "This Memorandum of Understanding is executed in both the English language and Bahasa Indonesia. Both versions are equally authentic. In the event of any conflict between the English version and the Bahasa Indonesia version, the English version shall prevail.",
        "Statutory Reference": "Law No. 24/2009 (UU Bahasa) Art. 31; Supreme Court Circular No. 3/2010",
        "Statutory Detail": "Law No. 24/2009 Art. 31 requires Bahasa Indonesia for agreements involving Indonesian private parties in certain contexts. The 2013 Nine AM case established that courts can invalidate Indonesian-law agreements not in Bahasa Indonesia. Dual-language execution with English prevailing is the safest approach for SG→ID MOUs.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "CRITICAL: Always recommend dual-language Bahasa Indonesia / English execution for SG→ID MOUs to prevent invalidation risk under Law No. 24/2009.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Memorandum of Understanding"
      },
      {
        "Concept ID": "MOU-ID-012",
        "Label": "Bea Materai stamp duty",
        "SG Behavior": "No stamp duty for MOUs in Singapore",
        "ID Requirement": "IDR 10,000 Bea Materai required for agreements executed in Indonesia or used in Indonesian legal proceedings",
        "Operation": "INSERT",
        "Template Clause": "[NOTICE — NOT A CONTRACTUAL CLAUSE]: Under Indonesian Law No. 10/2020 on Stamp Duty (Bea Materai), this Memorandum of Understanding requires affixing of Bea Materai stamps of IDR 10,000 per original copy executed in or intended for use in Indonesia. Electronic Bea Materai is available via Peruri.",
        "Statutory Reference": "Law No. 10/2020 (Bea Materai); Government Regulation No. 86/2021",
        "Statutory Detail": "Bea Materai does not affect contract validity but affects admissibility in Indonesian courts. Retroactive stamping (nazegeling) is available but inconvenient.",
        "Risk Level": "Low",
        "Requires Human Review": "No",
        "Notes": "Flag Bea Materai for all SG→ID documents. Electronic Bea Materai via Peruri is the modern approach.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Memorandum of Understanding"
      }
    ]
  },
  "Service Agreement Clauses (SG-ID)": {
    "headers": [
      "Concept ID",
      "Label",
      "SG Behavior",
      "ID Requirement",
      "Operation",
      "Template Clause",
      "Statutory Reference",
      "Statutory Detail",
      "Risk Level",
      "Requires Human Review",
      "Notes",
      "Automation Type",
      "Document Type"
    ],
    "records": [
      {
        "Concept ID": "SA-ID-001",
        "Label": "Governing law",
        "SG Behavior": "Singapore law",
        "ID Requirement": "Indonesian law recommended; for service agreements with Indonesian counterparty, Indonesian law increases enforceability domestically",
        "Operation": "PARAMETERIZED",
        "Template Clause": "This Agreement shall be governed by and construed in accordance with the laws of [GOVERNING LAW: Indonesian law recommended for enforceability against Indonesian service providers/clients; Singapore law acceptable with SIAC arbitration].",
        "Statutory Reference": "Indonesian Civil Code Art. 1338; Law No. 30/1999",
        "Statutory Detail": "For SG→ID service agreements, Indonesian governing law with SIAC arbitration provides the best combination of local enforceability and procedural certainty. If the service provider is Indonesian, Indonesian courts will generally apply Indonesian law regardless of choice of law clause.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "PARAMETERIZED — governing law choice depends on which party is Indonesian and where performance occurs.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Service Agreement"
      },
      {
        "Concept ID": "SA-ID-002",
        "Label": "Dispute resolution",
        "SG Behavior": "SIAC arbitration; 1 or 3 arbitrators per deal size",
        "ID Requirement": "SIAC strongly recommended; BANI acceptable for Indonesian party preference; avoid Indonesian courts for commercial disputes",
        "Operation": "REPLACE",
        "Template Clause": "Any dispute arising out of or in connection with this Agreement shall be referred to and finally resolved by arbitration administered by the Singapore International Arbitration Centre (SIAC) in accordance with its Arbitration Rules. The seat of arbitration shall be Singapore. The tribunal shall consist of [1 (one) / 3 (three)] arbitrator(s). The language of arbitration shall be English.",
        "Statutory Reference": "Law No. 30/1999; Presidential Decree No. 34/1981",
        "Statutory Detail": "SIAC awards enforceable in Indonesia via Central Jakarta District Court. Indonesian Commercial Court proceedings are significantly slower than arbitration and less predictable for foreign parties.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "SIAC strongly preferred. Indonesian courts have a backlog and enforcement of foreign court judgments is not available (Indonesia has no reciprocal enforcement treaties).",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Service Agreement"
      },
      {
        "Concept ID": "SA-ID-003",
        "Label": "Party identification — Indonesian entity",
        "SG Behavior": "Singapore UEN and registered address",
        "ID Requirement": "Indonesian party must be identified with NPWP (tax identification number) and NIB (business identification number from OSS); specify PT (Perseroan Terbatas) or PT PMA for foreign-owned entity",
        "Operation": "REWRITE",
        "Template Clause": "[INDONESIAN PARTY]: [Company name], a [PT / PT PMA] incorporated under the laws of the Republic of Indonesia, with its registered address at [address], NPWP No. [tax ID], NIB No. [business ID] (the \"[Role]\").",
        "Statutory Reference": "Law No. 40/2007 on Limited Liability Companies; Government Regulation No. 5/2021 (OSS)",
        "Statutory Detail": "NPWP (Nomor Pokok Wajib Pajak) is the Indonesian tax identification number — mandatory for all legal entities. NIB (Nomor Induk Berusaha) replaced the former SIUP and TDP as the primary business identification number under the OSS system. Including both in the contract header establishes the Indonesian party's legal identity and is standard Indonesian commercial practice.",
        "Risk Level": "Medium",
        "Requires Human Review": "No",
        "Notes": "Always require NPWP and NIB from Indonesian counterparties — these are their primary legal identifiers. PT PMA for foreign-owned entities, PT for Indonesian-owned.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Service Agreement"
      },
      {
        "Concept ID": "SA-ID-004",
        "Label": "Service description and scope",
        "SG Behavior": "Defined scope with SOW/schedule",
        "ID Requirement": "Same; Indonesian courts interpret scope of services strictly — comprehensive SOW is essential; avoid open-ended \"such other services as agreed\" language",
        "Operation": "REWRITE",
        "Template Clause": "The Service Provider shall provide the services described in Schedule 1 (Statement of Work) to this Agreement (the \"Services\"). The Services shall be provided strictly in accordance with the specifications, timelines, and deliverables set out in Schedule 1. Any additional services outside the scope of Schedule 1 shall require a written variation order signed by both Parties.",
        "Statutory Reference": "Indonesian Civil Code Art. 1601 (service contracts — perjanjian untuk melakukan pekerjaan)",
        "Statutory Detail": "Indonesian Civil Code distinguishes between employment contracts (perjanjian kerja) and service contracts (perjanjian untuk melakukan pekerjaan). A poorly defined service scope may lead Indonesian courts to recharacterise the arrangement as an employment relationship, triggering Manpower Law (UU Ketenagakerjaan) obligations including severance pay.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "CRITICAL: Vague service scope risks recharacterisation as employment under Manpower Law. This is the most common legal error in SG→ID service agreements.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Service Agreement"
      },
      {
        "Concept ID": "SA-ID-005",
        "Label": "Independent contractor — not employment",
        "SG Behavior": "Standard independent contractor disclaimer",
        "ID Requirement": "CRITICAL for Indonesia — Manpower Law (UU Ketenagakerjaan) imposes significant obligations if arrangement recharacterised as employment; specific Indonesian disclaimers required",
        "Operation": "INSERT",
        "Template Clause": "The Service Provider is an independent contractor (kontraktor independen) and not an employee, agent, or partner of the Client. The Parties expressly agree that this Agreement does not create an employment relationship (hubungan kerja) under Law No. 13/2003 on Manpower (UU Ketenagakerjaan) as amended by the Cipta Kerja Law (Law No. 11/2020). The Service Provider shall be solely responsible for all taxes, social security contributions (BPJS), and other employment-related obligations of its personnel.",
        "Statutory Reference": "Law No. 13/2003 on Manpower (UU Ketenagakerjaan); Law No. 11/2020 (Cipta Kerja); Constitutional Court Decision No. 27/PUU-IX/2011",
        "Statutory Detail": "Indonesian courts apply a substance-over-form test for employment relationships. If a service arrangement has the characteristics of employment (supervision, fixed hours, economic dependence), it may be recharacterised as employment regardless of contractual labelling. Constitutional Court Decision No. 27/2011 held that certain outsourcing arrangements constituted employment. Consequences of recharacterisation: statutory severance (UPMK), BPJS contributions, and gratuity obligations.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "CRITICAL clause for SG→ID service agreements. Indonesia's Manpower Law is strict on employment recharacterisation. Include NPWP of individual service providers if applicable.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Service Agreement"
      },
      {
        "Concept ID": "SA-ID-006",
        "Label": "Fees and payment — currency",
        "SG Behavior": "SGD or USD with GST at 9%",
        "ID Requirement": "USD recommended for SG→ID; IDR for domestic-only arrangements; withholding tax (PPh 23) applies to service fees paid to Indonesian service providers",
        "Operation": "REWRITE",
        "Template Clause": "The Client shall pay the Service Provider the fees set out in Schedule 2 (Fee Schedule) in [CURRENCY: USD strongly recommended / IDR if domestic]. All fees are exclusive of applicable Indonesian taxes. If the Service Provider is an Indonesian resident entity receiving fees from a foreign payer, Indonesian withholding tax (PPh 23) at [2% for Indonesian corporate service provider / 20% for individual / reduced rate under Singapore-Indonesia DTA] may apply — the Parties shall each bear their own applicable tax obligations.",
        "Statutory Reference": "Indonesian Income Tax Law (UU PPh) Art. 23; Singapore-Indonesia Double Taxation Agreement (DTA)",
        "Statutory Detail": "PPh 23 (withholding tax on service income) applies at 2% for Indonesian corporate entities and up to 20% for individuals. Under the Singapore-Indonesia DTA (in force since 1992), withholding tax on business profits may be reduced or eliminated depending on permanent establishment analysis. Indonesian VAT (PPN) at 11% applies to taxable services performed in Indonesia.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "PPh 23 withholding and PPN (Indonesian VAT at 11%) are critical tax considerations for SG→ID service agreements. Always flag for tax adviser review.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Service Agreement"
      },
      {
        "Concept ID": "SA-ID-007",
        "Label": "Payment terms and late interest",
        "SG Behavior": "30 days from invoice; SORA + 2% late interest",
        "ID Requirement": "Payment terms standard; Indonesian late interest based on Bank Indonesia benchmark rate (BI Rate); specify in IDR or USD",
        "Operation": "REWRITE",
        "Template Clause": "The Client shall pay each invoice within thirty (30) calendar days of the invoice date. Any unpaid amounts shall accrue interest at the rate of [BI Rate + 2% per annum (IDR) / SOFR + 2% per annum (USD)] from the due date until the date of actual payment. All payments shall be made by telegraphic transfer to the Service Provider's designated bank account.",
        "Statutory Reference": "Indonesian Civil Code Art. 1243; Bank Indonesia Regulation on interest rates",
        "Statutory Detail": "Bank Indonesia (BI) benchmark rate is the Indonesian equivalent of SORA. For USD-denominated agreements, SOFR + 2% is appropriate. Indonesian courts may adjust contractually agreed interest rates that are considered unconscionable under Civil Code Art. 1339.",
        "Risk Level": "Low",
        "Requires Human Review": "No",
        "Notes": "Use SOFR + 2% for USD agreements and BI Rate + 2% for IDR agreements. Indonesian courts have discretion to reduce excessive interest rates.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Service Agreement"
      },
      {
        "Concept ID": "SA-ID-008",
        "Label": "Intellectual property ownership",
        "SG Behavior": "Work product assigned to client; background IP licensed",
        "ID Requirement": "Same principle; Indonesian IP law requires written assignment; specify DGIP (Directorate General of Intellectual Property) registration for patents and trademarks",
        "Operation": "REWRITE",
        "Template Clause": "All work product, deliverables, and materials created by the Service Provider specifically for the Client under this Agreement (the \"Deliverables\") shall, upon creation, vest in and be assigned to the Client. The Service Provider hereby assigns (mengalihkan) all intellectual property rights in the Deliverables to the Client with effect from creation. The Service Provider retains ownership of its pre-existing tools, methodologies, and background IP and grants the Client a non-exclusive, perpetual licence to use such background IP to the extent incorporated in the Deliverables.",
        "Statutory Reference": "Law No. 28/2014 (Copyright Law); Law No. 13/2016 (Patents); Law No. 20/2016 (Trademarks); Indonesian Civil Code Art. 570",
        "Statutory Detail": "Indonesian Copyright Law requires written assignment for copyright transfer. Patent assignment requires registration with DJKI (Direktorat Jenderal Kekayaan Intelektual / DGIP). The word \"mengalihkan\" (assign) in the Indonesian context carries clear transfer-of-ownership meaning and should appear in dual-language agreements.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "Indonesian IP assignment must be in writing. For significant IP, registration of assignment with DJKI (DGIP) is recommended for third-party enforceability.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Service Agreement"
      },
      {
        "Concept ID": "SA-ID-009",
        "Label": "Confidentiality",
        "SG Behavior": "Standard confidentiality with 3-year post-termination period; indefinite for trade secrets",
        "ID Requirement": "Align with Law No. 30/2000 (Trade Secrets) and UU PDP; use Indonesian term rahasia dagang for trade secrets",
        "Operation": "REWRITE",
        "Template Clause": "Each Party shall maintain the confidentiality of the other Party's Confidential Information and shall not disclose it to any third party without prior written consent. This obligation continues for three (3) years after termination, except that trade secrets (rahasia dagang) shall be protected indefinitely under Law No. 30/2000.",
        "Statutory Reference": "Law No. 30/2000 on Trade Secrets; UU PDP (Law No. 27/2022)",
        "Statutory Detail": "Indonesian trade secret law provides indefinite protection for qualifying rahasia dagang. Including the Indonesian statutory term strengthens enforceability in Indonesian courts.",
        "Risk Level": "Medium",
        "Requires Human Review": "No",
        "Notes": "Dual duration: 3 years general, indefinite for rahasia dagang. Include Indonesian statutory reference for court enforceability.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Service Agreement"
      },
      {
        "Concept ID": "SA-ID-010",
        "Label": "Personal data protection (UU PDP)",
        "SG Behavior": "PDPA compliance clause",
        "ID Requirement": "UU PDP (Law No. 27/2022) full mandatory baseline; cross-border transfer restrictions apply",
        "Operation": "INSERT",
        "Template Clause": "To the extent any Services involve processing of personal data as defined under Law No. 27/2022 on Personal Data Protection (UU PDP), each Party shall: (a) process personal data only for the purposes specified in this Agreement; (b) implement appropriate security measures; (c) not transfer personal data outside Indonesia except in compliance with UU PDP Chapter VII; (d) notify the other Party within 24 hours of discovering a personal data breach; and (e) upon request, assist the other Party in fulfilling data subject rights under UU PDP.",
        "Statutory Reference": "Law No. 27/2022 (UU PDP); Government Regulation on Electronic Systems (PP No. 71/2019)",
        "Statutory Detail": "UU PDP fully in force as of October 2024. Cross-border personal data transfers from Indonesia require: (a) the recipient country has equivalent data protection levels; or (b) contractual safeguards are in place. Singapore's PDPA is generally considered adequate but Indonesian counsel should confirm. Penalties under UU PDP: up to 2% of annual revenue for data breach non-disclosure.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "UU PDP is now fully enforceable. Any service agreement involving personal data of Indonesian individuals must include full UU PDP compliance obligations.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Service Agreement"
      },
      {
        "Concept ID": "SA-ID-011",
        "Label": "Limitation of liability",
        "SG Behavior": "Mutual cap; exclusion of consequential loss; IP breach uncapped",
        "ID Requirement": "Indonesian courts may not enforce limitation of liability clauses that are unconscionable or contrary to good faith (itikad baik); moderate caps are enforceable",
        "Operation": "REWRITE",
        "Template Clause": "Neither Party's liability to the other under this Agreement shall exceed the total fees paid by the Client in the [twelve (12) / six (6)] months preceding the event giving rise to the claim. Neither Party shall be liable for indirect, special, consequential, or punitive loss. This limitation does not apply to: (a) liability for breach of confidentiality; (b) IP infringement; (c) gross negligence or wilful misconduct; or (d) death or personal injury.",
        "Statutory Reference": "Indonesian Civil Code Art. 1247, 1248 (consequential loss); Art. 1339 (unconscionable terms)",
        "Statutory Detail": "Indonesian Civil Code Art. 1247-1248 limits recoverable damages to foreseeable losses. Consequential loss exclusions are generally enforceable but Indonesian courts may look through limitation clauses where the breach was fraudulent or grossly negligent (Art. 1339, 1340). Limitation clauses that are entirely one-sided may be struck down as contrary to good faith.",
        "Risk Level": "Medium",
        "Requires Human Review": "Yes",
        "Notes": "Indonesian courts apply itikad baik (good faith) review to limitation clauses. Entirely one-sided caps may be unenforceable. Mutual caps with standard carve-outs are enforceable.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Service Agreement"
      },
      {
        "Concept ID": "SA-ID-012",
        "Label": "Termination rights",
        "SG Behavior": "Termination for convenience (30 days) and for cause (14-day cure period)",
        "ID Requirement": "Indonesian Civil Code Art. 1266 requires court approval for unilateral termination UNLESS expressly waived — this waiver MUST be included",
        "Operation": "REWRITE",
        "Template Clause": "Either Party may terminate this Agreement: (a) for convenience, by giving thirty (30) calendar days' prior written notice; or (b) for cause, immediately if the other Party commits a material breach and fails to remedy it within fourteen (14) calendar days of written notice. The Parties expressly waive the requirement for court approval of termination under Article 1266 of the Indonesian Civil Code (KUHPerdata), to the extent permitted by applicable law.",
        "Statutory Reference": "Indonesian Civil Code Art. 1266, 1267",
        "Statutory Detail": "Indonesian Civil Code Art. 1266 provides that termination of bilateral contracts (perjanjian timbal balik) requires a court order (putusan pengadilan) unless the contract expressly provides for out-of-court termination. This is a critical difference from Singapore law where no court order is needed. Without the Art. 1266 waiver, a party terminating without court order risks the termination being invalid.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "CRITICAL: Art. 1266 waiver is mandatory for all SG→ID service agreements. Without it, unilateral termination may be legally invalid under Indonesian law.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Service Agreement"
      },
      {
        "Concept ID": "SA-ID-013",
        "Label": "Force majeure",
        "SG Behavior": "Common law force majeure with 30-day longstop",
        "ID Requirement": "Indonesian concept of \"keadaan memaksa\" (force majeure) under Civil Code Art. 1244-1245; include Indonesian term and government regulation as trigger",
        "Operation": "REWRITE",
        "Template Clause": "Neither Party shall be liable for delay or failure to perform its obligations (other than payment obligations) due to a Force Majeure Event (keadaan memaksa). \"Force Majeure Event\" means any event beyond a Party's reasonable control including natural disaster (bencana alam), pandemic, war, government action (termasuk kebijakan pemerintah), or regulatory change. A Party claiming force majeure must notify the other within five (5) Business Days. If force majeure continues for sixty (60) days, either Party may terminate by written notice.",
        "Statutory Reference": "Indonesian Civil Code Art. 1244, 1245 (keadaan memaksa)",
        "Statutory Detail": "Indonesian Civil Code Art. 1244-1245 recognises force majeure (keadaan memaksa) as releasing a party from liability. Indonesian force majeure interpretation includes government regulation changes (kebijakan pemerintah) — relevant given Indonesia's history of regulatory changes affecting foreign investment. Payment obligations are typically not excused by force majeure under Indonesian commercial practice.",
        "Risk Level": "Medium",
        "Requires Human Review": "No",
        "Notes": "Include government regulation changes as a force majeure trigger — this is specific to Indonesia and not typically included in Singapore-law agreements.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Service Agreement"
      },
      {
        "Concept ID": "SA-ID-014",
        "Label": "Language requirement (UU Bahasa)",
        "SG Behavior": "English as governing language",
        "ID Requirement": "Law No. 24/2009 requires Bahasa Indonesia; dual-language execution mandatory for significant service agreements",
        "Operation": "INSERT",
        "Template Clause": "This Agreement is executed in both the English language and Bahasa Indonesia. Both versions shall be equally authentic. In the event of any inconsistency between the English and Bahasa Indonesia versions, the English version shall prevail.",
        "Statutory Reference": "Law No. 24/2009 (UU Bahasa) Art. 31; Supreme Court Circular No. 3/2010",
        "Statutory Detail": "Risk of contract invalidation in Indonesian courts if agreement is not in Bahasa Indonesia. The 2013 Nine AM precedent applies equally to service agreements. Dual-language execution with English prevailing is the commercial standard for SG→ID service agreements.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "CRITICAL: Always dual-language for SG→ID service agreements. Bahasa Indonesia version must be professionally translated — machine translation is not acceptable for commercial contracts.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Service Agreement"
      },
      {
        "Concept ID": "SA-ID-015",
        "Label": "Bea Materai and tax obligations",
        "SG Behavior": "No stamp duty; GST at 9%",
        "ID Requirement": "Bea Materai IDR 10,000; PPh 23 withholding tax; PPN (VAT) at 11%; BPJS Ketenagakerjaan for individual service providers",
        "Operation": "INSERT",
        "Template Clause": "[NOTICE — NOT A CONTRACTUAL CLAUSE] TAX OBLIGATIONS NOTE: (1) Bea Materai: IDR 10,000 stamp duty required per original copy executed in Indonesia. (2) PPh 23: Indonesian withholding tax at 2% applies to service fees paid to Indonesian corporate service providers. (3) PPN: Indonesian VAT at 11% applies to taxable services performed in Indonesia — confirm with tax adviser whether Services constitute taxable supply in Indonesia. (4) Singapore GST: 9% GST applies to services supplied by Singapore GST-registered entities where applicable.",
        "Statutory Reference": "UU PPh Art. 23; UU PPN (Value Added Tax Law); Law No. 10/2020 (Bea Materai)",
        "Statutory Detail": "Tax obligations for SG→ID service agreements are complex: PPh 23 withholding, PPN, and Singapore GST may all apply simultaneously. A tax adviser in both jurisdictions should review the structure to avoid double taxation and ensure compliance.",
        "Risk Level": "High",
        "Requires Human Review": "Yes",
        "Notes": "Indonesian tax obligations for service agreements are significant and frequently overlooked by Singapore companies. Always flag for dual-jurisdiction tax review.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Service Agreement"
      }
    ]
  }
}

def upload_table(table_name, records):
    encoded = table_name.replace(" ", "%20")
    url = f"https://api.airtable.com/v0/{BASE_ID}/{encoded}"
    total = 0
    for i in range(0, len(records), 10):
        batch = records[i:i+10]
        payload = {"records": [{"fields": r} for r in batch]}
        r = requests.post(url, headers=HEADERS, json=payload)
        if r.status_code in (200, 201):
            total += len(batch)
            print(f"  Batch {i//10+1}: {len(batch)} records OK")
        else:
            print(f"  Batch {i//10+1} FAILED: {r.status_code} — {r.text[:200]}")
        time.sleep(0.3)
    return total

print("Uploading SG-ID LCM records to Airtable...\n")
grand_total = 0

for table_name, data in ALL_DATA.items():
    print(f"Table: {table_name} — {len(data['records'])} records")
    total = upload_table(table_name, data["records"])
    grand_total += total
    print(f"  ✅ {total} uploaded\n")

print(f"TOTAL: {grand_total} records uploaded")
