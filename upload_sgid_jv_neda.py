"""
Qarta SG-ID JV + Non-Exclusive Distribution Upload Script
Run: python upload_sgid_jv_neda.py
"""
import requests, json, time

API_KEY = "pataU1CHASPyWivFC.906b7535e4754d1a9715bd12c5150216a5e7035e1367f344086465b08aed5a2f"
BASE_ID = "appwmBfW20jnFo64x"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

ALL_DATA = {
  "JV Agreement Clauses (SG-ID)": {
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
        "Concept ID": "JV-ID-001",
        "Label": "Governing law and language",
        "SG Behavior": "Singapore law; Companies Act (Cap.50); English only",
        "ID Requirement": "Indonesian law (KUHPerdata + UU PT No. 40/2007); bilingual mandatory; Indonesian prevails; civil law framework throughout",
        "Template Clause": "Perjanjian ini diatur oleh dan ditafsirkan sesuai dengan hukum Republik Indonesia, termasuk KUHPerdata dan Undang-Undang No. 40 Tahun 2007 tentang Perseroan Terbatas ('UU PT'). Perjanjian ini dibuat dalam Bahasa Indonesia dan Bahasa Inggris; dalam hal pertentangan, versi Bahasa Indonesia yang berlaku. / This Agreement is governed by Indonesian law, including KUHPerdata and Law No. 40/2007 on Limited Liability Companies ('UU PT'). Made in Bahasa Indonesia and English; in case of inconsistency, the Bahasa Indonesia version prevails.",
        "Statutory Reference": "KUHPerdata Buku III; UU No. 40/2007 tentang PT (Company Law); UU No. 24/2009 Art.31 (Language Law)",
        "Statutory Detail": "Indonesian JV is governed by TWO overlapping legal frameworks: (1) KUHPerdata — governs the JV agreement as a contract between the parties; (2) UU PT No. 40/2007 — governs the PT JV Company's internal governance as a matter of Indonesian company law. UU PT is mandatory and cannot be contracted out — the JV agreement cannot override UU PT provisions. Good faith (itikad baik) under KUHPerdata Art.1338 applies to the JV agreement. Bilingual: SC Decision No. 601 K/Pdt/2015 — Indonesian version prevails.",
        "Risk Level": "High",
        "Notes": "Auto-apply. Critical distinction from SG JV — TWO governing statutes (KUHPerdata + UU PT). All JV provisions must be consistent with UU PT mandatory requirements.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-002",
        "Label": "Dispute resolution",
        "SG Behavior": "SIAC; Singapore seat; 3-arbitrator panel; emergency arbitrator",
        "ID Requirement": "BANI or SIAC; BANI for Indonesian enforcement priority; 3-arbitrator panel for JV disputes; New York Convention",
        "Template Clause": "[OPTION A — BANI]: Setiap perselisihan diselesaikan melalui arbitrase di BANI, Jakarta, 3 arbiter, dalam Bahasa Indonesia dan/atau Bahasa Inggris, sesuai Peraturan BANI. / Any dispute by BANI arbitration, Jakarta, 3 arbitrators, Bahasa Indonesia and/or English.\n\n[OPTION B — SIAC]: Any dispute by SIAC arbitration, Singapore seat, English, 3 arbitrators, enforceable in Indonesia under Presidential Decree No. 34/1981. Emergency arbitration under SIAC Rules available for urgent governance disputes.",
        "Statutory Reference": "UU No. 30/1999 (Arbitration Law); Keppres No. 34/1981 (New York Convention); BANI Rules 2022; SIAC Rules (7th Ed)",
        "Statutory Detail": "For JV disputes — which are typically high-value governance, deadlock, and capital disputes — SIAC is often preferred over BANI for: (1) procedural predictability; (2) emergency arbitrator for urgent governance relief; (3) international enforcement. BANI is preferred where the primary concern is enforcement of monetary awards against the Indonesian JV partner. Three-arbitrator panel is mandatory for JV agreements. SIAC awards enforceable in Indonesia via Pengadilan Negeri Jakarta Pusat — recognition proceedings required but generally granted.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "PARAMETERIZED — SIAC recommended for JV governance disputes (predictability + emergency arbitrator); BANI for monetary enforcement priority. Lawyer review to confirm based on parties' risk profile.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-003",
        "Label": "JV Company — PT PMA incorporation",
        "SG Behavior": "Singapore private company limited by shares; Companies Act (Cap.50); ACRA; minimum 1 SG-resident director",
        "ID Requirement": "Indonesian PT PMA (Penanaman Modal Asing — Foreign Investment Company); BKPM/OSS approval; minimum capital; foreign ownership limits by sector (Positive Investment List)",
        "Template Clause": "Para Pihak sepakat untuk mendirikan Perusahaan JV dalam bentuk Perseroan Terbatas Penanaman Modal Asing ('PT PMA') berdasarkan UU No. 40/2007 dan UU No. 25/2007 tentang Penanaman Modal, dengan rincian sebagai berikut: Nama Perusahaan: [NAMA PT: tentukan]; Modal dasar: IDR / USD [MODAL DASAR: tentukan — minimum IDR 10 miliar kecuali sektor tertentu]; Modal ditempatkan dan disetor: [MODAL DISETOR: tentukan — minimum 25% dari modal dasar]; KBLI: [KODE KBLI: tentukan]. Para Pihak wajib memperoleh Nomor Induk Berusaha (NIB) melalui sistem OSS dalam [JANGKA WAKTU: tentukan — disarankan 60 hari] setelah penandatanganan Perjanjian ini. / The Parties agree to incorporate the JV Company as a Foreign Investment Company (PT PMA) under Law No. 40/2007 and Law No. 25/2007 on Investment, with: Company name: [PT NAME]; Authorised capital: IDR/USD [AMOUNT — minimum IDR 10 billion unless sector-specific rules apply]; Paid-up capital: [AMOUNT — minimum 25% of authorised]; KBLI: [CODE]. The Parties shall obtain a NIB via OSS within [PERIOD — recommend 60 days] after signing.",
        "Statutory Reference": "UU No. 40/2007 tentang PT (Company Law); UU No. 25/2007 tentang Penanaman Modal (Investment Law); PP No. 5/2021 (OSS); Perpres No. 10/2021 (Positive Investment List / DNI); BKPM/BKPMD requirements; Peraturan BKPM No. 4/2021",
        "Statutory Detail": "PT PMA is the mandatory vehicle for foreign investment in Indonesia. Key requirements:\n1. Positive Investment List (Perpres No. 10/2021): determines sectors open to foreign investment and maximum foreign ownership percentage by sector. Some sectors are 100% open; others have caps (e.g. retail trade 67%, certain services 49%). Verify before structuring equity split.\n2. Minimum capital: IDR 10 billion (~USD 630K) authorised capital for most PT PMAs; some sectors have higher minimums (e.g. financial services regulated by OJK). Paid-up capital minimum 25% of authorised.\n3. NIB via OSS: replaces old BKPM licence — all PT PMAs must have NIB. OSS system issues NIB automatically upon company registration. 4. Deed of establishment (Akta Pendirian) must be prepared by a Notaris (Indonesian notary) and approved by the Minister of Law and Human Rights (Kemenkumham). 5. Anggaran Dasar (articles of association) must comply with UU PT.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "MOST COMPLEX INCORPORATION REQUIREMENT — fundamentally different from SG JV. Lawyer review essential BEFORE signing JV agreement: (1) Confirm sector is open to foreign investment under Positive Investment List; (2) Confirm maximum foreign ownership percentage for the sector; (3) Confirm minimum capital requirements; (4) Engage Indonesian Notaris for Akta Pendirian — this is a legal requirement, not optional; PT PMA cannot be incorporated without notarial deed. Timeline: PT PMA incorporation typically takes 2-4 months.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-004",
        "Label": "Bea Meterai stamp duty",
        "SG Behavior": "No stamp duty",
        "ID Requirement": "IDR 10,000 Bea Meterai mandatory; JV agreement is a high-value commercial document — stamp before execution",
        "Template Clause": "Bea Meterai yang terhutang atas Perjanjian ini ditanggung oleh [PIHAK: tentukan — Para Pihak secara bersama]. Perjanjian ini wajib dibubuhi Bea Meterai sebelum penandatanganan sesuai UU No. 10/2020. / Bea Meterai payable on this Agreement shall be borne by [PARTY: specify — Parties jointly]. This Agreement shall be duly stamped before execution per Law No. 10/2020.",
        "Statutory Reference": "UU No. 10/2020 tentang Bea Meterai; PMK No. 134/2021",
        "Statutory Detail": "Identical to other SG→ID documents. IDR 10,000 mandatory. E-Meterai via Peruri. For JV agreements, both the JV agreement and the Akta Pendirian (notarial deed) require stamping.",
        "Risk Level": "Medium",
        "Notes": "Auto-apply. Note: Akta Pendirian (notarial deed for PT PMA) requires separate notarial authentication — Bea Meterai on JV agreement is separate from notarial fees.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-005",
        "Label": "Shareholding — Positive Investment List compliance",
        "SG Behavior": "Parties agree on percentage freely; no sector restrictions on foreign ownership",
        "ID Requirement": "Foreign ownership capped by sector under Positive Investment List (Perpres No. 10/2021); equity split must comply with maximum foreign ownership percentage",
        "Template Clause": "Setelah pendirian PT PMA, Para Pihak berlangganan saham PT JV sebagai berikut: [PIHAK SG]: [JUMLAH] saham, mewakili [PERSENTASE]% dari total saham yang diterbitkan; [PIHAK ID]: [JUMLAH] saham, mewakili [PERSENTASE]% dari total saham yang diterbitkan. Komposisi kepemilikan saham ini wajib mematuhi persentase kepemilikan asing maksimum yang diperbolehkan berdasarkan Daftar Positif Investasi (Perpres No. 10/2021) untuk bidang usaha dengan KBLI [KODE]. / Upon incorporation of the PT JV, the Parties subscribe for shares as follows: [SG PARTY]: [NUMBER] shares, representing [PERCENTAGE]% of total issued shares; [ID PARTY]: [NUMBER] shares, representing [PERCENTAGE]% of total issued shares. This shareholding must comply with the maximum foreign ownership percentage permitted under the Positive Investment List (Perpres No. 10/2021) for KBLI [CODE].",
        "Statutory Reference": "Perpres No. 10/2021 tentang Bidang Usaha Penanaman Modal (Positive Investment List); UU No. 25/2007 tentang Penanaman Modal; UU No. 40/2007 tentang PT",
        "Statutory Detail": "The Positive Investment List (Perpres No. 10/2021) classifies business activities into: (1) Open to 100% foreign ownership; (2) Open with conditions (maximum foreign ownership %, e.g. 67% for retail, 49% for certain services, 0% for closed sectors); (3) Reserved for SMEs (foreign investment not permitted). If the SG party wishes to hold more than the permitted foreign ownership percentage, the structure must be adjusted: nominee arrangements are illegal in Indonesia; the local partner must genuinely hold the required percentage. Shares in Indonesian PT are denominated in IDR — USD capital contributions are converted at the prevailing Bank Indonesia rate on the date of payment.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "CRITICAL — verify Positive Investment List compliance BEFORE agreeing equity split. A JV agreement that gives the SG party more than the permitted foreign ownership percentage is void to that extent. Nominee arrangements (Indonesian party holds shares on behalf of foreign party) are expressly prohibited under UU PT — criminal liability for both parties. Lawyer review to confirm maximum foreign ownership for specific KBLI sector.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-006",
        "Label": "Capital contributions and paid-up capital",
        "SG Behavior": "SGD; non-cash contributions require independent valuation; contribution timeline and default remedy",
        "ID Requirement": "IDR or USD; minimum paid-up capital 25% of authorised; non-cash contributions require KJPP valuation; Bank Indonesia reporting for foreign capital inflows",
        "Template Clause": "Masing-masing Pihak memberikan kontribusi modal kepada PT JV sebagai berikut: [PIHAK SG]: [KONTRIBUSI TUNAI: USD/IDR [jumlah]] / [KONTRIBUSI NON-TUNAI: uraikan aset — nilai IDR [jumlah] berdasarkan penilaian KJPP]; [PIHAK ID]: [KONTRIBUSI: uraikan]. Semua kontribusi tunai dibayarkan melalui transfer kawat ke rekening PT JV dalam [JANGKA WAKTU: tentukan — disarankan 30 hari] setelah penerbitan Akta Pendirian. Penanaman modal asing wajib dilaporkan kepada Bank Indonesia sesuai PBI No. 14/17/PBI/2012. / Each Party contributes to the PT JV as follows: [SG PARTY]: [CASH: USD/IDR amount] / [NON-CASH: describe asset — IDR value per KJPP valuation]; [ID PARTY]: [describe]. All cash contributions by telegraphic transfer to PT JV account within [PERIOD — recommend 30 days] after Akta Pendirian issuance. Foreign capital inflows reported to Bank Indonesia per PBI No. 14/17/PBI/2012.",
        "Statutory Reference": "UU No. 40/2007 tentang PT Art.33 (minimum paid-up capital); PP No. 7/2021 (minimum capital for PT PMA); KJPP (Kantor Jasa Penilai Publik) — licensed appraisers for non-cash valuations; PBI No. 14/17/PBI/2012 (LLD/LKPBU foreign capital reporting); IRAS transfer pricing (for SG party)",
        "Statutory Detail": "Non-cash contributions (IP, technology, equipment) MUST be valued by a KJPP (licensed public appraiser registered with Ministry of Finance) — this is a mandatory requirement under Indonesian company law, not merely good practice. Without KJPP valuation, the Kemenkumham may reject the Akta Pendirian. Foreign capital inflows above USD 10,000 must be reported to Bank Indonesia (LLD/LKPBU reporting) within the prescribed deadline. Minimum paid-up capital: 25% of authorised capital must be paid up before Kemenkumham approval — ensure cash contribution timeline aligns with incorporation timeline.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "Non-cash contribution KJPP valuation is legally mandatory — engage KJPP early as valuations take 2-4 weeks. Bank Indonesia LLD reporting is an ongoing obligation for the PT PMA. Lawyer review: IP contribution valuation has transfer pricing implications (IRAS for SG party + DJP for Indonesian PT). KJPP = Kantor Jasa Penilai Publik — must be registered with Kemenkeu.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-007",
        "Label": "Board of Directors (Direksi) — UU PT structure",
        "SG Behavior": "Board of directors; CEO appointed by board; minimum 1 SG-resident director; Companies Act duties",
        "ID Requirement": "PT has TWO separate governance bodies: Direksi (Board of Directors — management) AND Dewan Komisaris (Board of Commissioners — supervisory); both mandatory under UU PT",
        "Template Clause": "Direksi PT JV terdiri dari [JUMLAH: tentukan — disarankan 2-3] Direktur, diangkat sebagai berikut: [PIHAK SG] berhak menunjuk [JUMLAH] Direktur; [PIHAK ID] berhak menunjuk [JUMLAH] Direktur. Direktur Utama (Presiden Direktur) ditunjuk oleh [PIHAK: tentukan]. Anggota Direksi wajib berdomisili di Indonesia sesuai UU PT Pasal 93. Direksi berwenang mewakili PT JV dan mengelola kegiatan operasional sehari-hari. / The Direksi of the PT JV shall consist of [NUMBER — recommend 2-3] Directors, appointed as follows: [SG PARTY] entitled to appoint [NUMBER] Directors; [ID PARTY] entitled to appoint [NUMBER] Directors. The Presiden Direktur (CEO) nominated by [PARTY]. Directors must be domiciled in Indonesia per UU PT Art.93. Direksi represents and manages the PT JV's day-to-day operations.",
        "Statutory Reference": "UU No. 40/2007 tentang PT Art.92-107 (Direksi); Art.108-121 (Dewan Komisaris); Art.93 (domicile requirement)",
        "Statutory Detail": "FUNDAMENTAL DIFFERENCE from SG JV — Indonesian PT has a TWO-TIER governance structure:\nTIER 1 — Direksi (Board of Directors): Manages day-to-day operations. Each Director can individually bind the company unless the Anggaran Dasar requires joint signatures. Under UU PT Art.93, Directors must be domiciled in Indonesia — EXPAT DIRECTORS require KITAS (work permit) and Director's work permit (Izin Tinggal Terbatas). TIER 2 — Dewan Komisaris (Board of Commissioners): Supervises Direksi. Cannot manage the company — supervisory role only. Must have at least 1 Komisaris. The JV agreement must address BOTH tiers — a governance structure that addresses only the Direksi misses the supervisory layer where significant veto powers sit.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "MOST CRITICAL STRUCTURAL DIFFERENCE from SG JV. Director domicile in Indonesia requirement: expat SG party-appointed Directors need KITAS + Director work permit — factor into timeline (2-3 months to obtain). Each Director can INDIVIDUALLY bind the company unless Anggaran Dasar requires joint signatures — include four-eyes (joint signature) requirement in Anggaran Dasar for transactions above threshold.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-008",
        "Label": "Dewan Komisaris — Board of Commissioners",
        "SG Behavior": "No equivalent in Singapore company law; single-tier board only",
        "ID Requirement": "Dewan Komisaris mandatory under UU PT; supervisory role; cannot manage company; holds key veto powers; PT PMA must have Komisaris",
        "Template Clause": "Dewan Komisaris PT JV terdiri dari [JUMLAH: tentukan — disarankan 2] Komisaris, diangkat sebagai berikut: [PIHAK SG] berhak menunjuk [JUMLAH] Komisaris; [PIHAK ID] berhak menunjuk [JUMLAH] Komisaris. Komisaris Utama ditunjuk oleh [PIHAK: tentukan]. Dewan Komisaris berwenang untuk: (a) mengawasi kebijakan pengurusan oleh Direksi; (b) memberikan persetujuan atas tindakan Direksi yang ditetapkan dalam Anggaran Dasar sebagai memerlukan persetujuan Dewan Komisaris. / The Dewan Komisaris of the PT JV shall consist of [NUMBER — recommend 2] Commissioners, appointed: [SG PARTY] appoints [NUMBER]; [ID PARTY] appoints [NUMBER]. Komisaris Utama nominated by [PARTY]. Dewan Komisaris is authorised to: (a) supervise management policies of Direksi; (b) approve Direksi actions designated in the Anggaran Dasar as requiring Komisaris approval.",
        "Statutory Reference": "UU No. 40/2007 tentang PT Art.108-121 (Dewan Komisaris); Art.117 (Komisaris approval for certain Direksi actions)",
        "Statutory Detail": "Dewan Komisaris is the supervisory tier — it does NOT manage the company but supervises Direksi. Under UU PT Art.117, the Anggaran Dasar may require Dewan Komisaris approval for specific Direksi actions (equivalent to reserved matters in SG JV agreements). This is where minority party veto rights should be embedded — place key reserved matters requiring Komisaris approval in the Anggaran Dasar. Komisaris can be domiciled abroad (no Indonesian domicile requirement unlike Direksi). The SG party can appoint a Komisaris without Indonesian domicile — important for practical governance where the SG party wants board representation without Indonesia residency.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "UNIQUE TO INDONESIAN JV — no SG equivalent. Place minority party veto rights (reserved matters) in Anggaran Dasar as Komisaris approval requirements — this is the Indonesian mechanism for the reserved matters clause in SG JVs. Komisaris can be based in SG — no Indonesian domicile requirement. Lawyer review to ensure Anggaran Dasar embeds all reserved matter approvals in Komisaris authority correctly.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-009",
        "Label": "Reserved matters — Anggaran Dasar and RUPS",
        "SG Behavior": "Reserved matters list in JV agreement; shareholder approval required; supermajority threshold",
        "ID Requirement": "Reserved matters must be embedded in Anggaran Dasar to be effective under UU PT; RUPS (General Meeting of Shareholders) is the formal approval mechanism",
        "Template Clause": "Hal-hal berikut memerlukan persetujuan Rapat Umum Pemegang Saham (RUPS) dengan suara bulat / supermayoritas [AMBANG BATAS: tentukan]%: (a) perubahan Anggaran Dasar; (b) penambahan atau pengurangan modal; (c) penerbitan saham baru; (d) merger, akuisisi, atau pelepasan aset melebihi IDR/USD [AMBANG BATAS]; (e) transaksi dengan pihak terafiliasi melebihi IDR/USD [AMBANG BATAS]; (f) perubahan bidang usaha PT JV; (g) pembubaran PT JV. Hal-hal berikut memerlukan persetujuan Dewan Komisaris: [daftar tindakan operasional material sesuai Anggaran Dasar]. / The following require RUPS (General Meeting of Shareholders) approval by unanimous / supermajority [THRESHOLD]%: (a) amendments to Anggaran Dasar; (b) capital increase/decrease; (c) new share issuance; (d) merger, acquisition, or asset disposal above IDR/USD [THRESHOLD]; (e) related-party transactions above [THRESHOLD]; (f) change of PT JV business; (g) dissolution. The following require Dewan Komisaris approval: [list material operational actions per Anggaran Dasar].",
        "Statutory Reference": "UU No. 40/2007 tentang PT Art.75-91 (RUPS); Art.88 (supermajority — 3/4 quorum + 2/3 approval for special resolutions); Art.117 (Komisaris approval)",
        "Statutory Detail": "FUNDAMENTAL DIFFERENCE from SG JV — reserved matters must be embedded in BOTH the JV agreement AND the Anggaran Dasar to be enforceable under UU PT:\nJV Agreement: contractual obligation between the parties.\nAnggaran Dasar: governs the PT JV company's internal governance — must mirror the JV agreement's reserved matters structure.\nUU PT Art.88: special resolutions (amending Anggaran Dasar, dissolution) require quorum of 3/4 of total shares and approval of 2/3 of shares present — this is the statutory minimum. The Anggaran Dasar can set HIGHER thresholds (e.g. unanimity) for specific matters. RUPS can be held in person or via videoconference (post-2020 amendments to UU PT). Formal RUPS procedures (notice, quorum, minutes, notarisation of resolutions) must be followed — informal approvals are not valid under UU PT.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "Reserved matters in JV agreement alone are INSUFFICIENT — must be mirrored in Anggaran Dasar to bind the PT JV as a company law matter. Engage Indonesian Notaris to draft Anggaran Dasar consistent with JV agreement reserved matters structure. RUPS procedures are formal — any informal approval by shareholders without proper RUPS is not valid under UU PT and may be challenged.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-010",
        "Label": "Deadlock mechanism",
        "SG Behavior": "Escalation → mediation → Texas Shoot-Out (buy-sell); self-enforcing price mechanism",
        "ID Requirement": "Same commercial structure; Art.1266 waiver required; Indonesian court order not needed if waiver present; buy-sell mechanism enforceable",
        "Template Clause": "Para Pihak dengan ini secara tegas mengesampingkan Pasal 1266 dan 1267 KUHPerdata. Suatu 'Kebuntuan' (Deadlock) terjadi jika Para Pihak tidak dapat mencapai keputusan dalam [PERIODE: tentukan — disarankan 30 hari]. Prosedur penyelesaian: Langkah 1 — Eskalasi ke pimpinan senior masing-masing Pihak dalam [PERIODE ESKALASI: tentukan — disarankan 20 hari kerja]; Langkah 2 — Mediasi di BMUI (Badan Mediasi dan Arbitrase Asuransi Indonesia) atau lembaga mediasi yang disepakati dalam [PERIODE MEDIASI: tentukan — disarankan 30 hari]; Langkah 3 — Mekanisme Beli-Jual: Pihak yang memulai ('Offeror') menyampaikan harga per saham ('Harga Kebuntuan') kepada Pihak lain ('Offeree'). Offeree memilih dalam [PERIODE PEMILIHAN: tentukan — disarankan 30 hari] untuk membeli atau menjual pada Harga Kebuntuan. Jika Offeree tidak memilih dalam Periode Pemilihan, dianggap memilih untuk menjual. / [Art.1266 waiver as above]. A Deadlock occurs if Parties cannot reach a decision within [PERIOD — recommend 30 days]. Resolution: Step 1 — Escalation to senior management within [PERIOD — recommend 20 Business Days]; Step 2 — Mediation at agreed mediation centre within [PERIOD — recommend 30 days]; Step 3 — Buy-Sell: Offeror sets price per share (Deadlock Price); Offeree elects within [PERIOD — recommend 30 days] to buy or sell at Deadlock Price. Failure to elect = deemed election to sell.",
        "Statutory Reference": "KUHPerdata Art.1266-1267 (waiver); UU No. 30/1999 (mediation/arbitration); UU No. 40/2007 tentang PT (share transfer procedure)",
        "Statutory Detail": "Art.1266 waiver is mandatory — without it, triggering the buy-sell mechanism could require a court order. The verbatim Indonesian waiver text is required. Share transfer in PT (following buy-sell exercise) must comply with UU PT: (1) offer to existing shareholders first (right of first refusal) unless Anggaran Dasar waives this requirement; (2) RUPS approval may be required for share transfer depending on Anggaran Dasar; (3) Deed of share transfer (Akta Jual Beli Saham) by Notaris required. Texas Shoot-Out is commercially effective in Indonesia — KUHPerdata freedom of contract supports it. Deemed election to sell protects against inaction by Offeree.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "Art.1266 waiver verbatim Indonesian text is mandatory here — deadlock mechanism is a termination-adjacent mechanism. Share transfer following buy-sell must comply with UU PT and Anggaran Dasar — include Art.1266 waiver AND RUPS/pre-emption waiver in Anggaran Dasar if parties want clean execution of buy-sell without additional approvals. Lawyer review: liquidity asymmetry between SG and ID parties may disadvantage the party with less cash — consider valuation expert alternative to self-set price.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-011",
        "Label": "Dividend policy and tax",
        "SG Behavior": "Board-discretion or minimum percentage; SGD or USD; Singapore one-tier tax — no dividend WHT",
        "ID Requirement": "IDR or USD dividends; Indonesian WHT on dividends to non-residents (reduced by DTA); RUPS approval for dividend declaration",
        "Template Clause": "Dividen dinyatakan berdasarkan keputusan RUPS sesuai UU PT. Kebijakan dividen: [KEBIJAKAN DIVIDEN: pilih — (a) PT JV mendistribusikan tidak kurang dari [PERSENTASE]% dari laba bersih tahunan sebagai dividen, tunduk pada kecukupan kas; atau (b) dividen dinyatakan atas kebijaksanaan RUPS]. Dividen dibayarkan dalam [MATA UANG: USD / IDR] dalam [JANGKA WAKTU: tentukan — disarankan 30 hari] setelah tanggal deklarasi. Pajak penghasilan atas dividen yang dibayarkan kepada Pihak SG dipotong sesuai Pasal 26 UU PPh dengan tarif DTA Indonesia-Singapura yang berlaku (saat ini [TARIF: tentukan — biasanya 10% atau 15% tergantung kepemilikan]). / Dividends declared by RUPS per UU PT. Policy: [POLICY: select — (a) PT JV distributes not less than [%] of annual net profits subject to cash adequacy; or (b) at RUPS discretion]. Dividends paid in [CURRENCY: USD/IDR] within [PERIOD — recommend 30 days] after declaration. WHT on dividends to SG party deducted per PPh Pasal 26 at applicable DTA rate (currently [RATE — typically 10% or 15% depending on ownership]).",
        "Statutory Reference": "UU No. 40/2007 tentang PT Art.70-72 (profit distribution); UU PPh No. 36/2008 Pasal 26 (WHT on dividends); P3B Indonesia-Singapura (DTA)",
        "Statutory Detail": "SIGNIFICANT DIFFERENCE from SG JV — Indonesia imposes WHT on dividends to non-resident shareholders:\nStandard rate: 20% (PPh Pasal 26).\nDTA rate (with valid IRAS COR): typically 10% for ownership <25%; 10-15% for ownership ≥25% — verify current DTA rates as they may change.\nWithout IRAS COR: full 20% withheld — significant cash flow impact.\nRUPS dividend declaration: UU PT requires RUPS resolution for dividend declaration — informal board resolutions are insufficient. Dividend can only be paid from retained earnings — not from capital. UU PT Art.70 requires mandatory reserve fund allocation (5% of net profit per year until reserve equals 20% of issued capital) before dividend payment.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "IRAS COR must be obtained annually BEFORE each dividend payment to access DTA reduced WHT rates. Without COR: 20% WHT on ALL dividends — significant impact on SG party's return. RUPS procedure for dividend declaration is formal — ensure RUPS calendar is aligned with dividend payment expectations. Mandatory reserve fund allocation under UU PT Art.70 must be factored into dividend policy design.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-012",
        "Label": "IP contributed to JV — licence vs assignment",
        "SG Behavior": "Licence preferred for CN/SG party; assignment with IPOS registration; royalty arm's length under IRAS transfer pricing",
        "ID Requirement": "Licence preferred; DJKI registration for assignment; KJPP valuation for non-cash IP contribution; PPh WHT on royalties to non-residents; transfer pricing DJP scrutiny",
        "Template Clause": "[JIKA LISENSI HKI]: [PIHAK SG] memberikan kepada PT JV lisensi [eksklusif/non-eksklusif], [bebas royalti/berbayar royalti sebesar [TARIF ROYALTI]% dari pendapatan bersih], tidak dapat dialihkan, untuk menggunakan [HKI YANG DILISENSIKAN: uraikan] untuk menjalankan Bisnis JV di Wilayah selama Jangka Waktu Perjanjian. Lisensi berakhir otomatis pada pengakhiran Perjanjian ini. / [IF IP LICENCE]: [SG PARTY] grants PT JV a [exclusive/non-exclusive], [royalty-free/royalty-bearing at [ROYALTY RATE]% of net revenue], non-transferable licence to use [LICENSED IP] for the JV Business in the Territory during the Term. Licence terminates automatically on termination of this Agreement.\n\nPembayaran royalti kepada Pihak SG dikenakan PPh Pasal 26 sebesar [TARIF DTA: tentukan — biasanya 10-15% berdasarkan P3B Indonesia-Singapura]. / Royalty payments to SG Party subject to PPh Pasal 26 at [DTA RATE — typically 10-15% per Indonesia-Singapore DTA].",
        "Statutory Reference": "UU No. 20/2016 (Trade Marks); UU No. 13/2016 (Patents); UU No. 28/2014 (Copyright — moral rights non-waivable); DJKI registration; UU PPh Pasal 26 (WHT on royalties to non-residents); P3B Indonesia-Singapura; DGT PER-25/PJ/2018; IRAS transfer pricing guidelines",
        "Statutory Detail": "KEY DIFFERENCES from SG JV:\n1. Moral rights (hak moral): UU Hak Cipta Art.5-6 — non-waivable in Indonesia. IP creator's moral rights survive even after assignment of economic rights — acknowledging moral rights in the licence is required.\n2. Royalty WHT: royalties paid from Indonesian PT to SG licensor are subject to PPh Pasal 26 — standard 20%, reduced to 10-15% under DTA with valid IRAS COR. This significantly affects the economics of a royalty-bearing IP licence.\n3. DJKI registration: trade mark and patent assignments/licences must be registered with DJKI to be enforceable against third parties. DJKI registration takes 3-6 months.\n4. Transfer pricing: DJP scrutinises IP royalty arrangements between related parties — royalty rates must be arm's length (verified against OECD comparable data).",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "Licence is almost always preferable for SG party — protects IP if JV fails. Royalty WHT (PPh 26) must be factored into pricing — effective royalty rate is reduced by 10-20% depending on DTA compliance. DJKI registration of trade mark before JV commencement is strongly recommended — first-to-file jurisdiction. Moral rights acknowledgment clause is mandatory for any copyrighted material.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-013",
        "Label": "IP created by the JV — ownership and exit",
        "SG Behavior": "JV IP owned by JV Company; exit provisions for IP on dissolution or buyout",
        "ID Requirement": "JV IP owned by PT JV; moral rights of individual creators non-waivable; DJKI registration of JV IP; exit provisions critical",
        "Template Clause": "Seluruh kekayaan intelektual yang dibuat oleh PT JV atau karyawannya dalam menjalankan Bisnis JV ('HKI JV') menjadi milik PT JV. Pada saat pengakhiran atau pembubaran PT JV: [PENGATURAN HKI SAAT EXIT: pilih — (a) HKI JV dialihkan kepada [PIHAK: tentukan]; (b) setiap Pihak mendapatkan lisensi non-eksklusif, bebas royalti untuk menggunakan HKI JV di luar Bisnis JV]. Hak moral (hak moral) pencipta individual berdasarkan UU Hak Cipta No. 28/2014 tidak dapat dikesampingkan. / All IP created by PT JV or its employees in the JV Business ('JV IP') vests in PT JV. On termination/dissolution: [EXIT IP: select — (a) JV IP assigned to [PARTY]; (b) each Party receives non-exclusive royalty-free licence to use JV IP outside JV Business]. Moral rights (hak moral) of individual creators under Copyright Law No. 28/2014 cannot be waived.",
        "Statutory Reference": "UU No. 28/2014 tentang Hak Cipta Art.5-6 (moral rights); Art.34 (employer IP); UU No. 13/2016 tentang Paten Art.12 (employee inventions); DJKI",
        "Statutory Detail": "Identical structure to JV-SG-013 but with moral rights caveat. Indonesian Copyright Law Art.34: works created by PT JV employees in the course of employment vest in the PT JV as employer. Patents: UU Paten Art.12 — inventions by employees belong to employer if created in the scope of duties and using employer resources; otherwise employee retains. Employment contracts for PT JV employees must include IP assignment clauses consistent with UU Hak Cipta and UU Paten.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "Moral rights acknowledgment is mandatory. DJKI registration of JV IP (trade marks, patents) during the JV and on dissolution protects both parties. Exit IP disposition must be agreed upfront.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-014",
        "Label": "Transfer restrictions and pre-emption",
        "SG Behavior": "General prohibition; permitted transfers to affiliates; ROFR; constitution must mirror",
        "ID Requirement": "Transfer restrictions in Anggaran Dasar are binding on the PT; UU PT Art.57 right of first refusal exists by default; Notarial deed for share transfer",
        "Template Clause": "Tidak ada Pihak yang boleh mengalihkan sahamnya di PT JV tanpa persetujuan tertulis sebelumnya dari Pihak lain, kecuali Pengalihan yang Diizinkan. 'Pengalihan yang Diizinkan' berarti pengalihan kepada anak perusahaan atau perusahaan induk yang sepenuhnya dimiliki, dengan syarat entitas tersebut menandatangani Akta Pengikatan Diri. Sebelum pengalihan kepada pihak ketiga manapun, Pihak pengalih wajib terlebih dahulu menawarkan saham tersebut kepada Pihak lain dengan harga dan syarat yang sama ('Hak Membeli Pertama') dalam [PERIODE: tentukan — disarankan 30 hari]. Setiap pengalihan saham wajib dilakukan melalui Akta Jual Beli Saham di hadapan Notaris. / No Party may transfer PT JV shares without prior written consent except Permitted Transfers (to wholly-owned subsidiaries/holding companies bound by deed of adherence). Pre-emption: before any third-party transfer, the transferring Party shall first offer shares to the other Party at same price and terms (right of first refusal) within [PERIOD — recommend 30 days]. All share transfers by Notarial Deed (Akta Jual Beli Saham).",
        "Statutory Reference": "UU No. 40/2007 tentang PT Art.57-62 (share transfer); Art.57 (statutory ROFR); Anggaran Dasar restrictions",
        "Statutory Detail": "UU PT Art.57: shareholders of PT have a statutory right of first refusal on share transfers by other shareholders — this is a default protection under Indonesian company law. The JV agreement ROFR clause supplements and clarifies this default right. NOTARIAL DEED REQUIREMENT: All PT share transfers in Indonesia must be executed before a Notaris (Indonesian notary) — an Akta Jual Beli Saham (Deed of Sale and Purchase of Shares) is legally required. A private transfer agreement alone is insufficient. The notarial deed must then be reported to and approved by Kemenkumham for amendment of the company register. Transfer restrictions must be embedded in Anggaran Dasar to bind the company.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "Notarial deed requirement is non-negotiable — PT share transfers without notarial deed are legally incomplete. Budget for Notaris fees in share transfer timeline. Kemenkumham approval for Anggaran Dasar amendments takes 1-2 weeks. Transfer restrictions in JV agreement must be mirrored in Anggaran Dasar.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-015",
        "Label": "Drag-along and tag-along rights",
        "SG Behavior": "Drag-along by majority; tag-along for minority; equal price per share; enforceable under contract",
        "ID Requirement": "Drag-along and tag-along enforceable under KUHPerdata; share transfer by notarial deed; RUPS approval may be required; Anggaran Dasar must accommodate",
        "Template Clause": "Drag-Along: Jika Pihak yang memegang tidak kurang dari [AMBANG DRAG: tentukan]% saham ('Pihak Drag') bermaksud menjual seluruh sahamnya kepada pembeli pihak ketiga, Pihak Drag dapat mewajibkan Pihak lain ('Pihak yang Didrag') untuk menjual seluruh sahamnya kepada pembeli yang sama dengan harga per saham yang sama. Pihak yang Didrag wajib menyelesaikan pengalihan dalam [PERIODE: tentukan — disarankan 30 hari] setelah menerima pemberitahuan drag-along. / Drag-Along: If a Party holding ≥[DRAG THRESHOLD]% shares ('Dragging Party') proposes to sell all shares to a bona fide third party, Dragging Party may require other Party ('Dragged Party') to sell all shares to same buyer at same price per share. Dragged Party completes transfer within [PERIOD — recommend 30 days] of drag notice.\n\nTag-Along: Jika Pihak penjual bermaksud mengalihkan sahamnya kepada pihak ketiga, Pihak lain berhak ikut serta dalam penjualan tersebut dengan harga per saham yang sama ('Hak Ikut Serta') dengan memberitahukan dalam [PERIODE: tentukan — disarankan 15 hari] setelah menerima pemberitahuan pengalihan. / Tag-Along: If a selling Party proposes to transfer shares to a third party, the other Party has the right to join the sale at same price per share ('Tag-Along Right') by notice within [PERIOD — recommend 15 days] of transfer notice.",
        "Statutory Reference": "KUHPerdata Art.1338 (freedom of contract); UU No. 40/2007 tentang PT Art.57-62 (share transfer); Notarial deed requirement",
        "Statutory Detail": "Drag-along and tag-along are enforceable under KUHPerdata freedom of contract. Execution requires: (1) Notarial Akta Jual Beli Saham for the actual share transfer; (2) if the PT's Anggaran Dasar requires RUPS approval for share transfers, either include a deemed RUPS approval provision for drag/tag scenarios in the Anggaran Dasar, or ensure RUPS can be convened quickly. Equal price protection for Dragged/Tag-Along Party is fundamental — same rationale as SG JV. Positive Investment List compliance must be checked for the buyer — a transfer to a foreign buyer that would breach the maximum foreign ownership percentage is invalid under Indonesian investment law.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "Positive Investment List compliance check for the drag/tag buyer is required — cannot transfer to a foreign buyer if it would exceed the permitted foreign ownership percentage for the sector. Notarial deed timeline (typically 1-2 weeks) must be factored into drag/tag completion periods.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-016",
        "Label": "Non-compete — parties",
        "SG Behavior": "Non-compete during JV term and post-exit; SG restraint of trade doctrine; legitimate interest required",
        "ID Requirement": "KUHPerdata freedom of contract; UU No. 5/1999 Art.15 (exclusive dealing); 12-24 months defensible; geographic scope limited to Indonesia or JV territory",
        "Template Clause": "Selama Jangka Waktu Perjanjian dan selama [PERIODE: tentukan — disarankan 12-24 bulan] setelah tanggal Pihak tersebut tidak lagi memegang saham di PT JV, masing-masing Pihak tidak akan, secara langsung atau tidak langsung, di [WILAYAH GEOGRAFIS: tentukan — Indonesia / wilayah operasi JV], terlibat dalam bisnis yang bersaing langsung dengan Bisnis JV sebagaimana diuraikan dalam Lampiran [JADWAL BISNIS JV], tanpa persetujuan tertulis Pihak lain. / During the Term and for [PERIOD — recommend 12-24 months] after ceasing to hold PT JV shares, each Party shall not, directly or indirectly, in [GEOGRAPHIC SCOPE — Indonesia / JV operating territory], engage in business directly competing with the JV Business as described in Schedule [JV BUSINESS SCHEDULE], without prior written consent.",
        "Statutory Reference": "KUHPerdata Art.1338 (freedom of contract); Art.1337 (lawful cause); UU No. 5/1999 Art.15 (exclusive dealing); KPPU enforcement",
        "Statutory Detail": "Party-level non-competes in Indonesian JV agreements are enforceable under KUHPerdata Art.1338 (freedom of contract) where the JV itself is the legitimate interest. UU No. 5/1999 Art.15 risk: a non-compete preventing either party from engaging in any related business for an extended period could be challenged as exclusive dealing if it substantially restricts competition. KPPU has the power to void anti-competitive provisions. 12-24 months and geographic scope limited to JV territory is defensible; broader restrictions carry KPPU challenge risk.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "PARAMETERIZED — period and geographic scope require user input. Recommend defining JV Business precisely in schedule — KPPU review risk if scope is overbroad. Lawyer review to confirm proportionality.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-017",
        "Label": "Data protection — UU PDP for JV Company",
        "SG Behavior": "JV Company must comply with PDPA; DPO appointment; overseas transfer restrictions",
        "ID Requirement": "PT JV must comply with UU PDP No. 27/2022; DPO appointment recommended; 14-day breach notification; data flows between PT JV and SG party are cross-border transfers",
        "Template Clause": "Para Pihak wajib memastikan PT JV: (a) mengadopsi kebijakan perlindungan data pribadi yang sesuai dengan UU No. 27/2022 tentang UU PDP dalam [PERIODE: tentukan — disarankan 60 hari] setelah pendirian; (b) menunjuk Petugas Perlindungan Data Pribadi jika diwajibkan; (c) tidak mengalihkan data pribadi ke luar Indonesia kepada Para Pihak kecuali disertai perlindungan kontraktual yang setara dengan UU PDP Pasal 56; (d) memberitahu Para Pihak dalam 24 jam dan BSSN/Kominfo dalam 14 hari kalender jika terjadi pelanggaran data pribadi yang dapat dilaporkan. / Parties shall procure PT JV: (a) adopts UU PDP-compliant data protection policy within [PERIOD — recommend 60 days] of incorporation; (b) appoints a Data Protection Officer if required; (c) does not transfer personal data outside Indonesia to the Parties except under contractual safeguards equivalent to UU PDP Art.56; (d) notifies Parties within 24 hours and BSSN/Kominfo within 14 calendar days of a notifiable data breach.",
        "Statutory Reference": "UU No. 27/2022 tentang UU PDP Art.46 (breach notification 14 days); Art.56 (cross-border transfer); BSSN; Kominfo",
        "Statutory Detail": "UU PDP (effective October 2024) applies to PT JV as a data controller. Key differences from PDPA that affect the JV structure: (1) 14-day breach notification (vs PDPA 3 days) — internal 24-hour notification gives parties time to coordinate; (2) Cross-border transfer from PT JV to SG party requires contractual safeguards — Singapore has not received an adequacy determination from Indonesia; (3) Data localisation for strategic sectors (financial, health, government) under GR No. 71/2019 still applies alongside UU PDP; (4) Penalties: up to IDR 60 billion (~SGD 5.4M) or 2% of annual revenue. UU PDP implementing regulations still being finalised — monitor Kominfo.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "Lawyer review: data flows between PT JV and SG party require contractual safeguards under UU PDP Art.56. UU PDP implementing regulations still being finalised — track Kominfo updates quarterly.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-018",
        "Label": "Anti-corruption — UU Tipikor and KPK",
        "SG Behavior": "POCA; FCPA/UKBA where applicable; sanctions representations",
        "ID Requirement": "UU Tipikor; KPK enforcement; Gratifikasi prohibition; BUMN counterparty risk; sanctions screening for SG party",
        "Template Clause": "Masing-masing Pihak menyatakan, menjamin, dan berjanji bahwa: (a) akan mematuhi UU No. 31/1999 jo. UU No. 20/2001 (UU Tipikor) dan larangan Gratifikasi Pasal 12B; (b) tidak ada Pihak atau pejabatnya yang sedang dalam penyelidikan atau terkena sanksi oleh otoritas mana pun termasuk OFAC, EU, atau OFSI; (c) akan segera memberitahu Pihak lain jika terjadi perubahan status kepatuhan. / Each Party represents, warrants, and undertakes: (a) it will comply with UU Tipikor (Law No. 31/1999 as amended) and the Gratifikasi prohibition under Art.12B; (b) neither it nor its officers is under investigation or subject to sanctions by any authority including OFAC, EU, or OFSI; (c) it will promptly notify the other Party of any change in compliance status.",
        "Statutory Reference": "UU No. 31/1999 jo. UU No. 20/2001 (UU Tipikor); Art.12B (Gratifikasi); UU No. 30/2002 (KPK); MAS Notice on Sanctions; OFAC; EU Sanctions",
        "Statutory Detail": "Combined anti-corruption and sanctions representation for SG→ID JV. UU Tipikor: applies to PT JV and both party shareholders. Gratifikasi: IDR 1M threshold — particularly relevant where PT JV engages with government counterparties, regulators (OJK, BI, BPOM, BKPM), or BUMN. Sanctions: SG party's compliance with MAS Notice on Sanctions; Indonesian party's compliance with Indonesian sanctions (less developed regime but increasingly aligned with UN sanctions). BUMN counterparty: if either party is or becomes a BUMN-affiliated entity, its officers become Penyelenggara Negara — Gratifikasi obligations apply.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "Sanctions screening of Indonesian JV partner required before execution. Particularly important if Indonesian partner has government/BUMN links. KPK enforcement has included JV-related prosecutions in Indonesia.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-019",
        "Label": "Term and termination — Art.1266 waiver",
        "SG Behavior": "Fixed initial term; termination triggers; court order not required",
        "ID Requirement": "Art.1266 waiver verbatim mandatory; fixed initial term; termination for cause, convenience, regulatory event; dissolution via RUPS",
        "Template Clause": "Para Pihak dengan ini secara tegas mengesampingkan ketentuan Pasal 1266 dan Pasal 1267 KUHPerdata yang mensyaratkan penetapan pengadilan untuk pengakhiran perjanjian. / The Parties hereby expressly waive KUHPerdata Arts.1266 and 1267 court order requirement for termination.\n\nPerjanjian ini berlaku mulai tanggal penandatanganan dan berlanjut selama jangka waktu awal [JANGKA WAKTU AWAL: tentukan — disarankan 5 tahun] kecuali diakhiri lebih awal. Setelah Jangka Waktu Awal, Perjanjian dapat diakhiri dengan pemberitahuan tertulis [PERIODE PEMBERITAHUAN: tentukan — disarankan 12 bulan]. Perjanjian berakhir segera: (a) pelanggaran material yang tidak diperbaiki dalam 30 hari setelah pemberitahuan; (b) kepailitan atau PKPU Pihak lain; (c) perubahan hukum atau regulasi yang membuat Bisnis JV ilegal dan tidak dapat direstrukturisasi dalam 60 hari; atau (d) penyelesaian mekanisme beli-jual. / Agreement continues for initial term of [INITIAL TERM — recommend 5 years] unless earlier terminated. After Initial Term, terminable by [NOTICE — recommend 12 months] written notice. Terminates immediately on: (a) material breach unremedied after 30 days; (b) insolvency or PKPU; (c) regulatory change making JV Business illegal unremedied in 60 days; (d) completion of buy-sell mechanism.",
        "Statutory Reference": "KUHPerdata Art.1266-1267 (waiver); UU No. 37/2004 (Bankruptcy/PKPU); UU No. 40/2007 tentang PT Art.142 (dissolution grounds)",
        "Statutory Detail": "Art.1266 waiver is mandatory and verbatim Indonesian text is required — without it, termination requires a court order. 5-year initial term is appropriate for JVs — longer than distribution agreements to reflect higher establishment cost. PT PMA dissolution requires: RUPS resolution (special resolution) + Kemenkumham approval + liquidation process — this takes 6-18 months under UU PT Art.142-152. The JV agreement termination and the PT company dissolution are separate processes — the JV agreement terminates between the parties; the PT company is then wound up separately under UU PT procedures.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "Art.1266 waiver verbatim Indonesian text mandatory. PT company dissolution is a separate process from JV agreement termination — both must be addressed. PT dissolution takes 6-18 months and requires Notaris, Kemenkumham, DJP tax clearance, and RUPS resolutions. Factor PT dissolution timeline into exit planning.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-020",
        "Label": "Consequences of termination — PT dissolution",
        "SG Behavior": "Structured winding up per Companies Act; IP reassignment; survival of obligations",
        "ID Requirement": "PT dissolution under UU PT Art.142-152; RUPS special resolution; Kemenkumham approval; liquidator; DJP tax clearance required before final dissolution",
        "Template Clause": "Pada saat pengakhiran Perjanjian ini (selain melalui pembelian saham berdasarkan mekanisme deadlock atau drag-along): (a) Para Pihak mengadakan RUPS Luar Biasa untuk memutuskan pembubaran PT JV sesuai UU PT Pasal 142; (b) Para Pihak menunjuk likuidator dan mengawasi proses likuidasi sesuai UU PT Pasal 147-152; (c) aset PT JV didistribusikan sesuai urutan prioritas: (i) penyelesaian hutang kepada kreditur pihak ketiga; (ii) pengembalian pinjaman pemegang saham (pro rata jika tidak mencukupi); (iii) distribusi aset tersisa kepada pemegang saham sesuai persentase kepemilikan; (d) HKI yang dilisensikan kepada PT JV dikembalikan kepada pemberi lisensi; (e) kewajiban kerahasiaan dan non-bersaing tetap berlaku sesuai ketentuan masing-masing. / On termination (other than by share acquisition): (a) Parties convene RUPS to resolve PT JV dissolution per UU PT Art.142; (b) appoint liquidator and oversee liquidation per UU PT Art.147-152; (c) PT JV assets distributed: (i) third-party creditors settled; (ii) shareholder loans returned pro rata; (iii) remaining assets to shareholders per shareholding; (d) licensed IP reverts to licensor; (e) confidentiality and non-compete obligations survive per their respective clauses.",
        "Statutory Reference": "UU No. 40/2007 tentang PT Art.142-152 (pembubaran dan likuidasi); DJP tax clearance (Surat Keterangan Fiskal); Kemenkumham approval",
        "Statutory Detail": "PT dissolution process is significantly more complex than SG company winding up:\n1. RUPS special resolution: quorum 3/4 of shares, 3/4 approval (UU PT Art.144).\n2. Liquidator appointment: can be Direksi or external liquidator.\n3. Creditor notification: 30-day public notice and private creditor notices.\n4. DJP tax clearance (Surat Keterangan Fiskal): required before final dissolution — all tax obligations must be settled; this is often the longest step (3-6 months).\n5. Kemenkumham approval of dissolution deed.\nTotal timeline: 6-18 months minimum for PT dissolution.\nAsset distribution: Indonesian law creditor priority applies — contractual distribution between shareholders cannot override statutory creditor priority (UU PT Art.150).",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "PT dissolution timeline of 6-18 months must be factored into exit planning. DJP tax clearance is the critical path item — engage Indonesian tax adviser early. Kemenkumham approval required for dissolution deed — Notaris must prepare. Asset distribution between shareholders is subject to statutory creditor priority.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-021",
        "Label": "Confidentiality",
        "SG Behavior": "3-year post-exit; trade secrets indefinite; bilateral; JV company information protected",
        "ID Requirement": "UU Rahasia Dagang No. 30/2000; KUHPerdata; 3-year standard; identical structure to SA-ID-009",
        "Template Clause": "Masing-masing Pihak wajib menjaga kerahasiaan: (a) Informasi Rahasia Pihak lain yang diungkapkan sehubungan dengan Perjanjian ini; dan (b) informasi rahasia PT JV ('Informasi Rahasia JV'). Kewajiban ini berlaku selama Jangka Waktu Perjanjian dan selama [PERIODE PASCA-EXIT: tentukan — disarankan 3 tahun] setelah Pihak tersebut tidak lagi memegang saham di PT JV, dan tanpa batas waktu untuk rahasia dagang berdasarkan UU No. 30/2000. / Each Party shall keep confidential: (a) the other Party's Confidential Information; and (b) PT JV confidential information. Survives for [POST-EXIT PERIOD — recommend 3 years] after ceasing to hold PT JV shares, and indefinitely for trade secrets (UU No. 30/2000).",
        "Statutory Reference": "UU No. 30/2000 tentang Rahasia Dagang; KUHPerdata Art.1338; UU ITE No. 11/2008",
        "Statutory Detail": "Identical rationale to SA-ID-013. Trade Secrets Law (UU No. 30/2000) provides criminal penalties for misappropriation. Post-exit period tied to share disposal.",
        "Risk Level": "Medium",
        "Notes": "Auto-apply. 3-year post-exit period is market standard for Indonesian JV agreements.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-022",
        "Label": "Entire agreement, good faith, and variation",
        "SG Behavior": "Entire agreement supersedes MOU; written variation; electronic signatures valid",
        "ID Requirement": "Entire agreement; itikad baik acknowledgment mandatory; written variation; electronic execution valid under UU ITE",
        "Template Clause": "Perjanjian ini (beserta Lampiran dan Anggaran Dasar PT JV) merupakan keseluruhan kesepakatan Para Pihak dan menggantikan semua perjanjian sebelumnya termasuk MOU atau term sheet. Tidak ada perubahan yang mengikat kecuali dibuat secara tertulis dan ditandatangani oleh wakil yang berwenang. Para Pihak mengakui kewajiban itikad baik berdasarkan KUHPerdata Pasal 1338 yang tidak dapat dikesampingkan. Tanda tangan elektronik sah dan mengikat sesuai UU ITE Pasal 11. / This Agreement (with Schedules and PT JV Anggaran Dasar) is the entire agreement and supersedes all prior agreements including any MOU or term sheet. No amendment binding unless in writing and signed by authorised representatives. Parties acknowledge the mandatory good faith obligation under KUHPerdata Art.1338. Electronic signatures are valid per UU ITE Art.11.",
        "Statutory Reference": "KUHPerdata Art.1338 (itikad baik); Art.1339; UU ITE No. 11/2008 jo. No. 19/2016 Art.11 (electronic signatures)",
        "Statutory Detail": "Itikad baik is non-waivable and applies to the entire JV relationship — Indonesian courts have applied it to: (1) require reasonable notice even where short notice is contractually provided; (2) award damages for commercially unreasonable exercise of contractual rights; (3) prevent one party from acting inconsistently with representations made during negotiations. Electronic signatures under UU ITE are valid for Indonesian-law agreements. MOU supersession is important — the JV agreement should be the definitive document.",
        "Risk Level": "Medium",
        "Notes": "Auto-apply. Itikad baik acknowledgment is expected by Indonesian parties and sets correct expectations about Indonesian court interpretation approach.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      },
      {
        "Concept ID": "JV-ID-023",
        "Label": "Notices and force majeure",
        "SG Behavior": "Written notices; email valid; deemed receipt; force majeure with SG common law standard",
        "ID Requirement": "Bilingual notices; UU ITE for electronic notices; Indonesian address required; KUHPerdata overmacht; natural disasters relevant",
        "Template Clause": "Pemberitahuan: Semua pemberitahuan dibuat secara tertulis dalam Bahasa Indonesia dan Bahasa Inggris, disampaikan melalui: (a) pengiriman langsung; (b) pos tercatat atau kurir internasional; atau (c) email dengan konfirmasi penerimaan. Dianggap diterima: (a) saat pengiriman langsung; (b) 7 hari kerja setelah pos internasional; (c) hari kerja berikutnya setelah transmisi email. / Notices: All notices in Bahasa Indonesia and English, by: (a) hand delivery; (b) registered post or international courier; or (c) email with delivery confirmation. Deemed received: (a) on hand delivery; (b) 7 Business Days after international post; (c) next Business Day after email.\n\nKeadaan Kahar: Tidak ada Pihak yang bertanggung jawab atas kegagalan pelaksanaan akibat keadaan kahar (overmacht) termasuk bencana alam, gempa bumi, letusan gunung berapi, banjir, tsunami, perang, pandemi (BNPB), atau tindakan pemerintah yang secara langsung mencegah pelaksanaan. Jika berlanjut lebih dari 6 bulan, salah satu Pihak dapat mengakhiri Perjanjian. / Force Majeure: Neither Party liable for failure due to force majeure (overmacht) including natural disasters, earthquakes, volcanic eruptions, floods, tsunamis, war, pandemic (BNPB-declared), or government actions directly preventing performance. 6-month longstop then either Party may terminate.",
        "Statutory Reference": "UU ITE No. 11/2008 Art.11 (electronic communications); KUHPerdata Art.1244-1245 (overmacht); UU No. 24/2007 (Disaster Management); BNPB",
        "Statutory Detail": "Bilingual notices required — consistent with language clause. 7 Business Days for international post reflects SG-ID transit times. Force majeure: Indonesia's Ring of Fire geography makes natural disaster force majeure operationally significant. 6-month longstop for JV (longer than distribution — reflects higher establishment costs and longer-term nature). BNPB declaration of national disaster is the reference point for pandemic/disaster force majeure — specific Indonesian government declaration, not general media reports.",
        "Risk Level": "Medium",
        "Notes": "Auto-apply. Natural disaster force majeure references are operationally significant in Indonesia. 6-month longstop consistent with JV long-term nature.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Joint Venture Agreement (SG→ID)"
      }
    ]
  },
  "Non-Exclusive Distribution Clauses (SG-ID)": {
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
        "Concept ID": "NEDA-ID-001",
        "Label": "Governing law and language",
        "SG Behavior": "Singapore law; English only; no language requirement",
        "ID Requirement": "Indonesian law (KUHPerdata); bilingual mandatory; Indonesian version prevails",
        "Template Clause": "Perjanjian ini diatur oleh dan ditafsirkan sesuai dengan hukum Republik Indonesia (KUHPerdata). Perjanjian ini dibuat dalam Bahasa Indonesia dan Bahasa Inggris; dalam hal terdapat pertentangan, versi Bahasa Indonesia yang berlaku dan mengikat Para Pihak. / This Agreement is governed by the laws of Indonesia (KUHPerdata). Made in Bahasa Indonesia and English; in case of inconsistency, the Bahasa Indonesia version shall prevail and be binding on the Parties.",
        "Statutory Reference": "KUHPerdata Buku III; UU No. 24/2009 Art.31 (Language Law); SC Decision No. 601 K/Pdt/2015",
        "Statutory Detail": "Combines governing law and language requirement — identical rationale to DA-ID-001 and SA-ID-001/014. KUHPerdata civil law framework: good faith (itikad baik) Art.1338 is mandatory and non-waivable. Bilingual requirement: SC Decision No. 601 K/Pdt/2015 voided English-only agreement. Indonesian version prevails — 'equally authentic' creates interpretive uncertainty; Indonesian courts default to Indonesian version regardless.",
        "Risk Level": "High",
        "Notes": "Auto-apply. Sworn translator (penerjemah tersumpah) required for Bahasa Indonesia version.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-002",
        "Label": "Dispute resolution",
        "SG Behavior": "SIAC; Singapore seat; English language",
        "ID Requirement": "BANI or SIAC; BANI preferred for Indonesian enforcement; New York Convention applies",
        "Template Clause": "[OPTION A — BANI]: Setiap perselisihan diselesaikan melalui arbitrase di Badan Arbitrase Nasional Indonesia ('BANI'), Jakarta, dalam Bahasa Indonesia dan/atau Bahasa Inggris, sesuai Peraturan BANI yang berlaku. / Any dispute shall be resolved by BANI arbitration, Jakarta seat, Bahasa Indonesia and/or English, under BANI Rules.\n\n[OPTION B — SIAC]: Any dispute shall be referred to SIAC arbitration, Singapore seat, English language, enforceable in Indonesia under Presidential Decree No. 34/1981 (New York Convention ratification).",
        "Statutory Reference": "UU No. 30/1999 (Arbitration Law); Keppres No. 34/1981 (New York Convention); BANI Rules 2022",
        "Statutory Detail": "Identical to DA-ID-002. BANI preferred for non-exclusive distribution disputes where Indonesian enforcement (payment collection, stock return) is primary concern. SIAC preferred where SG principal's IP or confidentiality protection is primary. In non-exclusive arrangements, payment disputes with Indonesian distributors are the most common issue — BANI direct enforcement advantage is more significant than in exclusive arrangements.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "PARAMETERIZED — BANI strongly recommended for non-exclusive DA where multiple distributors may be involved and payment enforcement is primary risk.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-003",
        "Label": "Bea Meterai stamp duty",
        "SG Behavior": "No stamp duty on commercial agreements",
        "ID Requirement": "IDR 10,000 Bea Meterai mandatory; e-Meterai available; unstamped agreement inadmissible as evidence",
        "Template Clause": "Bea Meterai yang terhutang atas Perjanjian ini ditanggung oleh [PIHAK: tentukan — Para Pihak bersama / Distributor]. Perjanjian ini wajib dibubuhi Bea Meterai sebelum penandatanganan sesuai UU No. 10/2020. / Bea Meterai payable on this Agreement shall be borne by [PARTY: specify]. This Agreement shall be duly stamped before execution per Law No. 10/2020.",
        "Statutory Reference": "UU No. 10/2020 tentang Bea Meterai; PMK No. 134/2021; e-Meterai via Peruri",
        "Statutory Detail": "Identical to DA-ID-003. IDR 10,000 (~SGD 0.85) mandatory. E-Meterai via peruri.co.id. Unstamped agreement can be subsequently stamped (nazegeling) but may be challenged as inadmissible evidence in Indonesian courts before stamping.",
        "Risk Level": "Medium",
        "Notes": "Auto-apply. Trivial cost but non-negotiable for evidentiary admissibility.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-004",
        "Label": "Non-exclusive appointment — triple carve-out",
        "SG Behavior": "Clear non-exclusive statement; Principal retains full rights to appoint others and sell directly",
        "ID Requirement": "Express non-exclusive statement mandatory; Indonesian courts have protected distributors claiming implied exclusivity even without written exclusive terms; triple carve-out essential",
        "Template Clause": "Prinsipal dengan ini menunjuk Distributor sebagai distributor non-eksklusif untuk memasarkan, mempromosikan, mendistribusikan, dan menjual Produk di Wilayah selama Jangka Waktu Perjanjian. Untuk menghindari keraguan: (a) Prinsipal berhak menunjuk distributor, agen, atau penjual lain untuk Produk di dalam atau di luar Wilayah; (b) Prinsipal berhak menjual Produk secara langsung di Wilayah; dan (c) Distributor tidak memiliki hak eksklusivitas atau perlindungan wilayah apapun. / The Principal hereby appoints the Distributor as a non-exclusive distributor to market, promote, distribute, and sell the Products in the Territory during the Term. For the avoidance of doubt: (a) the Principal retains the right to appoint any number of other distributors, agents, or resellers for the Products within or outside the Territory; (b) the Principal retains the right to sell the Products directly in the Territory; and (c) the Distributor shall have no claim to exclusivity or territorial protection of any kind.",
        "Statutory Reference": "KUHPerdata Art.1338 (freedom of contract); Art.1342 (clear terms interpreted literally); Permendag No. 22/M-DAG/PER/3/2016",
        "Statutory Detail": "CRITICAL DIFFERENCE from DA-ID exclusive. Indonesian courts have awarded damages to distributors claiming implied exclusivity based on: (1) long-standing distribution relationships without a written non-exclusive statement; (2) sole distribution of the product in the territory in practice even without an exclusive agreement. The triple carve-out in (a)-(b)-(c) forecloses all three common implied exclusivity arguments. Permendag No. 22/2016 requires registration of SOLE (exclusive) distributor appointments — non-exclusive appointments do not require registration but the non-exclusive character must be clearly documented to avoid the Permendag regime being applied by default.",
        "Risk Level": "High",
        "Notes": "MOST IMPORTANT DIFFERENCE from exclusive DA. All three sub-clauses (a)(b)(c) are mandatory. Do not use softened language ('primary distributor', 'preferred distributor') — these have been construed as implied exclusivity in Indonesian disputes. Auto-apply — no exceptions.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-005",
        "Label": "Indonesian distributor entity — PT requirement",
        "SG Behavior": "Distributor can be any legal entity; no restriction",
        "ID Requirement": "Distributor must be PT (Perseroan Terbatas) incorporated in Indonesia; valid NIB and KBLI classification required",
        "Template Clause": "Distributor menyatakan dan menjamin bahwa Distributor adalah Perseroan Terbatas (PT) yang sah berdasarkan hukum Indonesia dengan Nomor Induk Berusaha (NIB): [NIB] dan klasifikasi KBLI [KODE KBLI] untuk kegiatan distribusi. / The Distributor represents and warrants that it is a validly incorporated Indonesian Perseroan Terbatas (PT) with NIB: [NIB] and KBLI classification [KBLI CODE] for distribution activities. The Distributor holds all required business licences under the OSS system for the distribution of the Products.",
        "Statutory Reference": "UU No. 40/2007 tentang PT; PP No. 5/2021 (OSS); Perpres No. 10/2021 (Positive Investment List); KBLI 2020",
        "Statutory Detail": "Identical to DA-ID-005. PT status and NIB verification are pre-contract due diligence. In non-exclusive arrangements, SG principals may appoint multiple distributors — each must independently satisfy the PT and NIB requirements. Appointing a non-PT entity (individual, CV, or foreign entity) as Indonesian distributor creates contract enforceability risk and potential customs/import licence problems.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "Auto-apply. In non-exclusive arrangements with multiple distributors, verify PT status and NIB for EACH distributor separately. Lawyer review to confirm KBLI code is correct for the product category.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-006",
        "Label": "Product registration — BPOM / SNI",
        "SG Behavior": "Distributor handles Territory compliance; Principal warrants manufacture-country compliance",
        "ID Requirement": "BPOM registration mandatory for food/cosmetics/pharma/medical devices; SNI for regulated goods; distributor holds licence as local responsible party",
        "Template Clause": "Distributor bertanggung jawab untuk memperoleh semua persetujuan BPOM, sertifikasi SNI, dan izin lain yang diperlukan untuk impor, pemasaran, dan penjualan Produk di Indonesia. Prinsipal menyediakan dokumentasi teknis, laporan uji, dan sertifikat kesesuaian yang diperlukan. / The Distributor shall obtain all required BPOM approvals, SNI certifications, and other licences for import, marketing, and sale of the Products in Indonesia. The Principal shall provide technical documentation, test reports, and certificates of conformity required for registration.",
        "Statutory Reference": "Peraturan BPOM No. 27/2017 (MD/ML registration); UU No. 20/2014 (SNI Law); Permendag No. 82/2017",
        "Statutory Detail": "KEY DIFFERENCE from exclusive DA — in a non-exclusive arrangement with multiple distributors, BPOM registration creates a specific complexity: only ONE entity can hold the BPOM marketing authorisation (izin edar) for a specific product. If multiple non-exclusive distributors are appointed, the Principal must decide: (1) one distributor holds BPOM and sub-licenses distribution to others (complex); (2) Principal establishes a local PT to hold BPOM registration directly (more control); (3) only one distributor handles BPOM-regulated products while others handle non-regulated. This is the most operationally complex aspect of non-exclusive distribution in Indonesia for regulated product categories.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "CRITICAL for regulated product categories. Lawyer review essential: BPOM registration structure must be decided BEFORE appointing multiple non-exclusive distributors. Recommend SG principal establishes own PT PMA to hold BPOM registration if planning multi-distributor non-exclusive network — avoids BPOM held by one distributor creating leverage over others.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-007",
        "Label": "Import licence and customs — API-U",
        "SG Behavior": "Distributor handles import; Incoterms 2020 governs risk",
        "ID Requirement": "API-U mandatory; Incoterms 2020 applicable; ATIGA Form D for SG-origin goods",
        "Template Clause": "Pengiriman Produk dilakukan berdasarkan syarat [INCOTERMS: tentukan — misalnya CIF Pelabuhan Jakarta] sesuai Incoterms 2020. Distributor wajib memiliki dan mempertahankan API-U (Angka Pengenal Importir Umum) yang valid selama Jangka Waktu Perjanjian. Bea Masuk dan PPN Impor ditanggung Distributor. Prinsipal menyediakan Surat Keterangan Asal (Form D ASEAN) untuk mendapatkan tarif preferensial ATIGA. / Delivery on [INCOTERMS: specify] per Incoterms 2020. Distributor shall maintain a valid API-U throughout the Term. Import duties and VAT on imports borne by Distributor. Principal shall provide ASEAN Form D certificates of origin for ATIGA preferential tariff rates.",
        "Statutory Reference": "PMK No. 188/2010 (API-U); Incoterms 2020 (ICC); ASEAN Trade in Goods Agreement (ATIGA); INSW",
        "Statutory Detail": "Identical to DA-ID-007. In non-exclusive arrangements with multiple distributors, each distributor independently requires API-U — verify before appointment. ATIGA Form D from SG origin typically gives 0% import duty — significant cost advantage; always include as Principal obligation.",
        "Risk Level": "Medium",
        "Notes": "PARAMETERIZED — Incoterms rule requires user input. CIF Port of Jakarta standard for SG→ID sea freight. Each distributor in a multi-distributor network needs separate API-U verification.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-008",
        "Label": "Sales efforts — no minimum purchase",
        "SG Behavior": "Commercially reasonable efforts; no binding minimum in non-exclusive context",
        "ID Requirement": "Commercially reasonable efforts standard; binding minimum purchase not appropriate without exclusivity consideration; Indonesian good faith applies",
        "Template Clause": "Distributor wajib menggunakan upaya yang wajar secara komersial untuk memasarkan dan menjual Produk di Wilayah. [OPSIONAL — TARGET PENJUALAN NON-MENGIKAT]: Jika Para Pihak menyepakati target penjualan, target tersebut bersifat indikatif dan tidak mengikat serta tidak merupakan kondisi Perjanjian ini. / The Distributor shall use commercially reasonable efforts to market and sell the Products in the Territory. [OPTIONAL — NON-BINDING SALES TARGET]: If the Parties agree on sales targets, such targets shall be indicative only and shall not constitute binding commitments or conditions of this Agreement.",
        "Statutory Reference": "KUHPerdata Art.1338 (good faith); Art.1243 (wanprestasi — breach)",
        "Statutory Detail": "KEY DIFFERENCE from DA-ID exclusive. Binding minimum purchase obligations are commercially inappropriate in non-exclusive arrangements — the distributor receives no territorial protection in return. Indonesian good faith (itikad baik) adds weight to this: Indonesian courts may find a minimum purchase commitment unreasonable where the distributor has no corresponding exclusivity benefit. 'Commercially reasonable efforts' (upaya yang wajar secara komersial) is a lower standard than 'best efforts' (upaya terbaik) — appropriate for non-exclusive context.",
        "Risk Level": "Low",
        "Notes": "KEY DIFFERENCE from DA-ID. No binding minimum purchase. Non-binding sales targets in a schedule are acceptable for performance management purposes only.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-009",
        "Label": "Resale price — competition law (KPPU)",
        "SG Behavior": "Competition Act s.34 — resale price maintenance per se violation",
        "ID Requirement": "UU No. 5/1999 (Anti-Monopoly Law) — resale price maintenance prohibited; KPPU enforcement; non-exclusive context increases cartel risk with multiple distributors",
        "Template Clause": "Prinsipal dapat memberikan harga jual kembali yang disarankan (harga rekomendasi) namun Distributor bebas menentukan harga jual kembalinya sendiri. Tidak ada ketentuan dalam Perjanjian ini yang merupakan penetapan harga atau pengaturan harga jual kembali yang melanggar UU No. 5 Tahun 1999. / The Principal may provide recommended resale prices but the Distributor is free to determine its own resale prices. Nothing in this Agreement constitutes price fixing or resale price maintenance in violation of Law No. 5/1999.",
        "Statutory Reference": "UU No. 5/1999 Art.5 (price fixing); Art.8 (vertical price fixing); Art.15 (exclusive dealing); KPPU",
        "Statutory Detail": "Resale price maintenance is prohibited — identical to DA-ID-008. HEIGHTENED RISK in non-exclusive context: a Principal sending the same recommended price list to multiple non-exclusive distributors could constitute a hub-and-spoke price-fixing arrangement under UU No. 5/1999 Art.5 (horizontal price fixing via vertical coordination). KPPU has pursued hub-and-spoke cases. Recommended prices must be genuinely non-binding across all distributors — any evidence of coordination between distributors on pricing creates cartel risk.",
        "Risk Level": "High",
        "Notes": "Auto-apply. Hub-and-spoke cartel risk is specific to non-exclusive arrangements with multiple distributors — higher risk than exclusive. KPPU fines up to IDR 25 billion. Ensure recommended price lists are clearly marked non-binding across all distributor communications.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-010",
        "Label": "Payment terms, currency, and withholding tax",
        "SG Behavior": "USD or SGD; no withholding tax issues from SG side",
        "ID Requirement": "USD preferred; PPh 26 on cross-border payments (reduced by DTA); LLD reporting >USD 10,000",
        "Template Clause": "Semua pembayaran dilakukan dalam [MATA UANG: USD / SGD] melalui transfer kawat dalam [JANGKA WAKTU: tentukan — misalnya 30 hari sejak tanggal invoice]. Distributor memotong PPh Pasal 26 sebesar [TARIF DTA: tentukan] atas pembayaran kepada Prinsipal dan menyediakan Bukti Potong PPh 26 dalam 30 hari setelah pemotongan. Prinsipal menyediakan IRAS Certificate of Residence tahunan untuk mengakses tarif DTA. / All payments in [CURRENCY: USD / SGD] by telegraphic transfer within [PERIOD: specify]. Distributor withholds PPh Pasal 26 at [DTA RATE] on payments to Principal and provides Bukti Potong PPh 26 within 30 days. Principal provides annual IRAS Certificate of Residence to access DTA reduced rates.",
        "Statutory Reference": "UU PPh No. 36/2008 Pasal 26; P3B Indonesia-Singapura (DTA); PBI No. 14/17/PBI/2012 (LLD reporting); DGT PER-25/PJ/2018",
        "Statutory Detail": "Identical to DA-ID-009. PPh 26 standard rate 20%, reduced to ~10% under DTA with IRAS COR. Without IRAS COR, full 20% applies — cannot be recovered. LLD reporting obligation for Indonesian party on transactions >USD 10,000. USD strongly recommended for SG→ID distribution agreements.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "PARAMETERIZED — currency and payment terms require user input. Tax adviser review for DTA rate applicable to specific payment type (product purchase vs royalty vs management fee).",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-011",
        "Label": "IP licence — trade marks and brand",
        "SG Behavior": "Limited revocable licence; goodwill to Principal; anti-registration clause; IPOS registration",
        "ID Requirement": "DJKI trade mark registration critical — Indonesia is first-to-file; anti-squatting clause essential; non-exclusive licence aligns with appointment",
        "Template Clause": "Prinsipal memberikan kepada Distributor lisensi terbatas, non-eksklusif, tidak dapat dialihkan, dan dapat dicabut untuk menggunakan HKI Prinsipal semata-mata untuk pemasaran dan distribusi Produk di Wilayah selama Jangka Waktu Perjanjian. Seluruh goodwill yang dihasilkan dari penggunaan merek dagang Prinsipal oleh Distributor menjadi milik eksklusif Prinsipal. Distributor tidak boleh mendaftarkan merek dagang yang identik atau membingungkan dengan merek dagang Prinsipal di yurisdiksi mana pun. / The Principal grants the Distributor a limited, non-exclusive, non-transferable, revocable licence to use the Principal's IP solely for marketing and distributing the Products in the Territory. All goodwill from Distributor's use of Principal's trade marks accrues exclusively to the Principal. Distributor shall not register any trade mark identical or confusingly similar to Principal's marks in any jurisdiction.",
        "Statutory Reference": "UU No. 20/2016 tentang Merek dan Indikasi Geografis; DJKI; UU No. 28/2014 (Copyright — moral rights)",
        "Statutory Detail": "Identical to DA-ID-010. Trade mark squatting risk exists equally in non-exclusive arrangements. In non-exclusive arrangements with multiple distributors, the anti-registration clause is even more important — multiple Indonesian distributor entities each have the opportunity to register the Principal's marks at DJKI. DJKI registration of Principal's marks before appointing ANY distributor is strongly recommended.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "DJKI trade mark registration before appointment is strongly recommended. In multi-distributor non-exclusive network, each distributor must be contractually bound by anti-registration clause.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-012",
        "Label": "Term and renewal — shorter for non-exclusive",
        "SG Behavior": "Fixed initial term; auto-renewal with notice; shorter term appropriate for non-exclusive",
        "ID Requirement": "Fixed term; unilateral exit right; shorter initial term appropriate for non-exclusive; KUHPerdata indefinite agreements can be terminated on reasonable notice",
        "Template Clause": "Perjanjian ini berlaku mulai Tanggal Mulai dan berlanjut selama jangka waktu awal [JANGKA WAKTU AWAL: tentukan — disarankan 1 tahun untuk non-eksklusif] ('Jangka Waktu Awal'), kecuali diakhiri lebih awal. Setelah Jangka Waktu Awal, Perjanjian ini diperpanjang secara otomatis untuk periode [PERPANJANGAN: tentukan — disarankan 1 tahun] kecuali salah satu Pihak memberikan pemberitahuan tertulis tidak kurang dari [PEMBERITAHUAN NON-PERPANJANGAN: tentukan — disarankan 30 hari] sebelum berakhirnya periode yang sedang berjalan. / This Agreement commences on the Start Date and continues for an initial term of [INITIAL TERM: specify — recommend 1 year for non-exclusive] unless earlier terminated. After the Initial Term, it renews automatically for [RENEWAL: specify — recommend 1 year] periods unless either Party gives not less than [NON-RENEWAL NOTICE: specify — recommend 30 days] written notice before expiry of the then-current term.",
        "Statutory Reference": "KUHPerdata Art.1338 (freedom of contract); Art.1266 (termination); common practice",
        "Statutory Detail": "KEY DIFFERENCE from exclusive DA. 1-year initial term is appropriate for non-exclusive arrangements — lower investment by both parties, shorter commitment. 30-day non-renewal notice is sufficient for non-exclusive (vs 90 days for exclusive). KUHPerdata: indefinite agreements can be terminated on reasonable notice even without express termination right — but fixed term with auto-renewal is cleaner and preferred.",
        "Risk Level": "Low",
        "Notes": "PARAMETERIZED — initial term, renewal period, and notice require user input. 1-year initial term recommended for non-exclusive. Shorter commitment period is a commercial advantage of non-exclusive model.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-013",
        "Label": "Termination — Art.1266 waiver",
        "SG Behavior": "Termination for cause; termination for convenience; no court order required",
        "ID Requirement": "KUHPerdata Art.1266 court order requirement must be expressly waived; verbatim Indonesian text required; shorter notice than exclusive",
        "Template Clause": "Para Pihak dengan ini secara tegas mengesampingkan ketentuan Pasal 1266 dan Pasal 1267 Kitab Undang-Undang Hukum Perdata (KUHPerdata) yang mensyaratkan penetapan pengadilan untuk pengakhiran perjanjian. / The Parties hereby expressly waive the requirements of Articles 1266 and 1267 of the Indonesian Civil Code (KUHPerdata) which require a court order for termination.\n\nEither Party may terminate this Agreement: (a) for material breach (wanprestasi) — 30 days written notice specifying the breach, effective if unremedied; (b) for convenience — [NOTICE PERIOD: specify, recommend 30–60 days for non-exclusive] written notice; (c) immediately — on insolvency, PKPU, or bankruptcy of the other Party under UU No. 37/2004. Upon termination, all outstanding payments for Products delivered become immediately due.",
        "Statutory Reference": "KUHPerdata Art.1266–1267; UU No. 37/2004 (Bankruptcy Law); Permendag No. 22/2016",
        "Statutory Detail": "Art.1266 waiver is equally mandatory in non-exclusive DA as in exclusive — without it, termination requires a court order (1-3 years). KEY DIFFERENCE from exclusive DA: shorter convenience termination notice (30-60 days vs 90-180 days) reflects lower infrastructure investment by non-exclusive distributor. Indonesian distributor protection principles (Permendag No. 22/2016) apply to sole (exclusive) distributors primarily — non-exclusive distributors have less statutory protection on termination, making the shorter notice period more commercially defensible. Good faith (itikad baik) still applies — do not terminate abruptly without reason.",
        "Risk Level": "High",
        "Notes": "CRITICAL — verbatim Art.1266 waiver in Indonesian is non-negotiable. 30-60 days convenience notice is appropriate for non-exclusive; longer periods create unnecessary lock-in without exclusivity benefit. Auto-apply.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-014",
        "Label": "Post-termination — lighter obligations",
        "SG Behavior": "IP return; stock sell-off; shorter transition; no customer list transfer in non-exclusive",
        "ID Requirement": "IP return mandatory; stock resolution; BPOM transfer if applicable; no customer list transfer obligation in non-exclusive context",
        "Template Clause": "Pada saat pengakhiran Perjanjian ini: (a) Distributor segera menghentikan penggunaan HKI Prinsipal dan mengembalikan atau memusnahkan semua materi merek; (b) atas pilihan Prinsipal, Distributor menjual sisa stok dalam [PERIODE JUAL: tentukan — disarankan 60 hari] atau mengembalikan stok yang masih layak jual dengan biaya Prinsipal; (c) jika berlaku, Distributor membantu pengalihan registrasi BPOM kepada distributor baru yang ditunjuk Prinsipal; (d) masing-masing Pihak segera mengembalikan atau memusnahkan Informasi Rahasia pihak lain. / On termination: (a) Distributor immediately ceases use of Principal IP and returns or destroys all brand materials; (b) at Principal's election, Distributor sells remaining stock within [SELL-OFF: specify — recommend 60 days] or returns saleable stock at Principal's cost; (c) if applicable, Distributor assists transfer of BPOM registration to Principal's new distributor; (d) each Party promptly returns or destroys the other's Confidential Information.",
        "Statutory Reference": "Peraturan BPOM (registration transfer); Permendag No. 22/2016; KUHPerdata Art.1338",
        "Statutory Detail": "KEY DIFFERENCES from exclusive DA: (1) no customer list transfer — in non-exclusive context, customers may have relationships with multiple distributors; the customer list is less uniquely attributable to one distributor and harder to enforce; (2) no transition cooperation obligation beyond BPOM assistance — lower investment by non-exclusive distributor justifies lighter exit obligations; (3) 60-day sell-off (vs 90 days for exclusive) consistent with shorter overall commitment; BPOM transfer assistance included where relevant to product category.",
        "Risk Level": "Medium",
        "Notes": "PARAMETERIZED — sell-off period requires user input. No customer list transfer in non-exclusive. BPOM transfer assistance only where Products require BPOM registration — flag in form.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-015",
        "Label": "Non-compete — narrow scope, short duration",
        "SG Behavior": "Customer non-solicitation only; 6 months max; weaker without exclusivity consideration",
        "ID Requirement": "KUHPerdata freedom of contract; UU No. 5/1999 Art.15 (exclusive dealing); narrow non-compete or customer non-solicitation only; lawyer review mandatory",
        "Template Clause": "[OPSIONAL — HANYA JIKA DISTRIBUTOR MEMILIKI AKSES KE INFORMASI RAHASIA ATAU HARGA]: Selama Jangka Waktu Perjanjian dan selama [PERIODE: tentukan — disarankan maksimal 6 bulan] setelah pengakhiran, Distributor tidak akan secara langsung mendekati pelanggan Prinsipal yang telah diidentifikasi sebagai pelanggan aktif selama 12 bulan sebelum pengakhiran, untuk membeli produk yang bersaing dengan Produk. [JIKA TIDAK ADA AKSES INFORMASI RAHASIA: hapus klausul ini — tidak dapat dilaksanakan tanpa pertimbangan eksklusivitas.] / [OPTIONAL — ONLY WHERE DISTRIBUTOR HAS ACCESS TO CONFIDENTIAL INFORMATION OR PRICING]: During the Term and for [PERIOD: specify — recommend max 6 months] following termination, Distributor shall not directly solicit Principal's customers with whom Distributor had material contact in the preceding 12 months to purchase competing products. [IF NO CONFIDENTIAL INFORMATION ACCESS: omit this clause entirely.]",
        "Statutory Reference": "KUHPerdata Art.1338; Art.1337 (lawful cause); UU No. 5/1999 Art.15 (exclusive dealing)",
        "Statutory Detail": "KEY DIFFERENCE from exclusive DA. Without exclusivity as consideration, a broad non-compete is very difficult to enforce under KUHPerdata — courts require legitimate consideration. Customer non-solicitation (narrower than full non-compete) is more defensible where the distributor had genuine access to Principal's confidential customer information. UU No. 5/1999 Art.15 risk: a non-compete preventing the distributor from carrying any competing product for an extended period could be challenged as exclusive dealing restricting competition. 6 months maximum. KPPU has pursued exclusive dealing cases in Indonesian distribution.",
        "Risk Level": "Medium",
        "Requires Human Review": "checked",
        "Notes": "PARAMETERIZED — optional, only where distributor has confidential information access. Lawyer review mandatory before including any restraint. 6 months is the defensible maximum without exclusivity consideration.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-016",
        "Label": "Confidentiality",
        "SG Behavior": "3-year post-termination; trade secrets indefinite; standard carve-outs",
        "ID Requirement": "UU Rahasia Dagang No. 30/2000; KUHPerdata; 3-year standard; bilateral obligation",
        "Template Clause": "Masing-masing Pihak wajib menjaga kerahasiaan Informasi Rahasia yang diterima dari Pihak lain dan tidak mengungkapkannya tanpa persetujuan tertulis sebelumnya, kecuali: kepada karyawan atau penasihat profesional yang terikat kewajiban kerahasiaan setara; atau sesuai kewajiban hukum. Kewajiban ini berlaku selama 3 tahun setelah pengakhiran untuk Informasi Rahasia umum dan tanpa batas waktu untuk rahasia dagang (UU No. 30/2000). / Each Party shall keep confidential all Confidential Information and not disclose it without prior written consent, except to bound employees/advisers or as required by law. Survives termination for 3 years (general) and indefinitely (trade secrets under UU No. 30/2000).",
        "Statutory Reference": "UU No. 30/2000 tentang Rahasia Dagang; KUHPerdata Art.1338; UU ITE No. 11/2008",
        "Statutory Detail": "Identical to DA-ID-015. Trade Secrets Law (UU No. 30/2000) provides civil and criminal remedies — up to 2 years imprisonment for misappropriation. In non-exclusive arrangements, confidentiality is particularly important: the distributor may have access to pricing information shared across multiple non-exclusive distributors — breach creates hub-and-spoke pricing risk (see NEDA-ID-009).",
        "Risk Level": "Medium",
        "Notes": "Auto-apply. Bilateral obligation — distributor's customer data and sales intelligence are also confidential from Principal's perspective.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-017",
        "Label": "Data protection — UU PDP",
        "SG Behavior": "PDPA; 3-day breach notification; PDPC",
        "ID Requirement": "UU PDP No. 27/2022; 14-day breach notification; cross-border transfer restrictions; customer data shared with Principal triggers transfer obligations",
        "Template Clause": "Para Pihak sepakat memproses data pribadi sesuai UU No. 27/2022 tentang Pelindungan Data Pribadi (UU PDP). Dalam hal pelanggaran data, Pihak terdampak memberitahu otoritas berwenang dan subjek data dalam 14 hari kalender. Pengalihan data pribadi pelanggan dari Indonesia ke Singapura wajib disertai perlindungan kontraktual yang setara dengan standar UU PDP Pasal 56. / The Parties agree to process personal data per UU No. 27/2022 (UU PDP). Breach notification to competent authority and data subjects within 14 calendar days. Transfer of customer personal data from Indonesia to Singapore requires contractual safeguards equivalent to UU PDP Art.56 standards.",
        "Statutory Reference": "UU No. 27/2022 tentang UU PDP Art.46 (breach notification); Art.56 (cross-border transfer); Kominfo/BSSN",
        "Statutory Detail": "Identical to DA-ID-016. Customer data sharing between Indonesian distributor and SG principal is a cross-border transfer under UU PDP Art.56. In non-exclusive arrangements with multiple distributors, each distributor-to-principal data flow is a separate cross-border transfer — each requires compliant contractual safeguards. UU PDP implementing regulations still being finalised — monitor Kominfo.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "Lawyer review: customer data flows in multi-distributor non-exclusive network create multiple parallel cross-border transfer obligations under UU PDP Art.56. Each must be separately documented.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-018",
        "Label": "Limitation of liability",
        "SG Behavior": "Mutual cap; consequential loss exclusion; UCTA reasonableness",
        "ID Requirement": "KUHPerdata Art.1247–1248 foreseeable loss; good faith limits extreme exclusions; no UCTA equivalent; mutual cap at 12-month fees defensible",
        "Template Clause": "Tunduk pada tanggung jawab yang tidak dapat dikecualikan, total tanggung jawab masing-masing Pihak berdasarkan Perjanjian ini tidak melebihi [BATAS: tentukan — misalnya total pembayaran dalam 12 bulan sebelum klaim / nilai USD tertentu]. Tidak ada Pihak yang bertanggung jawab atas kerugian tidak langsung, konsekuensial, atau kehilangan keuntungan. / Subject to non-excludable liability, each Party's total liability shall not exceed [CAP: specify — e.g. total payments in the 12 months preceding the claim / fixed USD amount]. Neither Party shall be liable for indirect, consequential, or loss of profit damages.",
        "Statutory Reference": "KUHPerdata Art.1247 (foreseeable loss); Art.1248; Art.1365 (perbuatan melawan hukum)",
        "Statutory Detail": "Identical to DA-ID-017. Liability caps enforceable under KUHPerdata freedom of contract subject to good faith. In non-exclusive context, potential liability claims are generally lower than exclusive (no lost territory claims) but lost profit claims from terminated distributors remain a risk.",
        "Risk Level": "High",
        "Requires Human Review": "checked",
        "Notes": "PARAMETERIZED — cap amount requires user input. 12-month fees is defensible benchmark. Lawyer review for quantum relative to agreement value.",
        "Automation Type": "PARAMETERIZED",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-019",
        "Label": "Anti-corruption — UU Tipikor and KPK",
        "SG Behavior": "POCA compliance; FCPA/UKBA where applicable",
        "ID Requirement": "UU Tipikor; KPK enforcement; Gratifikasi prohibition; particularly relevant where distributor sells to government or SOE buyers",
        "Template Clause": "Para Pihak sepakat mematuhi UU No. 31/1999 jo. UU No. 20/2001 (UU Tipikor) dan larangan Gratifikasi berdasarkan Pasal 12B UU Tipikor. Distributor tidak boleh menawarkan, menjanjikan, atau memberikan sesuatu yang bernilai kepada Penyelenggara Negara untuk mendapatkan bisnis atau keuntungan tidak wajar. Prinsipal dapat mengakhiri Perjanjian ini segera jika Distributor melanggar klausul ini secara material. / The Parties agree to comply with UU Tipikor (Law No. 31/1999 as amended) and the Gratifikasi prohibition under Art.12B. Distributor shall not offer, promise, or give anything of value to any Indonesian government official (Penyelenggara Negara) to obtain business or improper advantage. Principal may terminate immediately on material breach of this clause.",
        "Statutory Reference": "UU No. 31/1999 jo. UU No. 20/2001 (UU Tipikor); UU No. 30/2002 (KPK); Art.12B (Gratifikasi); Singapore POCA (Cap.241)",
        "Statutory Detail": "Identical to DA-ID-018. In non-exclusive distribution, anti-bribery risk is heightened where multiple distributors compete for the same government or SOE buyers — competitive pressure may incentivise Gratifikasi. SG principal is exposed to FCPA/UKBA liability for distributor conduct where principal had knowledge or failed to implement adequate controls.",
        "Risk Level": "High",
        "Notes": "Auto-apply. Particularly important where distributors sell to government procurement (LKPP), BUMN, hospitals, schools, or other government-affiliated buyers.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
      },
      {
        "Concept ID": "NEDA-ID-020",
        "Label": "Force majeure, entire agreement, and boilerplate",
        "SG Behavior": "SG common law force majeure; entire agreement; written variation; third-party rights exclusion",
        "ID Requirement": "KUHPerdata overmacht; natural disasters operationally significant; itikad baik acknowledgment; entire agreement limited effect in civil law",
        "Template Clause": "Force Majeure: Tidak ada Pihak yang bertanggung jawab atas kegagalan pelaksanaan yang disebabkan keadaan kahar (force majeure/overmacht) termasuk bencana alam, gempa bumi, letusan gunung berapi, banjir, perang, pandemi yang dinyatakan oleh pemerintah Indonesia (BNPB), atau tindakan pemerintah yang secara langsung mencegah pelaksanaan. Jika keadaan kahar berlanjut lebih dari [LONGSTOP: tentukan — disarankan 60 hari], salah satu Pihak dapat mengakhiri tanpa kewajiban. / Force Majeure: Neither Party liable for failure caused by force majeure (keadaan kahar) including natural disasters, earthquakes, volcanic eruptions, floods, war, pandemic declared by Indonesian government (BNPB), or government actions directly preventing performance. 60-day longstop then either Party may terminate.\n\nEntire Agreement: Perjanjian ini merupakan keseluruhan kesepakatan Para Pihak. Tidak ada perubahan yang mengikat kecuali tertulis dan ditandatangani. Para Pihak mengakui kewajiban itikad baik berdasarkan KUHPerdata Pasal 1338. / This Agreement is the entire agreement. No amendment binding unless in writing and signed. Parties acknowledge the good faith (itikad baik) obligation under KUHPerdata Art.1338 which cannot be excluded.",
        "Statutory Reference": "KUHPerdata Art.1244–1245 (overmacht); Art.1338 (itikad baik); UU No. 24/2007 (Disaster Management); BNPB",
        "Statutory Detail": "Force majeure: natural disasters have direct operational relevance in Indonesia — Ring of Fire geography, 127 active volcanoes, ~7,000 earthquakes annually. 60-day longstop for distribution (same as exclusive). Entire agreement: KUHPerdata Art.1338 good faith obligation cannot be waived — acknowledgment sets correct expectations for both parties. Indonesian courts have more interpretive latitude than SG courts — itikad baik acknowledgment reduces the risk of either party being surprised by judicial application.",
        "Risk Level": "Medium",
        "Notes": "Auto-apply. Combined clause for efficiency — force majeure, entire agreement, and itikad baik acknowledgment. PARAMETERIZED for longstop period only.",
        "Automation Type": "FULL_AUTO",
        "Document Type": "Non-Exclusive Distribution Agreement (SG→ID)"
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
        r = requests.post(url, headers=HEADERS, json={"records": [{"fields": rec} for rec in batch]})
        if r.status_code in (200, 201):
            total += len(batch)
            print(f"  Batch {i//10+1}: {len(batch)} records OK")
        else:
            print(f"  Batch {i//10+1} FAILED: {r.status_code} — {r.text[:200]}")
        time.sleep(0.3)
    return total

print("Uploading SG-ID JV + Non-Exclusive Distribution records...\n")
grand_total = 0
for table_name, data in ALL_DATA.items():
    print(f"Table: {table_name} — {len(data['records'])} records")
    total = upload_table(table_name, data["records"])
    grand_total += total
    print(f"  ✅ {total} uploaded\n")
print(f"TOTAL: {grand_total} records uploaded")
