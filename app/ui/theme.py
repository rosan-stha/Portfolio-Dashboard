"""CSS injection — TradingView dark theme."""
import streamlit as st

from app.config import BG, CARD, BORDER, TEXT, MUTED, BLUE


def inject() -> None:
    """Inject the global stylesheet. Call once, right after st.set_page_config."""
    st.markdown(f"""
<style>
/* ── Base ── */
html, body, [class*="css"] {{
    font-family: 'Inter', 'Trebuchet MS', sans-serif;
    background-color: {BG};
    color: {TEXT};
}}
.stApp {{ background-color: {BG}; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background-color: {CARD};
    border-right: 1px solid {BORDER};
}}

/* ── Metric cards ── */
[data-testid="metric-container"] {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 18px 22px;
}}
[data-testid="stMetricValue"] {{
    color: {TEXT};
    font-size: 1.35rem;
    font-weight: 700;
}}
[data-testid="stMetricLabel"] {{
    color: {MUTED};
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.09em;
}}

/* ── Tabs ── */
[data-testid="stTabs"] button {{
    color: {MUTED};
    font-size: 0.85rem;
    background: none;
    border: none;
}}
[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {TEXT};
    border-bottom: 2px solid {BLUE};
    font-weight: 600;
}}

/* ── Upload zone ── */
[data-testid="stFileUploadDropzone"] {{
    background-color: {CARD};
    border: 2px dashed {BLUE};
    border-radius: 10px;
}}

/* ── Divider ── */
hr {{ border-color: {BORDER}; }}

/* ── Headings ── */
h1, h2, h3 {{ color: {TEXT}; font-weight: 700; }}

/* ── Small uppercase section labels ── */
.lbl {{
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {MUTED};
    margin-bottom: 6px;
    font-family: 'Space Mono', 'Courier New', monospace;
}}

/* ── HTML data tables ── */
.ptable {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
}}
.ptable th {{
    background-color: {BORDER};
    color: {MUTED};
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-size: 0.68rem;
    padding: 9px 14px;
    text-align: left;
    white-space: nowrap;
    border-bottom: 1px solid #363a4a;
}}
.ptable td {{
    padding: 8px 14px;
    border-bottom: 1px solid {BORDER};
    color: {TEXT};
    background-color: {BG};
}}
.ptable tr:hover td {{ background-color: {CARD}; }}
.ptable .tot td {{
    background-color: {BORDER};
    font-weight: 700;
    border-top: 2px solid #363a4a;
}}

/* ── Data editor (ticker mapping) ── */
[data-testid="stDataFrame"] {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
</style>
""", unsafe_allow_html=True)
