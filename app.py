"""SkyQueryChat Web UI — Clean Light Theme.

Run with:
    streamlit run app.py
"""
from __future__ import annotations
import os
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Sync Streamlit Cloud secrets into os.environ
try:
    if hasattr(st, "secrets"):
        for k, v in st.secrets.items():
            if isinstance(v, (str, int, float, bool)):
                os.environ.setdefault(str(k), str(v))
            elif isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    if isinstance(sub_v, (str, int, float, bool)):
                        os.environ.setdefault(str(sub_k), str(sub_v))
except Exception:
    pass

from skyquery.agent import SkyQueryAgent
from skyquery.planner import LLMPlanner
from skyquery.store import GridStore, ensure_data

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SkyQueryChat",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Clean Human-Designed Light Theme CSS
# -----------------------------------------------------------------------------
# Color palette:
#   Off-white page: #FAFAF7
#   White cards:    #FFFFFF
#   Charcoal text:  #1F2933
#   Accent:         #0F766E (deep teal)
#   Warning:        #B45309 (amber)
#   Border:         #E5E7EB (light gray)
#   Muted gray:     #6B7280
CUSTOM_CSS = """
<style>
/* Global Font & Background */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    color: #1F2933 !important;
    background-color: #FAFAF7 !important;
}

.stApp {
    background-color: #FAFAF7 !important;
}

/* Page Header Hierarchy */
.app-header {
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid #E5E7EB;
}

.app-title {
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #1F2933 !important;
    margin: 0 0 4px 0 !important;
    letter-spacing: -0.02em;
}

.app-subtitle {
    font-size: 15px !important;
    color: #6B7280 !important;
    margin: 0 !important;
    line-height: 1.5 !important;
}

/* Section Headings */
h1, h2, h3, h4 {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: #1F2933 !important;
    font-weight: 600 !important;
}

h3 {
    font-size: 18px !important;
    margin-top: 16px !important;
    margin-bottom: 12px !important;
}

/* Sidebar Customization */
[data-testid="stSidebar"] {
    background-color: #F4F4F0 !important;
    border-right: 1px solid #E5E7EB !important;
    padding-top: 24px !important;
}

[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #1F2933 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin-bottom: 8px !important;
}

[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background-color: #FFFFFF !important;
    color: #1F2933 !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 6px !important;
    padding: 8px 12px !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    text-align: left !important;
    margin-bottom: 6px !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #FAFAF7 !important;
    border-color: #0F766E !important;
    color: #0F766E !important;
}

/* Chat Input Bar */
[data-testid="stChatInput"] {
    border-color: #E5E7EB !important;
    background-color: #FFFFFF !important;
    border-radius: 8px !important;
}

[data-testid="stChatInput"] textarea {
    color: #1F2933 !important;
    font-size: 15px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #9CA3AF !important;
}

/* Chat Messages */
[data-testid="stChatMessage"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    padding: 16px !important;
    margin-bottom: 16px !important;
}

/* Metric Cards */
.metric-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 12px;
}

.metric-label {
    font-size: 13px;
    color: #6B7280;
    font-weight: 500;
    margin-bottom: 4px;
}

.metric-value {
    font-size: 22px;
    font-weight: 600;
    color: #1F2933;
    line-height: 1.2;
}

.metric-delta {
    font-size: 12px;
    margin-top: 4px;
    font-weight: 500;
}

.metric-delta.positive {
    color: #B45309;
}

.metric-delta.negative {
    color: #0F766E;
}

.metric-delta.neutral {
    color: #6B7280;
}

/* Out-of-scope Calm Box */
.calm-notice-box {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-left: 3px solid #B45309;
    border-radius: 8px;
    padding: 16px;
    margin: 12px 0;
}

.calm-notice-text {
    font-size: 15px;
    color: #1F2933;
    line-height: 1.5;
    margin-bottom: 12px;
}

.calm-notice-heading {
    font-size: 13px;
    font-weight: 600;
    color: #6B7280;
    margin-bottom: 6px;
}

/* Collapsible Expander */
[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    margin-top: 16px !important;
}

[data-testid="stExpander"] summary {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #1F2933 !important;
    padding: 10px 14px !important;
}

/* Code & JSON styling */
code {
    background-color: #F4F4F0 !important;
    color: #0F766E !important;
    border: 1px solid #E5E7EB !important;
    padding: 2px 5px !important;
    border-radius: 4px !important;
    font-size: 13px !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Resource Caching & Fail-Safe Agent Loading
# -----------------------------------------------------------------------------
@st.cache_resource
def get_store() -> GridStore:
    return GridStore(ensure_data())


@st.cache_resource
def get_agent(use_llm: bool, groq_key_hash: str = "") -> SkyQueryAgent:
    store = get_store()
    llm = LLMPlanner() if use_llm else LLMPlanner("none")
    return SkyQueryAgent(store=store, llm=llm)


def get_llm_probe() -> tuple[LLMPlanner, str]:
    planner = LLMPlanner("auto")
    status = planner.startup_self_test() if planner.available else "No API key configured"
    return planner, status


# -----------------------------------------------------------------------------
# Chart Helpers (Altair 6.x)
# -----------------------------------------------------------------------------
def build_trend_chart(row: dict, intent: str) -> alt.Chart | None:
    """Builds a daily NO2 line chart with area fill, observation dots, baseline, and peak."""
    # Select series: context_series (30d) if available and intent == 'current', else series
    series = row.get("context_series") if (intent == "current" and row.get("context_series")) else row.get("series")
    if not series:
        return None

    dates = [s[0] for s in series]
    vals = [(s[1] / 1e15 if s[1] is not None else np.nan) for s in series]

    df = pd.DataFrame({"date": pd.to_datetime(dates), "raw_val": vals})
    if df["raw_val"].isna().all():
        return None

    # Time-weighted interpolation across observation gaps
    df_idx = df.set_index("date")
    df["interpolated"] = df_idx["raw_val"].interpolate(method="time").bfill().ffill().values
    df["status"] = np.where(df["raw_val"].notna(), "Observed retrieval", "Cloudy (interpolated)")

    # 1. Subtle light area fill
    area = alt.Chart(df).mark_area(
        opacity=0.08,
        color="#0F766E",
    ).encode(
        x=alt.X("date:T", axis=alt.Axis(title="Date", grid=False, domainColor="#E5E7EB", tickColor="#E5E7EB", labelColor="#6B7280", titleColor="#1F2933")),
        y=alt.Y("interpolated:Q", axis=alt.Axis(title="NO₂ (10¹⁵ molecules/cm²)", grid=True, gridColor="#E5E7EB", domain=False, labelColor="#6B7280", titleColor="#1F2933")),
    )

    # 2. Daily line curve
    line = alt.Chart(df).mark_line(
        color="#0F766E",
        strokeWidth=2,
    ).encode(
        x="date:T",
        y="interpolated:Q",
    )

    # 3. Observation dots: distinct styling for real observation vs interpolated cloudy days
    points = alt.Chart(df).mark_circle(size=45).encode(
        x="date:T",
        y="interpolated:Q",
        color=alt.Color(
            "status:N",
            scale=alt.Scale(
                domain=["Observed retrieval", "Cloudy (interpolated)"],
                range=["#0F766E", "#9CA3AF"],
            ),
            legend=alt.Legend(
                title=None,
                orient="top-right",
                labelFontSize=12,
                symbolSize=45,
                labelColor="#1F2933",
            ),
        ),
        tooltip=[
            alt.Tooltip("date:T", title="Date", format="%b %d, %Y"),
            alt.Tooltip("interpolated:Q", title="NO₂ (10¹⁵ mol/cm²)", format=".2f"),
            alt.Tooltip("status:N", title="Status"),
        ],
    )

    layers = [area, line, points]

    # 4. Dashed line for 30-day baseline mean if present
    mean_val = row.get("context_mean") or row.get("mean")
    if mean_val is not None:
        mean_scaled = mean_val / 1e15
        mean_df = pd.DataFrame({"mean": [mean_scaled], "label": ["30-day baseline mean"]})
        mean_rule = alt.Chart(mean_df).mark_rule(
            color="#B45309",
            strokeDash=[4, 4],
            strokeWidth=1.5,
        ).encode(y="mean:Q")
        layers.append(mean_rule)

    # 5. Highlight Peak Day with marker and text annotation
    if row.get("peak_date") and row.get("peak_value") is not None:
        peak_df = pd.DataFrame({
            "date": [pd.to_datetime(row["peak_date"])],
            "val": [row["peak_value"] / 1e15],
            "label": [f"Peak: {row['peak_value'] / 1e15:.2f}"],
        })
        peak_point = alt.Chart(peak_df).mark_circle(
            size=90,
            color="#B45309",
            stroke="#FFFFFF",
            strokeWidth=2,
        ).encode(
            x="date:T",
            y="val:Q",
            tooltip=[
                alt.Tooltip("date:T", title="Peak Date", format="%b %d, %Y"),
                alt.Tooltip("val:Q", title="Peak Value", format=".2f"),
            ],
        )
        peak_text = alt.Chart(peak_df).mark_text(
            align="center",
            dy=-14,
            fontSize=11,
            fontWeight=600,
            color="#B45309",
        ).encode(
            x="date:T",
            y="val:Q",
            text="label:N",
        )
        layers.extend([peak_point, peak_text])

    combined = alt.layer(*layers).properties(
        height=340,
    ).configure_view(
        strokeWidth=0,
    )
    return combined


def build_compare_chart(rows: list[dict]) -> alt.Chart | None:
    """Builds a multi-city comparison line chart with direct end-of-line labels."""
    records = []
    for r in rows[:6]:
        loc = r["location"]
        series = r.get("series") or []
        for d, v in series:
            records.append({
                "date": pd.to_datetime(d),
                "location": loc,
                "value": (v / 1e15 if v is not None else np.nan),
            })

    if not records:
        return None

    df = pd.DataFrame(records)
    if df["value"].isna().all():
        return None

    # Interpolate gaps per location
    df_clean = []
    for loc, group in df.groupby("location"):
        g = group.sort_values("date").set_index("date")
        g["value"] = g["value"].interpolate(method="time").bfill().ffill()
        df_clean.append(g.reset_index())
    df_plot = pd.concat(df_clean, ignore_index=True)

    # Colorblind-safe palette (teal, blue, amber, purple, green, red)
    palette = ["#0F766E", "#2563EB", "#D97706", "#7C3AED", "#059669", "#DC2626"]

    lines = alt.Chart(df_plot).mark_line(strokeWidth=2).encode(
        x=alt.X("date:T", axis=alt.Axis(title="Date", grid=False, domainColor="#E5E7EB", tickColor="#E5E7EB", labelColor="#6B7280", titleColor="#1F2933")),
        y=alt.Y("value:Q", axis=alt.Axis(title="NO₂ (10¹⁵ molecules/cm²)", grid=True, gridColor="#E5E7EB", domain=False, labelColor="#6B7280", titleColor="#1F2933")),
        color=alt.Color("location:N", scale=alt.Scale(range=palette), legend=None),
        tooltip=[
            alt.Tooltip("date:T", title="Date", format="%b %d, %Y"),
            alt.Tooltip("location:N", title="Location"),
            alt.Tooltip("value:Q", title="NO₂ (10¹⁵ mol/cm²)", format=".2f"),
        ],
    )

    # Direct end-of-line labels
    last_pts = df_plot.sort_values("date").groupby("location").last().reset_index()
    labels = alt.Chart(last_pts).mark_text(
        align="left",
        dx=6,
        fontSize=12,
        fontWeight=600,
    ).encode(
        x="date:T",
        y="value:Q",
        text="location:N",
        color=alt.Color("location:N", scale=alt.Scale(range=palette), legend=None),
    )

    return (lines + labels).properties(height=340).configure_view(strokeWidth=0)


def build_rank_chart(ranking: list[str], rows: list[dict]) -> alt.Chart | None:
    """Builds a horizontal sorted bar chart with value labels at bar ends."""
    row_map = {r["location"]: r for r in rows}
    data = []
    for i, name in enumerate(ranking[:10]):
        r = row_map.get(name)
        if r and r.get("mean") is not None:
            data.append({
                "City": name,
                "Value": r["mean"] / 1e15,
                "is_top": (i == 0),
            })

    if not data:
        return None

    df_rank = pd.DataFrame(data)
    bars = alt.Chart(df_rank).mark_bar(
        height=22,
        cornerRadiusEnd=3,
    ).encode(
        y=alt.Y("City:N", sort="-x", axis=alt.Axis(title=None, ticks=False, domain=False, labelFontSize=12, labelColor="#1F2933")),
        x=alt.X("Value:Q", axis=alt.Axis(title="NO₂ (10¹⁵ molecules/cm²)", grid=True, gridColor="#E5E7EB", domain=False, labelColor="#6B7280", titleColor="#1F2933")),
        color=alt.condition(alt.datum.is_top, alt.value("#0F766E"), alt.value("#CBD5E1")),
        tooltip=[
            alt.Tooltip("City:N", title="City"),
            alt.Tooltip("Value:Q", title="Mean NO₂ (10¹⁵)", format=".2f"),
        ],
    )

    labels = alt.Chart(df_rank).mark_text(
        align="left",
        dx=6,
        fontSize=12,
        fontWeight=500,
        color="#1F2933",
    ).encode(
        y=alt.Y("City:N", sort="-x"),
        x="Value:Q",
        text=alt.Text("Value:Q", format=".2f"),
    )

    return (bars + labels).properties(height=max(180, len(df_rank) * 36)).configure_view(strokeWidth=0)


# -----------------------------------------------------------------------------
# Response Presentation Component
# -----------------------------------------------------------------------------
def render_response(resp, message_id: int) -> None:
    """Renders answer text, metric cards, Altair chart, and audit provenance."""
    if resp.planner_used == "rules":
        st.caption("Offline planner used")
    # 1. Out-of-scope / Refusal Handling
    if not resp.ok:
        st.markdown(
            f"""
            <div class="calm-notice-box">
                <div class="calm-notice-text">{resp.answer}</div>
                <div class="calm-notice-heading">Suggested questions to try:</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        sample_cols = st.columns(3)
        suggestions = [
            "Air quality in Punjab",
            "NO2 in Delhi right now",
            "Compare NO2 in Delhi and Mumbai last month",
        ]
        for idx, col in enumerate(sample_cols):
            with col:
                if st.button(suggestions[idx], key=f"sugg_{message_id}_{idx}", width="stretch"):
                    st.session_state["pending_query"] = suggestions[idx]
                    st.rerun()

        # Audit expander even for errors (provenance)
        with st.expander("How this was verified", expanded=False):
            st.markdown(f"**Planner:** `{resp.planner_used}`")
            if resp.plan:
                st.json(resp.plan)
            st.markdown("**Pipeline Steps:**")
            for step in resp.trace:
                st.markdown(f"- `{step['step']}`: {step['detail']}")
        return

    # 2. Answer text first
    st.markdown(resp.answer)

    # 3. Metric cards (2-4 cards)
    result = resp.result or {}
    rows = result.get("rows", [])
    intent = result.get("intent", "answer")

    if rows:
        num_cards = min(len(rows), 4)
        cols = st.columns(num_cards)
        for i in range(num_cards):
            r = rows[i]
            loc_name = r["location"]
            latest_val = r.get("latest_value") or r.get("mean")
            val_fmt = f"{latest_val / 1e15:.2f} ×10¹⁵" if latest_val is not None else "N/A"

            delta_str = "No baseline"
            delta_class = "neutral"

            if r.get("context_mean") and latest_val is not None:
                pct = (latest_val - r["context_mean"]) / r["context_mean"] * 100
                delta_str = f"{pct:+.1f}% vs 30d baseline"
                delta_class = "positive" if pct > 0 else "negative"
            elif r.get("change_pct") is not None:
                pct = r["change_pct"]
                delta_str = f"{pct:+.1f}% trend"
                delta_class = "positive" if pct > 0 else "negative"

            mean_val = r.get("context_mean") or r.get("mean")
            mean_fmt = f"{mean_val / 1e15:.2f} ×10¹⁵" if mean_val is not None else "N/A"

            with cols[i]:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">{loc_name}</div>
                        <div class="metric-value">{val_fmt}</div>
                        <div class="metric-delta {delta_class}">{delta_str}</div>
                        <div style="font-size: 11px; color: #6B7280; margin-top: 6px;">30d Mean: {mean_fmt}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # 4. Chart rendering
    chart = None
    if intent == "rank" and result.get("ranking"):
        chart = build_rank_chart(result["ranking"], rows)
    elif intent == "compare" and len(rows) >= 2:
        chart = build_compare_chart(rows)
    elif rows:
        chart = build_trend_chart(rows[0], intent)

    if chart is not None:
        st.altair_chart(chart, width="stretch")
    elif resp.ok and not rows:
        st.info("No satellite observations available for this selection.")

    # 5. Collapsed "How this was verified" expander
    with st.expander("How this was verified", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Planner:** `{resp.planner_used}`")
            if resp.plan:
                st.json(resp.plan)
        with c2:
            st.markdown("**Pipeline Steps:**")
            for step in resp.trace:
                st.markdown(f"- `{step['step']}`: {step['detail']}")

        if resp.verification and resp.verification.get("checks"):
            st.markdown("**Independent Math Checks (Pure-Python Re-computation):**")
            df_checks = pd.DataFrame(resp.verification["checks"])
            st.dataframe(df_checks, width="stretch")


# -----------------------------------------------------------------------------
# Sidebar Configuration Panel
# -----------------------------------------------------------------------------
store = get_store()
groq_key_val = os.environ.get("GROQ_API_KEY", "")
llm_probe, groq_status = get_llm_probe()

with st.sidebar:
    st.markdown("### Configuration")

    if not llm_probe.available:
        st.info("💡 **LLM Planner is offline.** Enter your API Key below to activate it:")
        user_key = st.text_input(
            "API Key (Groq or OpenAI)",
            type="password",
            placeholder="gsk_... or sk-...",
            help="Enter a Groq (gsk_...) or OpenAI (sk-...) API key, or add it to Streamlit Cloud Settings → Secrets.",
            key="sidebar_api_key_input",
        )
        if user_key and user_key.strip():
            k = user_key.strip()
            if k.startswith("gsk_"):
                os.environ["GROQ_API_KEY"] = k
                os.environ["SKYQUERY_PROVIDER"] = "groq"
            else:
                os.environ["OPENAI_API_KEY"] = k
                os.environ["SKYQUERY_PROVIDER"] = "openai"
            st.rerun()

    use_llm = st.toggle(
        "Use LLM planner",
        value=llm_probe.available,
        disabled=not llm_probe.available,
        help="When enabled, queries are planned by the LLM. If disabled or unavailable, the offline rule planner is used.",
    )

    active_planner_name = llm_probe.name if (use_llm and llm_probe.available) else "RulePlanner (offline)"
    st.markdown(f"**Active planner:** `{active_planner_name}`")
    st.markdown(f"**Data period:** {store.first_date} to {store.last_date}")
    st.markdown(f"**Coverage:** {store.bounds_text()}")
    st.markdown(f"**Source:** {store.source}")
    st.markdown(f"**Valid grid cells:** {store.valid_cell_count}")
    if store.is_synthetic:
        st.warning("Demo synthetic data")
    if llm_probe.available and groq_status != "OK":
        st.caption(f"Groq self-test: {groq_status}")

    st.markdown("---")
    st.markdown("### Example Questions")
    example_list = [
        "Air quality in Punjab",
        "NO2 in Delhi right now",
        "Compare NO2 in Delhi and Mumbai last month",
        "Rank the top 5 most polluted cities in India",
        "Worst day for NO2 in Bengaluru in September",
        "Is NO2 in Mumbai rising over the last 60 days?",
        "Average NO2 in Kolkata last week",
        "what is PM2.5 in Delhi",
    ]

    clicked_example = None
    for ex in example_list:
        if st.button(ex, width="stretch"):
            clicked_example = ex

    st.markdown("---")
    if st.button("Clear chat", width="stretch"):
        st.session_state["history"] = []
        st.rerun()


# -----------------------------------------------------------------------------
# Main Application Header
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="app-header">
        <div class="app-title">SkyQueryChat</div>
        <div class="app-subtitle">Ask questions about satellite NO2 over India</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Session State & Conversation Display
# -----------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

for message_id, item in enumerate(st.session_state.history):
    with st.chat_message("user"):
        st.write(item["q"])
    with st.chat_message("assistant"):
        render_response(item["r"], message_id)


# -----------------------------------------------------------------------------
# Query Execution & Error Handling
# -----------------------------------------------------------------------------
# Check pending query from suggestion buttons or clicked sidebar example
pending_q = st.session_state.pop("pending_query", None)
user_input = st.chat_input("Ask a question about satellite NO₂…")
active_query = pending_q or clicked_example or user_input

if active_query:
    with st.chat_message("user"):
        st.write(active_query)

    # Initialize agent with fail-safe fallback
    agent = get_agent(bool(use_llm and llm_probe.available), groq_key_val)

    try:
        with st.spinner("Analyzing satellite data..."):
            response = agent.ask(active_query)
    except Exception as exc:
        # Wrap LLM call so that if Groq fails, it falls back to RulePlanner
        fallback_agent = SkyQueryAgent(store=store, llm=LLMPlanner("none"))
        response = fallback_agent.ask(active_query)
        response.trace.append({
            "step": "offline_fallback",
            "detail": f"Switched to offline planner due to API error: {exc}",
        })

    st.session_state.history.append({"q": active_query, "r": response})

    with st.chat_message("assistant"):
        render_response(response, len(st.session_state.history) - 1)
