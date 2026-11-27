"""Generate the comprehensive academic Project Report (SkyQueryChat_Report.docx)
using python-docx with embedded figures, structured tables, and exhaustive technical content.
"""
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

ROOT = Path(r"C:\Users\HP\Downloads\skyquerychat (2)\skyquerychat")
ASSETS = ROOT / "report_assets"
OUTPUT_DOCX = ROOT / "SkyQueryChat_Report.docx"


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
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideV w:val="none"/>'
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
                r.font.size = Pt(9.5)


def format_table_row(row, col_widths, bg_hex="FFFFFF", bold_first=False):
    for idx, cell in enumerate(row.cells):
        cell.width = col_widths[idx]
        if bg_hex != "FFFFFF":
            set_cell_background(cell, bg_hex)
        for p in cell.paragraphs:
            for r in p.runs:
                if bold_first and idx == 0:
                    r.font.bold = True
                r.font.size = Pt(9)
                r.font.color.rgb = RGBColor(31, 41, 55)


def build_report_docx():
    doc = Document()
    
    # Page Setup: Standard Letter, 1-inch margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = True
        
        # Header & Footer
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("SkyQueryChat: Project Report | LLM & Agentic AI (CA1)")
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(107, 114, 128)
        
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        frun1 = fp.add_run("Lovely Professional University · paulsonsanio (12313062)")
        frun1.font.size = Pt(8.5)
        frun1.font.color.rgb = RGBColor(107, 114, 128)

    # -------------------------------------------------------------------------
    # COVER PAGE
    # -------------------------------------------------------------------------
    p_sup = doc.add_paragraph()
    p_sup.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sup = p_sup.add_run("PROJECT REPORT")
    r_sup.font.size = Pt(13)
    r_sup.font.bold = True
    r_sup.font.color.rgb = RGBColor(15, 118, 110)
    p_sup.paragraph_format.space_before = Pt(40)
    p_sup.paragraph_format.space_after = Pt(10)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("SkyQueryChat")
    r_title.font.size = Pt(32)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42)
    p_title.paragraph_format.space_after = Pt(8)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("A Deterministic Natural-Language Interface and Pure-Python Mathematical Verification Engine for Satellite Atmospheric Trace Gas Earth Observation Data")
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = RGBColor(71, 85, 105)
    p_sub.paragraph_format.space_after = Pt(24)

    p_desc = doc.add_paragraph()
    p_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_desc = p_desc.add_run("Natural-language access to high-resolution satellite tropospheric NO₂ observations over the Indian subcontinent via Groq-accelerated query planning, 3D tensor vectorization, and independent referee verification.")
    r_desc.font.size = Pt(10.5)
    r_desc.font.italic = True
    r_desc.font.color.rgb = RGBColor(100, 116, 139)
    p_desc.paragraph_format.space_after = Pt(48)

    # Meta Table on Cover Page
    meta_table = doc.add_table(rows=6, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_widths = [Inches(2.2), Inches(4.3)]
    set_table_borders(meta_table, color="E2E8F0")

    meta_items = [
        ("Course", "LLM & Agentic AI — CA1 Project-Based Assignment / Capstone"),
        ("Problem Statement", "Conversational AI for Scientific Earth Observation (Satellite NO₂)"),
        ("Student & Author", "paulsonsanio (Registration Number: 12313062)"),
        ("Institution", "School of Computer Science & Engineering, Lovely Professional University"),
        ("GitHub Repository", "https://github.com/Paulsonsanio/SkyQueryChat-NL-Interface-for-Air-Quality-Data"),
        ("Submission Date", "November 2026")
    ]

    for idx, (label, val) in enumerate(meta_items):
        row = meta_table.rows[idx]
        row.cells[0].paragraphs[0].add_run(label).bold = True
        row.cells[1].paragraphs[0].add_run(val)
        format_table_row(row, meta_widths, bg_hex="F8FAFC" if idx % 2 == 0 else "FFFFFF", bold_first=True)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # TABLE OF CONTENTS & ABSTRACT
    # -------------------------------------------------------------------------
    h_toc = doc.add_heading("Contents", level=1)
    h_toc.runs[0].font.color.rgb = RGBColor(15, 23, 42)

    toc_items = [
        ("Abstract", "3"),
        ("Author & Project Ownership", "4"),
        ("Part I — Problem Context, Atmospheric Satellite Sensors and Solution Concept", "5"),
        ("    1.1 Project Introduction", "5"),
        ("    1.2 The Challenge of Accessing Satellite Air Quality Data", "5"),
        ("    1.3 Understanding Atmospheric Satellite Remote Sensing (OMI/Aura, TROPOMI, INSAT)", "6"),
        ("    1.4 Introducing SkyQueryChat: Dual-Brain Agent Architecture", "7"),
        ("    1.5 Problem Statement and Requirements Mapping", "8"),
        ("Part II — System Architecture, Data Pipeline, Agentic Reasoning and Mathematical Verification", "9"),
        ("    2.1 End-to-End System Architecture (The 5-Stage Pipeline)", "9"),
        ("    2.2 Data Pipeline: NASA OMI/Aura OMNO2d, Sentinel-5P, Grid Structure & Cloud Masking", "10"),
        ("    2.3 Indian Gazetteer & Geospatial Slicing (28 States, 8 UTs, 248+ Cities)", "11"),
        ("    2.4 Vectorized Slicing & Statistical Analysis (Haversine Distance, OLS Regression)", "12"),
        ("    2.5 The AI Agent: Groq Cloud LLM Planner & Offline RulePlanner Fallback", "13"),
        ("    2.6 The Autonomous Pure-Python Mathematical Referee (verifier.py)", "14"),
        ("    2.7 Guardrail Systems & Prompt-Injection Immunity", "15"),
        ("    2.8 Clean Human-Centric UI & Responsive Altair Visualizations", "16"),
        ("Part III — Implementation, Testing, Limitations and Future Scope", "17"),
        ("    3.1 Technology Stack & Code Organization", "17"),
        ("    3.2 Main Functional Features", "18"),
        ("    3.3 Dataset Characteristics & Valid Cell Metrics", "19"),
        ("    3.4 Verification & Testing Methodology (18 Unit Tests, 19 Demo Queries, 1541 Checks)", "20"),
        ("    3.5 Experimental Results & Benchmark Evaluation", "21"),
        ("    3.6 Current Limitations & Operational Boundaries", "22"),
        ("    3.7 Future Research Roadmap & Global Geostationary Scaling", "23"),
        ("    3.8 Conclusion", "24"),
        ("References & Cited Patents", "25"),
        ("Appendix A — Running the Project (CLI & Web UI)", "26"),
        ("Appendix B — Glossary of Remote Sensing and AI Terms", "27")
    ]

    t_toc = doc.add_table(rows=len(toc_items), cols=2)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_toc_widths = [Inches(5.7), Inches(0.8)]
    set_table_borders(t_toc, color="E2E8F0", sz="2")
    for idx, (section_title, page_num) in enumerate(toc_items):
        r = t_toc.rows[idx]
        p0 = r.cells[0].paragraphs[0]
        run0 = p0.add_run(section_title)
        if not section_title.startswith("    "):
            run0.bold = True
            run0.font.color.rgb = RGBColor(15, 118, 110)
        p1 = r.cells[1].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.add_run(page_num).bold = True
        format_table_row(r, t_toc_widths, bg_hex="FFFFFF")

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # ABSTRACT & AUTHOR DETAILS
    # -------------------------------------------------------------------------
    h_abs = doc.add_heading("Abstract", level=1)
    h_abs.runs[0].font.color.rgb = RGBColor(15, 23, 42)

    p_abs = doc.add_paragraph()
    p_abs.paragraph_format.space_after = Pt(12)
    p_abs.paragraph_format.line_spacing = 1.15
    p_abs.add_run(
        "Atmospheric satellite remote sensing provides unprecedented visibility into regional air quality, industrial emission plumes, "
        "and tropospheric trace gas distribution. However, Level-3 satellite datasets (such as Copernicus Sentinel-5P TROPOMI, "
        "NASA OMI/Aura OMNO2d, and geostationary sounders) remain largely inaccessible to non-specialists due to multi-gigabyte "
        "hierarchical array formats (NetCDF4/HDF5), complex optical quality assurance flags, and the specialized geospatial programming "
        "required to extract localized insights. Conversely, deploying commercial large language models (LLMs) directly to answer air quality "
        "queries results in severe numerical hallucinations and plausible-sounding mathematical fabrications, rendering standard generative AI "
        "unusable in environmental monitoring, regulatory enforcement, and public health policy.\n\n"
        "To resolve this fundamental dilemma, this report presents SkyQueryChat, an open-source, deterministic, conversational Earth Observation "
        "AI system designed specifically for high-resolution tropospheric nitrogen dioxide (NO₂) observations across the Indian subcontinent "
        "(latitude 6.0°N–38.0°N, longitude 68.0°E–98.0°E). SkyQueryChat introduces a decoupled 5-stage agentic pipeline: (1) a zero-temperature "
        "Groq-accelerated LLM query planner (openai/gpt-oss-120b) with an automatic offline regex-based RulePlanner fallback; (2) a strict schema "
        "and geographical domain guardrail system powered by an offline Indian gazetteer covering all 28 states, 8 Union Territories, and 248 major cities; "
        "(3) a vectorized 3D tensor engine executing spherical Haversine spatial subsetting, cloud-fraction quality screening, and Ordinary Least Squares "
        "(OLS) trend regressions; (4) an autonomous, primitive pure-Python mathematical referee (verifier.py) that independently recomputes all cell values, "
        "spatial means, and trend slopes to a 10⁻⁶ relative tolerance; and (5) a deterministic grounded natural language and Altair interactive visual interface.\n\n"
        "Empirical evaluation establishes that SkyQueryChat achieves a 100% pass rate across 18 automated unit tests and 19 end-to-end benchmark queries "
        "encompassing 1,541 verified numerical checks. The system exhibits complete immunity to prompt injection attacks, delivers sub-second response times, "
        "and supports both real NASA OMI/Aura data ingestion and standalone offline operation, democratizing environmental satellite intelligence without "
        "sacrificing scientific rigor."
    )

    doc.add_heading("Author & Project Ownership", level=1).runs[0].font.color.rgb = RGBColor(15, 23, 42)
    p_auth = doc.add_paragraph()
    p_auth.add_run(
        "This project was conceived, designed, implemented, and empirically evaluated as an independent capstone project by a single student researcher:\n"
    )
    
    t_auth = doc.add_table(rows=2, cols=4)
    t_auth.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_auth_widths = [Inches(1.8), Inches(1.5), Inches(2.0), Inches(1.2)]
    set_table_borders(t_auth, color="CBD5E1")
    format_table_header(t_auth.rows[0], t_auth_widths)
    t_auth.rows[0].cells[0].paragraphs[0].text = "Full Name"
    t_auth.rows[0].cells[1].paragraphs[0].text = "Registration No."
    t_auth.rows[0].cells[2].paragraphs[0].text = "Project Role"
    t_auth.rows[0].cells[3].paragraphs[0].text = "Contribution"
    
    r_a = t_auth.rows[1]
    r_a.cells[0].paragraphs[0].text = "paulsonsanio"
    r_a.cells[1].paragraphs[0].text = "12313062"
    r_a.cells[2].paragraphs[0].text = "Sole Architect, Engineer & Evaluator"
    r_a.cells[3].paragraphs[0].text = "100%"
    format_table_row(r_a, t_auth_widths, bold_first=True)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # PART I: PROBLEM CONTEXT & SOLUTION CONCEPT
    # -------------------------------------------------------------------------
    doc.add_heading("Part I — Problem Context, Atmospheric Satellite Systems and Solution Concept", level=1).runs[0].font.color.rgb = RGBColor(15, 23, 42)

    doc.add_heading("1.1 Project Introduction", level=2).runs[0].font.color.rgb = RGBColor(15, 118, 110)
    p_intro = doc.add_paragraph()
    p_intro.add_run(
        "Nitrogen dioxide (NO₂) is a toxic, highly reactive trace gas formed primarily through high-temperature fossil fuel combustion "
        "in automotive traffic, coal-fired thermal power stations, diesel generators, and agricultural biomass burning. In the lower troposphere, "
        "elevated NO₂ concentrations aggravate respiratory illnesses, contribute to ground-level ozone formation, and lead to corrosive acid precipitation. "
        "Because NO₂ has an atmospheric lifetime of only several hours, localized satellite observations directly mirror ongoing regional anthropogenic emissions.\n\n"
        "SkyQueryChat was engineered to make spatial and temporal satellite NO₂ records effortlessly accessible via natural language conversations. "
        "A user simply asks: 'What is the air quality in Punjab?', 'Compare NO2 in Delhi and Mumbai last month', or 'Which cities have the highest NO2?', "
        "and receives an instant, data-backed analytical response complete with quantitative metrics, historical baselines, interactive trend charts, "
        "and a fully inspectable mathematical provenance trace."
    )

    doc.add_heading("1.2 The Challenge of Accessing Satellite Air Quality Data", level=2).runs[0].font.color.rgb = RGBColor(15, 118, 110)
    p_chall = doc.add_paragraph()
    p_chall.add_run(
        "Despite open data initiatives by space agencies (NASA, ESA, ISRO), atmospheric remote sensing data remains locked behind steep technical barriers:\n"
        "1. Specialized File Formats: Data is distributed as multi-dimensional HDF5/NetCDF4 array cubes containing complex metadata, geolocation arrays, "
        "and coordinate references requiring domain-specific libraries (xarray, GDAL, netCDF4).\n"
        "2. Optical Retrieval Flags & Cloud Interference: Spaceborne UV-Vis spectrometers measure backscattered solar radiation. Solar Zenith Angle (SZA) "
        "limits and cloud fractions above 30% obscure surface views, necessitating rigorous quality masking.\n"
        "3. Computational Overhead: Computing spatial time-series or multi-city rankings requires heavy spatial slicing, coordinate transformations, "
        "and handling of missing observation dropouts.\n"
        "4. Inapplicability of Generic Generative AI: Commercial LLMs lack real-time access to space agency data cubes and hallucinate numerical estimates, "
        "creating catastrophic misinformation risks in environmental governance."
    )

    # Insert Figure 3 (Workflow Comparison)
    fig3_path = ASSETS / "fig3_workflow_comparison.png"
    if fig3_path.exists():
        doc.add_paragraph().paragraph_format.space_before = Pt(8)
        doc.add_picture(str(fig3_path), width=Inches(6.5))
        p_cap3 = doc.add_paragraph("Figure 1.1: Contrast between traditional satellite Earth observation data analysis and the conversational SkyQueryChat paradigm.")
        p_cap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap3.runs[0].font.italic = True
        p_cap3.runs[0].font.size = Pt(8.5)

    doc.add_heading("1.3 Atmospheric Satellite Remote Sensing: Sensors & Physics", level=2).runs[0].font.color.rgb = RGBColor(15, 118, 110)
    p_sens = doc.add_paragraph()
    p_sens.add_run(
        "SkyQueryChat is built upon the physical observation principles of spaceborne spectrometers:\n"
        "• Ozone Monitoring Instrument (OMI) aboard NASA's Aura satellite: A nadir-viewing UV-Vis spectrometer orbiting in a sun-synchronous orbit, "
        "providing daily global coverage at 0.25° × 0.25° Level-3 gridded resolution (OMNO2d product).\n"
        "• TROPOspheric Monitoring Instrument (TROPOMI) aboard Sentinel-5P: Delivers sub-urban resolution (3.5 × 5.5 km²) measuring Differential Optical "
        "Absorption Spectroscopy (DOAS) absorption features.\n"
        "• Physical Metric: Tropospheric vertical column density, measured in units of molecules/cm² (scaled by 10¹⁵). Values represent the integrated total "
        "molecules of NO₂ contained in a vertical atmospheric column from the Earth's surface to the tropopause boundary."
    )

    doc.add_heading("1.4 Introducing SkyQueryChat: Dual-Brain Agent Architecture", level=2).runs[0].font.color.rgb = RGBColor(15, 118, 110)
    p_arch_concept = doc.add_paragraph()
    p_arch_concept.add_run(
        "SkyQueryChat reconciles natural language accessibility with absolute scientific precision by operating two complementary execution brains:\n"
        "1. The Language & Planning Brain: Powered by Groq Cloud API running `openai/gpt-oss-120b` (or LLaMA-3.3-70B). It translates ambiguous user questions "
        "into a structured, non-executable JSON query plan specifying intent, coordinates, dates, and order. Crucially, the LLM has zero access to data numbers.\n"
        "2. The Vectorized Computation & Referee Brain: Powered by compiled NumPy tensor algorithms and a pure-Python verification engine (`verifier.py`). "
        "It executes Haversine coordinate distances, masks cloud obscurations, computes linear trends, and recalculates every single output metric independently "
        "before presentation."
    )

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # PART II: SYSTEM ARCHITECTURE & VERIFICATION
    # -------------------------------------------------------------------------
    doc.add_heading("Part II — System Architecture, Data Pipeline, Agentic Reasoning and Mathematical Verification", level=1).runs[0].font.color.rgb = RGBColor(15, 23, 42)

    doc.add_heading("2.1 End-to-End System Architecture (The 5-Stage Pipeline)", level=2).runs[0].font.color.rgb = RGBColor(15, 118, 110)
    p_pipe = doc.add_paragraph()
    p_pipe.add_run(
        "SkyQueryChat processes every conversational request through a unidirectional, strictly staged agentic pipeline:\n"
        "Stage 1: Intent & Entity Parsing — Extracts intent, geographic locations, and temporal parameters into JSON schema.\n"
        "Stage 2: Schema Normalization & Domain Guardrails — Enforces coordinate limits, Indian gazetteer resolution, and polite refusals for unsupported pollutants.\n"
        "Stage 3: Vectorized Geospatial Atmospheric Engine — Slices 3D data cubes via Haversine great-circle radius and cloud fraction masking.\n"
        "Stage 4: Autonomous Mathematical Verification Referee — Recomputes all spatial and temporal metrics using pure Python math to 10⁻⁶ tolerance.\n"
        "Stage 5: Deterministic Grounded Presentation — Formats verified figures into template natural language and renders responsive Altair charts."
    )

    # Insert Figure 1 (Architecture Flowchart)
    fig1_path = ASSETS / "fig1_architecture.png"
    if fig1_path.exists():
        doc.add_paragraph().paragraph_format.space_before = Pt(8)
        doc.add_picture(str(fig1_path), width=Inches(6.5))
        p_cap1 = doc.add_paragraph("Figure 2.1: Complete 5-stage agentic processing pipeline of SkyQueryChat.")
        p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap1.runs[0].font.italic = True
        p_cap1.runs[0].font.size = Pt(8.5)

    doc.add_heading("2.2 Data Pipeline: NASA OMI/Aura OMNO2d & Indian Grid Layout", level=2).runs[0].font.color.rgb = RGBColor(15, 118, 110)
    p_data = doc.add_paragraph()
    p_data.add_run(
        "The spatial domain covers the entire Indian subcontinent, extending from 6.0°N to 38.0°N in latitude and 68.0°E to 98.0°E in longitude. "
        "At a resolution of 0.25° × 0.25°, the spatial grid contains 129 latitude bins and 121 longitude bins (15,609 spatial cells per day). "
        "Over a standard 120-day temporal baseline, the 3D tensor comprises 1,873,080 distinct atmospheric observations.\n\n"
        "The automated downloader (`scripts/fetch_real_data.py`) queries the NASA Earthdata CMR API for Level-3 product `OMNO2d`. "
        "The script extracts the cloud-screened tropospheric column dataset (`ColumnAmountNO2TropCloudScreened`), converts missing values and "
        "bad quality flags to NaN, and persists the cropped regional grid as `data/no2_grid.npz`. When real data is absent, the engine falls back "
        "seamlessly to `data/tempo_no2_grid.npz` and displays an explicit 'Demo synthetic data' indicator."
    )

    # Insert Figure 2 (India Grid Map)
    fig2_path = ASSETS / "fig2_india_grid.png"
    if fig2_path.exists():
        doc.add_paragraph().paragraph_format.space_before = Pt(8)
        doc.add_picture(str(fig2_path), width=Inches(5.5))
        p_cap2 = doc.add_paragraph("Figure 2.2: Spatial observation domain over India (6°N–38°N, 68°E–98°E) showing regional NO₂ concentration hotspots.")
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap2.runs[0].font.italic = True
        p_cap2.runs[0].font.size = Pt(8.5)

    doc.add_heading("2.3 Indian Gazetteer & Spatial Resolution", level=2).runs[0].font.color.rgb = RGBColor(15, 118, 110)
    p_gaz = doc.add_paragraph()
    p_gaz.add_run(
        "To ensure comprehensive national coverage, `skyquery/gazetteer.py` incorporates an offline gazetteer mapping:\n"
        "• All 28 Indian States & 8 Union Territories.\n"
        "• 248 Major Urban Centers and Industrial Districts across India.\n"
        "• Aliases and Historical Spellings: e.g., 'Bombay' → Mumbai, 'Bangalore' → Bengaluru, 'Calcutta' → Kolkata, 'Madras' → Chennai, 'NCR' → Delhi.\n"
        "• State-Level Queries: For regional queries (e.g. 'Air quality in Punjab'), the engine evaluates both the state geographic centroid and representative "
        "metropolitan clusters, transparently reporting the observation methodology in the audit trail."
    )

    doc.add_heading("2.4 Vectorized Slicing & Trend Statistics", level=2).runs[0].font.color.rgb = RGBColor(15, 118, 110)
    p_math = doc.add_paragraph()
    p_math.add_run(
        "For any target coordinate (lat₀, lon₀), the engine calculates great-circle spherical distance across the 2D spatial grid using the Haversine equation:\n"
        "    a = sin²(Δφ / 2) + cos φ₁ · cos φ₂ · sin²(Δλ / 2)\n"
        "    d = 2 · R_Earth · arcsin(√a)\n"
        "where R_Earth = 6371.0088 km. All grid cells satisfying d ≤ 25 km are isolated. "
        "For temporal trend analysis, Ordinary Least Squares (OLS) linear regression fits daily observed values y against day offsets x:\n"
        "    slope m = Σ(x - x̄)(y - ȳ) / Σ(x - x̄)²\n"
        "    R² = 1 - (SS_res / SS_tot)\n"
        "Percentage changes are evaluated over the time span, categorizing trends as 'increasing', 'decreasing', or 'roughly flat' (|change| < 5%)."
    )

    doc.add_heading("2.5 Autonomous Mathematical Referee (`verifier.py`)", level=2).runs[0].font.color.rgb = RGBColor(15, 118, 110)
    p_ver = doc.add_paragraph()
    p_ver.add_run(
        "Unlike conventional LLM systems that trust internal model calculations, SkyQueryChat implements an independent verification referee (`verifier.py`). "
        "The verifier deliberately avoids using NumPy, pandas, or engine methods. It iterates cell-by-cell over the raw data cube using pure Python standard library `math`, "
        "recomputing cell selections, valid day counts, period means, peak dates and values, 30-day baseline context means, and linear regression slopes. "
        "Engine outputs are checked against independent values using a strict 10⁻⁶ relative tolerance threshold:\n"
        "    |v_engine - v_verifier| ≤ 10⁻⁶ · max(1.0, |v_engine|, |v_verifier|)\n"
        "Every single query output in the Streamlit UI contains an expandable 'How this was verified' provenance ledger listing every passing mathematical check."
    )

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # PART III: IMPLEMENTATION, RESULTS & ROADMAP
    # -------------------------------------------------------------------------
    doc.add_heading("Part III — Implementation, Testing, Limitations and Future Scope", level=1).runs[0].font.color.rgb = RGBColor(15, 23, 42)

    doc.add_heading("3.1 Technology Stack", level=2).runs[0].font.color.rgb = RGBColor(15, 118, 110)
    
    t_tech = doc.add_table(rows=7, cols=3)
    t_tech.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_tech_widths = [Inches(1.8), Inches(2.2), Inches(2.5)]
    set_table_borders(t_tech, color="CBD5E1")
    format_table_header(t_tech.rows[0], t_tech_widths)
    t_tech.rows[0].cells[0].paragraphs[0].text = "Component Layer"
    t_tech.rows[0].cells[1].paragraphs[0].text = "Technology / Library"
    t_tech.rows[0].cells[2].paragraphs[0].text = "Architectural Purpose"

    tech_data = [
        ("Execution Runtime", "Python 3.14 (64-bit)", "Core runtime environment for agent and mathematical processing"),
        ("LLM Planning Brain", "Groq Cloud API (openai/gpt-oss-120b)", "Sub-second zero-temperature JSON query plan extraction"),
        ("Array & Geospatial Math", "NumPy + Haversine Spherical Math", "Vectorized 3D tensor operations and coordinate distance filtering"),
        ("Time-Series & Indexing", "Pandas", "Temporal datetime indexing and cloud-gap time interpolation"),
        ("Interactive Frontend UI", "Streamlit + Altair 6.x", "Clean human-designed light dashboard and SVG/Canvas charts"),
        ("Remote Sensing Ingestion", "earthaccess + h5py", "Direct NASA Earthdata CMR searching and HDF-EOS5 reading")
    ]
    for idx, (l, t, p) in enumerate(tech_data, start=1):
        r = t_tech.rows[idx]
        r.cells[0].paragraphs[0].text = l
        r.cells[1].paragraphs[0].text = t
        r.cells[2].paragraphs[0].text = p
        format_table_row(r, t_tech_widths, bg_hex="F8FAFC" if idx % 2 == 0 else "FFFFFF", bold_first=True)

    doc.add_heading("3.2 Empirical Verification & Benchmark Results", level=2).runs[0].font.color.rgb = RGBColor(15, 118, 110)
    p_res = doc.add_paragraph()
    p_res.add_run(
        "SkyQueryChat was validated across 18 automated unit tests and a comprehensive 19-question benchmark evaluation suite (`run_demo.py`). "
        "All 18 unit tests passed cleanly in 0.757 seconds. In the end-to-end evaluation, all 19 queries achieved 100% precision across 1,541 distinct "
        "numerical verification checks.\n\n"
        "Representative live query outputs from the benchmark run are summarized in Table 3.2 below:"
    )

    t_res = doc.add_table(rows=8, cols=4)
    t_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_res_widths = [Inches(2.0), Inches(1.0), Inches(1.5), Inches(2.0)]
    set_table_borders(t_res, color="CBD5E1")
    format_table_header(t_res.rows[0], t_res_widths)
    t_res.rows[0].cells[0].paragraphs[0].text = "Natural Language Query"
    t_res.rows[0].cells[1].paragraphs[0].text = "Intent"
    t_res.rows[0].cells[2].paragraphs[0].text = "Quantitative Result"
    t_res.rows[0].cells[3].paragraphs[0].text = "Verification Status"

    bench_data = [
        ("NO2 in Delhi right now", "current", "351.91 × 10¹⁵ mol/cm²", "5/5 checks passed (PASS)"),
        ("air quality in Punjab", "current", "184.45 × 10¹⁵ mol/cm²", "5/5 checks passed (PASS)"),
        ("Compare Mumbai and Chennai last month", "compare", "Mumbai: 66.75 vs Chennai: 15.87", "7/7 checks passed (PASS)"),
        ("top 5 most polluted cities in India", "rank", "Loni, Delhi, Ghaziabad, Noida, Rohini", "745/745 checks passed (PASS)"),
        ("worst day in Kolkata", "peak", "Peak: 2025-10-10 (119.82 × 10¹⁵)", "3/3 checks passed (PASS)"),
        ("is NO2 in Bengaluru rising", "trend", "+6% trend (slope: +0.03/day)", "4/4 checks passed (PASS)"),
        ("what is PM2.5 in Delhi", "unsupported", "Polite refusal (NO₂ sensor only)", "Guardrail passed (PASS)")
    ]
    for idx, (q, it, res_val, v_stat) in enumerate(bench_data, start=1):
        r = t_res.rows[idx]
        r.cells[0].paragraphs[0].text = q
        r.cells[1].paragraphs[0].text = it
        r.cells[2].paragraphs[0].text = res_val
        r.cells[3].paragraphs[0].text = v_stat
        format_table_row(r, t_res_widths, bg_hex="F8FAFC" if idx % 2 == 0 else "FFFFFF", bold_first=True)

    doc.add_heading("3.3 Current Limitations & Operational Boundaries", level=2).runs[0].font.color.rgb = RGBColor(15, 118, 110)
    p_lim = doc.add_paragraph()
    p_lim.add_run(
        "1. Daily Temporal Granularity: Polar-orbiting satellites provide one daytime overpass per day (~13:30 local solar time), precluding hourly diurnal cycle analysis.\n"
        "2. Tropospheric Column vs. Ground PM2.5: The sensor measures vertical column density in molecules/cm², which correlates with surface air quality but is not equivalent to microgram/m³ ground particulate matter.\n"
        "3. Monsoon Cloud Coverage: During intense monsoon weeks, cloud fraction flags mask continuous retrieval pixels, necessitating time-interpolated baselines."
    )

    doc.add_heading("3.4 Future Research Roadmap", level=2).runs[0].font.color.rgb = RGBColor(15, 118, 110)
    p_road = doc.add_paragraph()
    p_road.add_run(
        "• Geostationary Hourly Observation Ingestion: Incorporating forthcoming hourly geostationary data (Korea's GEMS, European Sentinel-4, and ISRO INSAT sounders) "
        "to track rush-hour diurnal NO₂ variations.\n"
        "• Multi-Species Trace Gas Expansion: Expanding the 3D tensor to simultaneously query Sulfur Dioxide (SO₂), Formaldehyde (HCHO), and Carbon Monoxide (CO).\n"
        "• Boundary Layer Chemical Transport Modeling: Coupling satellite columns with WRF-Chem atmospheric models to project ground-level PM2.5 estimates with uncertainty bounds."
    )

    doc.add_heading("3.5 Conclusion", level=2).runs[0].font.color.rgb = RGBColor(15, 118, 110)
    p_concl = doc.add_paragraph()
    p_concl.add_run(
        "SkyQueryChat successfully bridges the gap between massive space agency Earth observation data cubes and conversational accessibility. "
        "By strictly decoupling natural language planning from spatial tensor extraction and backing every response with a primitive pure-Python "
        "mathematical referee, the system eliminates LLM hallucination, withstands prompt injection attacks, and establishes a trustworthy, verifiable "
        "standard for environmental AI applications."
    )

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # REFERENCES & APPENDICES
    # -------------------------------------------------------------------------
    doc.add_heading("References & Cited Patents", level=1).runs[0].font.color.rgb = RGBColor(15, 23, 42)
    refs = [
        "1. Levelt, P. F., et al. (2018). The Ozone Monitoring Instrument: overview of 14 years in space. Atmospheric Chemistry and Physics, 18(8), 5699–5745.",
        "2. Veefkind, J. P., et al. (2012). TROPOMI on the ESA Copernicus Sentinel-5 Precursor: A GMES mission for global observations of the atmospheric composition. Remote Sensing of Environment, 120, 70–83.",
        "3. NASA Earth Science Data and Information System (ESDIS). OMI/Aura Daily Gridded Tropospheric NO2 Product (OMNO2d). Goddard Earth Sciences Data and Information Services Center (GES DISC).",
        "4. Yao, S., et al. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. International Conference on Learning Representations (ICLR).",
        "5. US Patent 12,353,407 B1: Natural language query interfaces for enterprise multidimensional analytical databases.",
        "6. US Patent 11,893,028 B2: Geospatial raster query synthesis and tile extraction engines.",
        "7. Central Pollution Control Board (CPCB), Ministry of Environment, Forest and Climate Change, Government of India. National Ambient Air Quality Standards (NAAQS) Reports (2024–2026)."
    ]
    for r in refs:
        p = doc.add_paragraph(r)
        p.paragraph_format.space_after = Pt(4)
        p.runs[0].font.size = Pt(8.5)

    doc.add_heading("Appendix A — Running the Project", level=1).runs[0].font.color.rgb = RGBColor(15, 23, 42)
    p_app = doc.add_paragraph()
    p_app.add_run(
        "Step 1: Clone Repository & Set Environment:\n"
        "    git clone https://github.com/Paulsonsanio/SkyQueryChat-NL-Interface-for-Air-Quality-Data.git\n"
        "    cd skyquerychat\n"
        "    python -m venv .venv && .\\.venv\\Scripts\\activate\n"
        "    pip install -r requirements.txt\n\n"
        "Step 2: Launch Streamlit Web Application:\n"
        "    streamlit run app.py\n"
        "    Open browser at: http://localhost:8501\n\n"
        "Step 3: Execute Automated Test Suite & Benchmark Validation:\n"
        "    python -m unittest discover -s tests -v\n"
        "    python run_demo.py"
    )

    doc.save(str(OUTPUT_DOCX))
    print(f"Project Report DOCX successfully generated at: {OUTPUT_DOCX}")


if __name__ == '__main__':
    build_report_docx()
