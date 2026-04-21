import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

# ── Colour palette ─────────────────────────────────────────────────────────────
RED      = RGBColor(192, 0, 0)        # placeholders / deleted text
DARK_RED = RGBColor(128, 0, 0)        # lawyer review
GREEN    = RGBColor(0, 128, 0)        # inserted text / action: NONE
AMBER    = RGBColor(204, 102, 0)      # action: USER INPUT
BLUE     = RGBColor(0, 70, 127)       # action: VERIFY
BLUE_HDR = RGBColor(46, 117, 182)     # commentary clause headers

FONT   = "Arial"
BODY   = Pt(11)
SMALL  = Pt(9)

# ── Regex ──────────────────────────────────────────────────────────────────────
RE_PLACEHOLDER   = re.compile(r'(\[[A-Z][A-Z0-9 _]+:[^\]]{1,120}\])')
RE_TOP_CLAUSE    = re.compile(r'^\d+\.\s{1,4}[A-Z]')
RE_SUB_CLAUSE    = re.compile(r'^\d+\.\d+\s{1,4}\S')
RE_SUB_SUB       = re.compile(r'^\d+\.\d+\.\d+\s{1,4}\S')
RE_SEPARATOR     = re.compile(r'^[━─=]{5,}')
RE_CLAUSE_HEADER = re.compile(r'^\[CLAUSE\s+[\d.]+', re.IGNORECASE)
RE_PDPA_ITEM     = re.compile(r'^[✅⚠️☑]')


# ── Low-level XML helpers ──────────────────────────────────────────────────────

def _fmt(run, bold=False, italic=False, strike=False, color=None, size=None):
    run.font.name  = FONT
    run.font.bold  = bold
    run.font.italic = italic
    run.font.strike = strike
    run.font.size  = size or BODY
    if color:
        run.font.color.rgb = color


def _para_spacing(para, before=0, after=80):
    sp = OxmlElement('w:spacing')
    sp.set(qn('w:before'), str(before))
    sp.set(qn('w:after'),  str(after))
    para._p.get_or_add_pPr().append(sp)


def _add_box_border(para, color_hex="800000", bg_hex=None):
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


def _add_page_number(paragraph):
    """Insert a PAGE field into a footer paragraph."""
    run = paragraph.add_run()
    for tag, text in [('begin', None), ('instrText', ' PAGE '), ('end', None)]:
        if tag == 'instrText':
            el = OxmlElement('w:instrText')
            el.set(qn('xml:space'), 'preserve')
            el.text = text
        else:
            el = OxmlElement('w:fldChar')
            el.set(qn('w:fldCharType'), tag)
        run._r.append(el)


def _new_doc(header_text: str) -> Document:
    doc = Document()
    sect = doc.sections[0]
    sect.top_margin    = Inches(1)
    sect.bottom_margin = Inches(1)
    sect.left_margin   = Inches(1.25)
    sect.right_margin  = Inches(1.25)

    # Header
    hp = sect.header.paragraphs[0]
    hp.text = header_text
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _fmt(hp.runs[0], bold=True, size=SMALL, color=DARK_RED)

    # Footer: centred page number
    fp = sect.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _add_page_number(fp)

    # Default Normal style
    normal = doc.styles['Normal']
    normal.font.name = FONT
    normal.font.size = BODY

    return doc


# ── Shared clause heading detection ───────────────────────────────────────────

def _heading_level(line: str):
    """Return 1/2/3 if line looks like a clause heading, else 0."""
    if RE_SUB_SUB.match(line):
        return 3
    if RE_SUB_CLAUSE.match(line):
        return 2
    if RE_TOP_CLAUSE.match(line):
        return 1
    return 0


def _add_clause_heading(doc, text: str, level: int):
    para = doc.add_paragraph()
    _para_spacing(para, before=160 if level == 1 else 80, after=60)
    run = para.add_run(text)
    _fmt(run, bold=True)
    return para


# ── CLEAN.DOCX ─────────────────────────────────────────────────────────────────

def _para_with_placeholders(doc, line: str):
    """Add a paragraph, rendering [PLACEHOLDER: ...] as bold red."""
    para = doc.add_paragraph()
    _para_spacing(para)
    for part in RE_PLACEHOLDER.split(line):
        if not part:
            continue
        run = para.add_run(part)
        if RE_PLACEHOLDER.fullmatch(part):
            _fmt(run, bold=True, color=RED)
        else:
            _fmt(run)
    return para


def _build_clean(text: str, company_name: str, doc_type: str) -> Document:
    doc = _new_doc("QARTA LEGAL — ADAPTED FOR SINGAPORE LAW")

    in_lawyer_block = False
    in_checklist    = False
    checklist_rows  = []
    current_cat     = "USER INPUT"

    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue

        # ── Checklist section ──────────────────────────────────────────────────
        if 'COMPLETION CHECKLIST' in s:
            in_checklist = True
            p = doc.add_paragraph()
            _para_spacing(p, before=240, after=80)
            _add_box_border(p, color_hex="800000")
            run = p.add_run(s)
            _fmt(run, bold=True, color=DARK_RED)
            continue

        if in_checklist:
            if RE_SEPARATOR.match(s):
                continue
            if s.startswith('USER INPUT REQUIRED'):
                current_cat = 'USER INPUT'
            elif s.startswith('EXTERNAL VERIFICATION'):
                current_cat = 'VERIFY'
            elif s.startswith('LAWYER REVIEW REQUIRED'):
                current_cat = 'LAWYER REVIEW'
            elif s.startswith('□'):
                checklist_rows.append((current_cat, s[1:].strip()))
            continue

        # ── Separator lines (ornamental) ───────────────────────────────────────
        if RE_SEPARATOR.match(s):
            continue

        # ── Lawyer review warning block ────────────────────────────────────────
        if s.startswith('┌'):
            in_lawyer_block = True
            continue
        if s.startswith('└'):
            in_lawyer_block = False
            continue

        if in_lawyer_block or ('⚠' in s and 'LAWYER REVIEW' in s.upper()):
            p = doc.add_paragraph()
            _para_spacing(p, before=40, after=40)
            _add_box_border(p, color_hex="800000", bg_hex="FFE0E0")
            run = p.add_run(s.lstrip('│ '))
            is_header = 'LAWYER REVIEW REQUIRED' in s.upper()
            _fmt(run, bold=is_header, color=DARK_RED)
            if not in_lawyer_block:
                in_lawyer_block = True
            continue

        if s.startswith('│'):
            if in_lawyer_block:
                p = doc.add_paragraph()
                _para_spacing(p, before=0, after=40)
                _add_box_border(p, color_hex="800000", bg_hex="FFE0E0")
                run = p.add_run(s.lstrip('│ '))
                _fmt(run, color=DARK_RED)
            continue

        # ── Clause headings ────────────────────────────────────────────────────
        lvl = _heading_level(s)
        if lvl:
            _add_clause_heading(doc, s, lvl)
            continue

        # ── Normal paragraph with placeholder colouring ────────────────────────
        _para_with_placeholders(doc, s)

    # ── Render completion checklist as table ───────────────────────────────────
    if checklist_rows:
        doc.add_paragraph()
        tbl = doc.add_table(rows=1, cols=3)
        tbl.style = 'Table Grid'
        for cell, label in zip(tbl.rows[0].cells, ['Category', 'Action required', 'Clause / Reference']):
            p = cell.paragraphs[0]
            p.clear()
            run = p.add_run(label)
            _fmt(run, bold=True)

        cat_colors = {'USER INPUT': AMBER, 'VERIFY': BLUE, 'LAWYER REVIEW': DARK_RED}

        for cat, item in checklist_rows:
            # Split item into text + clause ref if separated by " — "
            if ' — ' in item:
                item_text, _, clause_ref = item.rpartition(' — ')
            else:
                item_text, clause_ref = item, ''
            row = tbl.add_row().cells
            color = cat_colors.get(cat, GREEN)
            for cell, txt in zip(row, [cat, item_text, clause_ref]):
                p = cell.paragraphs[0]
                p.clear()
                run = p.add_run(txt)
                _fmt(run, color=color, bold=(cat == 'LAWYER REVIEW'))

    return doc


# ── REDLINE.DOCX ───────────────────────────────────────────────────────────────

def _build_redline(text: str) -> Document:
    doc = _new_doc("QARTA LEGAL — REDLINE VERSION")

    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if RE_SEPARATOR.match(s):
            continue

        lvl = _heading_level(s)
        if lvl:
            _add_clause_heading(doc, s, lvl)
            continue

        para = doc.add_paragraph()
        _para_spacing(para)

        if s.startswith('>> INSERTED:'):
            label, _, rest = s.partition(':')
            _fmt(para.add_run(label + ': '), bold=True, color=GREEN)
            _fmt(para.add_run(rest.strip()), color=GREEN)

        elif s.startswith('>> REMOVED:') or s.startswith('ORIGINAL:'):
            label, _, rest = s.partition(':')
            _fmt(para.add_run(label + ': '), bold=True, color=RED, strike=True)
            _fmt(para.add_run(rest.strip()), color=RED, strike=True)

        elif '⚠' in s and 'LAWYER REVIEW' in s.upper():
            _add_box_border(para, color_hex="800000")
            _fmt(para.add_run(s), bold=True, color=DARK_RED)

        else:
            _fmt(para.add_run(s))

    return doc


# ── COMMENTARY.DOCX ────────────────────────────────────────────────────────────

FIELD_LABELS = ('Original:', 'Change:', 'Reason:', 'Action required:')


def _action_color(text: str) -> tuple:
    """Return (color, bold) for the action required value."""
    u = text.upper()
    if 'LAWYER REVIEW' in u:
        return DARK_RED, True
    if 'USER INPUT' in u:
        return AMBER, False
    if 'VERIFY' in u:
        return BLUE, False
    if 'NONE' in u:
        return GREEN, False
    return None, False


def _build_commentary(text: str) -> Document:
    doc = _new_doc("QARTA LEGAL — COMMENTARY AND LEGAL BASIS")

    in_pdpa  = False
    pdpa_rows = []

    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue

        # ── PDPA checklist ─────────────────────────────────────────────────────
        if 'PDPA COMPLIANCE CHECKLIST' in s:
            in_pdpa = True
            p = doc.add_paragraph()
            _para_spacing(p, before=240, after=80)
            _fmt(p.add_run(s), bold=True, color=DARK_RED)
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
            p = doc.add_paragraph()
            _para_spacing(p, before=200, after=60)
            _add_box_border(p, color_hex="2E75B6")
            _fmt(p.add_run(s), bold=True, color=BLUE_HDR)
            continue

        # ── Four-field labels ──────────────────────────────────────────────────
        matched = next((lbl for lbl in FIELD_LABELS if s.startswith(lbl)), None)
        if matched:
            rest = s[len(matched):].strip()
            para = doc.add_paragraph()
            _para_spacing(para, before=0, after=40)
            _fmt(para.add_run(matched + ' '), bold=True)
            if matched == 'Action required:':
                color, bold = _action_color(rest)
                _fmt(para.add_run(rest), bold=bold, color=color)
            else:
                _fmt(para.add_run(rest))
            continue

        # ── Recommendation / sub-lines ─────────────────────────────────────────
        if s.startswith('→') or s.startswith('Recommendation:'):
            para = doc.add_paragraph()
            _para_spacing(para, before=0, after=40)
            _fmt(para.add_run(s), italic=True)
            continue

        # ── Default ────────────────────────────────────────────────────────────
        para = doc.add_paragraph()
        _para_spacing(para)
        _fmt(para.add_run(s))

    if pdpa_rows:
        _render_pdpa_table(doc, pdpa_rows)

    return doc


def _render_pdpa_table(doc: Document, rows: list):
    tbl = doc.add_table(rows=1, cols=2)
    tbl.style = 'Table Grid'
    for cell, label in zip(tbl.rows[0].cells, ['PDPA Obligation', 'Status']):
        p = cell.paragraphs[0]
        p.clear()
        _fmt(p.add_run(label), bold=True)

    for text in rows:
        is_risk = text.startswith('PDPC enforcement risk')
        if ' — ' in text:
            item, _, status = text.rpartition(' — ')
        else:
            item, status = text, ''

        item   = item.lstrip('✅⚠️☑ ').strip()
        status = status.strip()

        u = status.upper()
        color = (GREEN    if any(x in u for x in ('INSERTED', 'COMPLIANT', 'LOW'))  else
                 AMBER    if any(x in u for x in ('PARAMETERIZED', 'MEDIUM'))       else
                 DARK_RED if any(x in u for x in ('LAWYER', 'HIGH'))               else
                 None)

        row = tbl.add_row().cells
        for cell, txt in zip(row, [item, status]):
            p = cell.paragraphs[0]
            p.clear()
            run = p.add_run(txt)
            _fmt(run, bold=is_risk, color=color)


# ── Public entry point ─────────────────────────────────────────────────────────

def build_outputs(
    clean_text: str,
    redline_text: str,
    commentary_text: str,
    company_name: str,
    doc_type: str,
    output_dir: str,
    job_id: str = None,
) -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    prefix = f"{job_id}_" if job_id else ""

    paths = {}

    clean_doc = _build_clean(clean_text, company_name, doc_type)
    paths['clean'] = str(out / f"{prefix}clean.docx")
    clean_doc.save(paths['clean'])

    redline_doc = _build_redline(redline_text)
    paths['redline'] = str(out / f"{prefix}redline.docx")
    redline_doc.save(paths['redline'])

    commentary_doc = _build_commentary(commentary_text)
    paths['commentary'] = str(out / f"{prefix}commentary.docx")
    commentary_doc.save(paths['commentary'])

    return paths
