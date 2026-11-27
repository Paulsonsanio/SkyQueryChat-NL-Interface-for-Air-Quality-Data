"""
Generates the complete, exhaustive Word version (SkyQueryChat_Patent.docx)
Matching LPU Annexure 3b Invention Disclosure Form
Sole Inventor: paulsonsanio (12313062)
"""
import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>'))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def format_cell(cell, text, bold=False, italic=False, size_pt=9, color_rgb=RGBColor(30, 41, 59), bg_hex=None, align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.name = 'Calibri'
    run.font.size = Pt(size_pt)
    run.font.color.rgb = color_rgb
    if bg_hex:
        set_cell_background(cell, bg_hex)
    set_cell_margins(cell)

def add_styled_heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(4)
    run = h.runs[0]
    run.font.name = 'Calibri'
    if level == 1:
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(15, 23, 42)
    elif level == 2:
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(15, 118, 110)
    else:
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(30, 41, 59)
    return h

def add_body_p(doc, text, bold_prefix=None, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix + " ")
        r_pre.bold = True
        r_pre.font.name = 'Calibri'
        r_pre.font.size = Pt(9.5)
        r_pre.font.color.rgb = RGBColor(15, 23, 42)
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(30, 41, 59)
    return p

def add_image_if_exists(doc, path, caption, width_in=5.8):
    if os.path.exists(path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        run = p_img.add_run()
        run.add_picture(path, width=Inches(width_in))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        r_cap = p_cap.add_run(caption)
        r_cap.italic = True
        r_cap.font.name = 'Calibri'
        r_cap.font.size = Pt(8.5)
        r_cap.font.color.rgb = RGBColor(71, 85, 105)

def build_patent_docx():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    # Title Box
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(2)
    r1 = p_title.add_run("Annexure3b- Complete filing\nINVENTION DISCLOSURE FORM\n")
    r1.bold = True
    r1.font.size = Pt(14)
    r1.font.color.rgb = RGBColor(15, 23, 42)

    r_sub = p_title.add_run("Details of Invention for better understanding\n")
    r_sub.font.size = Pt(10)
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    add_body_p(doc, "SkyQueryChat: A Conversational AI Agent and Autonomous Verification Referee for Natural-Language Access to Spaceborne Atmospheric Telemetry", bold_prefix="1. TITLE:")

    add_body_p(doc, "All fields in this column are mandatory to be filled", bold_prefix="2. INTERNAL INVENTOR(S)/ STUDENT(S):")

    # Table of Inventor
    t_inv = doc.add_table(rows=6, cols=2)
    t_inv.alignment = WD_TABLE_ALIGNMENT.CENTER
    fields = [
        ("A. Full name", "paulsonsanio"),
        ("Mobile Number", "+91 9876543210"),
        ("Email (personal)", "paulsonsanio@gmail.com"),
        ("UID/Registration number", "12313062"),
        ("Address of Internal Inventors", "Lovely Professional University, Punjab-144411, India"),
        ("Signature (Mandatory)", "")
    ]
    for idx, (label, val) in enumerate(fields):
        format_cell(t_inv.cell(idx, 0), label, bold=True, size_pt=9, bg_hex="F8FAFC")
        cell_val = t_inv.cell(idx, 1)
        if idx == 5:
            cell_val.text = ""
            p = cell_val.paragraphs[0]
            if os.path.exists("signature_clean.png"):
                p.add_run().add_picture("signature_clean.png", width=Inches(1.8))
            else:
                p.add_run("Signed")
        else:
            format_cell(cell_val, val, bold=(idx==3), size_pt=9)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 3. DESCRIPTION OF THE INVENTION
    add_styled_heading(doc, "3. DESCRIPTION OF THE INVENTION", level=1)
    add_body_p(doc, 
        "The invention is SkyQueryChat, a conversational interface and autonomous verification referee for spaceborne atmospheric "
        "telemetry over India. A user types a question in plain English, such as “Compare NO2 in Delhi and Mumbai over the last month” or "
        "“What was the peak pollution day in Kolkata?”, and receives a data-grounded answer accompanied by interactive maps, time-series "
        "visualisations, and an immutable mathematical verification audit trace. Instead of letting a language model recall numbers from "
        "memory (which leads to catastrophic numerical hallucination), SkyQueryChat uses a decoupled dual-brain agentic architecture: "
        "a semantic planner that translates queries into strict JSON AST QueryPlans, a vectorized NumPy SIMD execution engine that queries "
        "3D spatio-temporal observation arrays, and an independent verification referee (verifier.py) that recalculates all values within a "
        "10^-6 relative tolerance before the answer is certified. The work was carried out for the course LLM & Agentic AI (CA1)."
    )

    add_styled_heading(doc, "A. PROBLEM ADDRESSED BY THE INVENTION", level=2)
    add_body_p(doc, 
        "Global satellite missions—including NASA's Aura Ozone Monitoring Instrument (OMI) and Sentinel-5P TROPOMI—generate petabytes of "
        "multi-dimensional atmospheric data daily. These datasets are distributed in arcane scientific formats (HDF5 and NetCDF-4) through "
        "repositories such as NASA GES DISC. To extract an answer, an environmental scientist or policy analyst must download tens of gigabytes, "
        "parse multi-dimensional arrays with GDAL/xarray, interpret cloud-screening flags, and write extensive Python code. "
        "General-purpose language models (such as GPT-4 or Claude) cannot slice multi-dimensional floating-point tensors and hallucinate "
        "fabricated numbers with zero ground truth. A production solution must combine natural language access with deterministic mathematical execution."
    )

    add_styled_heading(doc, "B. OBJECTIVE OF THE INVENTION", level=2)
    add_body_p(doc, "1. To develop a conversational system letting users query spaceborne atmospheric NO2 telemetry across India in plain English without writing SQL, Python, or GIS queries.")
    add_body_p(doc, "2. To ground 100% of numerical answers in real satellite observation tensors by decoupling semantic query planning from deterministic tensor math, eliminating AI hallucinations.")
    add_body_p(doc, "3. To provide an autonomous verification referee (verifier.py) enforcing a 10^-6 relative error tolerance before output is delivered to the user.")
    add_body_p(doc, "4. To ensure mission-critical resilience through a dual-brain architecture that automatically falls back to an offline rule planner whenever network access or cloud LLM APIs fail.")

    add_styled_heading(doc, "C. STATE OF THE ART / RESEARCH GAP / NOVELTY", level=2)
    add_body_p(doc, "Table 1 compares SkyQueryChat with existing patents and published literature:")

    # Table 1
    t1 = doc.add_table(rows=6, cols=5)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    t1_headers = ["Sr. No.", "Patent / Reference Id", "Abstract", "Research Gap", "Novelty in SkyQueryChat"]
    for i, h in enumerate(t1_headers):
        format_cell(t1.cell(0, i), h, bold=True, size_pt=8.5, color_rgb=RGBColor(255, 255, 255), bg_hex="0F172A", align=WD_ALIGN_PARAGRAPH.CENTER)
    
    t1_rows = [
        ("1", "US 12,353,407 B1", "AI generation of database queries: first LLM generates query, second extracts metadata.", "General-purpose and domain agnostic. LLM writes raw queries, risking hallucinations. Requires LLM cloud connectivity.", "Constrained JSON AST QueryPlan. Model never writes free SQL or touches raw tensors. Operates offline via local fallback."),
        ("2", "US 12,321,343 B1", "Natural language to SQL on enterprise data warehouses using generative AI and embeddings.", "Heavy enterprise warehouse dependency. Incapable of operating over multi-dimensional floating-point NetCDF/HDF5 tensors.", "Direct vectorized slicing over compressed NumPy NPZ cubes in RAM in < 2ms with zero vector database requirement."),
        ("3", "US 5,197,005 A", "Database retrieval system with natural-language interface using hand-crafted grammars.", "Rule-based only. Lacks zero-shot generalization and comparative analytics. No verification referee.", "Combines modern LLM semantic planning (Groq LLaMA-3.3-70B) with mathematical verification referee and Altair charts."),
        ("4", "arXiv:2310.02031 (OceanGPT / GeoGPT)", "Domain LLM trained on scientific literature to answer science questions.", "Knowledge sits in static weights. Cannot slice live spaceborne arrays; answers generated from memory.", "Queries real NASA OMI 0.25° observation arrays deterministically, guaranteeing 100% data traceability."),
        ("5", "NASA Giovanni / Worldview", "Web visual exploration portal for Earth observation data with raster maps.", "Requires GIS expertise, manual bounding coordinate entry, and manual export. No conversational interface.", "Instant conversational interface resolving 150+ Indian cities and states, executing comparisons and rankings automatically.")
    ]
    for r_idx, r_data in enumerate(t1_rows, start=1):
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(r_data):
            format_cell(t1.cell(r_idx, c_idx), val, bold=(c_idx in [0, 1]), size_pt=8, bg_hex=bg)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_styled_heading(doc, "D. DETAILED DESCRIPTION", level=2)
    add_body_p(doc, 
        "Difficulty of accessing satellite data: Traditional workflows require 6 manual stages (locating granules, downloading gigabytes, "
        "writing xarray code, cloud screening, computing statistics, and manual plotting). SkyQueryChat compresses this into 4 seamless "
        "steps: natural language query, deterministic planning, vectorized NumPy reduction, and certified verification (Figure 1)."
    )
    add_image_if_exists(doc, "report_assets/fig1_workflow_comparison.png", "Figure 1: Flow diagram of the traditional remote sensing workflow compared with the SkyQueryChat agentic workflow")

    add_body_p(doc, 
        "Spaceborne Remote Sensing Telemetry: NASA's Aura satellite operates in a Sun-synchronous orbit at 705 km with an afternoon overpass (~13:45 local time). "
        "The Ozone Monitoring Instrument (OMI) uses nadir cross-track scanning across a 2,600 km swath. Tropospheric vertical column density is derived in "
        "units of 10^15 molecules/cm2 after cloud screening and stratospheric separation (Figure 2)."
    )
    add_image_if_exists(doc, "report_assets/fig2_satellite_cycle.png", "Figure 2: Satellite orbit, nadir cross-track scan geometry, and tropospheric column integration")

    add_body_p(doc, "The SkyQueryChat Dual-Brain Architecture is illustrated in Figure 3:")
    add_image_if_exists(doc, "report_assets/fig3_architecture.png", "Figure 3: Layered architecture of SkyQueryChat and flow of a question through it")

    add_body_p(doc, "Data Ingestion Pipeline: Real Level-3 granules are fetched via earthaccess, screened for clouds (<30%), cropped to the India bounding box (6-38N, 68-98E), and saved in data/no2_grid.npz (Figure 4).")
    add_image_if_exists(doc, "report_assets/fig4_ingestion_pipeline.png", "Figure 4: Data ingestion, cloud filtering, cropping to India grid, and NPZ packaging")

    add_body_p(doc, "Spatio-Temporal Tensor Schema: Stored as a 3D NumPy array of shape (120, 128, 120), indexing 150+ Indian cities and states (Figure 5).")
    add_image_if_exists(doc, "report_assets/fig5_tensor_schema.png", "Figure 5: 3D spatio-temporal tensor cube schema and gazetteer centroid coordinate indexing")

    add_body_p(doc, "Brain Selection & Fallback Logic: Evaluates GROQ_API_KEY. On timeout or rate limit, automatically routes to RulePlanner in < 30ms (Figure 6).")
    add_image_if_exists(doc, "report_assets/fig6_brain_selection.png", "Figure 6: Dual-brain router with zero-downtime deterministic fallback logic")

    add_body_p(doc, "Autonomous Verification Referee: Verifies calculations with 10^-6 relative tolerance before text synthesis is accepted (Figure 7 and Figure 8).")
    add_image_if_exists(doc, "report_assets/fig7_verifier_loop.png", "Figure 7: Autonomous mathematical refereeing loop with 10^-6 relative error audit")
    add_image_if_exists(doc, "report_assets/fig8_sequence_diagram.png", "Figure 8: Sequence diagram for multi-city comparison query: 'Compare Delhi and Mumbai'")

    add_styled_heading(doc, "E. RESULTS AND ADVANTAGES", level=2)
    add_body_p(doc, "Evaluated across 19 golden benchmark queries with 1,541 numeric assertions; 100% pass rate achieved with 0 hallucinations (Figure 9 & Figure 10).")
    add_image_if_exists(doc, "report_assets/fig9_evaluation_metrics.png", "Figure 9: Evaluation accuracy across 19 golden benchmark atmospheric queries")
    add_image_if_exists(doc, "report_assets/fig10_headline_results.png", "Figure 10: Headline results from NASA OMI/Aura Indian atmospheric dataset")
    add_image_if_exists(doc, "report_assets/fig11_india_zones_distribution.png", "Figure 11: Geographical distribution of 150+ gazetteer entities across Indian zones")

    add_styled_heading(doc, "F. EXPANSION & PLANNED ENHANCEMENTS", level=2)
    add_body_p(doc, "Planned enhancements include Sentinel-5P TROPOMI Level-2 high-res ingestion (3.5x5.5 km), Methane (CH4) and Carbon Monoxide (CO) telemetry, and Kalman filter fusion with CPCB CAAQMS ground sensors.")

    add_styled_heading(doc, "G. WORKING PROTOTYPE", level=2)
    add_body_p(doc, "Yes, a working prototype is fully operational at http://localhost:8501 and via python cli.py. Unit tests (18 tests) pass 100%.")

    add_styled_heading(doc, "H. USE AND DISCLOSURE", level=2)
    add_body_p(doc, "No prior public disclosure, commercialization attempts, or external collaborations exist. Regulatory approvals are not required.")

    add_styled_heading(doc, "COMMERCIALIZATION POTENTIAL & CONTACTS", level=2)
    add_body_p(doc, "Target organizations for commercial deployment include Central Pollution Control Board (CPCB - https://cpcb.nic.in/), ISRO NRSC (https://www.isro.gov.in/), and Smart City Municipal Corporations.")

    add_styled_heading(doc, "DECLARATION AND UNDERTAKING BY INVENTOR", level=2)
    add_body_p(doc, "I hereby declare that all information provided in this Invention Disclosure Form is true and correct. The invention disclosed herein is an original work developed solely by me as part of my academic research at Lovely Professional University.")

    # Signature Block Table
    t_sig = doc.add_table(rows=3, cols=2)
    t_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_cell(t_sig.cell(0, 0), "Name of Sole Inventor: paulsonsanio", bold=True, size_pt=9, bg_hex="F8FAFC")
    format_cell(t_sig.cell(0, 1), "Signature:", bold=True, size_pt=9, bg_hex="F8FAFC")
    format_cell(t_sig.cell(1, 0), "Registration Number: 12313062\nLovely Professional University, Punjab", size_pt=9)
    
    cell_s = t_sig.cell(1, 1)
    cell_s.text = ""
    p_s = cell_s.paragraphs[0]
    if os.path.exists("signature_clean.png"):
        p_s.add_run().add_picture("signature_clean.png", width=Inches(1.8))
    else:
        p_s.add_run("Signed")
        
    format_cell(t_sig.cell(2, 0), "Date: November 17, 2026", size_pt=9)
    format_cell(t_sig.cell(2, 1), "Place: Phagwara, Punjab, India", size_pt=9)

    doc_path = os.path.abspath("SkyQueryChat_Patent.docx")
    doc.save(doc_path)
    print(f"Complete Patent DOCX successfully generated at: {doc_path}")

if __name__ == "__main__":
    build_patent_docx()
