from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Sequence

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_ALIGN_VERTICAL, WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


WORKSPACE = Path(r".")
WORK = WORKSPACE / "_internship_report_work"
FINAL = WORKSPACE / "Research_Internship_Report_Chanphot_Wongtaweesup_PSQ_SCO.docx"
TOC_PAGES_PATH = WORK / "toc_pages.json"

FIG_FRAMEWORK = Path(
    r"ontology/docs/figures"
    r"\psq_sco_ontology_framework_diagram.png"
)
FIG_CASES = Path(
    r"genai_engine/paper/overleaf_live_recovered_20260714"
    r"\psq_paper120_design.png"
)


# narrative_proposal preset, resolved into explicit tokens
PAGE_WIDTH_IN = 8.5
PAGE_HEIGHT_IN = 11.0
MARGIN_IN = 1.0
USABLE_WIDTH_DXA = 9360  # 6.5 inches
TABLE_INDENT_DXA = 120
CELL_TOP_BOTTOM_DXA = 80
CELL_START_END_DXA = 120
BASE_FONT = "Calibri"
BODY_SIZE = 11
BODY_AFTER = 8
BODY_LINE = 1.333
H1_SIZE = 16
H2_SIZE = 13
H3_SIZE = 12

NAVY = "19375F"
BLUE = "2E74B5"
DARK_BLUE = "1F4D78"
TEAL = "2D7F86"
GOLD = "A97917"
BLACK = "000000"
MUTED = "666666"
LIGHT = "F4F6F9"
LIGHT_BLUE = "E8EEF5"
LIGHT_GREEN = "E9F2EC"
LIGHT_GOLD = "FFF4D6"
WHITE = "FFFFFF"
GRID = "B8C2CC"


def rgb(hex_color: str) -> RGBColor:
    return RGBColor.from_string(hex_color)


def set_run_font(
    run,
    *,
    name: str = BASE_FONT,
    size: float | None = None,
    color: str | None = None,
    bold: bool | None = None,
    italic: bool | None = None,
):
    run.font.name = name
    run._element.get_or_add_rPr()
    rfonts = run._element.rPr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        run._element.rPr.insert(0, rfonts)
    rfonts.set(qn("w:ascii"), name)
    rfonts.set(qn("w:hAnsi"), name)
    rfonts.set(qn("w:eastAsia"), name)
    if size is not None:
        run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = rgb(color)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    return run


def add_field(run, instruction: str, display_text: str = "1"):
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    txt = OxmlElement("w:t")
    txt.text = display_text
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_begin, instr, fld_sep, txt, fld_end])


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    marker = OxmlElement("w:tblHeader")
    marker.set(qn("w:val"), "true")
    tr_pr.append(marker)


def prevent_row_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    marker = OxmlElement("w:cantSplit")
    tr_pr.append(marker)


def set_cell_margins(cell, top=CELL_TOP_BOTTOM_DXA, start=CELL_START_END_DXA,
                     bottom=CELL_TOP_BOTTOM_DXA, end=CELL_START_END_DXA):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for tag, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{tag}"))
        if node is None:
            node = OxmlElement(f"w:{tag}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_cell_shading(cell, fill: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_table_borders(table, color=GRID, size=4):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = borders.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            borders.append(node)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), str(size))
        node.set(qn("w:space"), "0")
        node.set(qn("w:color"), color)


def set_table_geometry(table, widths_dxa: Sequence[int], indent_dxa=TABLE_INDENT_DXA):
    if sum(widths_dxa) != USABLE_WIDTH_DXA:
        raise ValueError(f"Table widths must total {USABLE_WIDTH_DXA}: {widths_dxa}")
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl = table._tbl
    tbl_pr = tbl.tblPr

    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(USABLE_WIDTH_DXA))
    tbl_w.set(qn("w:type"), "dxa")

    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), str(indent_dxa))
    tbl_ind.set(qn("w:type"), "dxa")

    grid = tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths_dxa:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)

    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            width = widths_dxa[idx]
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(width))
            tc_w.set(qn("w:type"), "dxa")
            cell.width = Inches(width / 1440)
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_paragraph_shading(paragraph, fill: str, border: str | None = None):
    p_pr = paragraph._p.get_or_add_pPr()
    shd = p_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        p_pr.append(shd)
    shd.set(qn("w:fill"), fill)
    if border:
        p_bdr = p_pr.find(qn("w:pBdr"))
        if p_bdr is None:
            p_bdr = OxmlElement("w:pBdr")
            p_pr.append(p_bdr)
        for edge in ("top", "left", "bottom", "right"):
            node = OxmlElement(f"w:{edge}")
            node.set(qn("w:val"), "single")
            node.set(qn("w:sz"), "4")
            node.set(qn("w:space"), "4")
            node.set(qn("w:color"), border)
            p_bdr.append(node)


def add_hyperlink(paragraph, text: str, url: str, color=BLUE, underline=True):
    part = paragraph.part
    rel_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), rel_id)
    run = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    r_fonts = OxmlElement("w:rFonts")
    r_fonts.set(qn("w:ascii"), BASE_FONT)
    r_fonts.set(qn("w:hAnsi"), BASE_FONT)
    color_el = OxmlElement("w:color")
    color_el.set(qn("w:val"), color)
    r_pr.append(r_fonts)
    r_pr.append(color_el)
    if underline:
        u = OxmlElement("w:u")
        u.set(qn("w:val"), "single")
        r_pr.append(u)
    run.append(r_pr)
    t = OxmlElement("w:t")
    t.text = text
    run.append(t)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)
    return hyperlink


def add_body(doc: Document, text: str, *, bold_lead: str | None = None,
             italic=False, after=BODY_AFTER, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph(style="Normal")
    p.alignment = align
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = BODY_LINE
    if bold_lead and text.startswith(bold_lead):
        r1 = p.add_run(bold_lead)
        set_run_font(r1, size=BODY_SIZE, bold=True)
        r2 = p.add_run(text[len(bold_lead):])
        set_run_font(r2, size=BODY_SIZE, italic=italic)
    else:
        r = p.add_run(text)
        set_run_font(r, size=BODY_SIZE, italic=italic)
    return p


def add_rich(doc: Document, pieces: Iterable[tuple[str, dict]], *,
             align=WD_ALIGN_PARAGRAPH.JUSTIFY, after=BODY_AFTER):
    p = doc.add_paragraph(style="Normal")
    p.alignment = align
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = BODY_LINE
    for text, opts in pieces:
        r = p.add_run(text)
        set_run_font(
            r,
            size=opts.get("size", BODY_SIZE),
            color=opts.get("color", BLACK),
            bold=opts.get("bold"),
            italic=opts.get("italic"),
        )
    return p


def add_bullet(doc: Document, text: str, level=0):
    style = "List Bullet" if level == 0 else "List Bullet 2"
    p = doc.add_paragraph(style=style)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.left_indent = Inches(0.375 + 0.25 * level)
    p.paragraph_format.first_line_indent = Inches(-0.194)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.208
    set_run_font(p.add_run(text), size=BODY_SIZE)
    return p


def add_numbered(doc: Document, text: str):
    p = doc.add_paragraph(style="List Number")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.left_indent = Inches(0.375)
    p.paragraph_format.first_line_indent = Inches(-0.194)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.208
    set_run_font(p.add_run(text), size=BODY_SIZE)
    return p


def add_manual_numbered(doc: Document, number: int, text: str):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.left_indent = Inches(0.375)
    p.paragraph_format.first_line_indent = Inches(-0.194)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.208
    set_run_font(p.add_run(f"{number}. "), size=BODY_SIZE)
    set_run_font(p.add_run(text), size=BODY_SIZE)
    return p


def add_callout(doc: Document, label: str, text: str, *, fill=LIGHT_GOLD, border=GOLD):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.12)
    p.paragraph_format.right_indent = Inches(0.12)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.line_spacing = 1.2
    set_paragraph_shading(p, fill, border)
    set_run_font(p.add_run(f"{label}: "), size=10.5, color=NAVY, bold=True)
    set_run_font(p.add_run(text), size=10.5, color=BLACK)
    return p


def add_table(
    doc: Document,
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
    widths_dxa: Sequence[int],
    *,
    font_size=9.0,
    header_fill=LIGHT_BLUE,
    first_col_bold=False,
    column_alignments: Sequence[int] | None = None,
):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    hdr = table.rows[0]
    set_repeat_table_header(hdr)
    prevent_row_split(hdr)
    for idx, text in enumerate(headers):
        cell = hdr.cells[idx]
        set_cell_shading(cell, header_fill)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.0
        set_run_font(p.add_run(text), size=font_size, color=NAVY, bold=True)
    for row_data in rows:
        row = table.add_row()
        prevent_row_split(row)
        for idx, text in enumerate(row_data):
            cell = row.cells[idx]
            p = cell.paragraphs[0]
            if column_alignments:
                p.alignment = column_alignments[idx]
            else:
                p.alignment = (
                    WD_ALIGN_PARAGRAPH.CENTER if idx == 0 and len(headers) > 2
                    else WD_ALIGN_PARAGRAPH.LEFT
                )
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.05
            set_run_font(
                p.add_run(str(text)),
                size=font_size,
                bold=(first_col_bold and idx == 0),
            )
    set_table_geometry(table, widths_dxa)
    set_table_borders(table)
    after = doc.add_paragraph()
    after.paragraph_format.space_after = Pt(2)
    return table


def add_figure(doc: Document, path: Path, caption: str, *, width_in=6.35, alt_text=""):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run()
    shape = run.add_picture(str(path), width=Inches(width_in))
    try:
        shape._inline.docPr.set("descr", alt_text or caption)
        shape._inline.docPr.set("title", caption.split(".", 1)[0])
    except Exception:
        pass
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_before = Pt(0)
    cap.paragraph_format.space_after = Pt(10)
    cap.paragraph_format.keep_with_next = True
    set_run_font(cap.add_run(caption), size=9, color=MUTED, italic=True)


def add_reference(doc: Document, number: int, text: str, url: str | None = None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.first_line_indent = Inches(-0.25)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.05
    set_run_font(p.add_run(f"[{number}] "), size=9.5, bold=True, color=NAVY)
    set_run_font(p.add_run(text), size=9.5)
    if url:
        set_run_font(p.add_run(" "), size=9.5)
        add_hyperlink(p, url, url, color=BLUE)
    return p


def add_project_source(doc: Document, code: str, title: str, path: str, role: str):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.left_indent = Inches(0.28)
    p.paragraph_format.first_line_indent = Inches(-0.28)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.05
    set_run_font(p.add_run(f"[{code}] "), size=9.2, color=NAVY, bold=True)
    set_run_font(p.add_run(f"{title}. "), size=9.2, bold=True)
    set_run_font(p.add_run(f"{role} "), size=9.2)
    set_run_font(p.add_run(f"Path: {path}"), size=8.6, color=MUTED, italic=True)
    return p


def add_heading(doc: Document, text: str, level: int, *, page_break=False):
    if page_break:
        doc.add_page_break()
    p = doc.add_paragraph(text, style=f"Heading {level}")
    p.paragraph_format.keep_with_next = True
    return p


def configure_styles(doc: Document):
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = BASE_FONT
    normal.font.size = Pt(BODY_SIZE)
    normal.font.color.rgb = rgb(BLACK)
    normal._element.rPr.rFonts.set(qn("w:ascii"), BASE_FONT)
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), BASE_FONT)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(BODY_AFTER)
    normal.paragraph_format.line_spacing = BODY_LINE
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for name, size, color, before, after in [
        ("Heading 1", H1_SIZE, BLUE, 18, 10),
        ("Heading 2", H2_SIZE, BLUE, 12, 6),
        ("Heading 3", H3_SIZE, DARK_BLUE, 8, 4),
    ]:
        st = styles[name]
        st.font.name = BASE_FONT
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = rgb(color)
        st._element.rPr.rFonts.set(qn("w:ascii"), BASE_FONT)
        st._element.rPr.rFonts.set(qn("w:hAnsi"), BASE_FONT)
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.keep_with_next = True

    for name in ["List Bullet", "List Bullet 2", "List Number"]:
        st = styles[name]
        st.font.name = BASE_FONT
        st.font.size = Pt(BODY_SIZE)
        st._element.rPr.rFonts.set(qn("w:ascii"), BASE_FONT)
        st._element.rPr.rFonts.set(qn("w:hAnsi"), BASE_FONT)

    if "Caption" not in styles:
        styles.add_style("Caption", WD_STYLE_TYPE.PARAGRAPH)
    caption = styles["Caption"]
    caption.font.name = BASE_FONT
    caption.font.size = Pt(9)
    caption.font.italic = True
    caption.font.color.rgb = rgb(MUTED)


def configure_section(section):
    section.page_width = Inches(PAGE_WIDTH_IN)
    section.page_height = Inches(PAGE_HEIGHT_IN)
    section.top_margin = Inches(MARGIN_IN)
    section.bottom_margin = Inches(MARGIN_IN)
    section.left_margin = Inches(MARGIN_IN)
    section.right_margin = Inches(MARGIN_IN)
    section.header_distance = Inches(0.45)
    section.footer_distance = Inches(0.45)
    section.different_first_page_header_footer = True

    header = section.header
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(0)
    set_run_font(
        p.add_run("RESEARCH INTERNSHIP REPORT  |  PERSONASHIELD QUEST PSQ-SCO"),
        size=8.5,
        color=MUTED,
        bold=True,
    )

    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.paragraph_format.space_before = Pt(0)
    fp.paragraph_format.space_after = Pt(0)
    set_run_font(fp.add_run("Chanphot Wongtaweesup  |  ReaLearn  |  Page "), size=8.5, color=MUTED)
    page_run = fp.add_run()
    set_run_font(page_run, size=8.5, color=MUTED)
    add_field(page_run, " PAGE ")


def build_document():
    toc_pages = {}
    if TOC_PAGES_PATH.exists():
        toc_pages = json.loads(TOC_PAGES_PATH.read_text(encoding="utf-8"))

    doc = Document()
    configure_styles(doc)
    configure_section(doc.sections[0])
    doc.core_properties.title = (
        "Research Internship Report: Ontology-Guided Scenario Control Generation "
        "for GenAI in Cybersecurity Serious Game"
    )
    doc.core_properties.subject = "PersonaShield Quest Scenario Control Ontology (PSQ-SCO)"
    doc.core_properties.author = "Chanphot Wongtaweesup"
    doc.core_properties.keywords = (
        "PSQ-SCO, ontology, knowledge graph, cybersecurity serious game, "
        "retrieval-augmented generation, ReaLearn, Tohoku University"
    )

    # Editorial cover
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(70)
    p.paragraph_format.space_after = Pt(18)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run_font(p.add_run("RESEARCH INTERNSHIP REPORT"), size=11, color=GOLD, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    set_run_font(
        p.add_run(
            "Ontology-Guided Scenario Control Generation for GenAI "
            "in Cybersecurity Serious Game"
        ),
        size=27,
        color=NAVY,
        bold=True,
    )

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(28)
    set_run_font(
        p.add_run("PersonaShield Quest Scenario Control Ontology (PSQ-SCO)"),
        size=15,
        color=TEAL,
        italic=True,
    )

    for line, bold in [
        ("Chanphot Wongtaweesup", True),
        ("Ph.D. Student, Asian Institute of Technology", False),
        ("Research Intern, 8 May 2026 - 6 August 2026", False),
        ("ReaLearn (Trustworthy AI Lab)", True),
        ("Advanced Institute of So-Go-Chi (Convergence Knowledge) Informatics", False),
        ("Tohoku University, Japan", False),
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(3)
        set_run_font(p.add_run(line), size=11.5 if bold else 10.5, color=NAVY if bold else MUTED, bold=bold)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(34)
    p.paragraph_format.space_after = Pt(3)
    set_run_font(p.add_run("Research host and mentor: Teeradaj Racharak"), size=10, color=MUTED)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run_font(p.add_run("Report evidence current through 26 July 2026"), size=9.5, color=MUTED, italic=True)

    doc.add_page_break()

    add_heading(doc, "Report Profile", 1)
    add_table(
        doc,
        ["Field", "Details"],
        [
            ["Intern", "Chanphot Wongtaweesup"],
            ["Home institution", "Asian Institute of Technology (AIT), Ph.D. student"],
            ["Host group", "ReaLearn (Trustworthy AI Lab), Tohoku University"],
            ["Host institute", "Advanced Institute of So-Go-Chi (Convergence Knowledge) Informatics"],
            ["Internship period", "8 May 2026 - 6 August 2026"],
            ["Initial framing", "Ontology-Driven Emotion-Aware Adaptive Cybersecurity Training Framework (ODEACT)"],
            ["Final research focus", "Ontology-Guided Scenario Control Generation for GenAI in Cybersecurity Serious Game"],
            ["Primary artifact", "PersonaShield Quest Scenario Control Ontology (PSQ-SCO) v9.1"],
        ["Report status", "Complete research report based on evidence through 26 July; close-out actions to 6 August are marked in progress or planned"],
        ],
        [2160, 7200],
        font_size=9.5,
        first_col_bold=True,
        column_alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT],
    )

    add_callout(
        doc,
        "Scope correction",
        "The final PSQ-SCO v9.1 is a scenario-control ontology, not a full emotion or pedagogy ontology. "
        "The broader ODEACT concept remains the parent research framework, while the internship deliverable was deliberately narrowed "
        "to executable scenario control, cybersecurity structure, quality rules, evidence, provenance, and engine mappings.",
        fill=LIGHT_BLUE,
        border=BLUE,
    )

    add_heading(doc, "Executive Summary", 1, page_break=True)
    add_body(
        doc,
        "This internship transformed an initial idea for an ontology-driven, emotion-aware adaptive cybersecurity framework into a bounded and testable "
        "research contribution: the PersonaShield Quest Scenario Control Ontology (PSQ-SCO). The final focus was not to model all learning, emotion, or "
        "cybersecurity knowledge. It was to provide an explicit pre-generation contract for a serious-game scenario engine so that learner context, channel, "
        "attack or legitimate-message structure, safe responses, quality rules, evidence, and provenance could be selected and audited before an LLM generated prose."
    )
    add_body(
        doc,
        "The work progressed from literature review and competency-question design to OWL/RDF implementation, SPARQL queries, HermiT reasoning, knowledge-graph export, "
        "engine bindings, a four-condition generation study, a three-layer evaluation framework, and an IJCKG 2026 Education Track manuscript. The latest ontology release "
        "evidence reports 73 declared domain classes (74 when the evaluator includes owl:Thing), 49 object properties, 39 datatype properties, 17 annotation properties, "
        "133 named individuals, 3,229 triples, and a 311-node/3,164-edge export. All eight positive/negative ASK tests passed, HermiT found no inconsistency or unsatisfiable "
        "classes, and 4,362 bounded completeness checks passed for the CQ1-CQ4 scope [P11-P15]."
    )
    add_body(
        doc,
        "The matched engine study used 120 frozen case specifications, four generation conditions, and three local open-weight LLMs, yielding 1,440 finalized records. "
        "Under the latest common-case contract used in the July 23 manuscript, every method reached the ceiling on JSON, game-schema, eight-control, and common-concept checks. "
        "The ontology therefore did not prove superior general scenario quality. Its demonstrated value was mechanism-level: typed constraints, provenance, traceability, "
        "content-quality rules, and auditability. The structured-ontology condition had the strongest secondary method-conditioned diagnostics and the best relative diversity "
        "profile, while a separate Graph-Walk v1 follow-up verified graph-walk prompt exposure but also revealed lower live-model-content retention and greater repair use [P18-P21]."
    )
    add_body(
        doc,
        "The principal scholarly output is a Springer LNCS/LNAI manuscript titled “Ontology-Guided Scenario Control Generation for GenAI in Cybersecurity Serious Game.” "
        "The folder contains a complete, citation-checked Overleaf package and targeted evaluation repairs dated 23 July 2026. No EasyChair receipt or other submission evidence "
        "was found, so this report describes the paper as manuscript-ready rather than submitted or accepted. The official IJCKG 2026 full-paper deadline was 24 July 2026; "
        "submission status should be confirmed during close-out [22, P20]."
    )

    add_heading(doc, "Contents", 1, page_break=True)
    toc_entries = [
        "Executive Summary",
        "1. Internship Timeline and Linked Work",
        "2. Complete Work: Ontology, Engine Integration, and Evaluation",
        "3. Internship Results: Ontology, Evaluation, and Paper",
        "References",
        "Appendix A. Dated Slide-Deck Evidence",
        "Appendix B. Project Artifact Inventory",
        "Appendix C. Validation and Evaluation Evidence Matrix",
        "Appendix D. Close-out Checklist to 6 August 2026",
    ]
    toc_rows = [[entry, str(toc_pages.get(entry, "—"))] for entry in toc_entries]
    add_table(
        doc,
        ["Section", "Page"],
        toc_rows,
        [8200, 1160],
        font_size=10,
        column_alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER],
    )
    add_body(
        doc,
        "The page numbers in this contents list are materialized from the final rendered document for deterministic review.",
        italic=True,
        after=0,
        align=WD_ALIGN_PARAGRAPH.LEFT,
    )

    # Section 1
    add_heading(doc, "1. Internship Timeline and Linked Work", 1, page_break=True)
    add_body(
        doc,
        "The internship ran for thirteen weeks from 8 May to 6 August 2026. Ten dated ReaLearn presentation decks provide the contemporaneous weekly record, while versioned "
        "ontology and engine artifacts document the technical work between presentations. The timeline below links each week to the research transition it enabled. “Completed” "
        "means supported by a dated artifact in the folders. “In progress” and “Planned” distinguish work after the last evidence deck from work that has not yet occurred."
    )
    timeline_rows = [
        ["1", "8-14 May", "Onboarding and research framing",
         "Mapped PersonaShield Quest, the GenAI/RAG scenario engine, and the wider affective-adaptive Ph.D. framework. Identified the internship subproblem: an ontology as a vocabulary and constraint layer.",
         "Completed"],
        ["2", "15-21 May", "Ontology purpose and literature scan",
         "Presented the ODEACT concept; studied Ontology Development 101; reviewed COFELET, COMAT, GENICS, MITRE ATT&CK/CAPEC, and serious-game ontology work. Defined offline validation plus runtime selection as the intended architecture [P1-P2].",
         "Completed"],
        ["3", "22-28 May", "Scope, CQs, and source inventory",
         "Adopted the seven-step ontology method; specified phishing, smishing, vishing, roles, age groups, difficulty, safe responses, and evidence. Drafted CQ1-CQ5 and inventoried Thai/English datasets and authoritative sources [P3].",
         "Completed"],
        ["4", "29 May-4 Jun", "Term and evidence consolidation",
         "Normalized scenario, learner, attack, evidence, provenance, and pedagogy-related terms; mapped candidate reused concepts and prepared ontology-ready source material for later OWL implementation.",
         "Completed"],
        ["5", "5-11 Jun", "Ontology engineering design",
         "Deepened KG/RAG and trustworthy-AI literature; refined CQ inputs, expected answers, and test cases; designed four conceptual pillars and the properties/constraints required for deterministic SPARQL answers [P4].",
         "Completed"],
        ["6", "12-18 Jun", "OWL/KG implementation and experiment protocol",
         "Built the ontology in Protégé/OWL; established class, property, instance, evidence, and binding structures; designed the 120-case x 3-model x 3/4-condition evaluation and targeted IJCKG 2026 [P5].",
         "Completed"],
        ["7", "19-25 Jun", "Executable CQs and paper draft",
         "Implemented and demonstrated CQ1 scenario selection, CQ2 cybersecurity structure, CQ3 alignment/quality logic, and CQ4 evidence grounding; documented expected rows and began the conference manuscript and engine integration [P6].",
         "Completed"],
        ["8", "26 Jun-2 Jul", "Reviewer-aligned scope correction",
         "Renamed the artifact PSQ-SCO; separated the wider ODEACT framework from the scenario-control ontology; replaced pedagogical CQ3 with content-quality control; removed the pedagogy branch in v9.1; regenerated bindings, KG exports, tests, and release reports [P7, P12-P15].",
         "Completed"],
        ["9", "3-9 Jul", "Four-condition generation and early evaluation",
         "Ran prompt-only, text-RAG, structured ontology+RAG, and ontology-to-text generation with Mistral 7B, Qwen2.5 7B, and Qwen3 8B. Established three evaluation layers and recovered a complete 120-case comparison set [P8].",
         "Completed"],
        ["10", "10-16 Jul", "Metric audit and manuscript revision",
         "Separated common-case conformance from mechanism-conditioned diagnostics; documented corpus imbalance, retrieval misses, provenance limits, composite-index caveats, diversity measures, and the lack of human/learner evidence. Produced Overleaf-ready manuscript and result bundles [P9, P17-P20].",
         "Completed"],
        ["11", "17-23 Jul", "Final evaluation repair and Graph-Walk follow-up",
         "Finalized the July 18 v5 metric contract and July 23 targeted manuscript repair. Ran a separate Graph-Walk v1 experiment verifying 360/360 walk exposure, then documented treatment exposure, live-content retention, repair use, and diversity trade-offs [P10, P18-P21].",
         "Completed"],
        ["12", "24-30 Jul", "Report and publication close-out",
         "Synthesize the internship report, reconcile the manuscript with the latest supplementary evaluation, confirm whether IJCKG submission occurred, archive exact hashes, and prepare the handover package.",
         "In progress"],
        ["13", "31 Jul-6 Aug", "Final handover",
         "Deliver final report and artifact index; record unresolved limitations and recommended experiments; confirm repository/archive locations, ownership, licensing checks, and the next research milestone.",
         "Planned"],
    ]
    add_table(
        doc,
        ["Week", "Dates", "Focus", "Linked work and evidence", "Status"],
        timeline_rows,
        [700, 1180, 1780, 4680, 1020],
        font_size=8.15,
        header_fill=LIGHT_BLUE,
        column_alignments=[
            WD_ALIGN_PARAGRAPH.CENTER,
            WD_ALIGN_PARAGRAPH.CENTER,
            WD_ALIGN_PARAGRAPH.LEFT,
            WD_ALIGN_PARAGRAPH.LEFT,
            WD_ALIGN_PARAGRAPH.CENTER,
        ],
    )

    add_heading(doc, "1.1 Research evolution across the internship", 2)
    add_body(
        doc,
        "Phase I - broad framework (May). The original ODEACT framing treated the ontology as the semantic foundation of an emotion-aware adaptive training architecture. "
        "This was useful for locating the internship within the Ph.D. project, but it included more learner, emotion, and pedagogy concepts than could be defended and evaluated during the placement."
    )
    add_body(
        doc,
        "Phase II - ontology and CQ implementation (June). The work became a task-oriented application ontology built around answerable competency questions, trusted sources, "
        "engine mappings, and explicit scenario templates. Weekly presentations changed from conceptual diagrams to SPARQL queries, expected result rows, reasoner checks, and a paper plan."
    )
    add_body(
        doc,
        "Phase III - reviewer-aligned PSQ-SCO and evaluation (late June-July). The final scope removed the PedagogicalKnowledgeEntity branch, retained scenario selection, "
        "cybersecurity structure, content-quality control, and evidence/provenance, and moved the research claim from “adaptive pedagogy” to “auditable scenario control.” "
        "The empirical work then compared four knowledge-delivery mechanisms under a matched design and explicitly separated common conformance from mechanism-specific diagnostics."
    )

    add_heading(doc, "1.2 Work-product linkage", 2)
    add_table(
        doc,
        ["Research activity", "Resulting work product", "Downstream use"],
        [
            ["Literature and standards review", "Ontology method, reused concepts, source and dataset register", "Defined scope and reference vocabulary"],
            ["Competency-question design", "CQ1-CQ4 SELECT queries and eight positive/negative ASK tests", "Made requirements executable"],
            ["OWL/RDF modeling", "PSQ-SCO v9.1 ontology and KG exports", "Provided the control graph"],
            ["Reviewer response", "v9 and v9.1 change logs plus no-pedagogy correction", "Aligned claims with implemented scope"],
            ["Engine integration", "Semantic packet, ontology-to-text documents, field mappings, scenario schemas", "Delivered ontology knowledge to local LLMs"],
            ["Evaluation engineering", "Three-layer evaluator, frozen 120-case design, corpus/metric audits", "Separated ontology, scenario, and comparison claims"],
            ["Paper preparation", "LNCS/LNAI manuscript, figures, BibTeX, targeted change manifests", "Converted the internship into a scholarly output"],
            ["Supplementary study", "Graph-Walk v1 exposure and generation-integrity audit", "Exposed treatment fidelity and repair dependence"],
        ],
        [2550, 3600, 3210],
        font_size=8.8,
        column_alignments=[WD_ALIGN_PARAGRAPH.LEFT] * 3,
    )

    # Section 2
    add_heading(doc, "2. Complete Work: Ontology, Engine Integration, and Evaluation", 1, page_break=True)
    add_heading(doc, "2.1 Research problem and final objective", 2)
    add_body(
        doc,
        "PersonaShield Quest requires more than plausible phishing prose. Each playable record must preserve the assigned learner role, stage, age band, channel, malicious or legitimate variant, "
        "difficulty, attack type, safe behavior, answer choices, feedback, and evidence trace. Text RAG may provide examples, but an example is not an explicit contract. The final internship objective "
        "was therefore to design and test a compact ontology-guided control layer that makes those requirements queryable before generation and auditable after generation [11-13]."
    )
    add_callout(
        doc,
        "Final research statement",
        "PSQ-SCO is an OWL/RDF scenario-control ontology and ontology-based knowledge graph for selecting, constraining, grounding, and auditing GenAI-generated cybersecurity serious-game scenarios. "
        "It does not generate prose, modify itself from LLM outputs, represent all pedagogy, or prove learning outcomes.",
        fill=LIGHT_GREEN,
        border=TEAL,
    )

    add_heading(doc, "2.2 Ontology engineering method", 2)
    add_body(
        doc,
        "The modeling process followed an iterative ontology-development pattern: define domain and scope; formulate competency questions; identify reusable vocabularies and trusted sources; enumerate terms; "
        "construct classes and properties; populate controlled individuals; and validate with reasoning and queries [4, 5, 6, 9, 10]. The internship added an application-engineering layer: every retained term had to "
        "support a competency question, a validation rule, an evidence path, or a runtime mapping."
    )
    for item in [
        "Domain boundary: phishing, smishing, vishing, and legitimate communication for a cybersecurity-awareness serious game.",
        "Control boundary: learner/persona context, scenario template, channel, variant, difficulty, attack or legitimate structure, safe action, quality rules, evidence, and provenance.",
        "Excluded boundary: complete pedagogy, complete emotion modeling, malware/network execution, live malicious content, universal cyber-threat coverage, and automatic classroom approval.",
        "Standards and sources: OWL 2, SPARQL 1.1, PROV-O concepts, SHACL-informed constraint design, MITRE ATT&CK/CAPEC mappings, peer-reviewed training research, and curated project datasets [5-8, 16].",
        "Validation boundary: logical consistency, expected/prohibited query patterns, bounded CQ completeness, mapping preservation, and application-level checks.",
    ]:
        add_bullet(doc, item)

    add_heading(doc, "2.3 Ontology modules and architecture", 2)
    add_figure(
        doc,
        FIG_FRAMEWORK,
        "Figure 1. PSQ-SCO framework: scenario inputs and trusted knowledge are resolved through the ontology and query layer into engine packets, then audited through validation and runtime feedback (project artifact P16).",
        width_in=6.4,
        alt_text="Architecture diagram showing scenario inputs and trusted knowledge feeding the PSQ-SCO knowledge graph, query layer, engine packets, scenario engine, validation, and runtime feedback.",
    )
    add_body(
        doc,
        "The architecture maintains a strict trust boundary. The normative ontology is read-only during generation. A deterministic parser or SPARQL query selects eligible templates, required and prohibited concepts, "
        "quality rules, safe responses, and source identifiers. The LLM produces the player-facing record, and deterministic validators decide whether the final object is structurally usable. Generated text is not written "
        "back into the ontology without review."
    )
    add_table(
        doc,
        ["Module", "Representative content", "Function"],
        [
            ["Learner control", "Persona role, age band, stage and transition constraints, retrieval mode", "Selects context-compatible templates"],
            ["Cybersecurity structure", "Channel, variant, attack/legitimate type, cues, indicators, safe response, ATT&CK/CAPEC mappings", "Constrains the content contract"],
            ["Content quality", "Eligibility, consistency, separation, evidence, acceptance, rejection, scores, decisions", "Makes generated-content rules explicit"],
            ["Evidence and provenance", "Evidence packs, source artifacts, datasets, source IDs, provenance records", "Supports traceability and audit"],
            ["Engine mapping", "Semantic-packet fields, controlled vocabulary, runtime bindings, scenario identifiers", "Connects OWL/RDF to the generation pipeline"],
        ],
        [1800, 4140, 3420],
        font_size=8.7,
        column_alignments=[WD_ALIGN_PARAGRAPH.LEFT] * 3,
    )

    add_heading(doc, "2.4 Scope correction from v9 to v9.1", 2)
    add_body(
        doc,
        "Reviewer feedback led to the most important modeling decision of the internship. PSQ-SCO v9 renamed the ontology, made quality control explicit, and separated the broader ODEACT framework from the scenario-control artifact. "
        "Version 9.1 then removed the PedagogicalKnowledgeEntity branch and related Bloom, learning-objective, hint, feedback, and pedagogical runtime fields. The correction removed 36 resources, 10 properties, 605 triples, and one "
        "malformed anonymous OWL restriction. It preserved CQ1-CQ4 scenario control, cybersecurity structure, content-quality control, evidence grounding, semantic-packet export, and validation metadata [P12-P13]."
    )
    add_table(
        doc,
        ["Profile item", "v9", "v9.1", "Interpretation"],
        [
            ["Classes", "86", "73 declared domain classes", "Pedagogy branch removed; evaluator may report 74 including owl:Thing"],
            ["Object properties", "59", "49", "Pedagogy-linking properties removed"],
            ["Datatype properties", "39", "39", "Runtime data contract retained"],
            ["Named individuals", "156", "133", "Pedagogy individuals removed"],
            ["Graph export", "357 nodes / 3,636 edges", "311 nodes / 3,164 edges", "Smaller bounded control graph"],
            ["Runtime records", "12,425", "12,425", "Engine-facing corpus preserved"],
        ],
        [1760, 1450, 2050, 4100],
        font_size=8.6,
        column_alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT],
    )

    add_heading(doc, "2.5 Competency questions and executable answers", 2)
    add_body(
        doc,
        "The final ontology is organized around four competency questions. Each question has a SELECT interface for the expected answer and one positive plus one negative ASK test. This test-driven structure converts abstract ontology requirements into repeatable, version-controlled evidence [10]."
    )
    add_table(
        doc,
        ["CQ", "Question answered", "Observed v9.1 result", "Engine use"],
        [
            ["CQ1", "Which templates satisfy the requested learner state, transition, role, age, channel, variant, attack type, difficulty, and retrieval mode?", "2 eligible SMS templates: one fake bank-link smishing case and one legitimate internal reminder", "Template selection and case controls"],
            ["CQ2", "Which cybersecurity or legitimate-communication concepts define the selected template?", "13 bindings including T1566.003, CAPEC-164, smishing, credential harvesting, fear, urgency, three red flags, safe response, and reporting", "Must-include and must-exclude concepts"],
            ["CQ3", "Which content-quality rules, thresholds, decisions, scores, and violations govern the template and candidate?", "8 active rules; candidate marked for review with quality 0.92, confidence 0.88, and no violation", "Validation and technical triage"],
            ["CQ4", "Which evidence, datasets, and provenance support the attack classification, indicators, and response?", "12 bindings for the voice template across ATT&CK T1566.004, CAPEC-164, a peer-reviewed training source, IRS transcript, and provenance record", "Evidence packet and audit trace"],
        ],
        [650, 3930, 2860, 1920],
        font_size=8.25,
        column_alignments=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT],
    )

    add_heading(doc, "2.6 Ontology and knowledge-graph validation", 2)
    add_body(
        doc,
        "Validation was deliberately multi-layered. HermiT evaluated OWL consistency; RDFLib executed SPARQL queries; project scripts checked the CQ contracts, graph noise, scope removal, OWL restriction structure, runtime export, and mapping preservation. "
        "The resulting claim is bounded completeness for the six templates and four competency-question contracts, not universal cybersecurity completeness."
    )
    add_table(
        doc,
        ["Validation item", "Result", "Evidence-safe interpretation"],
        [
            ["RDF/XML release load", "PASS; 3,229 triples", "The release file is parseable under the tested toolchain"],
            ["HermiT reasoning", "Consistent; 0 unsatisfiable classes; 3.636 s", "Logical consistency for the tested ontology file"],
            ["SPARQL ASK tests", "8/8 passed", "Expected and prohibited CQ patterns behaved as specified"],
            ["CQ SELECT rows", "CQ1=2, CQ2=13, CQ3=8, CQ4=12", "The published query interface returned documented answers"],
            ["Bounded relationship checks", "4,362/4,362 passed", "Complete only for the declared CQ1-CQ4 test scope"],
            ["CQ completeness edges", "72/72; 30/30; 6/6; 12/12", "All required template-edge patterns were present"],
            ["Graph noise", "0 dangling local references; 0 errors/warnings", "No detected local export defects"],
            ["Removed-scope audit", "25 forbidden terms; 0 literal or graph hits", "The pruned pedagogy scope is absent"],
            ["OWL restriction audit", "0 malformed anonymous restrictions", "The v9.1 structural correction removed the prior artificial parent"],
            ["Runtime mapping", "1,440/1,440 preserved", "Every evaluated scenario retained the required ontology-relevant controls"],
        ],
        [2600, 2350, 4410],
        font_size=8.45,
        column_alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT],
    )

    add_heading(doc, "2.7 Engine integration and generation conditions", 2)
    add_body(
        doc,
        "The engine reused the existing PersonaShield prompt, RAG, schema, validator, and local Ollama interfaces. PSQ-SCO was integrated through two representations: a directly serialized semantic packet and selected ontology records verbalized as text. "
        "The four conditions held the case specification and JSON schema constant while changing the additional knowledge delivered to the model."
    )
    add_table(
        doc,
        ["Condition", "Implementation", "Research purpose"],
        [
            ["A. Prompt only", "Frozen case controls and base JSON instructions; no external retrieval or ontology context", "Baseline instruction-following"],
            ["B. Text RAG", "Condition A plus external Chroma retrieval when an eligible record is returned", "Value and failure modes of example retrieval"],
            ["C. Structured ontology + RAG", "Condition B plus a typed PSQ-SCO packet with templates, rules, evidence, must-include, and must-exclude fields", "Explicit semantic control and traceability"],
            ["D. Ontology to text + RAG", "External retrieval plus selected ontology records verbalized as text; lexical selection in the main study", "Text-only ontology delivery and representation effects"],
        ],
        [1650, 4750, 2960],
        font_size=8.55,
        column_alignments=[WD_ALIGN_PARAGRAPH.LEFT] * 3,
    )
    add_callout(
        doc,
        "Terminology safeguard",
        "The main Condition D was not a learned ontology embedding, Microsoft GraphRAG, or a random walk. In the frozen main run, the four-document limit excluded the optional relation walk. "
        "Graph-Walk v1 was evaluated later as a separate, non-overwriting experiment with verified walk exposure.",
        fill=LIGHT_GOLD,
        border=GOLD,
    )

    add_heading(doc, "2.8 Experimental design and data", 2)
    add_figure(
        doc,
        FIG_CASES,
        "Figure 2. Construction of the 120 matched case specifications and 1,440-record main experiment (project paper artifact P17). “Live output” records successful model calls; deterministic repair and retained-model-content are audited separately.",
        width_in=6.4,
        alt_text="Diagram showing 30 base groups expanded to 90 anchors and 30 repetitions, producing 120 cases and 1,440 outputs across three models and four methods.",
    )
    add_body(
        doc,
        "The design comprises 30 base groups (3 channels x 2 variants x 5 roles), 90 difficulty anchors, and 30 balanced stage/age repetitions. Each of the three local models generated the same 120 case IDs under four conditions. "
        "This is a matched control grid, not a random sample of stories and not 120 stochastic repetitions."
    )
    add_table(
        doc,
        ["Design component", "Value", "Meaning"],
        [
            ["Roles", "Finance, HR, IT, Management, Other", "24 cases per role"],
            ["Channels", "Email, SMS/chat, voice", "40 cases per channel"],
            ["Variants", "Fake and real/legitimate", "60 cases per variant"],
            ["Models", "Mistral 7B; Qwen2.5 7B Instruct; Qwen3 8B", "Local open-weight conditions"],
            ["Methods", "Prompt; Text RAG; Structured ontology; Ontology text", "Same case and schema, different context"],
            ["Main record count", "120 x 3 x 4 = 1,440", "One finalized record per case-model-method cell"],
            ["External corpus", "23 files; 87,661 raw; 29,731 after caps; 28,728 indexed", "Chroma cosine HNSW retrieval profile"],
            ["Corpus imbalance", "89.93% email; 97.35% English", "Limits channel and multilingual generalization"],
        ],
        [2400, 3100, 3860],
        font_size=8.6,
        column_alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT],
    )

    add_heading(doc, "2.9 Three-layer evaluation framework", 2)
    add_manual_numbered(doc, 1, "Layer 1 - Ontology function: class/property inventory, HermiT consistency, unsatisfiable classes, SPARQL CQ tests, and runtime mapping preservation.")
    add_manual_numbered(doc, 2, "Layer 2 - Scenario validation: JSON, game schema, frozen controls, common-case concept oracle, provenance fields, contradictions, and technical triage.")
    add_manual_numbered(doc, 3, "Layer 3 - Method/model comparison: matched diagnostics, method-conditioned concepts, traceability, composite-index sensitivity, diversity, repetition, treatment exposure, and generation integrity.")
    add_body(
        doc,
        "This separation is a central research outcome. It prevents ontology correctness, generated-record conformance, and educational effectiveness from being collapsed into one score. It also prevents a mechanism-aware composite from being described as a general percentage of quality [18-20]."
    )

    add_heading(doc, "2.10 Main-study results and their interpretation", 2)
    add_body(
        doc,
        "The latest July 23 manuscript uses a method-invariant common-case contract for primary conformance. All 1,440 finalized records passed JSON, game-schema, exact eight-control, and common-case precision/recall/F1 checks. "
        "This ceiling is evidence that the post-processed pipeline enforces the frozen contract; it is not evidence of perfect prose, realism, pedagogy, or source faithfulness."
    )
    add_table(
        doc,
        ["Condition", "Common gates", "Method-conditioned F1", "Grounding G", "Trace T", "Contradiction E", "OCIeq", "Emb. div.", "Self-BLEU"],
        [
            ["A Prompt", "1.000", ".512", ".481", "N/A", ".000", ".799", ".343", ".885"],
            ["B Text RAG", "1.000", ".448", ".782", ".928", ".000", ".846", ".375", ".811"],
            ["C Structured", "1.000", ".545", "1.000", ".996", ".000", ".909", ".388", ".791"],
            ["D Ontology text", "1.000", ".399", "1.000", ".968", ".003", ".879", ".376", ".806"],
        ],
        [1500, 900, 1100, 900, 800, 900, 860, 1200, 1200],
        font_size=7.7,
        column_alignments=[WD_ALIGN_PARAGRAPH.LEFT] + [WD_ALIGN_PARAGRAPH.CENTER] * 8,
    )
    add_body(
        doc,
        "Structured ontology had the highest method-conditioned precision/F1, complete provenance-field presence, the strongest mean trace resolution, the highest secondary equal-weight operational index, the highest embedding diversity, "
        "and the lowest Self-BLEU. Ontology-to-text had the highest method-conditioned recall and the lowest repeated-title rate, but one contradiction in the main study. Because several diagnostics are conditioned on ontology/provenance exposure and OCIeq is uncalibrated, "
        "the safe conclusion is that structured guidance improves observability and selected secondary diagnostics in this implementation, not that it universally improves scenario quality."
    )
    add_body(
        doc,
        "The evaluation also exposed treatment heterogeneity. External context was recorded for 226/360 Text-RAG, 221/360 structured-ontology, and 242/360 ontology-text rows in the main study. Consequently, the nominal RAG labels did not imply retrieval exposure on every row. "
        "This limits causal claims and motivates future reruns that guarantee or stratify retrieval exposure."
    )

    add_heading(doc, "2.11 Graph-Walk v1 supplementary evaluation", 2)
    add_body(
        doc,
        "A separate non-overwriting July 23 experiment replaced only Condition D with an explicit deterministic greedy relevance walk. It verified that a selected_subgraph_walk document reached all 360 assigned prompts. "
        "The follow-up is valuable because it distinguishes prompt treatment, successful live calls, retained live-model content, deterministic replacement, engine validation, and final technical acceptance."
    )
    add_table(
        doc,
        ["Graph-Walk v1 measure", "Result", "Interpretation"],
        [
            ["Verified walk exposure", "360/360 (100%)", "The declared graph-walk document reached every Condition-D prompt"],
            ["External vector context", "234/360 (65.0%)", "Only these rows received the complete nominal hybrid treatment"],
            ["Live-model content retained", "239/360 (66.39%)", "121 rows used deterministic schema-safe replacement"],
            ["Engine validation pass", "151/360 (41.94%)", "Narrow generation-engine rules are stricter than the final technical gate"],
            ["Final technical acceptance", "360/360", "Post-processed records passed the evaluator; human approval still required"],
            ["Embedding diversity", "0.3732", "Lower than structured ontology (0.3882)"],
            ["Self-BLEU", "0.8398", "More lexical repetition than structured ontology (0.7906)"],
            ["Main contribution", "Treatment fidelity", "Graph-Walk v1 improved reproducibility of Condition D, not universal quality"],
        ],
        [3000, 2100, 4260],
        font_size=8.55,
        column_alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT],
    )

    add_heading(doc, "2.12 Limitations and research-integrity safeguards", 2)
    for item in [
        "The ontology is bounded to the CQ1-CQ4 scenario-control scope; it is not universally complete.",
        "The final automatic common-case metrics reached a ceiling and cannot rank the four representations.",
        "One generation per cell does not estimate decoding variance; recovered runs used heterogeneous timing and repair paths.",
        "Successful live calls are not equivalent to retained raw model output; deterministic parsing, repair, or replacement affected attribution.",
        "Retrieval was absent for many nominal RAG rows, and the historical Chroma embedding artifact/version was not fully frozen.",
        "The corpus is dominated by English email, limiting SMS, voice, Thai, cultural, and organizational generalization.",
        "Presence and resolution of evidence identifiers do not prove that each generated claim is supported by a source.",
        "Diversity and composite-index scores are relative diagnostics, not validated acceptance thresholds.",
        "No completed blinded expert ratings, inter-rater reliability, learner study, retention measure, or transfer measure is evidenced.",
        "All scenarios require cybersecurity, pedagogy, ethics, privacy, and licensing review before deployment.",
    ]:
        add_bullet(doc, item)

    # Section 3
    add_heading(doc, "3. Internship Results: Ontology, Evaluation, and Paper", 1, page_break=True)
    add_heading(doc, "3.1 Tangible research outputs", 2)
    add_table(
        doc,
        ["Output category", "Completed deliverables", "Internship value"],
        [
            ["Ontology release", "PSQ-SCO v9.1 OWL/RDF, TXT export, namespace/versioning, controlled vocabulary", "A bounded and reviewable control contract"],
            ["Knowledge graph", "JSON/TTL/CSV graph exports, class hierarchy, instance catalog, 311 nodes and 3,164 edges", "Queryable and auditable graph representation"],
            ["CQ and validation suite", "Four SELECT queries; eight ASK cases; HermiT report; completeness, noise, and scope audits", "Repeatable functional evidence"],
            ["Engine bindings", "Semantic-packet schemas, field mappings, engine data bindings, ontology-to-text corpus and traces", "Operational connection to PersonaShield Quest"],
            ["Generation study", "120 frozen cases x 4 conditions x 3 local LLMs", "Matched method comparison"],
            ["Evaluation engine", "Three-layer metrics, paired/matched reports, treatment and generation-integrity audits", "Claim discipline and reproducibility"],
            ["Technical documentation", "Ontology, engine, evaluation, corpus, metrics, reviewer-response, and user guides", "Handover and future maintenance"],
            ["Paper package", "LNCS/LNAI LaTeX, figure, BibTeX, targeted changes, citation checks, result tables", "Scholarly dissemination artifact"],
            ["Weekly dissemination", "Ten dated ReaLearn slide presentations", "Iterative advisor/lab feedback and progress trace"],
        ],
        [2050, 4300, 3010],
        font_size=8.45,
        column_alignments=[WD_ALIGN_PARAGRAPH.LEFT] * 3,
    )

    add_heading(doc, "3.2 Technical results", 2)
    add_body(
        doc,
        "The ontology result is a smaller, clearer, and reviewer-aligned v9.1 release that passes the declared logical, query, mapping, completeness, and noise checks. The decisive achievement is not the size of the graph but the relationship between requirements and evidence: "
        "each competency question has an executable interface; each scenario template has declared control and evidence relations; and the engine can export the resulting constraints without allowing LLM text to alter the normative graph."
    )
    add_body(
        doc,
        "The engine result is a reproducible comparison architecture for four knowledge-delivery conditions. It demonstrates that a typed ontology packet and ontology verbalization are different treatments and should not be collapsed into one “ontology RAG” label. "
        "The Graph-Walk v1 follow-up further shows why treatment exposure and content retention must be audited rather than inferred from a condition name."
    )
    add_body(
        doc,
        "The evaluation result is methodological separation. Ontology correctness, scenario conformance, mechanism exposure, diversity, source traceability, human approval, and learner outcomes are different constructs. The internship documents what each metric can and cannot support, "
        "which is directly aligned with ReaLearn’s focus on combining knowledge representation, machine learning, and systematic evaluation for trustworthy AI [1-3]."
    )

    add_heading(doc, "3.3 Research and professional learning outcomes", 2)
    for item in [
        "Ontology engineering: competency-question-driven scope, OWL/RDF modeling, properties and individuals, versioning, and reviewer-safe boundary statements.",
        "Knowledge representation and reasoning: HermiT consistency checks, SPARQL query design, positive/negative tests, provenance modeling, and bounded completeness.",
        "GenAI system design: separating normative knowledge, retrieved context, prompts, structured outputs, validators, and scenario-pool admission.",
        "Experimental design: matched case IDs, control-factor balance, frozen conditions, local open-weight models, and distinction between pipeline and causal ablation studies.",
        "Evaluation literacy: standard versus project-specific metrics, ceiling effects, treatment fidelity, retrieval exposure, diversity diagnostics, composite-index sensitivity, and human-evaluation requirements.",
        "Research communication: weekly lab presentations, reviewer-response change logs, technical documentation, an LNCS/LNAI manuscript, and evidence-based limitation writing.",
        "Trustworthy-AI practice: traceability, auditability, reproducibility, ethics, privacy, licensing, and explicit refusal to equate fluent or technically valid output with educational effectiveness.",
    ]:
        add_bullet(doc, item)

    add_heading(doc, "3.4 Paper result", 2)
    add_rich(
        doc,
        [
            ("Final manuscript title: ", {"bold": True, "color": NAVY}),
            ("Ontology-Guided Scenario Control Generation for GenAI in Cybersecurity Serious Game", {"italic": True}),
        ],
        align=WD_ALIGN_PARAGRAPH.LEFT,
    )
    add_body(
        doc,
        "The latest local paper bundle identifies Chanphot Wongtaweesup, Teeradaj Racharak, Watanee Jearanaiwongkul, Chutiporn Anutariya, and Frederic Andres as authors and targets the IJCKG 2026 Education Track. "
        "The manuscript presents PSQ-SCO, four executable competency questions, two ontology-delivery mechanisms, a matched four-condition/three-model comparison, and an instructional deployment workflow. It is formatted for Springer LNCS/LNAI and includes a citation-complete BibTeX file and targeted evaluation repairs [P20]."
    )
    add_body(
        doc,
        "The paper’s strongest defensible conclusion is that PSQ-SCO provides explicit, typed, and auditable control when baseline prompting already satisfies a constrained schema. Structured ontology leads the secondary mechanism-conditioned and diversity diagnostics, but the common automatic gates reach ceiling. "
        "Accordingly, the paper establishes control and auditability rather than superior human-rated quality or learning gains."
    )
    add_callout(
        doc,
        "Publication status",
        "A submission-ready manuscript package is present. No submission receipt, paper ID, acceptance notice, or camera-ready evidence was found in the supplied folders. The official IJCKG 2026 Research/In-Use/Education full-paper deadline was 24 July 2026. "
        "The internship handover should record the actual submission status and, if needed, identify an alternative dissemination route such as the poster/demo track or a later venue [22].",
        fill=LIGHT_GOLD,
        border=GOLD,
    )

    add_heading(doc, "3.5 Overall internship contribution", 2)
    add_body(
        doc,
        "The internship contributed an end-to-end trustworthy-AI research workflow: formal requirements were encoded in an ontology, queried into engine-ready controls, tested against positive and negative cases, carried through a local GenAI pipeline, and evaluated with explicit claim boundaries. "
        "This provides PersonaShield Quest with a maintainable scenario-control layer and provides ReaLearn with a concrete case study connecting knowledge representation, machine learning, explainability, and evaluation."
    )
    add_body(
        doc,
        "For Chanphot Wongtaweesup’s Ph.D. research, the placement clarified how the ontology component should relate to the broader affective-adaptive framework. PSQ-SCO can be retained as a bounded pre-generation control layer, while emotion adaptation, pedagogy, human expert review, and learner-effect studies remain separate modules and research questions. "
        "This separation makes future thesis claims more precise and reduces the risk that one ontology is asked to represent every concern."
    )

    add_heading(doc, "3.6 Recommended next work", 2)
    recommended_next_work = [
        "Reconcile the paper’s main-study tables with the separate Graph-Walk v1 supplement and state clearly whether the supplement is included, excluded, or reported as future work.",
        "Freeze one clean experimental environment: model versions, prompts, decoding settings, seeds where supported, Chroma version, embedding artifact/hash, index fingerprint, hardware, and one timing schema.",
        "Preserve raw model text, parsed output, repaired output, replacement output, validation failures, and final accepted object as distinct auditable stages.",
        "Guarantee or stratify external-retrieval exposure and export query, rank, score, source ID, and claim-source mapping.",
        "Run repeated generations per cell and analyze within-cell variance before making causal method comparisons.",
        "Complete a blinded expert study with cybersecurity and educational-technology raters, a predefined rubric, agreement statistics, and adjudication.",
        "Conduct a learner study measuring decision quality, transfer, retention, engagement, and the affective-adaptive components outside PSQ-SCO.",
        "Expand beyond English-dominant email data to balanced Thai/English, SMS, voice, multi-channel, organizational, and culturally varied cases.",
        "Complete source-license, privacy, personal-data, dual-use, and release-readiness audits before public dataset or scenario release.",
        "Create a versioned handover archive containing the final ontology, queries, reports, engine configuration, paper bundle, checksums, and a single authoritative README.",
    ]
    for number, item in enumerate(recommended_next_work, start=1):
        add_manual_numbered(doc, number, item)

    add_heading(doc, "3.7 Conclusion", 2)
    add_body(
        doc,
        "The internship achieved its revised objective. It produced a validated scenario-control ontology, operational engine integration, a matched generation/evaluation study, and a scholarly manuscript. PSQ-SCO v9.1 is logically consistent and functionally complete for the declared CQ1-CQ4 test scope. "
        "Its strongest contribution is explicit control and auditability across ontology, generation, and evaluation. The automatic experiment does not establish better learning or universally better scenarios, and the report preserves that limitation as part of the research result rather than treating it as a failure."
    )

    # References
    add_heading(doc, "References", 1, page_break=True)
    add_heading(doc, "External and academic references", 2)
    references = [
        (1, "ReaLearn (Trustworthy AI Lab). Home page: research group at Tohoku University focused on reasoning and learning for trustworthy AI. Accessed 26 July 2026.", "https://sites.google.com/view/racharak-lab"),
        (2, "Advanced Institute of So-Go-Chi (Convergence Knowledge) Informatics, Tohoku University. Home and research overview. Accessed 26 July 2026.", "https://www.aisogochi.tohoku.ac.jp/en/home-en"),
        (3, "Racharak, T. Professional profile and ReaLearn description. Accessed 26 July 2026.", "https://sites.google.com/view/teeradaj"),
        (4, "Noy, N. F., & McGuinness, D. L. (2001). Ontology Development 101: A Guide to Creating Your First Ontology. Stanford Knowledge Systems Laboratory.", "https://protege.stanford.edu/publications/ontology_development/ontology101.pdf"),
        (5, "W3C. (2012). OWL 2 Web Ontology Language Document Overview, Second Edition.", "https://www.w3.org/TR/owl2-overview/"),
        (6, "W3C. (2013). SPARQL 1.1 Query Language.", "https://www.w3.org/TR/sparql11-query/"),
        (7, "W3C. (2017). Shapes Constraint Language (SHACL).", "https://www.w3.org/TR/shacl/"),
        (8, "W3C. (2013). PROV-O: The PROV Ontology.", "https://www.w3.org/TR/prov-o/"),
        (9, "Glimm, B., Horrocks, I., Motik, B., Stoilos, G., & Wang, Z. (2014). HermiT: An OWL 2 Reasoner. Journal of Automated Reasoning, 53, 245-269.", "https://doi.org/10.1007/s10817-014-9305-1"),
        (10, "Keet, C. M., & Lawrynowicz, A. (2016). Test-Driven Development of Ontologies. ESWC 2016, LNCS 9678, 642-657.", "https://doi.org/10.1007/978-3-319-34129-3_39"),
        (11, "Lewis, P., Perez, E., Piktus, A., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS 33.", "https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html"),
        (12, "Hogan, A., Blomqvist, E., Cochez, M., et al. (2021). Knowledge Graphs. ACM Computing Surveys, 54(4), Article 71.", "https://doi.org/10.1145/3447772"),
        (13, "Pan, S., Luo, L., Wang, Y., et al. (2024). Unifying Large Language Models and Knowledge Graphs: A Roadmap. IEEE TKDE, 36(7), 3580-3599.", "https://doi.org/10.1109/TKDE.2024.3352100"),
        (14, "Arachchilage, N. A. G., & Love, S. (2013). A Game Design Framework for Avoiding Phishing Attacks. Computers in Human Behavior, 29(3), 706-714.", "https://doi.org/10.1016/j.chb.2012.12.018"),
        (15, "Clark, D. B., Tanner-Smith, E. E., & Killingsworth, S. S. (2016). Digital Games, Design, and Learning: A Systematic Review and Meta-Analysis. Review of Educational Research, 86(1), 79-122.", "https://doi.org/10.3102/0034654315582065"),
        (16, "MITRE. ATT&CK Phishing Techniques T1566/T1566.004 and CAPEC attack patterns. Accessed during the project in 2026.", "https://attack.mitre.org/techniques/T1566/"),
        (17, "Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings Using Siamese BERT-Networks. EMNLP-IJCNLP, 3982-3992.", "https://doi.org/10.18653/v1/D19-1410"),
        (18, "Tevet, G., & Berant, J. (2021). Evaluating the Evaluation of Diversity in Natural Language Generation. EACL, 326-346.", "https://doi.org/10.18653/v1/2021.eacl-main.25"),
        (19, "Cochran, W. G. (1950). The Comparison of Percentages in Matched Samples. Biometrika, 37(3/4), 256-266.", "https://doi.org/10.2307/2332378"),
        (20, "Greco, S., Ishizaka, A., Tasiou, M., & Torrisi, G. (2019). On the Methodological Framework of Composite Indices. Social Indicators Research, 141, 61-94.", "https://doi.org/10.1007/s11205-017-1832-9"),
        (21, "Pardo, A., & Siemens, G. (2014). Ethical and Privacy Principles for Learning Analytics. British Journal of Educational Technology, 45(3), 438-450.", "https://doi.org/10.1111/bjet.12152"),
        (22, "IJCKG 2026. Call for Papers and important dates. Education Track full papers use Springer LNCS/LNAI; extended full-paper deadline 24 July 2026. Accessed 26 July 2026.", "https://ijckg2026.aiat.or.th/call-for-papers"),
    ]
    for number, text, url in references:
        add_reference(doc, number, text, url)

    add_heading(doc, "Project evidence sources", 2)
    project_sources = [
        ("P1", "Chanphot Presentation 15 May 2026", str(WORKSPACE / "Chanphot Presentation 15_05_2026.pdf"), "Initial research context, ODEACT concept, ontology as vocabulary constraint layer, and early timeline."),
        ("P2", "Chanphot Presentation ReaLearn 20 May 2026", str(WORKSPACE / "Chanphot Presentation Realearn 20_05_2026.pdf"), "Ontology purpose, offline validation/runtime selection, and early related work."),
        ("P3", "Chanphot Presentation ReaLearn 28 May 2026", str(WORKSPACE / "Chanphot Presentation Realearn 28_05_2026.pdf"), "Seven-step method, scope, initial CQs, reuse plan, source inventory."),
        ("P4", "Chanphot Presentation ReaLearn 8 June 2026", str(WORKSPACE / "Chanphot Presentation Realearn 08_06_2026.pdf"), "KG/RAG literature, refined CQ contracts, sources, class/property design."),
        ("P5", "Chanphot Presentation ReaLearn 15 June 2026", str(WORKSPACE / "Chanphot Presentation Realearn 15_06_2026 (1).pdf"), "OWL/KG architecture, mappings, 120-case protocol, IJCKG plan."),
        ("P6", "Chanphot Presentation ReaLearn 23 June 2026", str(WORKSPACE / "Chanphot Presentation Realearn 23_06_2026 (2).pdf"), "Executable CQ queries and observed rows; paper abstract and milestones."),
        ("P7", "Chanphot Presentation ReaLearn 1 July 2026", str(WORKSPACE / "Chanphot Presentation Realearn 01_07_2026.pdf"), "Reviewer feedback, FOL, scope separation, validation and evaluation plan."),
        ("P8", "Chanphot Presentation ReaLearn 6 July 2026", str(WORKSPACE / "_Chanphot Presentation Realearn 06_07_2026 (1).pdf"), "Early 120-case three-layer evaluation results and limitations."),
        ("P9", "Chanphot Presentation ReaLearn 14 July 2026", str(WORKSPACE / "Chanphot Presentation Realearn 14 _07_2026 (1).pdf"), "Four modes, construct definitions, common versus operational metrics."),
        ("P10", "Chanphot Presentation ReaLearn 23 July 2026", str(WORKSPACE / "Chanphot Presentation Realearn 23_07_2026.pdf"), "Final paper-safe conclusions, three layers, limitations, ethics, and future work."),
        ("P11", "PSQ-SCO v9.1 release validation report", r"ontology/outputs/v9_1/release-validation-report.json", "Authoritative release counts, CQ, reasoner, completeness, error, and warning status."),
        ("P12", "PSQ-SCO v9 reviewer-aligned change log", r"ontology/docs/PSQ_SCO_v9_REVIEWER_ALIGNED_CHANGE_LOG.md", "Rename, CQ3 quality-control shift, rules, packets, and reasoning decisions."),
        ("P13", "PSQ-SCO v9.1 no-pedagogy correction log", r"ontology/docs/PSQ_SCO_v9_1_NO_PEDAGOGY_CHANGE_LOG.md", "Final scope correction and removed resources/properties/triples."),
        ("P14", "PSQ-SCO v9.1 KG completeness and error analysis", r"ontology/docs/PSQ_SCO_v9_1_KG_COMPLETENESS_AND_ERROR_ANALYSIS.md", "Bounded completeness definition and graph-noise evidence."),
        ("P15", "PSQ-SCO ontology validation analysis", r"ontology/docs/PSQ_SCO_Ontology_Validation_Analysis_Report.md", "Compact release validation summary."),
        ("P16", "PSQ-SCO ontology framework diagram", str(FIG_FRAMEWORK), "Architecture used in Figure 1."),
        ("P17", "Paper 120 matched-case design figure", str(FIG_CASES), "Experimental design used in Figure 2."),
        ("P18", "Four-condition GenAI engine monograph", r"genai_engine/docs/PERSONASHIELD_QUEST_FOUR_CONDITION_GENAI_ENGINE_COMPLETE_RESEARCH_MONOGRAPH.md", "Implementation-grounded engine, evaluation, metric, and limitation account."),
        ("P19", "Three-layer evaluation technical documentation", r"genai_engine/docs/THREE_LAYER_EVALUATION_TECHNICAL_DOCUMENTATION.md", "Metric definitions and output contracts."),
        ("P20", "Latest targeted IJCKG manuscript package", r"genai_engine/output/targeted_psq_sco_evaluation_repair/20260723_200851/overleaf/main.tex", "Final title, paper argument, common and mechanism-specific results, limitations, and conclusion."),
        ("P21", "Graph-Walk v1 separate comparative evaluation", r"genai_engine/output/three_layer_eval_graph_walk_v1_comparison/20260723_134114/PSQ_SCO_GRAPH_WALK_V1_SEPARATE_COMPARATIVE_EVALUATION.md", "Supplementary treatment-exposure, generation-integrity, and diversity evidence."),
    ]
    for code, title, path, role in project_sources:
        add_project_source(doc, code, title, path, role)

    # Appendices
    add_heading(doc, "Appendix A. Dated Slide-Deck Evidence", 1, page_break=True)
    add_body(
        doc,
        "The ten dated ReaLearn slide exports form the contemporaneous narrative of the internship. The table records how each presentation changed the research state rather than treating repeated introductory slides as new work."
    )
    add_table(
        doc,
        ["Date", "Deck", "Principal evidence used in this report"],
        [
            ["15 May", "P1", "Initial ODEACT internship objective; ontology as vocabulary/constraint layer; May-July plan"],
            ["20 May", "P2", "Ontology as domain and knowledge-control layer; offline generation/validation and runtime selection"],
            ["28 May", "P3", "Literature limitations; seven-step method; domain scope; CQ1-CQ5; Thai/English sources"],
            ["8 Jun", "P4", "KG/RAG trust literature; refined CQ inputs/outputs/tests; class/property/constraint plan"],
            ["15 Jun", "P5", "OWL/KG implementation, system architecture, bindings, evaluation protocol, IJCKG plan"],
            ["23 Jun", "P6", "Full SPARQL CQ demonstrations and expected result rows; initial paper abstract"],
            ["1 Jul", "P7", "Advisor/reviewer feedback; separation of scope; CQ3 quality-control revision; FOL and validation"],
            ["6 Jul", "P8", "Early 120-case results; three evaluation layers; initial conformance and limitations"],
            ["14 Jul", "P9", "Four modes; metric construct boundaries; common vs composite results; paper-safe wording"],
            ["23 Jul", "P10", "Final common-gate ceiling; auditability contribution; ethics, limitations, and next evidence"],
        ],
        [1100, 720, 7540],
        font_size=8.6,
        column_alignments=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT],
    )

    add_heading(doc, "Appendix B. Project Artifact Inventory", 1, page_break=True)
    add_heading(doc, "B.1 Ontology repository", 2)
    for item in [
        r"Final ontology: ontology/ontology/personashield-psq-sco-v9.1.owl",
        r"Knowledge-graph exports: ontology/knowledge_graph/v9_1",
        r"Competency queries: ontology/queries/v9_1",
        r"Validation evidence: ontology/outputs/v9_1",
        r"Ontology bindings and schemas: ontology/data/ontology_bindings",
        r"Change logs and guides: ontology/docs",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "B.2 GenAI engine repository", 2)
    for item in [
        r"Four-mode generation package: genai_engine/psq_sco_generation",
        r"Scenario generation entry points: generate_scenarios_prompt_only.py and generate_scenarios_sco.py",
        r"Three-layer evaluator: genai_engine/three_layer_evaluation",
        r"Main July 18 evaluation: genai_engine/output/three_layer_eval_live_recovered_methodology_v5_final/20260718_065435",
        r"Graph-Walk v1 experiment: genai_engine/output/experiments/paper120_mode4_graph_walk_v1/20260723_030518",
        r"Graph-Walk v1 evaluation: genai_engine/output/three_layer_eval_graph_walk_v1_comparison/20260723_134114",
        r"Latest targeted manuscript repair: genai_engine/output/targeted_psq_sco_evaluation_repair/20260723_200851",
        "Paper and technical documentation: genai_engine/paper and genai_engine/docs",
    ]:
        add_bullet(doc, item)

    add_heading(doc, "Appendix C. Validation and Evaluation Evidence Matrix", 1, page_break=True)
    add_table(
        doc,
        ["Claim", "Evidence artifact", "Supported conclusion", "Not supported"],
        [
            ["Ontology consistency", "HermiT report; release-validation report", "Consistent; zero unsatisfiable classes under tested reasoner", "Universal correctness or complete cyber coverage"],
            ["CQ function", "4 SELECT queries; 8 ASK tests", "Expected and prohibited graph patterns execute", "Quality of generated prose"],
            ["Bounded completeness", "4,362 checks; KG completeness report", "Complete for six templates and CQ1-CQ4 contract", "Universal ontology completeness"],
            ["Runtime compatibility", "1,440 mapping tests", "Required controls survive mapping", "Human acceptability"],
            ["Common scenario gates", "July 23 manuscript Layer 2", "Finalized records meet frozen executable controls", "Realism, pedagogy, source faithfulness"],
            ["Mechanism diagnostics", "Method summary and OCIeq sensitivity", "Structured packet exposes strong typed/provenance mechanisms", "General quality ranking"],
            ["Diversity", "Embedding diversity, Self-BLEU, title/choice repetition", "Relative repetition differences in this dataset", "Correctness or learner benefit"],
            ["Graph-walk treatment", "Graph-walk exposure audit", "360/360 assigned prompts received the walk document", "Optimal walk or model use of every fact"],
            ["Generation integrity", "Repair and retention audit", "Final records may differ from live-model content", "Pure model-only performance"],
            ["Paper readiness", "LaTeX/BibTeX bundle and change manifest", "Complete manuscript package exists", "Submission or acceptance"],
        ],
        [1850, 2650, 2780, 2080],
        font_size=8.25,
        column_alignments=[WD_ALIGN_PARAGRAPH.LEFT] * 4,
    )

    add_heading(doc, "Appendix D. Close-out Checklist to 6 August 2026", 1, page_break=True)
    checklist_rows = [
        ["Confirm IJCKG submission status and record paper ID/receipt", "Open", "No submission evidence found in supplied folders"],
        ["Choose authoritative manuscript and evaluation version", "Open", "Main study and Graph-Walk supplement must be related explicitly"],
        ["Re-run structural tests on final archive", "Planned", "Preserve ontology, query, mapping, and document QA logs"],
        ["Create checksums and one release manifest", "Planned", "Include ontology, engine config, evaluation inputs/outputs, paper"],
        ["Record licenses and redistribution restrictions", "Open", "Required before public release of corpus-derived content"],
        ["Document personal-data and dual-use review", "Open", "Required before deployment or learner study"],
        ["Deliver report and technical handover", "In progress", "This report is the narrative component"],
        ["Define next experiment owner and timeline", "Planned", "Repeated runs, human review, learner study, multilingual balance"],
        ["Archive final ReaLearn presentation and internship summary", "Planned", "Close the weekly evidence trail on 6 August"],
    ]
    add_table(
        doc,
        ["Close-out action", "Status", "Evidence or note"],
        checklist_rows,
        [4200, 1300, 3860],
        font_size=8.8,
        column_alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT],
    )
    add_callout(
        doc,
        "Final handover principle",
        "Preserve one authoritative release manifest that separates ontology evidence, generation evidence, evaluation evidence, manuscript evidence, and work still planned. "
        "This keeps the internship outcome reproducible without overstating completion.",
        fill=LIGHT_GREEN,
        border=TEAL,
    )

    # Ask Word/LibreOffice to update fields such as page numbers on open.
    settings = doc.settings._element
    update_fields = settings.find(qn("w:updateFields"))
    if update_fields is None:
        update_fields = OxmlElement("w:updateFields")
        settings.append(update_fields)
    update_fields.set(qn("w:val"), "true")

    doc.save(FINAL)
    print(FINAL)


if __name__ == "__main__":
    build_document()
