"""
docx_builder.py — Qarta Legal document formatter.

Produces three lawyer-ready Word documents per adaptation job:
  - clean.docx      : final adapted contract with deal profile + execution block
  - redline.docx    : change-tracked diff view
  - commentary.docx : clause-by-clause legal analysis

Typography spec:
  Body      — Georgia 10pt, #1A1A2E
  UI labels — Arial 8–9pt, #4B4B6B
  Metadata  — Courier New 8pt
  Headings  — Arial Bold, amethyst (#7C3AED) clause numbers
"""

import re
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

# ── Document type display labels ───────────────────────────────────────────────
DOC_TYPE_LABELS = {
    "nda":                                   "Non-Disclosure Agreement",
    "non_disclosure_agreement":              "Non-Disclosure Agreement",
    "jv_agreement":                          "Joint Venture Agreement",
    "joint_venture":                         "Joint Venture Agreement",
    "jv":                                    "Joint Venture Agreement",
    "mou":                                   "Memorandum of Understanding",
    "memorandum_of_understanding":           "Memorandum of Understanding",
    "service_agreement":                     "Service Agreement",
    "employment_contract":                   "Employment Contract",
    "employment":                            "Employment Contract",
    "exclusive_distribution":                "Exclusive Distribution Agreement",
    "exclusive_distribution_agreement":      "Exclusive Distribution Agreement",
    "non_exclusive_distribution":            "Non-Exclusive Distribution Agreement",
    "non_exclusive_distribution_agreement":  "Non-Exclusive Distribution Agreement",
    "sha":                                   "Shareholders Agreement",
    "shareholders_agreement":                "Shareholders Agreement",
    "ip_licence":                            "IP Licence Agreement",
    "ip_license":                            "IP Licence Agreement",
    "franchise":                             "Franchise Agreement",
    "franchise_agreement":                   "Franchise Agreement",
    "pdpa":                                  "PDPA Data Protection Agreement",
}

CORRIDOR_LABELS = {
    "CN_SG": "China → Singapore",
    "SG_ID": "Singapore → Indonesia",
    "CN_ID": "China → Indonesia",
    "SG_MY": "Singapore → Malaysia",
    "CN_MY": "China → Malaysia",
}

CORRIDOR_GOV_LAW = {
    "CN_SG": "Singapore Law",
    "SG_ID": "Indonesian Law",
    "CN_ID": "Indonesian Law",
    "SG_MY": "Malaysian Law",
    "CN_MY": "Malaysian Law",
}

# ── Colour palette ─────────────────────────────────────────────────────────────
AMETHYST   = RGBColor(0x7C, 0x3A, 0xED)   # #7C3AED
BODY_CLR   = RGBColor(0x1A, 0x1A, 0x2E)   # #1A1A2E
SECONDARY  = RGBColor(0x4B, 0x4B, 0x6B)   # #4B4B6B
ACTION_CLR = RGBColor(0xF5, 0x9E, 0x0B)   # #F59E0B amber
LAWYER_CLR = RGBColor(0x93, 0x33, 0xEA)   # #9333EA purple
NOTE_CLR   = RGBColor(0x26, 0x63, 0xEB)   # #2663EB blue
RED        = RGBColor(0xC0, 0x00, 0x00)
GREEN      = RGBColor(0x00, 0x7A, 0x3D)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)

# Hex strings for XML (no #)
AMETHYST_HEX   = "7C3AED"
ACTION_BG_HEX  = "FFF3E0"
ACTION_BDR_HEX = "F59E0B"
LAWYER_BG_HEX  = "FDF2F8"
LAWYER_BDR_HEX = "9333EA"
NOTE_BG_HEX    = "EFF6FF"
NOTE_BDR_HEX   = "2663EB"
COVER_BG_HEX   = "F5F3FF"   # near-white amethyst tint for cover block
TABLE_HDR_HEX  = "EDE9FE"   # light purple for table header rows
DIVIDER_HEX    = "DDD6FE"   # muted amethyst for divider lines

# ── Typography ─────────────────────────────────────────────────────────────────
FONT_BODY  = "Georgia"
FONT_UI    = "Arial"
FONT_MONO  = "Courier New"
SZ_BODY    = Pt(10)
SZ_SMALL   = Pt(8)
SZ_LABEL   = Pt(9)
SZ_TITLE   = Pt(14)
SZ_H1      = Pt(11)
SZ_H2      = Pt(10)

# ── Regex ──────────────────────────────────────────────────────────────────────
RE_PLACEHOLDER   = re.compile(r'(\[[A-Z][A-Z0-9 _]+:[^\]]{1,120}\])')
RE_TOP_CLAUSE    = re.compile(r'^(\d+)\.\s{1,4}([A-Z].*)$')
RE_SUB_CLAUSE    = re.compile(r'^(\d+\.\d+)\s{1,4}(\S.*)$')
RE_SUB_SUB       = re.compile(r'^(\d+\.\d+\.\d+)\s{1,4}(\S.*)$')
RE_SEPARATOR     = re.compile(r'^[━─=\-]{5,}$')
RE_CLAUSE_HEADER = re.compile(r'^\[CLAUSE\s+[\d.]+', re.IGNORECASE)
RE_PDPA_ITEM     = re.compile(r'^[✅⚠️☑]')
RE_ACTION_FLAG   = re.compile(r'^\s*[⚠*]\s*ACTION REQUIRED', re.IGNORECASE)
RE_LAWYER_FLAG   = re.compile(r'^\s*[⚠*┌│]\s*LAWYER REVIEW', re.IGNORECASE)
RE_NOTE_FLAG     = re.compile(r'^\s*[ℹ*]\s*NOTE[:\s]', re.IGNORECASE)
RE_BOX_START     = re.compile(r'^[┌╔]')
RE_BOX_END       = re.compile(r'^[└╚]')
RE_BOX_MID       = re.compile(r'^[│║]')

FIELD_LABELS = ('Original:', 'Change:', 'Reason:', 'Action required:')


# ══════════════════════════════════════════════════════════════════════════════
# Low-level XML / formatting helpers
# ══════════════════════════════════════════════════════════════════════════════

def _fmt(run, font=FONT_BODY, bold=False, italic=False, strike=False,
         color=None, size=None):
    run.font.name   = font
    run.font.bold   = bold
    run.font.italic = italic
    run.font.strike = strike
    run.font.size   = size or SZ_BODY
    run.font.color.rgb = color or BODY_CLR


def _para_spacing(para, before=0, after=80):
    sp = OxmlElement('w:spacing')
    sp.set(qn('w:before'), str(before))
    sp.set(qn('w:after'),  str(after))
    para._p.get_or_add_pPr().append(sp)


def _set_para_indent(para, left_twips=0):
    ind = OxmlElement('w:ind')
    ind.set(qn('w:left'), str(left_twips))
    para._p.get_or_add_pPr().append(ind)


def _add_left_border(para, bdr_hex, bg_hex=None, thickness='24'):
    """Left-accent flag box — thick left border only, optional background."""
    pPr = para._p.get_or_add_pPr()
    bdr = OxmlElement('w:pBdr')
    left = OxmlElement('w:left')
    left.set(qn('w:val'),   'single')
    left.set(qn('w:sz'),    thickness)
    left.set(qn('w:space'), '8')
    left.set(qn('w:color'), bdr_hex)
    bdr.append(left)
    pPr.append(bdr)
    if bg_hex:
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'),   'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'),  bg_hex)
        pPr.append(shd)


def _add_bottom_border(para, color_hex, thickness='18'):
    """Bottom border only — used as cover-header separator."""
    pPr = para._p.get_or_add_pPr()
    bdr = OxmlElement('w:pBdr')
    bot = OxmlElement('w:bottom')
    bot.set(qn('w:val'),   'single')
    bot.set(qn('w:sz'),    thickness)
    bot.set(qn('w:space'), '4')
    bot.set(qn('w:color'), color_hex)
    bdr.append(bot)
    pPr.append(bdr)


def _add_full_border(para, color_hex, bg_hex=None):
    """Full paragraph border box."""
    pPr = para._p.get_or_add_pPr()
    bdr = OxmlElement('w:pBdr')
    for side in ('top', 'left', 'bottom', 'right'):
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'),   'single')
        el.set(qn('w:sz'),    '6')
        el.set(qn('w:space'), '4')
        el.set(qn('w:color'), color_hex)
        bdr.append(el)
    pPr.append(bdr)
    if bg_hex:
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'),   'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'),  bg_hex)
        pPr.append(shd)


def _set_cell_bg(cell, fill_hex):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  fill_hex)
    tcPr.append(shd)


def _run_badge(para, text, bg_hex=AMETHYST_HEX, fg=WHITE):
    """Inline badge — colored background on run (e.g. 'AI-ASSISTED DRAFT')."""
    run = para.add_run(f"  {text}  ")
    run.font.name  = FONT_UI
    run.font.size  = SZ_SMALL
    run.font.bold  = True
    run.font.color.rgb = fg
    rPr = run._r.get_or_add_rPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  bg_hex)
    rPr.append(shd)
    return run


def _add_page_number(para):
    """Append a PAGE field into an existing paragraph."""
    run = para.add_run()
    for tag, val in [('begin', None), ('instrText', ' PAGE '), ('end', None)]:
        if tag == 'instrText':
            el = OxmlElement('w:instrText')
            el.set(qn('xml:space'), 'preserve')
            el.text = val
        else:
            el = OxmlElement('w:fldChar')
            el.set(qn('w:fldCharType'), tag)
        run._r.append(el)


def _horizontal_rule(doc, color_hex=DIVIDER_HEX):
    """Add a thin full-width horizontal rule paragraph."""
    p = doc.add_paragraph()
    _para_spacing(p, before=60, after=60)
    pPr = p._p.get_or_add_pPr()
    bdr = OxmlElement('w:pBdr')
    bot = OxmlElement('w:bottom')
    bot.set(qn('w:val'),   'single')
    bot.set(qn('w:sz'),    '4')
    bot.set(qn('w:space'), '1')
    bot.set(qn('w:color'), color_hex)
    bdr.append(bot)
    pPr.append(bdr)
    return p


# ══════════════════════════════════════════════════════════════════════════════
# Page header / footer
# ══════════════════════════════════════════════════════════════════════════════

def _setup_header_footer(section, doc_type_label: str, corridor_label: str):
    """
    Page header: 'QARTA LEGAL · {doc_type} · {corridor}'  (left)
                 'CONFIDENTIAL — FOR LAWYER REVIEW'         (right, bold red)
    Page footer: disclaimer italic (left) | page number (right)
    """
    # ── Header ────────────────────────────────────────────────────────────────
    header = section.header
    hp = header.paragraphs[0]
    hp.clear()

    # Tab stop at right edge of text area (6" = 8640 twips)
    pPr = hp._p.get_or_add_pPr()
    tabs_el = OxmlElement('w:tabs')
    tab_r = OxmlElement('w:tab')
    tab_r.set(qn('w:val'), 'right')
    tab_r.set(qn('w:pos'), '8640')
    tabs_el.append(tab_r)
    pPr.append(tabs_el)

    left_run = hp.add_run(f"QARTA LEGAL  ·  {doc_type_label}  ·  {corridor_label}")
    left_run.font.name  = FONT_UI
    left_run.font.size  = SZ_SMALL
    left_run.font.color.rgb = SECONDARY

    tab_run = hp.add_run('\t')

    right_run = hp.add_run("CONFIDENTIAL — FOR LAWYER REVIEW")
    right_run.font.name  = FONT_UI
    right_run.font.size  = SZ_SMALL
    right_run.font.bold  = True
    right_run.font.color.rgb = RED

    # ── Footer ────────────────────────────────────────────────────────────────
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.clear()

    pPr2 = fp._p.get_or_add_pPr()
    tabs_el2 = OxmlElement('w:tabs')
    tab_r2 = OxmlElement('w:tab')
    tab_r2.set(qn('w:val'), 'right')
    tab_r2.set(qn('w:pos'), '8640')
    tabs_el2.append(tab_r2)
    pPr2.append(tabs_el2)

    disc_run = fp.add_run(
        "AI-assisted adaptation. Not legal advice. Requires attorney review before execution."
    )
    disc_run.font.name   = FONT_UI
    disc_run.font.size   = SZ_SMALL
    disc_run.font.italic = True
    disc_run.font.color.rgb = SECONDARY

    fp.add_run('\t')
    _add_page_number(fp)


# ══════════════════════════════════════════════════════════════════════════════
# Cover block + deal profile table
# ══════════════════════════════════════════════════════════════════════════════

def _add_cover_block(doc, doc_type_label: str, corridor_label: str,
                     variant: str, date_str: str):
    """
    Cover header block at the top of the document body:
      Line 1: document title (bold, large)
      Line 2: corridor tag · variant label  +  AI-ASSISTED DRAFT badge
      Line 3: date — separated from body by amethyst bottom border
    """
    # Title paragraph
    p_title = doc.add_paragraph()
    _para_spacing(p_title, before=0, after=40)
    pPr = p_title._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  COVER_BG_HEX)
    pPr.append(shd)

    r_title = p_title.add_run(doc_type_label.upper())
    r_title.font.name  = FONT_UI
    r_title.font.size  = SZ_TITLE
    r_title.font.bold  = True
    r_title.font.color.rgb = AMETHYST

    # Subtitle: corridor + variant + badge
    p_sub = doc.add_paragraph()
    _para_spacing(p_sub, before=0, after=40)
    pPr2 = p_sub._p.get_or_add_pPr()
    shd2 = OxmlElement('w:shd')
    shd2.set(qn('w:val'),   'clear')
    shd2.set(qn('w:color'), 'auto')
    shd2.set(qn('w:fill'),  COVER_BG_HEX)
    pPr2.append(shd2)

    r_corr = p_sub.add_run(f"{corridor_label}  ·  {variant}")
    r_corr.font.name  = FONT_UI
    r_corr.font.size  = SZ_LABEL
    r_corr.font.color.rgb = SECONDARY

    _run_badge(p_sub, "AI-ASSISTED DRAFT")

    # Date line — with amethyst bottom border as separator
    p_date = doc.add_paragraph()
    _para_spacing(p_date, before=40, after=160)
    pPr3 = p_date._p.get_or_add_pPr()
    shd3 = OxmlElement('w:shd')
    shd3.set(qn('w:val'),   'clear')
    shd3.set(qn('w:color'), 'auto')
    shd3.set(qn('w:fill'),  COVER_BG_HEX)
    pPr3.append(shd3)
    _add_bottom_border(p_date, AMETHYST_HEX, thickness='12')

    r_date = p_date.add_run(f"Prepared: {date_str}")
    r_date.font.name  = FONT_MONO
    r_date.font.size  = SZ_SMALL
    r_date.font.color.rgb = SECONDARY


def _add_deal_profile_table(doc, corridor: str, doc_type: str,
                             company_name: str, date_str: str):
    """
    Two-column deal profile table:
      Field            Value
      ─────────────────────────────────
      Corridor         China → Singapore
      Document type    Non-Disclosure Agreement
      Party / Entity   [company_name]
      Governing law    Singapore Law
      Adaptation date  21 May 2026
    """
    rows_data = [
        ("Corridor",         CORRIDOR_LABELS.get(corridor.upper(), corridor)),
        ("Document type",    DOC_TYPE_LABELS.get(doc_type.lower(), doc_type)),
        ("Party / Entity",   company_name or "[PARTY NAME]"),
        ("Governing law",    CORRIDOR_GOV_LAW.get(corridor.upper(), "—")),
        ("Adaptation date",  date_str),
    ]

    tbl = doc.add_table(rows=1, cols=2)
    tbl.style = 'Table Grid'
    tbl.columns[0].width = Inches(1.8)
    tbl.columns[1].width = Inches(4.2)

    # Header row
    hdr_cells = tbl.rows[0].cells
    _set_cell_bg(hdr_cells[0], TABLE_HDR_HEX)
    _set_cell_bg(hdr_cells[1], TABLE_HDR_HEX)
    for cell, txt in zip(hdr_cells, ["Field", "Value"]):
        p = cell.paragraphs[0]
        p.clear()
        r = p.add_run(txt)
        r.font.name  = FONT_UI
        r.font.size  = SZ_LABEL
        r.font.bold  = True
        r.font.color.rgb = AMETHYST

    for field, value in rows_data:
        row = tbl.add_row().cells
        p_field = row[0].paragraphs[0]
        p_field.clear()
        rf = p_field.add_run(field)
        rf.font.name  = FONT_UI
        rf.font.size  = SZ_LABEL
        rf.font.bold  = True
        rf.font.color.rgb = SECONDARY

        p_val = row[1].paragraphs[0]
        p_val.clear()
        rv = p_val.add_run(value)
        rv.font.name  = FONT_BODY
        rv.font.size  = SZ_BODY
        rv.font.color.rgb = BODY_CLR

    # Spacing after table
    doc.add_paragraph()


# ══════════════════════════════════════════════════════════════════════════════
# Execution block
# ══════════════════════════════════════════════════════════════════════════════

def _add_execution_block(doc):
    """Two-column signature table at end of clean document."""
    _horizontal_rule(doc)

    p_hdr = doc.add_paragraph()
    _para_spacing(p_hdr, before=120, after=80)
    r = p_hdr.add_run("EXECUTION")
    r.font.name  = FONT_UI
    r.font.size  = SZ_H1
    r.font.bold  = True
    r.font.color.rgb = AMETHYST

    tbl = doc.add_table(rows=1, cols=2)
    tbl.style = 'Table Grid'

    for col_idx, party in enumerate(["PARTY A (Transferor / Employer / Licensor)",
                                      "PARTY B (Transferee / Employee / Licensee)"]):
        cell = tbl.rows[0].cells[col_idx]
        _set_cell_bg(cell, TABLE_HDR_HEX)
        p = cell.paragraphs[0]
        p.clear()
        r_hdr = p.add_run(party)
        r_hdr.font.name  = FONT_UI
        r_hdr.font.size  = SZ_LABEL
        r_hdr.font.bold  = True
        r_hdr.font.color.rgb = AMETHYST

    fields = [
        ("Signature", "_" * 38),
        ("Name",      "_" * 38),
        ("Title",     "_" * 38),
        ("Date",      "_" * 38),
    ]

    for label, blank in fields:
        row = tbl.add_row().cells
        for cell in row:
            p = cell.paragraphs[0]
            p.clear()
            _para_spacing(p, before=120, after=20)
            rl = p.add_run(f"{label}:  ")
            rl.font.name  = FONT_UI
            rl.font.size  = SZ_LABEL
            rl.font.bold  = True
            rl.font.color.rgb = SECONDARY
            rb = p.add_run(blank)
            rb.font.name  = FONT_BODY
            rb.font.size  = SZ_BODY
            rb.font.color.rgb = BODY_CLR


# ══════════════════════════════════════════════════════════════════════════════
# Clause heading helpers
# ══════════════════════════════════════════════════════════════════════════════

def _clause_parts(line: str):
    """
    Return (level, num_str, rest_str) if line is a clause heading, else (0,'','').
    E.g. '1. DEFINITIONS'   → (1, '1.', 'DEFINITIONS')
         '1.1 Scope'        → (2, '1.1', 'Scope')
         '1.1.1 Meaning'    → (3, '1.1.1', 'Meaning')
    """
    m = RE_SUB_SUB.match(line)
    if m:
        return 3, m.group(1), m.group(2)
    m = RE_SUB_CLAUSE.match(line)
    if m:
        return 2, m.group(1), m.group(2)
    m = RE_TOP_CLAUSE.match(line)
    if m:
        return 1, m.group(1) + '.', m.group(2)
    return 0, '', ''


def _add_clause_heading(doc, num_str: str, text_str: str, level: int):
    """
    Render clause heading with amethyst number + body-color text.
    Level 1: bold, larger spacing, followed by thin divider.
    Level 2: semi-bold, indented.
    Level 3: italic, more indented.
    """
    para = doc.add_paragraph()
    indent_map = {1: 0, 2: 360, 3: 720}   # twips
    _para_spacing(para,
                  before=200 if level == 1 else 100 if level == 2 else 60,
                  after=60)
    _set_para_indent(para, indent_map.get(level, 0))

    # Amethyst clause number
    r_num = para.add_run(num_str + "  ")
    r_num.font.name  = FONT_UI
    r_num.font.bold  = True
    r_num.font.size  = SZ_H1 if level == 1 else SZ_H2
    r_num.font.color.rgb = AMETHYST

    # Clause title text
    r_txt = para.add_run(text_str)
    r_txt.font.name   = FONT_UI
    r_txt.font.bold   = (level == 1)
    r_txt.font.italic = (level == 3)
    r_txt.font.size   = SZ_H1 if level == 1 else SZ_H2
    r_txt.font.color.rgb = BODY_CLR

    # Thin divider after top-level clause heading
    if level == 1:
        _horizontal_rule(doc)

    return para


# ══════════════════════════════════════════════════════════════════════════════
# Flag box helpers
# ══════════════════════════════════════════════════════════════════════════════

def _flag_style(flag_type: str):
    """Return (bdr_hex, bg_hex, label_color) for a flag severity."""
    if flag_type == 'action':
        return ACTION_BDR_HEX, ACTION_BG_HEX, ACTION_CLR
    if flag_type == 'lawyer':
        return LAWYER_BDR_HEX, LAWYER_BG_HEX, LAWYER_CLR
    if flag_type == 'note':
        return NOTE_BDR_HEX, NOTE_BG_HEX, NOTE_CLR
    return AMETHYST_HEX, "F5F3FF", AMETHYST


def _detect_flag(line: str):
    """Return 'action', 'lawyer', 'note', or None."""
    if RE_ACTION_FLAG.match(line):
        return 'action'
    if RE_LAWYER_FLAG.match(line):
        return 'lawyer'
    if RE_NOTE_FLAG.match(line):
        return 'note'
    return None


def _add_flag_para(doc, text: str, flag_type: str, is_label: bool = False):
    """Add one paragraph styled as a left-border flag box line."""
    bdr_hex, bg_hex, clr = _flag_style(flag_type)
    p = doc.add_paragraph()
    _para_spacing(p, before=20 if is_label else 0, after=20)
    _set_para_indent(p, 180)
    _add_left_border(p, bdr_hex, bg_hex=bg_hex)
    clean = text.lstrip('┌└│║⚠ℹ* ').strip()
    r = p.add_run(clean)
    r.font.name  = FONT_UI
    r.font.bold  = is_label
    r.font.size  = SZ_LABEL
    r.font.color.rgb = clr
    return p


# ══════════════════════════════════════════════════════════════════════════════
# CLEAN document builder
# ══════════════════════════════════════════════════════════════════════════════

def _para_with_placeholders(doc, line: str):
    """Body paragraph — [PLACEHOLDER: ...] rendered bold amber."""
    para = doc.add_paragraph()
    _para_spacing(para, after=80)
    for part in RE_PLACEHOLDER.split(line):
        if not part:
            continue
        r = para.add_run(part)
        if RE_PLACEHOLDER.fullmatch(part):
            r.font.name  = FONT_MONO
            r.font.size  = SZ_BODY
            r.font.bold  = True
            r.font.color.rgb = ACTION_CLR
        else:
            _fmt(r)
    return para


def _build_clean(text: str, company_name: str, doc_type: str,
                 corridor: str, date_str: str) -> Document:
    doc_type_label = DOC_TYPE_LABELS.get(doc_type.lower(), doc_type.replace('_', ' ').title())
    corridor_label = CORRIDOR_LABELS.get(corridor.upper(), corridor)

    doc = Document()
    sect = doc.sections[0]
    sect.top_margin    = Inches(1.0)
    sect.bottom_margin = Inches(1.0)
    sect.left_margin   = Inches(1.25)
    sect.right_margin  = Inches(1.25)

    _setup_header_footer(sect, doc_type_label, corridor_label)

    # Normal style defaults
    doc.styles['Normal'].font.name = FONT_BODY
    doc.styles['Normal'].font.size = SZ_BODY

    # Cover block + deal profile
    _add_cover_block(doc, doc_type_label, corridor_label, "Clean Version", date_str)
    _add_deal_profile_table(doc, corridor, doc_type, company_name, date_str)

    flag_type = None

    for line in text.splitlines():
        s = line.strip()
        if not s:
            if flag_type:
                flag_type = None   # blank line ends flag block
            continue

        # ── Separators ────────────────────────────────────────────────────────
        if RE_SEPARATOR.match(s):
            continue

        # ── Box-drawing block end ──────────────────────────────────────────────
        if RE_BOX_END.match(s):
            flag_type = None
            continue

        # ── Box-drawing block start / mid — classify on first line ────────────
        if RE_BOX_START.match(s):
            detected = _detect_flag(s) or 'lawyer'
            flag_type = detected
            _add_flag_para(doc, s, flag_type, is_label=True)
            continue

        if RE_BOX_MID.match(s) and flag_type:
            _add_flag_para(doc, s, flag_type, is_label=False)
            continue

        # ── Inline flag lines ──────────────────────────────────────────────────
        detected = _detect_flag(s)
        if detected:
            flag_type = detected
            _add_flag_para(doc, s, flag_type, is_label=True)
            continue

        if flag_type and (s.startswith(' ') or s.startswith('\t') or
                          not RE_TOP_CLAUSE.match(s)):
            _add_flag_para(doc, s, flag_type, is_label=False)
            continue

        # Non-flag line resets flag context
        flag_type = None

        # ── Clause headings ────────────────────────────────────────────────────
        level, num_str, text_str = _clause_parts(s)
        if level:
            _add_clause_heading(doc, num_str, text_str, level)
            continue

        # ── Body paragraph with placeholder colouring ─────────────────────────
        _para_with_placeholders(doc, s)

    # Execution block
    _add_execution_block(doc)

    return doc


# ══════════════════════════════════════════════════════════════════════════════
# REDLINE document builder
# ══════════════════════════════════════════════════════════════════════════════

def _build_redline(text: str, doc_type: str, corridor: str,
                   date_str: str) -> Document:
    doc_type_label = DOC_TYPE_LABELS.get(doc_type.lower(), doc_type.replace('_', ' ').title())
    corridor_label = CORRIDOR_LABELS.get(corridor.upper(), corridor)

    doc = Document()
    sect = doc.sections[0]
    sect.top_margin    = Inches(1.0)
    sect.bottom_margin = Inches(1.0)
    sect.left_margin   = Inches(1.25)
    sect.right_margin  = Inches(1.25)

    _setup_header_footer(sect, doc_type_label, corridor_label)
    doc.styles['Normal'].font.name = FONT_BODY
    doc.styles['Normal'].font.size = SZ_BODY

    _add_cover_block(doc, doc_type_label, corridor_label, "Redline Version", date_str)

    flag_type = None

    for line in text.splitlines():
        s = line.strip()
        if not s:
            flag_type = None
            continue
        if RE_SEPARATOR.match(s):
            continue
        if RE_BOX_END.match(s):
            flag_type = None
            continue

        # ── Inserted / removed markers ─────────────────────────────────────────
        if s.startswith('>> INSERTED:') or s.startswith('INSERTED:'):
            _, _, rest = s.partition(':')
            para = doc.add_paragraph()
            _para_spacing(para, after=80)
            r_lbl = para.add_run("INSERTED: ")
            r_lbl.font.name  = FONT_UI
            r_lbl.font.bold  = True
            r_lbl.font.size  = SZ_LABEL
            r_lbl.font.color.rgb = GREEN
            r_body = para.add_run(rest.strip())
            _fmt(r_body, color=GREEN)
            continue

        if s.startswith('>> REMOVED:') or s.startswith('REMOVED:') or s.startswith('ORIGINAL:'):
            _, _, rest = s.partition(':')
            para = doc.add_paragraph()
            _para_spacing(para, after=80)
            r_lbl = para.add_run("REMOVED: ")
            r_lbl.font.name  = FONT_UI
            r_lbl.font.bold  = True
            r_lbl.font.size  = SZ_LABEL
            r_lbl.font.color.rgb = RED
            r_body = para.add_run(rest.strip())
            _fmt(r_body, color=RED, strike=True)
            continue

        # ── Flag boxes ────────────────────────────────────────────────────────
        if RE_BOX_START.match(s):
            flag_type = _detect_flag(s) or 'lawyer'
            _add_flag_para(doc, s, flag_type, is_label=True)
            continue
        if RE_BOX_MID.match(s) and flag_type:
            _add_flag_para(doc, s, flag_type)
            continue

        detected = _detect_flag(s)
        if detected:
            flag_type = detected
            _add_flag_para(doc, s, flag_type, is_label=True)
            continue
        if flag_type and not RE_TOP_CLAUSE.match(s):
            _add_flag_para(doc, s, flag_type)
            continue
        flag_type = None

        # ── Clause headings ────────────────────────────────────────────────────
        level, num_str, text_str = _clause_parts(s)
        if level:
            _add_clause_heading(doc, num_str, text_str, level)
            continue

        para = doc.add_paragraph()
        _para_spacing(para, after=80)
        _fmt(para.add_run(s))

    return doc


# ══════════════════════════════════════════════════════════════════════════════
# COMMENTARY document builder
# ══════════════════════════════════════════════════════════════════════════════

def _action_color(text: str):
    u = text.upper()
    if 'LAWYER REVIEW' in u:
        return LAWYER_CLR, True
    if 'ACTION REQUIRED' in u or 'USER INPUT' in u:
        return ACTION_CLR, False
    if 'VERIFY' in u:
        return NOTE_CLR, False
    if 'NONE' in u or 'FULL_AUTO' in u:
        return GREEN, False
    return BODY_CLR, False


def _render_pdpa_table(doc, rows: list):
    tbl = doc.add_table(rows=1, cols=2)
    tbl.style = 'Table Grid'
    hdr = tbl.rows[0].cells
    _set_cell_bg(hdr[0], TABLE_HDR_HEX)
    _set_cell_bg(hdr[1], TABLE_HDR_HEX)
    for cell, lbl in zip(hdr, ['PDPA / Data Protection Obligation', 'Status']):
        p = cell.paragraphs[0]
        p.clear()
        r = p.add_run(lbl)
        r.font.name  = FONT_UI
        r.font.size  = SZ_LABEL
        r.font.bold  = True
        r.font.color.rgb = AMETHYST

    for text in rows:
        is_risk = text.startswith('PDPC enforcement risk')
        item, _, status = text.rpartition(' — ') if ' — ' in text else (text, '', '')
        item   = item.lstrip('✅⚠️☑ ').strip()
        status = status.strip()

        u = status.upper()
        clr = (GREEN    if any(x in u for x in ('INSERTED', 'COMPLIANT', 'LOW'))   else
               ACTION_CLR if any(x in u for x in ('PARAMETERIZED', 'MEDIUM'))      else
               LAWYER_CLR if any(x in u for x in ('LAWYER', 'HIGH', 'REVIEW'))     else
               BODY_CLR)

        row = tbl.add_row().cells
        for cell, txt in zip(row, [item, status]):
            p = cell.paragraphs[0]
            p.clear()
            r = p.add_run(txt)
            _fmt(r, bold=is_risk, color=clr)


def _build_commentary(text: str, company_name: str, doc_type: str,
                       corridor: str, date_str: str) -> Document:
    doc_type_label = DOC_TYPE_LABELS.get(doc_type.lower(), doc_type.replace('_', ' ').title())
    corridor_label = CORRIDOR_LABELS.get(corridor.upper(), corridor)

    doc = Document()
    sect = doc.sections[0]
    sect.top_margin    = Inches(1.0)
    sect.bottom_margin = Inches(1.0)
    sect.left_margin   = Inches(1.25)
    sect.right_margin  = Inches(1.25)

    _setup_header_footer(sect, doc_type_label, corridor_label)
    doc.styles['Normal'].font.name = FONT_BODY
    doc.styles['Normal'].font.size = SZ_BODY

    _add_cover_block(doc, doc_type_label, corridor_label, "Commentary & Legal Basis", date_str)
    _add_deal_profile_table(doc, corridor, doc_type, company_name, date_str)

    in_pdpa = False
    pdpa_rows: list = []
    flag_type = None

    for line in text.splitlines():
        s = line.strip()
        if not s:
            flag_type = None
            continue

        # ── PDPA checklist ─────────────────────────────────────────────────────
        if 'PDPA COMPLIANCE CHECKLIST' in s or 'DATA PROTECTION CHECKLIST' in s:
            in_pdpa = True
            p = doc.add_paragraph()
            _para_spacing(p, before=240, after=80)
            _add_full_border(p, AMETHYST_HEX, COVER_BG_HEX)
            r = p.add_run(s)
            r.font.name  = FONT_UI
            r.font.bold  = True
            r.font.size  = SZ_H1
            r.font.color.rgb = AMETHYST
            continue

        if in_pdpa:
            if RE_SEPARATOR.match(s):
                if pdpa_rows:
                    _render_pdpa_table(doc, pdpa_rows)
                    pdpa_rows = []
                in_pdpa = False
                continue
            if RE_PDPA_ITEM.match(s) or s.startswith('PDPC enforcement risk'):
                pdpa_rows.append(s)
            continue

        if RE_SEPARATOR.match(s):
            continue

        # ── Clause entry header ────────────────────────────────────────────────
        if RE_CLAUSE_HEADER.match(s):
            _horizontal_rule(doc)
            p = doc.add_paragraph()
            _para_spacing(p, before=160, after=60)
            _add_left_border(p, AMETHYST_HEX, bg_hex=COVER_BG_HEX, thickness='18')
            r = p.add_run(s)
            r.font.name  = FONT_UI
            r.font.bold  = True
            r.font.size  = SZ_H1
            r.font.color.rgb = AMETHYST
            continue

        # ── Flag boxes ────────────────────────────────────────────────────────
        if RE_BOX_END.match(s):
            flag_type = None
            continue
        if RE_BOX_START.match(s):
            flag_type = _detect_flag(s) or 'lawyer'
            _add_flag_para(doc, s, flag_type, is_label=True)
            continue
        if RE_BOX_MID.match(s) and flag_type:
            _add_flag_para(doc, s, flag_type)
            continue
        detected = _detect_flag(s)
        if detected:
            flag_type = detected
            _add_flag_para(doc, s, flag_type, is_label=True)
            continue
        if flag_type and not RE_CLAUSE_HEADER.match(s):
            _add_flag_para(doc, s, flag_type)
            continue
        flag_type = None

        # ── Four-field structured labels ───────────────────────────────────────
        matched_label = next((lbl for lbl in FIELD_LABELS if s.startswith(lbl)), None)
        if matched_label:
            rest = s[len(matched_label):].strip()
            para = doc.add_paragraph()
            _para_spacing(para, before=0, after=40)
            _set_para_indent(para, 180)
            r_lbl = para.add_run(matched_label + ' ')
            r_lbl.font.name  = FONT_UI
            r_lbl.font.bold  = True
            r_lbl.font.size  = SZ_LABEL
            r_lbl.font.color.rgb = SECONDARY
            if matched_label == 'Action required:':
                clr, bold = _action_color(rest)
                r_val = para.add_run(rest)
                r_val.font.name  = FONT_UI
                r_val.font.bold  = bold
                r_val.font.size  = SZ_LABEL
                r_val.font.color.rgb = clr
            else:
                r_val = para.add_run(rest)
                _fmt(r_val)
            continue

        # ── Recommendations / arrows ───────────────────────────────────────────
        if s.startswith('→') or s.startswith('Recommendation:'):
            para = doc.add_paragraph()
            _para_spacing(para, before=0, after=40)
            _set_para_indent(para, 360)
            r = para.add_run(s)
            _fmt(r, italic=True, color=SECONDARY)
            continue

        # ── Default body paragraph ─────────────────────────────────────────────
        para = doc.add_paragraph()
        _para_spacing(para, after=80)
        _fmt(para.add_run(s))

    if pdpa_rows:
        _render_pdpa_table(doc, pdpa_rows)

    return doc


# ══════════════════════════════════════════════════════════════════════════════
# Public entry point
# ══════════════════════════════════════════════════════════════════════════════

def build_outputs(
    clean_text: str,
    redline_text: str,
    commentary_text: str,
    company_name: str,
    doc_type: str,
    output_dir: str,
    job_id: str = None,
    corridor: str = "CN_SG",
) -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    prefix = f"{job_id}_" if job_id else ""

    # Canonical preparation date (overrides any date Claude produced)
    date_str = datetime.utcnow().strftime("%d %B %Y")
    commentary_text = re.sub(
        r'(?i)Date of adaptation:[^\n]*',
        f'Date of adaptation: {date_str}',
        commentary_text,
    )

    paths = {}

    clean_doc = _build_clean(clean_text, company_name, doc_type, corridor, date_str)
    paths['clean'] = str(out / f"{prefix}clean.docx")
    clean_doc.save(paths['clean'])

    redline_doc = _build_redline(redline_text, doc_type, corridor, date_str)
    paths['redline'] = str(out / f"{prefix}redline.docx")
    redline_doc.save(paths['redline'])

    commentary_doc = _build_commentary(commentary_text, company_name, doc_type, corridor, date_str)
    paths['commentary'] = str(out / f"{prefix}commentary.docx")
    commentary_doc.save(paths['commentary'])

    return paths
