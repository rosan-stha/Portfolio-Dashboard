"""Atlas Terminal — global CSS injection via st.html().

st.html() (Streamlit >= 1.31) renders HTML directly into the page without
Markdown processing, so CSS selectors like *, *::before are never mis-parsed
as emphasis markers. No iframe, no JS parent-document tricks needed.
"""
import streamlit as st

_FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800"
    "&family=Space+Grotesk:wght@400;500;600;700"
    "&family=JetBrains+Mono:wght@400;500;600&display=swap"
)

_CSS = """
/* ══ CSS VARIABLES ═══════════════════════════════════════════════════════════ */
:root {
  --bg:           #050816;
  --bg-deep:      #03050f;
  --surface:      rgba(15, 23, 42, 0.85);
  --surface-2:    rgba(20, 28, 50, 0.85);
  --surface-3:    rgba(28, 38, 62, 0.75);
  --surface-solid:#0B1220;
  --border:       rgba(148, 163, 184, 0.10);
  --border-2:     rgba(148, 163, 184, 0.18);
  --border-glow:  rgba(6, 182, 212, 0.35);
  --text:         #F8FAFC;
  --text-2:       #CBD5E1;
  --muted:        #64748B;
  --muted-2:      #475569;
  --navy:         #1E3A8A;
  --navy-2:       #1E40AF;
  --blue:         #3B82F6;
  --cyan:         #06B6D4;
  --accent:       #06B6D4;
  --pos:          #22C55E;
  --pos-bg:       rgba(34, 197, 94, 0.10);
  --neg:          #EF4444;
  --neg-bg:       rgba(239, 68, 68, 0.10);
  --warn:         #F59E0B;
  --warn-bg:      rgba(245, 158, 11, 0.10);
  --grid:         rgba(148, 163, 184, 0.06);
  --shadow-lg:    0 10px 40px -10px rgba(0,0,0,0.6), 0 2px 8px rgba(0,0,0,0.4);
  --radius:       12px;
  --radius-sm:    8px;
}

/* ══ RESET & BASE ════════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[class*="css"],
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.stApp {
  font-family: 'Inter', 'SF Pro Display', system-ui, sans-serif !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-size: 13.5px;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

/* Radial gradient backdrop */
[data-testid="stAppViewContainer"] {
  background-image:
    radial-gradient(ellipse 1200px 600px at 20% -10%, rgba(30,58,138,0.30), transparent 60%),
    radial-gradient(ellipse 900px 500px at 100% 0%,  rgba(6,182,212,0.12), transparent 55%),
    radial-gradient(ellipse 1000px 600px at 50% 100%,rgba(30,64,175,0.18), transparent 60%) !important;
  min-height: 100vh;
}

/* Noise texture overlay */
[data-testid="stAppViewContainer"]::before {
  content: "";
  position: fixed; inset: 0;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0.6 0 0 0 0 0.7 0 0 0 0 0.9 0 0 0 0.022 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
  pointer-events: none;
  z-index: 0;
  opacity: 0.55;
}

.main .block-container {
  padding-top: 0.75rem !important;
  padding-bottom: 2.5rem !important;
  max-width: 100% !important;
}

/* ══ SIDEBAR ═════════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0A1228 0%, #060A1C 100%) !important;
  border-right: 1px solid var(--border) !important;
  min-width: 224px !important;
  max-width: 224px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 18px 14px !important; }
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] .stCaption p { color: var(--text) !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }

/* Nav radio — hide default dot, style as nav buttons */
[data-testid="stSidebar"] [data-testid="stRadio"] > label { display: none !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stWidgetLabel"] { display: none !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
  display: flex; flex-direction: column; gap: 2px;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  display: flex !important;
  align-items: center !important;
  padding: 8px 10px !important;
  border-radius: 8px !important;
  cursor: pointer !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  color: var(--text-2) !important;
  transition: all 160ms !important;
  border: none !important;
  background: transparent !important;
  width: 100% !important;
  position: relative !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
  background: rgba(59,130,246,0.08) !important;
  color: var(--text) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
  background: linear-gradient(90deg, rgba(59,130,246,0.18), rgba(6,182,212,0.06)) !important;
  color: var(--text) !important;
  font-weight: 600 !important;
  box-shadow: inset 0 0 0 1px rgba(59,130,246,0.25), 0 0 18px -6px rgba(59,130,246,0.35) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked)::before {
  content: "";
  position: absolute; left: 0; top: 8px; bottom: 8px;
  width: 2px;
  background: var(--cyan);
  box-shadow: 0 0 8px var(--cyan);
  border-radius: 2px;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label span:first-child { display: none !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label span:last-child {
  padding-left: 6px !important;
  font-family: 'Inter', sans-serif !important;
}

/* ══ STICKY HEADER ═══════════════════════════════════════════════════════════ */
.term-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 24px;
  border-bottom: 1px solid var(--border);
  background: rgba(5, 8, 22, 0.92);
  backdrop-filter: blur(20px);
  position: sticky; top: 0; z-index: 40;
  margin: -0.75rem -1rem 1.25rem;
  min-height: 62px;
}

/* ══ BRAND ════════════════════════════════════════════════════════════════════ */
.brand-bar {
  display: flex; align-items: center; gap: 10px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 16px;
}
.brand-logo {
  width: 32px; height: 32px; border-radius: 8px;
  background: linear-gradient(135deg, #3B82F6, #06B6D4);
  display: inline-flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 14px; color: #fff; flex-shrink: 0;
  box-shadow: 0 4px 16px -4px rgba(59,130,246,0.6), inset 0 1px 0 rgba(255,255,255,0.20);
}
.brand-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 14px; font-weight: 700; letter-spacing: -0.01em;
  color: var(--text); line-height: 1.1;
}
.brand-sub { font-size: 10px; color: var(--muted); letter-spacing: 0.08em; text-transform: uppercase; }

/* ══ TYPE UTILITIES ══════════════════════════════════════════════════════════ */
.eyebrow {
  font-size: 10.5px; font-weight: 600; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--muted); margin-bottom: 4px;
  font-family: 'Inter', sans-serif;
}
.lbl {
  font-size: 10.5px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.12em; color: var(--muted); margin-bottom: 6px;
  font-family: 'Inter', sans-serif;
}
.font-display { font-family: 'Space Grotesk', 'Inter', sans-serif !important; letter-spacing: -0.02em !important; }
.mono { font-family: 'JetBrains Mono', ui-monospace, monospace !important; font-variant-numeric: tabular-nums !important; }
.pos  { color: var(--pos) !important; }
.neg  { color: var(--neg) !important; }
.warn { color: var(--warn) !important; }
.cyan { color: var(--cyan) !important; }
.muted { color: var(--muted) !important; }

/* ══ CARDS ════════════════════════════════════════════════════════════════════ */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-lg);
  position: relative; overflow: hidden;
  padding: 16px; margin-bottom: 14px;
  animation: fadeup 400ms ease-out both;
}
.card::before {
  content: "";
  position: absolute; inset: 0;
  border-radius: inherit; padding: 1px;
  background: linear-gradient(180deg, rgba(255,255,255,0.06), transparent 30%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
  pointer-events: none;
}
.card--glow {
  box-shadow: var(--shadow-lg),
    0 0 0 1px rgba(6,182,212,0.12),
    0 0 40px -8px rgba(6,182,212,0.20);
}
.card--gradient-edge {
  border: 1px solid transparent;
  background:
    linear-gradient(var(--surface), var(--surface)) padding-box,
    linear-gradient(135deg, rgba(59,130,246,0.45), rgba(6,182,212,0.25) 50%, rgba(30,58,138,0.10)) border-box;
}
.card-hd {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding-bottom: 12px; margin-bottom: 12px;
  border-bottom: 1px solid var(--border);
}
.card-hd-inner { padding: 14px 16px 12px; border-bottom: 1px solid var(--border); }
.card-title { font-family: 'Space Grotesk','Inter',sans-serif; font-size: 15px; font-weight: 600; letter-spacing: -0.01em; color: var(--text); }
.card-sub   { font-size: 11.5px; color: var(--muted); margin-top: 3px; }

/* ══ KPI CARDS ════════════════════════════════════════════════════════════════ */
.kpi-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  display: flex; flex-direction: column;
  min-height: 158px; position: relative; overflow: hidden;
  box-shadow: var(--shadow-lg);
  animation: fadeup 400ms ease-out both;
}
.kpi-card::before {
  content: "";
  position: absolute; inset: 0; border-radius: inherit; padding: 1px;
  background: linear-gradient(180deg, rgba(255,255,255,0.06), transparent 30%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
  pointer-events: none;
}
.kpi-card--featured {
  border: 1px solid transparent;
  background:
    linear-gradient(var(--surface), var(--surface)) padding-box,
    linear-gradient(135deg, rgba(59,130,246,0.45), rgba(6,182,212,0.25) 50%, rgba(30,58,138,0.10)) border-box;
}
.kpi-card--glow {
  box-shadow: var(--shadow-lg),
    0 0 0 1px rgba(6,182,212,0.12),
    0 0 40px -8px rgba(6,182,212,0.20);
}
.kpi-eyebrow  { font-size: 9.5px; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); }
.kpi-jp       { font-size: 10.5px; color: var(--muted-2); margin-top: 3px; letter-spacing: 0.02em; }
.kpi-value    { font-family: 'Space Grotesk','JetBrains Mono',monospace; font-size: 28px; font-weight: 600; letter-spacing: -0.02em; line-height: 1.05; margin: 10px 0 4px; }
.kpi-value--lg   { font-size: 34px; }
.kpi-value--cyan { color: var(--cyan);  text-shadow: 0 0 24px rgba(6,182,212,0.4); }
.kpi-value--pos  { color: var(--pos);   text-shadow: 0 0 24px rgba(34,197,94,0.4); }
.kpi-value--neg  { color: var(--neg);   text-shadow: 0 0 24px rgba(239,68,68,0.4); }
.kpi-value--warn { color: var(--warn);  text-shadow: 0 0 24px rgba(245,158,11,0.4); }
.kpi-delta { font-size: 11.5px; color: var(--muted); margin-top: 2px; }
.kpi-footer { margin-top: auto; padding-top: 10px; border-top: 1px solid var(--border); }
.kpi-breakdown {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px;
  margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border);
}
.kpi-breakdown-item-label { font-size: 9.5px; color: var(--muted); letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 3px; }
.kpi-breakdown-item-value { font-family: 'JetBrains Mono',monospace; font-size: 12px; color: var(--text-2); font-weight: 500; }

/* ══ PILLS / BADGES ══════════════════════════════════════════════════════════ */
.pill {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 10.5px; font-weight: 500; letter-spacing: 0.04em;
  padding: 3px 8px; border-radius: 999px;
  background: var(--surface-3); color: var(--text-2);
  border: 1px solid var(--border); white-space: nowrap;
}
.pill-pos  { background: var(--pos-bg);  color: var(--pos);  border-color: rgba(34,197,94,0.25); }
.pill-neg  { background: var(--neg-bg);  color: var(--neg);  border-color: rgba(239,68,68,0.25); }
.pill-cyan { background: rgba(6,182,212,0.12); color: var(--cyan); border-color: rgba(6,182,212,0.30); }
.pill-warn { background: var(--warn-bg); color: var(--warn); border-color: rgba(245,158,11,0.25); }
.pill-blue { background: rgba(59,130,246,0.12); color: var(--blue); border-color: rgba(59,130,246,0.30); }

/* ══ CHIP STRIP (period selector) ════════════════════════════════════════════ */
.chips-strip {
  display: inline-flex;
  background: var(--surface-2);
  border: 1px solid var(--border);
  padding: 3px; border-radius: var(--radius-sm); gap: 2px;
}
.chip-btn {
  border: 0; background: transparent;
  color: var(--muted); padding: 5px 10px;
  font: 500 11.5px/1 'JetBrains Mono', monospace;
  letter-spacing: 0.04em; border-radius: 6px; cursor: pointer; transition: all 140ms;
}
.chip-btn:hover { color: var(--text-2); }
.chip-btn.active {
  background: linear-gradient(180deg, rgba(59,130,246,0.18), rgba(30,58,138,0.18));
  color: var(--text);
  box-shadow: inset 0 0 0 1px rgba(59,130,246,0.35), 0 0 12px -4px rgba(59,130,246,0.5);
}

/* ══ BUTTONS ══════════════════════════════════════════════════════════════════ */
[data-testid="stButton"] button {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: var(--radius-sm) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 12.5px !important; font-weight: 500 !important;
  transition: all 160ms !important;
  box-shadow: none !important;
}
[data-testid="stButton"] button:hover {
  border-color: var(--border-2) !important;
  background: var(--surface-3) !important;
  transform: translateY(-1px) !important;
}
[data-testid="stButton"] button[kind="primary"] {
  background: linear-gradient(180deg, #1E40AF, #1E3A8A) !important;
  border-color: rgba(59,130,246,0.40) !important;
  box-shadow: 0 6px 20px -6px rgba(59,130,246,0.5), inset 0 1px 0 rgba(255,255,255,0.10) !important;
}
[data-testid="stButton"] button[kind="primary"]:hover {
  background: linear-gradient(180deg, #2554d8, #1E40AF) !important;
  box-shadow: 0 10px 30px -6px rgba(59,130,246,0.7) !important;
}
[data-testid="stDownloadButton"] button {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: var(--radius-sm) !important;
  font-size: 12.5px !important;
}

/* ══ INPUTS ══════════════════════════════════════════════════════════════════ */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
  border-color: var(--border-glow) !important;
  box-shadow: 0 0 0 3px rgba(6,182,212,0.12) !important;
  outline: none !important;
}
input::placeholder { color: var(--muted-2) !important; }

/* ══ SELECT / RADIO / MULTISELECT ════════════════════════════════════════════ */
[data-testid="stRadio"] label span { color: var(--text-2) !important; }
[data-testid="stRadio"] label:has(input:checked) span { color: var(--text) !important; font-weight: 600 !important; }
[data-testid="stSelectbox"] span,
[data-testid="stMultiSelect"] span { color: var(--text) !important; }
[data-baseweb="select"] [data-baseweb="tag"] {
  background: rgba(59,130,246,0.15) !important;
  border: 1px solid rgba(59,130,246,0.30) !important;
  color: var(--text) !important;
}

/* ══ STREAMLIT METRICS ════════════════════════════════════════════════════════ */
[data-testid="metric-container"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 14px 16px !important;
  box-shadow: var(--shadow-lg) !important;
  position: relative; overflow: hidden;
}
[data-testid="metric-container"]::before {
  content: "";
  position: absolute; inset: 0; border-radius: inherit; padding: 1px;
  background: linear-gradient(180deg, rgba(255,255,255,0.06), transparent 30%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
  pointer-events: none;
}
[data-testid="stMetricValue"] {
  font-family: 'Space Grotesk','JetBrains Mono',monospace !important;
  font-size: 1.45rem !important; font-weight: 600 !important;
  color: var(--text) !important; letter-spacing: -0.02em !important;
}
[data-testid="stMetricLabel"] {
  font-family: 'Inter', sans-serif !important;
  font-size: 0.60rem !important; font-weight: 600 !important;
  text-transform: uppercase !important; letter-spacing: 0.12em !important;
  color: var(--muted) !important;
}
[data-testid="stMetricDelta"] { font-family: 'JetBrains Mono',monospace !important; font-size: 0.76rem !important; }
[data-testid="stMetricDelta"][data-direction="up"]   { color: var(--pos) !important; }
[data-testid="stMetricDelta"][data-direction="down"] { color: var(--neg) !important; }

/* ══ TABS ════════════════════════════════════════════════════════════════════ */
[data-testid="stTabs"] { background: transparent !important; }
[data-testid="stTabs"] button {
  font-family: 'Inter', sans-serif !important;
  font-size: 12.5px !important; font-weight: 500 !important;
  color: var(--muted) !important; background: transparent !important;
  border: none !important; padding: 8px 14px !important;
  border-radius: 6px !important; transition: all 140ms !important;
}
[data-testid="stTabs"] button:hover { color: var(--text-2) !important; }
[data-testid="stTabs"] button[aria-selected="true"] {
  background: linear-gradient(180deg, rgba(59,130,246,0.15), rgba(30,58,138,0.15)) !important;
  color: var(--text) !important; font-weight: 600 !important;
  box-shadow: inset 0 0 0 1px rgba(59,130,246,0.30), 0 0 12px -4px rgba(59,130,246,0.4) !important;
}
[data-testid="stTabsContent"] {
  padding-top: 1rem !important;
  border-top: 1px solid var(--border) !important;
}

/* ══ ALERTS / INFO ════════════════════════════════════════════════════════════ */
[data-testid="stAlert"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
}
[data-testid="stAlert"] p { color: var(--text-2) !important; }

/* ══ FILE UPLOAD ══════════════════════════════════════════════════════════════ */
[data-testid="stFileUploadDropzone"] {
  background: var(--surface) !important;
  border: 1px dashed var(--border-2) !important;
  border-radius: var(--radius-sm) !important;
  transition: all 160ms !important;
}
[data-testid="stFileUploadDropzone"]:hover { border-color: var(--border-glow) !important; }

/* ══ DIVIDER ══════════════════════════════════════════════════════════════════ */
hr { border-color: var(--border) !important; opacity: 1 !important; }

/* ══ HEADINGS ══════════════════════════════════════════════════════════════════ */
h1, h2, h3 {
  font-family: 'Space Grotesk','Inter',sans-serif !important;
  color: var(--text) !important; font-weight: 600 !important;
  letter-spacing: -0.02em !important;
}

/* ══ CAPTION ══════════════════════════════════════════════════════════════════ */
.stCaption, [data-testid="stCaptionContainer"] p { color: var(--muted) !important; font-size: 0.72rem !important; }

/* ══ DATA TABLES / DATAFRAMES ═════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
}

/* ══ PORTFOLIO TABLE ══════════════════════════════════════════════════════════ */
.ptable {
  width: 100%; border-collapse: collapse;
  font-size: 12.5px;
  font-family: 'JetBrains Mono', ui-monospace, monospace;
}
.ptable th {
  background: var(--surface-solid);
  color: var(--muted);
  text-transform: uppercase; letter-spacing: 0.12em;
  font-size: 10px; font-weight: 600;
  padding: 10px 12px; text-align: left;
  white-space: nowrap;
  border-bottom: 1px solid var(--border);
  font-family: 'Inter', sans-serif;
  position: sticky; top: 0;
}
.ptable td {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(148,163,184,0.08);
  color: var(--text);
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-size: 12.5px; transition: background 120ms;
}
.ptable tr:hover td { background: rgba(59,130,246,0.04); }
.ptable tr:last-child td { border-bottom: 0; }
.ptable .tot td {
  background: rgba(15,23,42,0.6); font-weight: 600;
  border-top: 1px solid var(--border-2); color: var(--text);
}

/* ══ AI INSIGHT CARDS ═════════════════════════════════════════════════════════ */
.ai-card { padding: 12px; border-radius: 10px; position: relative; margin-bottom: 10px; animation: fadeup 400ms ease-out both; }
.ai-card--warn { background: rgba(245,158,11,0.06); border: 1px solid rgba(245,158,11,0.30); }
.ai-card--ok   { background: rgba(6,182,212,0.06);  border: 1px solid rgba(6,182,212,0.30);  }
.ai-card--info { background: rgba(59,130,246,0.06); border: 1px solid rgba(59,130,246,0.30); }
.ai-card--perf { background: rgba(34,197,94,0.06);  border: 1px solid rgba(34,197,94,0.30);  }
.ai-badge { font-size: 9px; font-weight: 700; letter-spacing: 0.12em; padding: 2px 7px; background: rgba(0,0,0,0.25); border-radius: 3px; display: inline-block; margin-bottom: 4px; }
.ai-title { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 5px; }
.ai-body  { font-size: 11.5px; color: var(--text-2); line-height: 1.5; margin-bottom: 8px; }
.ai-action { font-size: 10.5px; color: var(--muted); }

/* ══ NEWS TICKER ══════════════════════════════════════════════════════════════ */
.news-ticker-wrap {
  background: var(--surface);
  border: 1px solid var(--border); border-radius: var(--radius);
  padding: 10px 16px;
  display: flex; align-items: center; gap: 16px;
  overflow: hidden; margin-bottom: 14px;
}
.news-ticker-scroll {
  flex: 1; overflow: hidden; position: relative;
  mask-image: linear-gradient(90deg, transparent, #000 5%, #000 95%, transparent);
  -webkit-mask-image: linear-gradient(90deg, transparent, #000 5%, #000 95%, transparent);
}
.news-ticker-inner { display: inline-flex; gap: 40px; white-space: nowrap; animation: scroll-ticker 60s linear infinite; }
.news-item-time { font-family: 'JetBrains Mono',monospace; font-size: 11px; color: var(--muted); }
.news-item-src  { font-size: 10px; font-weight: 700; letter-spacing: 0.08em; color: var(--cyan); }
.news-item-text { font-size: 12px; color: var(--text-2); }

/* ══ ACCOUNT TAGS ═════════════════════════════════════════════════════════════ */
.acct-tag { font-size: 9.5px; font-weight: 600; letter-spacing: 0.06em; padding: 2px 6px; border: 1px solid currentColor; border-radius: 3px; opacity: 0.9; display: inline-block; }
.acct-tsumitate { color: var(--pos); }
.acct-growth    { color: var(--cyan); }
.acct-tokutei   { color: var(--muted); }

/* ══ LIVE DOT ══════════════════════════════════════════════════════════════════ */
.live-dot {
  display: inline-block; width: 7px; height: 7px; border-radius: 50%;
  background: var(--pos);
  box-shadow: 0 0 8px var(--pos), 0 0 16px rgba(34,197,94,0.5);
  animation: pulse-dot 1.6s ease-in-out infinite;
  vertical-align: middle;
}
.live-dot-red {
  display: inline-block; width: 6px; height: 6px; border-radius: 50%;
  background: var(--neg); box-shadow: 0 0 8px var(--neg);
  animation: pulse-dot 1.6s ease-in-out infinite;
}

/* ══ FOOTER ════════════════════════════════════════════════════════════════════ */
.term-footer {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 24px;
  border-top: 1px solid var(--border);
  font-size: 11px; color: var(--muted);
  background: rgba(5,8,22,0.4);
  backdrop-filter: blur(20px);
  margin-top: 24px;
}

/* ══ PROGRESS BAR ══════════════════════════════════════════════════════════════ */
[data-testid="stProgress"] > div > div > div > div {
  background: linear-gradient(90deg, #1E40AF, #06B6D4) !important;
}

/* ══ CHAT INPUT ════════════════════════════════════════════════════════════════ */
[data-testid="stChatInput"] textarea {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInput"] textarea:focus {
  border-color: var(--border-glow) !important;
  box-shadow: 0 0 0 3px rgba(6,182,212,0.12) !important;
}
[data-testid="stChatMessage"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
}

/* ══ PLOTLY CHART CONTAINERS ══════════════════════════════════════════════════ */
[data-testid="stPlotlyChart"] {
  border-radius: var(--radius) !important;
  overflow: hidden;
}

/* ══ SELECT SLIDER ════════════════════════════════════════════════════════════ */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
  background: var(--cyan) !important;
  border-color: var(--cyan) !important;
  box-shadow: 0 0 10px rgba(6,182,212,0.5) !important;
}

/* ══ EXPANDER ═════════════════════════════════════════════════════════════════ */
[data-testid="stExpander"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
}
[data-testid="stExpander"] summary {
  font-family: 'Inter', sans-serif !important;
  font-size: 12.5px !important; color: var(--text-2) !important;
}

/* ══ SCROLLBARS ════════════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: rgba(148,163,184,0.18); border-radius: 6px; border: 2px solid transparent; background-clip: padding-box; }
::-webkit-scrollbar-thumb:hover { background: rgba(148,163,184,0.28); background-clip: padding-box; border: 2px solid transparent; }
::-webkit-scrollbar-track { background: transparent; }
::selection { background: rgba(6,182,212,0.35); }

/* ══ ANIMATIONS ════════════════════════════════════════════════════════════════ */
@keyframes fadeup {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.4; transform: scale(0.85); }
}
@keyframes scroll-ticker {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}

/* ══ HIDE STREAMLIT CHROME ════════════════════════════════════════════════════ */
#MainMenu, [data-testid="stToolbar"], [data-testid="manage-app-button"] { visibility: hidden !important; }
footer { visibility: hidden !important; }
[data-testid="stHeader"] { background: transparent !important; }
"""


def inject() -> None:
    st.html(
        f'<link rel="preconnect" href="https://fonts.googleapis.com">'
        f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        f'<link href="{_FONTS_URL}" rel="stylesheet">'
        f"<style>{_CSS}</style>"
    )
