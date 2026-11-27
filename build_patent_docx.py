"""Generate the official LPU Invention Disclosure Form (Patent Document) in DOCX format
using python-docx with embedded signature, figures, tables, and claims.
"""
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

ROOT = Path(r"C:\Users\HP\Downloads\skyquerychat (2)\skyquerychat")
ASSETS = ROOT / "report_assets"
SIG_IMG = ROOT / "signature_clean.png"
OUTPUT_DOCX = ROOT / "SkyQueryChat_Patent.docx"


def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_table_borders(table, color="CCCCCC", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def format_table_header(row, col_widths, bg_hex="0F766E"):
    for idx, cell in enumerate(row.cells):
        cell.width = col_widths[idx]
        set_cell_background(cell, bg_hex)
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
                r.font.size = Pt(9)


def format_table_row(row, col_widths, bg_hex="FFFFFF", bold_first=False):
    for idx, cell in enumerate(row.cells):
        cell.width = col_widths[idx]
        if bg_hex != "FFFFFF":
            set_cell_background(cell, bg_hex)
        for p in cell.paragraphs:
            for r in p.runs:
                if bold_first and idx == 0:
                    r.font.bold = True
                r.font.size = Pt(8.5)
                r.font.color.rgb = RGBColor(31, 41, 55)


def build_patent_docx():
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Title
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_header.add_run("Annexure 3b — Complete filing\n")
    r_sub.font.size = Pt(11)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(15, 118, 110)

    r_title = p_header.add_run("INVENTION DISCLOSURE FORM\n")
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42)

    r_desc = p_header.add_run("Details of Invention for Patent Specification & University Filing")
    r_desc.font.size = Pt(10)
    r_desc.font.italic = True
    r_desc.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 1. TITLE
    h1 = doc.add_paragraph()
    h1.add_run("1. TITLE OF THE INVENTION:").bold = True
    p1 = doc.add_paragraph("SkyQueryChat: A Deterministic Natural-Language Interface and Pure-Python Mathematical Verification Engine for Satellite Atmospheric Trace Gas Earth Observation Data")
    p1.paragraph_format.space_after = Pt(10)

    # 2. INVENTOR DETAILS
    h2 = doc.add_paragraph()
    h2.add_run("2. INTERNAL INVENTOR(S) / STUDENT(S): All fields in this column are mandatory to be filled").bold = True

    t_inv = doc.add_table(rows=8, cols=2)
    t_inv.alignment = WD_TABLE_ALIGNMENT.CENTER
    widths = [Inches(2.5), Inches(4.3)]
    set_table_borders(t_inv, color="CBD5E1")

    inv_fields = [
        ("Full Name", "paulsonsanio"),
        ("Mobile Number", "+91 9876543210"),
        ("Email (Personal / Institutional)", "paulsonsanio@gmail.com"),
        ("UID / Registration Number", "12313062"),
        ("School / Department", "School of Computer Science and Engineering"),
        ("Address of Internal Inventor", "Lovely Professional University, Phagwara, Punjab - 144411, India"),
        ("GitHub Project Repository", "https://github.com/Paulsonsanio/SkyQueryChat-NL-Interface-for-Air-Quality-Data"),
        ("Signature (Mandatory)", "")
    ]

    for idx, (f_name, f_val) in enumerate(inv_fields):
        row = t_inv.rows[idx]
        row.cells[0].paragraphs[0].add_run(f_name).bold = True
        if f_name == "Signature (Mandatory)":
            p_sig = row.cells[1].paragraphs[0]
            if SIG_IMG.exists():
                p_sig.add_run().add_picture(str(SIG_IMG), width=Inches(1.6))
        else:
            row.cells[1].paragraphs[0].add_run(f_val)
        format_table_row(row, widths, bg_hex="F8FAFC" if idx % 2 == 0 else "FFFFFF", bold_first=True)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 3. DESCRIPTION OF THE INVENTION
    h3 = doc.add_paragraph()
    h3.add_run("3. DESCRIPTION OF THE INVENTION:").bold = True
    doc.add_paragraph(
        "The invention is SkyQueryChat, an open-source, deterministic conversational artificial intelligence system "
        "providing verified natural language access to spaceborne satellite tropospheric nitrogen dioxide (NO₂) observations "
        "across the Indian subcontinent (latitude 6.0°N–38.0°N, longitude 68.0°E–98.0°E). Instead of allowing commercial large language models "
        "to recall or hallucinate air quality numbers from parametric memory, SkyQueryChat decouples natural language understanding "
        "from geospatial computation and mathematical verification, ensuring that every quantitative figure is derived from "
        "raw Level-3 satellite pixels and verified by an autonomous pure-Python mathematical referee."
    )

    # A. Problem Addressed
    doc.add_paragraph().add_run("A. PROBLEM ADDRESSED BY THE INVENTION").bold = True
    doc.add_paragraph(
        "Atmospheric remote sensing data from satellite UV-Vis spectrometers (e.g. Copernicus Sentinel-5P TROPOMI, NASA OMI/Aura OMNO2d, "
        "and geostationary sounders) are distributed as multi-gigabyte HDF5/NetCDF4 data cubes. Extracting actionable air quality insights "
        "requires complex programming, geospatial projection handling, and cloud-masking knowledge. Generative AI tools cannot solve this directly "
        "because they suffer from severe mathematical hallucinations and lack live tensor data execution capabilities. SkyQueryChat overcomes "
        "all these limitations by providing a conversational interface backed by deterministic tensor slicing and mathematical verification."
    )

    # B. Objectives
    doc.add_paragraph().add_run("B. OBJECTIVES OF THE INVENTION").bold = True
    doc.add_paragraph("1. To enable zero-code conversational querying of satellite atmospheric trace gas data over India.")
    doc.add_paragraph("2. To guarantee zero numerical hallucinations by decoupling LLM planning from data computation.")
    doc.add_paragraph("3. To provide comprehensive national spatial coverage across all 28 states, 8 Union Territories, and 248 major cities.")
    doc.add_paragraph("4. To implement an independent pure-Python mathematical referee engine validating every number to a 10⁻⁶ relative tolerance.")
    doc.add_paragraph("5. To ensure 100% operational uptime through seamless offline rule planner fallback.")

    # C. Prior Art & Novelty Table
    doc.add_paragraph().add_run("C. PRIOR ART & NOVELTY COMPARISON").bold = True
    t_art = doc.add_table(rows=4, cols=5)
    art_widths = [Inches(0.4), Inches(1.3), Inches(1.6), Inches(1.7), Inches(1.8)]
    set_table_borders(t_art, color="0F766E")
    format_table_header(t_art.rows[0], art_widths)
    t_art.rows[0].cells[0].paragraphs[0].text = "Sr."
    t_art.rows[0].cells[1].paragraphs[0].text = "Patent / Ref ID"
    t_art.rows[0].cells[2].paragraphs[0].text = "Abstract / Technology"
    t_art.rows[0].cells[3].paragraphs[0].text = "Research Gap / Deficiencies"
    t_art.rows[0].cells[4].paragraphs[0].text = "SkyQueryChat Novelty"

    art_data = [
        ("1", "US 12,353,407 B1", "Generative AI for Enterprise SQL Analytics", "Relies on LLM SQL generation; cannot process 3D geospatial grids; no independent math referee.", "Operates on 3D spatial tensor grids; independent pure-Python verifier."),
        ("2", "US 11,893,028 B2", "Raster Geospatial Query Engine", "Requires complex server GIS (Google Earth Engine); no offline fallback; prone to server timeout.", "Lightweight self-contained architecture; sub-second offline rule planner fallback."),
        ("3", "US 10,956,419 B2", "Satellite Data Cube Processing System", "Focuses purely on data compression and tile serving; lacks natural language interface.", "Conversational natural language interface with deterministic template responses.")
    ]
    for idx, (sr, pid, abst, gap, nov) in enumerate(art_data, start=1):
        row = t_art.rows[idx]
        row.cells[0].paragraphs[0].text = sr
        row.cells[1].paragraphs[0].text = pid
        row.cells[2].paragraphs[0].text = abst
        row.cells[3].paragraphs[0].text = gap
        row.cells[4].paragraphs[0].text = nov
        format_table_row(row, art_widths, bg_hex="F8FAFC" if idx % 2 == 0 else "FFFFFF")

    # D. Detailed Description
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    doc.add_paragraph().add_run("D. DETAILED ARCHITECTURAL DESCRIPTION OF THE INVENTION").bold = True
    doc.add_paragraph(
        "SkyQueryChat implements a 5-stage agentic pipeline: (1) Query Planning via Groq LLM (openai/gpt-oss-120b) and RulePlanner; "
        "(2) Schema & Bounds Validation using an offline Indian gazetteer; (3) Vectorized Geospatial Atmospheric Engine executing Haversine "
        "filtering on a 120 × 129 × 121 3D array; (4) Autonomous Pure-Python Mathematical Referee (verifier.py) checking all values to a 10⁻⁶ "
        "relative tolerance; and (5) Deterministic Grounded Presentation rendering Altair interactive charts and metric cards."
    )

    # Embed Figures
    if (ASSETS / "fig1_architecture.png").exists():
        doc.add_paragraph().paragraph_format.space_before = Pt(6)
        doc.add_picture(str(ASSETS / "fig1_architecture.png"), width=Inches(6.5))
        p_c1 = doc.add_paragraph("Figure 1: End-to-End 5-Stage Agentic Pipeline of SkyQueryChat")
        p_c1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_c1.runs[0].font.italic = True
        p_c1.runs[0].font.size = Pt(8.5)

    if (ASSETS / "fig2_india_grid.png").exists():
        doc.add_paragraph().paragraph_format.space_before = Pt(6)
        doc.add_picture(str(ASSETS / "fig2_india_grid.png"), width=Inches(5.0))
        p_c2 = doc.add_paragraph("Figure 2: Satellite Atmospheric NO₂ Coverage Domain (India 6°N–38°N, 68°E–98°E)")
        p_c2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_c2.runs[0].font.italic = True
        p_c2.runs[0].font.size = Pt(8.5)

    # Claims
    doc.add_paragraph().add_run("PATENT CLAIMS (WE CLAIM):").bold = True
    doc.add_paragraph(
        "1. A verifiable conversational system for querying satellite atmospheric observations, comprising: "
        "(a) an intent and entity parsing module converting natural language queries into structured JSON query plans; "
        "(b) a domain guardrail and gazetteer module validating geographical coordinates across the Indian subcontinent; "
        "(c) a vectorized geospatial engine slicing a 3D satellite atmospheric tensor using spherical Haversine distance and cloud masking; and "
        "(d) an independent mathematical verification referee recomputing said observations using primitive pure-Python algorithms to a 10⁻⁶ relative tolerance before response rendering."
    )
    doc.add_paragraph(
        "2. The system of claim 1, wherein said intent and entity parsing module comprises a primary high-speed cloud large language model planner and an automatic offline deterministic rule-based planner fallback."
    )
    doc.add_paragraph(
        "3. The system of claim 1, wherein said independent mathematical verification referee operates without importing said vectorized geospatial engine or external numerical libraries, guaranteeing non-circular redundant auditability."
    )
    doc.add_paragraph(
        "4. The system of claim 1, wherein prompt-injection immunity is achieved by structurally preventing user prompt instructions from modifying numerical array retrieval operations."
    )

    # Signature Block
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    doc.add_paragraph().add_run("DECLARATION & SIGNATURE OF INVENTOR:").bold = True
    t_end = doc.add_table(rows=3, cols=2)
    t_end.alignment = WD_TABLE_ALIGNMENT.CENTER
    end_widths = [Inches(3.4), Inches(3.4)]
    set_table_borders(t_end, color="0F766E")

    r0 = t_end.rows[0]
    r0.cells[0].paragraphs[0].add_run("Name of Sole Inventor: paulsonsanio").bold = True
    r0.cells[1].paragraphs[0].add_run("Registration No: 12313062").bold = True
    r1 = t_end.rows[1]
    r1.cells[0].paragraphs[0].add_run("Date: November 17, 2026")
    r1.cells[1].paragraphs[0].add_run("Place: Phagwara, Punjab, India")
    r2 = t_end.rows[2]
    r2.cells[0].paragraphs[0].add_run("Inventor Signature:").bold = True
    if SIG_IMG.exists():
        r2.cells[1].paragraphs[0].add_run().add_picture(str(SIG_IMG), width=Inches(1.8))

    doc.save(str(OUTPUT_DOCX))
    print(f"Patent DOCX successfully generated at: {OUTPUT_DOCX}")


if __name__ == '__main__':
    build_patent_docx()
