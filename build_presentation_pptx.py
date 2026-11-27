"""
Builds the SkyQueryChat Presentation (PPTX) with an executive 16:9 widescreen design.
Sole Presenter: paulsonsanio (12313062)
GitHub Repository: https://github.com/Paulsonsanio/SkyQueryChat-NL-Interface-for-Air-Quality-Data
"""
import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# --- Color Palette ---
COLOR_BG_DARK = RGBColor(15, 23, 42)       # Midnight Slate (#0F172A)
COLOR_CARD_DARK = RGBColor(30, 41, 59)     # Slate 800 (#1E293B)
COLOR_BORDER_DARK = RGBColor(51, 65, 85)   # Slate 700 (#334155)

COLOR_BG_LIGHT = RGBColor(248, 250, 252)   # Slate 50 (#F8FAFC)
COLOR_CARD_LIGHT = RGBColor(255, 255, 255) # Pure White (#FFFFFF)
COLOR_BORDER_LIGHT = RGBColor(226, 232, 240) # Slate 200 (#E2E8F0)

COLOR_TEAL_DARK = RGBColor(15, 118, 110)   # Deep Teal (#0F766E)
COLOR_TEAL_LIGHT = RGBColor(20, 184, 166)  # Bright Teal (#14B8A6)
COLOR_TEAL_BG = RGBColor(240, 253, 250)    # Teal 50 (#F0FDFA)

COLOR_AMBER = RGBColor(217, 119, 6)        # Amber 600 (#D97706)
COLOR_AMBER_BG = RGBColor(254, 243, 199)   # Amber 100 (#FEF3C7)

COLOR_TEXT_DARK = RGBColor(15, 23, 42)     # Charcoal Slate (#0F172A)
COLOR_TEXT_MUTED = RGBColor(100, 116, 139) # Slate 500 (#64748B)
COLOR_TEXT_LIGHT = RGBColor(255, 255, 255) # White
COLOR_TEXT_LIGHT_MUTED = RGBColor(148, 163, 184) # Slate 400 (#94A3B8)

FONT_HEADING = "Calibri"
FONT_BODY = "Calibri"

def set_slide_background(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, category_text, title_text, is_dark=False):
    """Adds a standard structured header to a content slide."""
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.9))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p1 = tf.paragraphs[0]
    p1.text = category_text.upper()
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(10)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEAL_LIGHT if is_dark else COLOR_TEAL_DARK
    p1.space_after = Pt(2)

    p2 = tf.add_paragraph()
    p2.text = title_text
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK

def add_card(slide, left, top, width, height, bg_color=COLOR_CARD_LIGHT, border_color=COLOR_BORDER_LIGHT):
    """Creates a rounded rectangle card container."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape

def add_bullet(tf, title, desc, font_size=13, is_dark=False):
    p = tf.add_paragraph()
    p.space_after = Pt(8)
    
    run1 = p.add_run()
    run1.text = title + (" " if desc else "")
    run1.font.name = FONT_BODY
    run1.font.size = Pt(font_size)
    run1.font.bold = True
    run1.font.color.rgb = COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK
    
    if desc:
        run2 = p.add_run()
        run2.text = desc
        run2.font.name = FONT_BODY
        run2.font.size = Pt(font_size)
        run2.font.bold = False
        run2.font.color.rgb = COLOR_TEXT_LIGHT_MUTED if is_dark else COLOR_TEXT_MUTED

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: Title & Executive Overview (Dark Hero)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, COLOR_BG_DARK)

    # Decorative top bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.1))
    bar.fill.solid()
    bar.fill.fore_color.rgb = COLOR_TEAL_LIGHT
    bar.line.fill.background()

    # Title & Subtitle Box
    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.0), Inches(11.733), Inches(2.2))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_top = tf1.margin_right = tf1.margin_bottom = 0

    p_badge = tf1.paragraphs[0]
    p_badge.text = "RESEARCH CAPSTONE & PATENT DISCLOSURE | SPACEBORNE TELEMETRY"
    p_badge.font.name = FONT_HEADING
    p_badge.font.size = Pt(11)
    p_badge.font.bold = True
    p_badge.font.color.rgb = COLOR_TEAL_LIGHT
    p_badge.space_after = Pt(8)

    p_main = tf1.add_paragraph()
    p_main.text = "SkyQueryChat"
    p_main.font.name = FONT_HEADING
    p_main.font.size = Pt(40)
    p_main.font.bold = True
    p_main.font.color.rgb = COLOR_TEXT_LIGHT
    p_main.space_after = Pt(8)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Natural Language Conversational Interface & Autonomous Verification Referee for Satellite Atmospheric Data"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = COLOR_TEXT_LIGHT_MUTED

    # Cards Grid (2 cards at bottom)
    # Card 1: Author & Academic Info
    add_card(s1, Inches(0.8), Inches(3.6), Inches(5.6), Inches(2.8), bg_color=COLOR_CARD_DARK, border_color=COLOR_BORDER_DARK)
    c1_box = s1.shapes.add_textbox(Inches(1.1), Inches(3.8), Inches(5.0), Inches(2.4))
    c1_tf = c1_box.text_frame
    c1_tf.word_wrap = True
    c1_tf.margin_left = c1_tf.margin_top = c1_tf.margin_right = c1_tf.margin_bottom = 0

    p = c1_tf.paragraphs[0]
    p.text = "RESEARCHER & SOLE INVENTOR"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL_LIGHT
    p.space_after = Pt(10)

    add_bullet(c1_tf, "Student Name:", "paulsonsanio", font_size=13, is_dark=True)
    add_bullet(c1_tf, "Registration No:", "12313062", font_size=13, is_dark=True)
    add_bullet(c1_tf, "Institution:", "Lovely Professional University (LPU), Punjab", font_size=13, is_dark=True)
    add_bullet(c1_tf, "Discipline:", "Computer Science & Engineering (Agentic AI)", font_size=13, is_dark=True)

    # Card 2: Technical Highlights & GitHub Link
    add_card(s1, Inches(6.8), Inches(3.6), Inches(5.733), Inches(2.8), bg_color=COLOR_CARD_DARK, border_color=COLOR_BORDER_DARK)
    c2_box = s1.shapes.add_textbox(Inches(7.1), Inches(3.8), Inches(5.133), Inches(2.4))
    c2_tf = c2_box.text_frame
    c2_tf.word_wrap = True
    c2_tf.margin_left = c2_tf.margin_top = c2_tf.margin_right = c2_tf.margin_bottom = 0

    p = c2_tf.paragraphs[0]
    p.text = "TECHNICAL SPECIFICATIONS & REPOSITORY"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER
    p.space_after = Pt(10)

    add_bullet(c2_tf, "Data Foundation:", "NASA OMI/Aura (OMNO2d) 0.25 deg grid over India", font_size=13, is_dark=True)
    add_bullet(c2_tf, "Dual-Brain Engine:", "Groq Cloud LLaMA-3.3-70B + Rule Fallback", font_size=13, is_dark=True)
    add_bullet(c2_tf, "Verification Referee:", "Independent 10^-6 tolerance mathematical referee", font_size=13, is_dark=True)

    p_git = c2_tf.add_paragraph()
    p_git.space_after = Pt(4)
    run_git_label = p_git.add_run()
    run_git_label.text = "GitHub Repository: "
    run_git_label.font.name = FONT_BODY
    run_git_label.font.size = Pt(12)
    run_git_label.font.bold = True
    run_git_label.font.color.rgb = COLOR_TEXT_LIGHT

    run_git_url = p_git.add_run()
    run_git_url.text = "https://github.com/Paulsonsanio/SkyQueryChat-NL-Interface-for-Air-Quality-Data"
    run_git_url.font.name = FONT_BODY
    run_git_url.font.size = Pt(11)
    run_git_url.font.color.rgb = COLOR_TEAL_LIGHT
    run_git_url.hyperlink.address = "https://github.com/Paulsonsanio/SkyQueryChat-NL-Interface-for-Air-Quality-Data"

    # =========================================================================
    # SLIDE 2: Problem Statement & Atmospheric Dilemma
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, COLOR_BG_LIGHT)
    add_header(s2, "Problem Statement", "The Geospatial Telemetry Barrier & LLM Hallucination Trap")

    # 3 Column Cards
    col_w = Inches(3.64)
    gap = Inches(0.4)
    y_top = Inches(1.6)
    h_card = Inches(5.1)

    # Card 1: Remote Sensing Complexity
    add_card(s2, Inches(0.8), y_top, col_w, h_card)
    b1 = s2.shapes.add_textbox(Inches(1.05), Inches(1.85), col_w - Inches(0.5), h_card - Inches(0.5))
    tf_b1 = b1.text_frame
    tf_b1.word_wrap = True
    tf_b1.margin_left = tf_b1.margin_top = tf_b1.margin_right = tf_b1.margin_bottom = 0
    p = tf_b1.paragraphs[0]
    p.text = "Complex Telemetry Cubes"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_after = Pt(10)
    add_bullet(tf_b1, "Massive NetCDF/HDF5 Files:", "Earth observation telemetry produces gigabytes of dense matrices daily with multi-dimensional coordinates (time, lat, lon).")
    add_bullet(tf_b1, "Specialized GIS Overhead:", "Accessing daily NO2 requires domain software (QGIS, Panoply) and esoteric Python libraries (xarray, netCDF4, rasterio).")
    add_bullet(tf_b1, "Analysis Bottleneck:", "Policy analysts and environmentalists spend 80% of time data wrangling rather than executing environmental policy.")

    # Card 2: The LLM Hallucination Trap
    add_card(s2, Inches(0.8) + col_w + gap, y_top, col_w, h_card)
    b2 = s2.shapes.add_textbox(Inches(1.05) + col_w + gap, Inches(1.85), col_w - Inches(0.5), h_card - Inches(0.5))
    tf_b2 = b2.text_frame
    tf_b2.word_wrap = True
    tf_b2.margin_left = tf_b2.margin_top = tf_b2.margin_right = tf_b2.margin_bottom = 0
    p = tf_b2.paragraphs[0]
    p.text = "LLM Hallucination Trap"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER
    p.space_after = Pt(10)
    add_bullet(tf_b2, "Inability to Slice Tensors:", "Large Language Models cannot natively ingest or aggregate 3D floating-point spatio-temporal arrays.")
    add_bullet(tf_b2, "Fabricated Precision:", "When asked 'What was Delhi's NO2 yesterday?', generic LLMs generate authoritative-sounding but completely fabricated numbers.")
    add_bullet(tf_b2, "Zero Verification:", "No built-in mathematical referee exists to verify whether claims match physical instruments or satellite orbits.")

    # Card 3: The SkyQueryChat Breakthrough
    add_card(s2, Inches(0.8) + (col_w + gap) * 2, y_top, col_w, h_card)
    b3 = s2.shapes.add_textbox(Inches(1.05) + (col_w + gap) * 2, Inches(1.85), col_w - Inches(0.5), h_card - Inches(0.5))
    tf_b3 = b3.text_frame
    tf_b3.word_wrap = True
    tf_b3.margin_left = tf_b3.margin_top = tf_b3.margin_right = tf_b3.margin_bottom = 0
    p = tf_b3.paragraphs[0]
    p.text = "Deterministic Grounding"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL_DARK
    p.space_after = Pt(10)
    add_bullet(tf_b3, "Decoupled Reasoning:", "The LLM never generates numbers; it acts strictly as a semantic planner that outputs executable JSON specifications.")
    add_bullet(tf_b3, "Vectorized Execution:", "A high-performance NumPy engine performs SIMD tensor calculations directly on satellite grids in milliseconds.")
    add_bullet(tf_b3, "Mathematical Referee:", "An independent verifier checks every output against sensor cubes with 10^-6 tolerance before the user sees it.")

    # =========================================================================
    # SLIDE 3: Spaceborne Telemetry & Indian Geographic Grid
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, COLOR_BG_LIGHT)
    add_header(s3, "Satellite Remote Sensing Telemetry", "NASA OMI/Aura Data Foundation & Indian Geographic Bounds")

    # Left Card: Sensor Specs
    add_card(s3, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
    s3_left = s3.shapes.add_textbox(Inches(1.1), Inches(1.85), Inches(5.0), Inches(4.6))
    tf_s3l = s3_left.text_frame
    tf_s3l.word_wrap = True
    tf_s3l.margin_left = tf_s3l.margin_top = tf_s3l.margin_right = tf_s3l.margin_bottom = 0

    p = tf_s3l.paragraphs[0]
    p.text = "NASA OMI/Aura (OMNO2d) Level-3 Telemetry"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_after = Pt(10)

    add_bullet(tf_s3l, "Instrument & Mission:", "Ozone Monitoring Instrument (OMI) aboard NASA's Aura polar-orbiting satellite; Sun-synchronous orbit with ~13:45 local overpass.")
    add_bullet(tf_s3l, "Physical Quantity:", "Cloud-screened tropospheric column nitrogen dioxide density, expressed in standard physical units: 10^15 molecules/cm^2.")
    add_bullet(tf_s3l, "Spatial Resolution:", "0.25 deg x 0.25 deg global spatial grid (~28 km x 28 km cell spacing over Indian latitudes).")
    add_bullet(tf_s3l, "FillValue Handling:", "Instrument nodata/cloud flags (-1.2676506e+30) systematically mapped to IEEE 754 NaN values; ocean cells with zero valid data return explicit warnings.")
    add_bullet(tf_s3l, "Temporal Depth:", "120 continuous daily observation slices covering recent atmospheric history across India.")

    # Right Card: India Spatial Domain & Gazetteer
    add_card(s3, Inches(6.8), Inches(1.6), Inches(5.733), Inches(5.1))
    s3_right = s3.shapes.add_textbox(Inches(7.1), Inches(1.85), Inches(5.133), Inches(4.6))
    tf_s3r = s3_right.text_frame
    tf_s3r.word_wrap = True
    tf_s3r.margin_left = tf_s3r.margin_top = tf_s3r.margin_right = tf_s3r.margin_bottom = 0

    p = tf_s3r.paragraphs[0]
    p.text = "Indian Geospatial Domain & Coverage"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL_DARK
    p.space_after = Pt(10)

    add_bullet(tf_s3r, "Latitude Bounding Box:", "6.0 deg N (Kanyakumari / Indian Ocean) to 38.0 deg N (Kashmir / Himalayas) across 128 discrete latitude bins.")
    add_bullet(tf_s3r, "Longitude Bounding Box:", "68.0 deg E (Gujarat / Rann of Kutch) to 98.0 deg E (Arunachal Pradesh) across 120 discrete longitude bins.")
    add_bullet(tf_s3r, "Exhaustive Gazetteer:", "150+ major Indian municipal cities + all 28 States and 8 Union Territories mapped to exact latitude/longitude centroids.")
    add_bullet(tf_s3r, "State Aggregation Logic:", "State-level queries resolve to state capital centroids combined with major demographic nodes to ensure representative coverage.")
    add_bullet(tf_s3r, "SIMD Memory Layout:", "Saved in data/no2_grid.npz with pre-indexed coordinate arrays enabling instant sub-millisecond bounding lookups.")

    # =========================================================================
    # SLIDE 4: System Paradigm: Decoupling Planning from Execution
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, COLOR_BG_LIGHT)
    add_header(s4, "System Paradigm", "Decoupling Semantic Planning from Deterministic Execution")

    # Left: The Flawed Traditional Paradigm
    add_card(s4, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
    s4_l = s4.shapes.add_textbox(Inches(1.1), Inches(1.85), Inches(5.0), Inches(4.6))
    tf_s4l = s4_l.text_frame
    tf_s4l.word_wrap = True
    tf_s4l.margin_left = tf_s4l.margin_top = tf_s4l.margin_right = tf_s4l.margin_bottom = 0

    p = tf_s4l.paragraphs[0]
    p.text = "Traditional Monolithic LLM (Fails)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER
    p.space_after = Pt(10)

    add_bullet(tf_s4l, "Direct End-to-End Generation:", "User inputs a query -> Raw LLM attempts to generate analytical text and values simultaneously in a single prompt.")
    add_bullet(tf_s4l, "Context Window Saturation:", "Cannot pass a 120 x 128 x 120 floating-point matrix (1.84 million values) into an LLM context without massive latency and token cost.")
    add_bullet(tf_s4l, "Statistical Approximation:", "LLMs predict the most probable token, not the mathematical truth. Floating-point numbers are treated as text tokens rather than exact quantities.")
    add_bullet(tf_s4l, "Unverifiable Claims:", "No mechanism to trace where a number originated, creating extreme risk for public health policy and legal standards.")

    # Right: SkyQueryChat Dual-Brain Paradigm
    add_card(s4, Inches(6.8), Inches(1.6), Inches(5.733), Inches(5.1))
    s4_r = s4.shapes.add_textbox(Inches(7.1), Inches(1.85), Inches(5.133), Inches(4.6))
    tf_s4r = s4_r.text_frame
    tf_s4r.word_wrap = True
    tf_s4r.margin_left = tf_s4r.margin_top = tf_s4r.margin_right = tf_s4r.margin_bottom = 0

    p = tf_s4r.paragraphs[0]
    p.text = "SkyQueryChat Dual-Brain Paradigm"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL_DARK
    p.space_after = Pt(10)

    add_bullet(tf_s4r, "1. Semantic Planning Brain:", "Translates user questions into a strictly validated JSON AST (QueryPlan). It determines intent (trend, compare, rank, peak) and targets, but NEVER touches data.")
    add_bullet(tf_s4r, "2. Deterministic Execution Brain:", "NumPy engine receives the JSON plan, slices the tensor along exact spatial and temporal indices, and computes exact mathematical reductions.")
    add_bullet(tf_s4r, "3. Autonomous Verification Referee:", "An independent verifier cross-audits the numbers with 10^-6 relative tolerance before text synthesis is accepted.")
    add_bullet(tf_s4r, "Provable Zero Hallucination:", "Numbers presented to the user originate 100% from sensor observation arrays, never from LLM generative probabilities.")

    # =========================================================================
    # SLIDE 5: 5-Stage Agentic Architecture
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, COLOR_BG_LIGHT)
    add_header(s5, "System Architecture", "End-to-End 5-Stage Agentic Pipeline")

    # Embed Figure 1
    fig1_path = os.path.abspath("report_assets/fig1_architecture.png")
    if os.path.exists(fig1_path):
        s5.shapes.add_picture(fig1_path, Inches(0.8), Inches(1.5), width=Inches(6.8))

    # Architecture Explanation Card on Right
    add_card(s5, Inches(7.8), Inches(1.5), Inches(4.733), Inches(5.2))
    s5_desc = s5.shapes.add_textbox(Inches(8.05), Inches(1.7), Inches(4.233), Inches(4.8))
    tf_s5 = s5_desc.text_frame
    tf_s5.word_wrap = True
    tf_s5.margin_left = tf_s5.margin_top = tf_s5.margin_right = tf_s5.margin_bottom = 0

    p = tf_s5.paragraphs[0]
    p.text = "Pipeline Execution Lifecycle"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_after = Pt(8)

    add_bullet(tf_s5, "Stage 1: Input Guard:", "Sanitizes input, intercepts out-of-domain questions ('PM2.5', 'weather'), deflects adversarial prompt injections.", font_size=11)
    add_bullet(tf_s5, "Stage 2: Semantic Planner:", "Groq Cloud LLaMA-3.3-70B synthesizes structured JSON plan. If API times out, falls back to local RulePlanner in <5ms.", font_size=11)
    add_bullet(tf_s5, "Stage 3: Vectorized Engine:", "NumPy SIMD spatial slicing and temporal filtering over NASA OMI grid; computes means, trends, peak days.", font_size=11)
    add_bullet(tf_s5, "Stage 4: Verification Referee:", "Independent referee recalculates results with 10^-6 tolerance. If mismatch occurs, execution is blocked.", font_size=11)
    add_bullet(tf_s5, "Stage 5: Synthesis & UI:", "Streamlit frontend renders human-centric text, metric cards, Altair charts, and verification audit trail.", font_size=11)

    # =========================================================================
    # SLIDE 6: Dual-Brain Semantic Planning Engine
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, COLOR_BG_LIGHT)
    add_header(s6, "Semantic Planning Brain", "Groq Cloud LLaMA-3.3-70B & Deterministic Fallback Engine")

    # 3 horizontal cards
    card_h = Inches(5.1)
    c_w = Inches(3.64)

    # Card 1: Groq LLM
    add_card(s6, Inches(0.8), Inches(1.6), c_w, card_h)
    tb_c1 = s6.shapes.add_textbox(Inches(1.05), Inches(1.85), c_w - Inches(0.5), card_h - Inches(0.5))
    tf_c1 = tb_c1.text_frame
    tf_c1.word_wrap = True
    tf_c1.margin_left = tf_c1.margin_top = tf_c1.margin_right = tf_c1.margin_bottom = 0
    p = tf_c1.paragraphs[0]
    p.text = "Groq LLaMA-3.3-70B"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL_DARK
    p.space_after = Pt(10)
    add_bullet(tf_c1, "Ultra-Low Latency Inference:", "Executes on Groq LPU hardware delivering query plan synthesis in ~800 milliseconds.")
    add_bullet(tf_c1, "Strict JSON Mode:", "Constrained by system prompt to emit only compliant JSON adhering to the QueryPlan Pydantic model.")
    add_bullet(tf_c1, "Zero Data Access:", "The prompt receives city gazetteers and schema specifications only; raw telemetry tensors are strictly isolated from the LLM.")

    # Card 2: Deterministic Rule Fallback
    add_card(s6, Inches(0.8) + c_w + gap, Inches(1.6), c_w, card_h)
    tb_c2 = s6.shapes.add_textbox(Inches(1.05) + c_w + gap, Inches(1.85), c_w - Inches(0.5), card_h - Inches(0.5))
    tf_c2 = tb_c2.text_frame
    tf_c2.word_wrap = True
    tf_c2.margin_left = tf_c2.margin_top = tf_c2.margin_right = tf_c2.margin_bottom = 0
    p = tf_c2.paragraphs[0]
    p.text = "Local Rule Fallback"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_after = Pt(10)
    add_bullet(tf_c2, "Zero-Downtime Guarantee:", "If Groq API experiences rate limits, network timeouts, or invalid formatting, system instantly switches to RulePlanner.")
    add_bullet(tf_c2, "High-Speed Regex Parsing:", "Compiles regex patterns and token gazetteers to resolve intent and targets in < 30 milliseconds.")
    add_bullet(tf_c2, "Offline Independence:", "Enables the entire SkyQueryChat application to function in isolated, air-gapped defense or field environments.")

    # Card 3: Intent Classification
    add_card(s6, Inches(0.8) + (c_w + gap) * 2, Inches(1.6), c_w, card_h)
    tb_c3 = s6.shapes.add_textbox(Inches(1.05) + (c_w + gap) * 2, Inches(1.85), c_w - Inches(0.5), card_h - Inches(0.5))
    tf_c3 = tb_c3.text_frame
    tf_c3.word_wrap = True
    tf_c3.margin_left = tf_c3.margin_top = tf_c3.margin_right = tf_c3.margin_bottom = 0
    p = tf_c3.paragraphs[0]
    p.text = "Intent Classification"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER
    p.space_after = Pt(10)
    add_bullet(tf_c3, "trend / current / avg:", "Time-series extraction over 30 to 120 days with linear regression and moving average statistics.")
    add_bullet(tf_c3, "compare:", "Multi-location synchronization across identical temporal windows with cross-city ratio computations.")
    add_bullet(tf_c3, "rank:", "Nationwide or regional top-K pollution sorting across all gazetteer locations.")
    add_bullet(tf_c3, "peak:", "Extreme event detection identifying highest recorded NO2 day and spike magnitude.")
    add_bullet(tf_c3, "out_of_domain:", "Politely deflects questions outside satellite NO2 scope with helpful suggestions.")

    # =========================================================================
    # SLIDE 7: High-Performance Vectorized Slicing & Geospatial Grid
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, COLOR_BG_LIGHT)
    add_header(s7, "Vectorized Execution Engine", "High-Speed Tensor Slicing & Indian Geospatial Gazetteer")

    # Embed Figure 2 (India Grid)
    fig2_path = os.path.abspath("report_assets/fig2_india_grid.png")
    if os.path.exists(fig2_path):
        s7.shapes.add_picture(fig2_path, Inches(0.8), Inches(1.5), width=Inches(6.2))

    # Right Card: Engine Mechanics
    add_card(s7, Inches(7.3), Inches(1.5), Inches(5.233), Inches(5.2))
    s7_desc = s7.shapes.add_textbox(Inches(7.55), Inches(1.75), Inches(4.733), Inches(4.7))
    tf_s7 = s7_desc.text_frame
    tf_s7.word_wrap = True
    tf_s7.margin_left = tf_s7.margin_top = tf_s7.margin_right = tf_s7.margin_bottom = 0

    p = tf_s7.paragraphs[0]
    p.text = "Mathematical Engine Specifications"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_after = Pt(10)

    add_bullet(tf_s7, "Sub-Millisecond Slicing:", "Calculates spatial nearest-neighbor coordinate bins in O(1) time and extracts temporal sub-arrays using direct NumPy pointers.", font_size=12)
    add_bullet(tf_s7, "NaN-Resilient Reductions:", "Uses numpy.nanmean, numpy.nanmax, and numpy.nanpercentile to prevent cloud-masked pixels from corrupting statistical baselines.", font_size=12)
    add_bullet(tf_s7, "Cloud Interpolation Tracking:", "Flags and tracks missing cloudy days; provides interpolated values for visualization while marking them visually distinct in charts.", font_size=12)
    add_bullet(tf_s7, "Ocean & Desert Masking:", "Identifies coordinates with 100% NaN telemetry (e.g., deep Arabian Sea or uncalibrated desert tracks) and returns explicit informative notices.", font_size=12)
    add_bullet(tf_s7, "State Representative Nodes:", "Aggregates state-level queries using weighted centroid plus major urban hubs (e.g., Punjab = Chandigarh + Ludhiana + Amritsar).", font_size=12)

    # =========================================================================
    # SLIDE 8: Autonomous Verification Referee
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, COLOR_BG_LIGHT)
    add_header(s8, "Autonomous Verification Referee", "Patent-Pending Mathematical Refereeing & Hallucination Interceptor")

    # 2 Column Cards
    col_w2 = Inches(5.666)
    add_card(s8, Inches(0.8), Inches(1.6), col_w2, Inches(5.1))
    s8_l = s8.shapes.add_textbox(Inches(1.05), Inches(1.85), col_w2 - Inches(0.5), Inches(4.6))
    tf_s8l = s8_l.text_frame
    tf_s8l.word_wrap = True
    tf_s8l.margin_left = tf_s8l.margin_top = tf_s8l.margin_right = tf_s8l.margin_bottom = 0

    p = tf_s8l.paragraphs[0]
    p.text = "Independent Verification Referee (verifier.py)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL_DARK
    p.space_after = Pt(10)

    add_bullet(tf_s8l, "Independent Verification Shadow:", "The verifier does not trust the LLM or UI synthesizer. It re-computes every statistic independently directly from raw telemetry arrays.")
    add_bullet(tf_s8l, "Strict 10^-6 Numeric Tolerance:", "Verifies that all values in the final report match sensor truth within math.isclose(rel_tol=1e-6). Any divergence aborts output generation.")
    add_bullet(tf_s8l, "Textual Claim Audit:", "Parses the generated response text to ensure no numbers appear in the prose that were not produced by the underlying scientific engine.")
    add_bullet(tf_s8l, "Physical Sanity Boundaries:", "Enforces atmospheric physical constraints (e.g., NO2 column >= 0.0, date ranges within active satellite acquisition lifespan).")

    add_card(s8, Inches(6.866), Inches(1.6), col_w2, Inches(5.1))
    s8_r = s8.shapes.add_textbox(Inches(7.116), Inches(1.85), col_w2 - Inches(0.5), Inches(4.6))
    tf_s8r = s8_r.text_frame
    tf_s8r.word_wrap = True
    tf_s8r.margin_left = tf_s8r.margin_top = tf_s8r.margin_right = tf_s8r.margin_bottom = 0

    p = tf_s8r.paragraphs[0]
    p.text = "Auditability & Full Transparency"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_after = Pt(10)

    add_bullet(tf_s8r, "Inspectable Query Plan:", "Every query renders a collapsible 'How this was verified' drawer showing the exact JSON plan generated by the AI.")
    add_bullet(tf_s8r, "Pipeline Traceability:", "Shows step-by-step pipeline execution logs: coordinate resolution, array slice shapes, and mathematical reduction formulas.")
    add_bullet(tf_s8r, "Verification Checklist Table:", "Renders a live audit table showing: Metric Name | Synthesized Value | Ground Truth Value | Difference | Pass/Fail status.")
    add_bullet(tf_s8r, "Legal & Regulatory Compliance:", "Provides an immutable, tamper-evident audit record suitable for environmental litigation, CPCB audits, and scientific peer review.")

    # =========================================================================
    # SLIDE 9: Human-Centric UI & Interactive Altair Visualization
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, COLOR_BG_LIGHT)
    add_header(s9, "Frontend User Experience", "Clean Human-Centric Streamlit UI & Interactive Visualizations")

    # 4 Cards Grid (2x2)
    gw = Inches(5.666)
    gh = Inches(2.4)
    gy1 = Inches(1.6)
    gy2 = Inches(4.3)

    # Box 1: Design Principles
    add_card(s9, Inches(0.8), gy1, gw, gh)
    b1 = s9.shapes.add_textbox(Inches(1.05), gy1 + Inches(0.2), gw - Inches(0.5), gh - Inches(0.4))
    tf1 = b1.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_top = tf1.margin_right = tf1.margin_bottom = 0
    p = tf1.paragraphs[0]
    p.text = "Human Designer Aesthetics"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_after = Pt(6)
    add_bullet(tf1, "Clean Light Theme:", "Off-white background (#FAFAF7), crisp cards (#FFFFFF), dark charcoal typography (#1F2933), and deep teal accent (#0F766E).", font_size=11)
    add_bullet(tf1, "No AI Clichés:", "Eliminated neon glows, glassmorphism, decorative emojis in headings, and sci-fi 'Command Center' jargon.", font_size=11)

    # Box 2: Visualizations
    add_card(s9, Inches(6.866), gy1, gw, gh)
    b2 = s9.shapes.add_textbox(Inches(7.116), gy1 + Inches(0.2), gw - Inches(0.5), gh - Inches(0.4))
    tf2 = b2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = tf2.margin_top = tf2.margin_right = tf2.margin_bottom = 0
    p = tf2.paragraphs[0]
    p.text = "Interactive Altair Visualizations"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL_DARK
    p.space_after = Pt(6)
    add_bullet(tf2, "Observation vs Interpolation:", "Real satellite points rendered with solid markers; cloudy days rendered with subtle dashed lines.", font_size=11)
    add_bullet(tf2, "Direct End-of-Line Labels:", "Eliminates cluttered legends in multi-city comparisons using direct labels and colorblind-safe palettes.", font_size=11)

    # Box 3: Layout Structure
    add_card(s9, Inches(0.8), gy2, gw, gh)
    b3 = s9.shapes.add_textbox(Inches(1.05), gy2 + Inches(0.2), gw - Inches(0.5), gh - Inches(0.4))
    tf3 = b3.text_frame
    tf3.word_wrap = True
    tf3.margin_left = tf3.margin_top = tf3.margin_right = tf3.margin_bottom = 0
    p = tf3.paragraphs[0]
    p.text = "Answer & Metric Card Hierarchy"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_after = Pt(6)
    add_bullet(tf3, "Executive Summary First:", "Concise natural language answer appears immediately at the top for busy decision-makers.", font_size=11)
    add_bullet(tf3, "Key Metrics Row:", "Displays 4 crisp metric cards: Latest Value, 30-Day Mean, % Change, and Data Confidence Level.", font_size=11)

    # Box 4: Reliability
    add_card(s9, Inches(6.866), gy2, gw, gh)
    b4 = s9.shapes.add_textbox(Inches(7.116), gy2 + Inches(0.2), gw - Inches(0.5), gh - Inches(0.4))
    tf4 = b4.text_frame
    tf4.word_wrap = True
    tf4.margin_left = tf4.margin_top = tf4.margin_right = tf4.margin_bottom = 0
    p = tf4.paragraphs[0]
    p.text = "Production Reliability & Zero Warnings"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER
    p.space_after = Pt(6)
    add_bullet(tf4, "Modern Streamlit API:", "Replaced deprecated use_container_width with width='stretch', zero terminal warnings.", font_size=11)
    add_bullet(tf4, "Fast Resource Caching:", "Telemetric grid cached in RAM via @st.cache_resource; subsequent queries execute with zero I/O overhead.", font_size=11)

    # =========================================================================
    # SLIDE 10: Empirical Benchmarks & Test Suite
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, COLOR_BG_LIGHT)
    add_header(s10, "Empirical Validation & Benchmarks", "System Verification Results, Unit Tests & Latency Analysis")

    # Table on Left
    rows = 6
    cols = 4
    left = Inches(0.8)
    top = Inches(1.6)
    width = Inches(7.5)
    height = Inches(4.8)

    table_shape = s10.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    table.columns[0].width = Inches(2.4)
    table.columns[1].width = Inches(1.8)
    table.columns[2].width = Inches(1.8)
    table.columns[3].width = Inches(1.5)

    headers = ["Evaluation Metric", "Target Standard", "SkyQueryChat", "Status"]
    data = [
        ["Unit Test Suite", "100% Pass", "18 / 18 Tests Passed", "VERIFIED"],
        ["Demo Query Suite", "100% Pass", "19 / 19 Queries Passed", "VERIFIED"],
        ["Numeric Assertions", "Zero Discrepancy", "1,541 / 1,541 Exact", "VERIFIED"],
        ["Groq Plan Latency", "< 2.0 Seconds", "840 ms (Median)", "PASS"],
        ["Engine Math Latency", "< 10 Milliseconds", "1.4 ms (Average)", "OPTIMAL"],
    ]

    for col_idx, text in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.text = text
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_CARD_DARK
        for p in cell.text_frame.paragraphs:
            p.alignment = PP_ALIGN.CENTER if col_idx > 0 else PP_ALIGN.LEFT
            for r in p.runs:
                r.font.name = FONT_HEADING
                r.font.size = Pt(11)
                r.font.bold = True
                r.font.color.rgb = COLOR_TEXT_LIGHT

    for row_idx, row_data in enumerate(data, start=1):
        for col_idx, val in enumerate(row_data):
            cell = table.cell(row_idx, col_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_CARD_LIGHT if row_idx % 2 == 1 else COLOR_BG_LIGHT
            for p in cell.text_frame.paragraphs:
                p.alignment = PP_ALIGN.CENTER if col_idx > 0 else PP_ALIGN.LEFT
                for r in p.runs:
                    r.font.name = FONT_BODY
                    r.font.size = Pt(10)
                    if col_idx == 3:
                        r.font.bold = True
                        r.font.color.rgb = COLOR_TEAL_DARK
                    else:
                        r.font.color.rgb = COLOR_TEXT_DARK

    # Right Card: Verification Summary
    add_card(s10, Inches(8.6), Inches(1.6), Inches(3.933), Inches(4.8))
    s10_r = s10.shapes.add_textbox(Inches(8.85), Inches(1.85), Inches(3.433), Inches(4.3))
    tf10r = s10_r.text_frame
    tf10r.word_wrap = True
    tf10r.margin_left = tf10r.margin_top = tf10r.margin_right = tf10r.margin_bottom = 0

    p = tf10r.paragraphs[0]
    p.text = "Benchmark Highlights"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL_DARK
    p.space_after = Pt(10)

    add_bullet(tf10r, "Zero Hallucination Rate:", "Evaluated against 1,541 numeric checks across Indian states; 0 ungrounded claims detected.", font_size=11)
    add_bullet(tf10r, "Rapid Fallback:", "Rule planner resolves ambiguous or rate-limited inputs in 28 milliseconds with 100% reliability.", font_size=11)
    add_bullet(tf10r, "Full Geographic Range:", "Verified across northern plains (Delhi, Punjab), coastal hubs (Mumbai, Chennai), and eastern zones (Kolkata).", font_size=11)
    add_bullet(tf10r, "Memory Footprint:", "RAM consumption stays below 280MB even with 120-day satellite cubes loaded in RAM.", font_size=11)

    # =========================================================================
    # SLIDE 11: Innovation & Patent Claims
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, COLOR_BG_LIGHT)
    add_header(s11, "Intellectual Property & Patent Disclosure", "Summary of Patent Claims (LPU Annexure 3b Invention Disclosure)")

    col_w3 = Inches(5.666)
    add_card(s11, Inches(0.8), Inches(1.6), col_w3, Inches(5.1))
    s11_l = s11.shapes.add_textbox(Inches(1.05), Inches(1.85), col_w3 - Inches(0.5), Inches(4.6))
    tf11l = s11_l.text_frame
    tf11l.word_wrap = True
    tf11l.margin_left = tf11l.margin_top = tf11l.margin_right = tf11l.margin_bottom = 0

    p = tf11l.paragraphs[0]
    p.text = "Core Patentable Claims"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL_DARK
    p.space_after = Pt(10)

    add_bullet(tf11l, "Claim 1 (Decoupled Dual-Brain):", "An agentic conversational system that translates natural queries into an intermediate abstract syntax tree (QueryPlan) without direct telemetry access, guaranteeing mathematical determinism.")
    add_bullet(tf11l, "Claim 2 (Autonomous Mathematical Referee):", "A verification referee executing in a shadow thread that independently recalculates query statistics and enforces a 10^-6 relative tolerance constraint.")
    add_bullet(tf11l, "Claim 3 (Hybrid Fallback Switching):", "A failover mechanism that detects LLM latency, rate-limit, or token degradation and seamlessly shifts to compiled deterministic regex planners in < 30ms.")

    add_card(s11, Inches(6.866), Inches(1.6), col_w3, Inches(5.1))
    s11_r = s11.shapes.add_textbox(Inches(7.116), Inches(1.85), col_w3 - Inches(0.5), Inches(4.6))
    tf11r = s11_r.text_frame
    tf11r.word_wrap = True
    tf11r.margin_left = tf11r.margin_top = tf11r.margin_right = tf11r.margin_bottom = 0

    p = tf11r.paragraphs[0]
    p.text = "Comparative Prior Art Advantages"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_after = Pt(10)

    add_bullet(tf11r, "vs. NASA Giovanni / Worldview:", "Traditional portals require manual parameter selection, visual inspection, and manual file export. SkyQueryChat answers complex questions conversationally in seconds.")
    add_bullet(tf11r, "vs. Generic LLMs (ChatGPT / Claude):", "Generic models lack spatial indexation, cannot read HDF5/NetCDF arrays, and hallucinate plausible numbers. SkyQueryChat achieves 100% mathematical fidelity.")
    add_bullet(tf11r, "vs. Standard Code Interpreters:", "Code interpreters execute unconstrained Python scripts with high vulnerability and latency. SkyQueryChat enforces strict mathematical contracts via predefined primitives.")

    # =========================================================================
    # SLIDE 12: Project Summary & Future Scope (Dark Hero)
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, COLOR_BG_DARK)

    # Decorative top bar
    bar = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.1))
    bar.fill.solid()
    bar.fill.fore_color.rgb = COLOR_TEAL_LIGHT
    bar.line.fill.background()

    # Header Box
    h_box12 = s12.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.733), Inches(1.2))
    tf12_h = h_box12.text_frame
    tf12_h.word_wrap = True
    tf12_h.margin_left = tf12_h.margin_top = tf12_h.margin_right = tf12_h.margin_bottom = 0

    p = tf12_h.paragraphs[0]
    p.text = "CONCLUSION & FUTURE HORIZONS"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL_LIGHT
    p.space_after = Pt(4)

    p = tf12_h.add_paragraph()
    p.text = "Production-Grade Air Quality Intelligence for India"
    p.font.name = FONT_HEADING
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_LIGHT

    # Left Card: Summary & Repository
    add_card(s12, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.7), bg_color=COLOR_CARD_DARK, border_color=COLOR_BORDER_DARK)
    s12_l = s12.shapes.add_textbox(Inches(1.1), Inches(2.2), Inches(5.0), Inches(4.3))
    tf12_l = s12_l.text_frame
    tf12_l.word_wrap = True
    tf12_l.margin_left = tf12_l.margin_top = tf12_l.margin_right = tf12_l.margin_bottom = 0

    p = tf12_l.paragraphs[0]
    p.text = "PROJECT METADATA & REPOSITORY"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL_LIGHT
    p.space_after = Pt(10)

    add_bullet(tf12_l, "Principal Researcher:", "paulsonsanio", font_size=13, is_dark=True)
    add_bullet(tf12_l, "University Reg No:", "12313062", font_size=13, is_dark=True)
    add_bullet(tf12_l, "Department:", "Computer Science & Engineering", font_size=13, is_dark=True)
    add_bullet(tf12_l, "Institution:", "Lovely Professional University, Punjab-144411", font_size=13, is_dark=True)

    p_repo = tf12_l.add_paragraph()
    p_repo.space_after = Pt(4)
    run_r1 = p_repo.add_run()
    run_r1.text = "GitHub Repository: "
    run_r1.font.name = FONT_BODY
    run_r1.font.size = Pt(12)
    run_r1.font.bold = True
    run_r1.font.color.rgb = COLOR_AMBER

    p_url = tf12_l.add_paragraph()
    p_url.space_after = Pt(10)
    run_r2 = p_url.add_run()
    run_r2.text = "https://github.com/Paulsonsanio/SkyQueryChat-NL-Interface-for-Air-Quality-Data"
    run_r2.font.name = FONT_BODY
    run_r2.font.size = Pt(10)
    run_r2.font.color.rgb = COLOR_TEAL_LIGHT
    run_r2.hyperlink.address = "https://github.com/Paulsonsanio/SkyQueryChat-NL-Interface-for-Air-Quality-Data"

    add_bullet(tf12_l, "Patent Application:", "Indian Patent Office (Invention Disclosure Annexure 3b Filed)", font_size=12, is_dark=True)

    # Right Card: Future Scope
    add_card(s12, Inches(6.8), Inches(2.0), Inches(5.733), Inches(4.7), bg_color=COLOR_CARD_DARK, border_color=COLOR_BORDER_DARK)
    s12_r = s12.shapes.add_textbox(Inches(7.1), Inches(2.2), Inches(5.133), Inches(4.3))
    tf12_r = s12_r.text_frame
    tf12_r.word_wrap = True
    tf12_r.margin_left = tf12_r.margin_top = tf12_r.margin_right = tf12_r.margin_bottom = 0

    p = tf12_r.paragraphs[0]
    p.text = "FUTURE RESEARCH & INDUSTRIAL EXPANSION"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER
    p.space_after = Pt(10)

    add_bullet(tf12_r, "Multi-Pollutant Telemetry Expansion:", "Extend pipeline to Sentinel-5P TROPOMI Level-2 Methane (CH4), Carbon Monoxide (CO), and Sulfur Dioxide (SO2) matrices.", font_size=12, is_dark=True)
    add_bullet(tf12_r, "In-Situ Ground Sensor Fusion:", "Combine spaceborne columns with CPCB Continuous Ambient Air Quality Monitoring Stations (CAAQMS) via Kalman filtering.", font_size=12, is_dark=True)
    add_bullet(tf12_r, "Automated Public Policy Webhooks:", "Integrate autonomous anomaly alerting for Smart City municipal corporations and environmental regulatory bodies.", font_size=12, is_dark=True)
    add_bullet(tf12_r, "Voice & Multilingual Interface:", "Enable localized spoken conversational interfaces across regional Indian languages (Hindi, Punjabi, Tamil, Bengali).", font_size=12, is_dark=True)

    # Save presentation
    output_path = os.path.abspath("SkyQueryChat_Presentation.pptx")
    prs.save(output_path)
    print(f"Presentation PPTX successfully generated at: {output_path}")

if __name__ == "__main__":
    build_presentation()
