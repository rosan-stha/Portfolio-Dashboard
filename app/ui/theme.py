"""CSS injection — Portfolio Intelligence warm financial-pro theme."""
import streamlit as st

from app.config import ACCENT, BG, BG2, BORDER, CARD, GREEN, MUTED, RED, TEXT


def inject() -> None:
    """Inject the global stylesheet. Call once, right after st.set_page_config."""
    st.markdown(f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Sans+JP:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Serif:wght@400;500;600&display=swap" rel="stylesheet">
<style>
/* ── Base ── */
html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', 'IBM Plex Sans JP', system-ui, sans-serif;
    background-color: {BG};
    color: {TEXT};
    font-size: 14px;
    -webkit-font-smoothing: antialiased;
}}
.stApp {{ background-color: {BG}; }}
.main .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background-color: {CARD};
    border-right: 1px solid {BORDER};
}}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {{
    color: {TEXT};
}}

/* ── Metric cards ── */
[data-testid="metric-container"] {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 14px 16px;
}}
[data-testid="stMetricValue"] {{
    color: {TEXT};
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 1.2rem;
    font-weight: 500;
    letter-spacing: -0.02em;
}}
[data-testid="stMetricLabel"] {{
    color: {MUTED};
    font-size: 0.62rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}
[data-testid="stMetricDelta"] {{
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 0.78rem;
}}

/* ── Tabs ── */
[data-testid="stTabs"] button {{
    color: {MUTED};
    font-size: 0.84rem;
    font-weight: 500;
    background: none;
    border: none;
    letter-spacing: -0.005em;
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
}}
[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {TEXT};
    border-bottom: 2px solid {ACCENT};
    font-weight: 600;
}}
[data-testid="stTabsContent"] {{
    padding-top: 1.25rem;
}}

/* ── Upload zone ── */
[data-testid="stFileUploadDropzone"] {{
    background-color: {CARD};
    border: 1px dashed {BORDER};
    border-radius: 4px;
}}

/* ── Divider ── */
hr {{ border-color: {BORDER}; opacity: 1; }}

/* ── Headings ── */
h1, h2, h3 {{
    color: {TEXT};
    font-weight: 700;
    letter-spacing: -0.02em;
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
}}

/* ── Eyebrow / uppercase section label ── */
.lbl {{
    font-size: 0.62rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: {MUTED};
    margin-bottom: 6px;
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
}}

/* ── Brand header bar ── */
.brand-bar {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 14px;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 20px;
}}
.brand-logo {{
    width: 28px;
    height: 28px;
    border-radius: 4px;
    background: {TEXT};
    color: {CARD};
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: 'IBM Plex Serif', Georgia, serif;
    font-weight: 700;
    font-size: 14px;
    flex-shrink: 0;
    line-height: 1;
}}
.brand-title {{
    font-size: 13.5px;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: {TEXT};
    line-height: 1.15;
}}
.brand-sub {{
    font-size: 10.5px;
    color: {MUTED};
    letter-spacing: 0.04em;
}}
.brand-divider {{
    width: 1px;
    height: 22px;
    background: {BORDER};
    margin: 0 2px;
}}

/* ── HTML data tables ── */
.ptable {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
}}
.ptable th {{
    background-color: {BG2};
    color: {MUTED};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.62rem;
    font-weight: 600;
    padding: 8px 12px;
    text-align: left;
    white-space: nowrap;
    border-bottom: 1px solid {BORDER};
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
}}
.ptable td {{
    padding: 9px 12px;
    border-bottom: 1px solid {BORDER};
    color: {TEXT};
    background-color: {CARD};
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 0.8rem;
}}
.ptable tr:hover td {{ background-color: {BG2}; }}
.ptable .tot td {{
    background-color: {BG2};
    font-weight: 600;
    border-top: 1px solid {BORDER};
}}

/* ── Utility classes ── */
.mono {{
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-variant-numeric: tabular-nums;
}}
.gain {{ color: {GREEN}; }}
.loss {{ color: {RED}; }}

/* ── Data editor / dataframe ── */
[data-testid="stDataFrame"] {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 4px;
}}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 4px;
    color: {TEXT};
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
}}
[data-testid="stSelectbox"] > div {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 4px;
}}

/* ── Caption ── */
.stCaption, [data-testid="stCaptionContainer"] p {{
    color: {MUTED} !important;
    font-size: 0.72rem;
}}

/* ── Alert / info boxes ── */
[data-testid="stAlert"] {{
    border-radius: 4px;
    background-color: {CARD};
    border: 1px solid {BORDER};
}}

/* ── Selectbox / radio text ── */
[data-testid="stRadio"] label p,
[data-testid="stSelectbox"] span {{
    font-size: 0.84rem;
    color: {TEXT};
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
</style>
""", unsafe_allow_html=True)
