import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import defaultdict
import json

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Portfolio Intelligence", page_icon="📊", layout="wide")

# ── THEME ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

  html, body, [class*="css"] { font-family: 'Syne', sans-serif; background-color: #080b12; color: #e2e8f0; }
  .stApp { background-color: #080b12; }

  /* Grid background */
  .stApp::before {
    content: '';
    position: fixed; inset: 0;
    background-image: linear-gradient(rgba(0,229,160,0.03) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(0,229,160,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none; z-index: 0;
  }

  /* Sidebar */
  [data-testid="stSidebar"] { background-color: #0e1320; border-right: 1px solid #1e2d40; }

  /* Metric cards */
  [data-testid="metric-container"] {
    background-color: #111827;
    border: 1px solid #1e2d40;
    border-radius: 8px;
    padding: 20px;
    border-top: 2px solid #00e5a0;
  }
  [data-testid="stMetricValue"] { color: #00e5a0; font-family: 'Syne', sans-serif; font-size: 1.6rem; font-weight: 800; }
  [data-testid="stMetricLabel"] { color: #64748b; font-family: 'Space Mono', monospace; font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; }

  /* Tables */
  .stDataFrame { background-color: #111827; border-radius: 8px; border: 1px solid #1e2d40; }
  thead tr th { background-color: #0e1320 !important; color: #64748b !important; font-family: 'Space Mono', monospace !important; font-size: 0.7rem !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; }
  tbody tr:hover { background-color: rgba(0,229,160,0.04) !important; }

  /* Upload */
  [data-testid="stFileUploadDropzone"] { background-color: #111827; border: 1px dashed #00e5a0; border-radius: 8px; }

  /* Headers */
  h1, h2, h3 { color: #e2e8f0 !important; font-family: 'Syne', sans-serif !important; font-weight: 800 !important; }

  /* Section labels */
  .section-tag {
    display: inline-block;
    background: rgba(0,229,160,0.1);
    border: 1px solid rgba(0,229,160,0.3);
    color: #00e5a0;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.15em;
    padding: 3px 10px;
    border-radius: 2px;
    margin-bottom: 8px;
  }
  .section-title {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #64748b;
    font-family: 'Space Mono', monospace;
    margin-bottom: 12px;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] { background-color: #0e1320; border-bottom: 1px solid #1e2d40; gap: 4px; }
  .stTabs [data-baseweb="tab"] { background-color: transparent; color: #64748b; font-family: 'Space Mono', monospace; font-size: 11px; letter-spacing: 0.06em; border-radius: 4px 4px 0 0; }
  .stTabs [aria-selected="true"] { background-color: rgba(0,229,160,0.1) !important; color: #00e5a0 !important; border-bottom: 2px solid #00e5a0 !important; }

  /* Buttons */
  .stButton > button {
    background: rgba(0,229,160,0.1);
    border: 1px solid rgba(0,229,160,0.3);
    color: #00e5a0;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.08em;
    border-radius: 4px;
  }
  .stButton > button:hover { background: rgba(0,229,160,0.2); border-color: #00e5a0; }

  /* Inputs */
  .stTextInput input, .stSelectbox select {
    background-color: #111827 !important;
    border: 1px solid #1e2d40 !important;
    color: #e2e8f0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 12px !important;
    border-radius: 4px !important;
  }
  .stTextInput input:focus { border-color: rgba(0,229,160,0.4) !important; }

  /* Divider */
  hr { border-color: #1e2d40; }

  /* Search box */
  [data-testid="stTextInput"] input::placeholder { color: #64748b; }

  /* Activity row colors */
  .tx-buy   { color: #00e5a0; font-weight: 700; }
  .tx-sell  { color: #ff4560; font-weight: 700; }
  .tx-div   { color: #ffc94d; font-weight: 700; }

  /* Stat badges */
  .badge-green { background: rgba(0,229,160,0.12); color: #00e5a0; padding: 2px 8px; border-radius: 2px; font-family: 'Space Mono', monospace; font-size: 10px; font-weight: 700; }
  .badge-red   { background: rgba(255,69,96,0.12); color: #ff4560; padding: 2px 8px; border-radius: 2px; font-family: 'Space Mono', monospace; font-size: 10px; font-weight: 700; }
  .badge-gold  { background: rgba(255,201,77,0.12); color: #ffc94d; padding: 2px 8px; border-radius: 2px; font-family: 'Space Mono', monospace; font-size: 10px; font-weight: 700; }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: #080b12; }
  ::-webkit-scrollbar-thumb { background: #1e2d40; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── PLOTLY BASE LAYOUT ────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="#111827", plot_bgcolor="#111827",
    font=dict(color="#64748b", family="Space Mono"),
    margin=dict(t=20, b=20, l=20, r=20),
    xaxis=dict(gridcolor="#1e2d40", color="#64748b"),
    yaxis=dict(gridcolor="#1e2d40", color="#64748b"),
)
GREEN, RED, GOLD, BLUE = "#00e5a0", "#ff4560", "#ffc94d", "#3b82f6"
PALETTE = [GREEN,"#00c97d","#00ae5d","#009342",BLUE,"#2563eb","#1d4ed8",GOLD,"#f59e0b",RED,"#ef4444","#64748b"]

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-tag">⚙ SETTINGS</div>', unsafe_allow_html=True)
    st.markdown("### Column Mapping")
    st.caption("Match your CSV column names")
    col_ticker   = st.text_input("Ticker column",      value="ticker")
    col_shares   = st.text_input("Shares column",      value="shares")
    col_avgprice = st.text_input("Avg Buy Price col",  value="avg_price")
    st.markdown("---")
    st.markdown("### Display")
    currency = st.selectbox("Currency", ["JPY (¥)", "USD ($)"])
    SYM = "¥" if "JPY" in currency else "$"
    st.markdown("---")
    st.markdown("### Upload History CSV")
    hist_file = st.file_uploader("Transaction history CSV (optional)", type=["csv"], key="hist")
    st.markdown("---")
    st.markdown('<p style="color:#64748b;font-size:10px;font-family:Space Mono,monospace;">Data via Yahoo Finance · Not financial advice</p>', unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-tag">PAYPAY SECURITIES</div>', unsafe_allow_html=True)
st.markdown("## Portfolio Intelligence")
st.markdown("---")

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊  OVERVIEW", "📋  HOLDINGS", "📈  ACTIVITY", "💰  DIVIDENDS"])

# ── FILE UPLOAD ───────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload PayPay Securities CSV", type=["csv"], help="Export from PayPay Securities → Portfolio → Download CSV")

def load_demo():
    return pd.DataFrame({
        "ticker":    ["7203.T","9984.T","6758.T","4755.T","9433.T","MSFT","AMZN","NVDA","META","GOOGL"],
        "shares":    [10, 5, 8, 20, 15, 3, 2, 10, 4, 3],
        "avg_price": [2100,7800,12500,1800,4200,38000,42000,8500,55000,18000]
    })

@st.cache_data(ttl=300)
def fetch_stock(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period="5d")
        price = hist["Close"].iloc[-1] if not hist.empty else info.get("currentPrice", 0)
        prev  = hist["Close"].iloc[-2] if len(hist) >= 2 else price
        name  = info.get("longName") or info.get("shortName") or ticker
        return {"name": name, "price": round(float(price), 2), "prev": round(float(prev), 2), "currency": info.get("currency","JPY")}
    except Exception:
        return {"name": ticker, "price": 0, "prev": 0, "currency": "JPY"}

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
if uploaded_file:
    raw = pd.read_csv(uploaded_file, encoding="utf-8-sig")
    try:
        df = raw.rename(columns={col_ticker:"ticker", col_shares:"shares", col_avgprice:"avg_price"})[["ticker","shares","avg_price"]]
    except KeyError as e:
        st.error(f"Column not found: {e} — check sidebar mapping")
        st.stop()
else:
    st.info("📂 Demo mode — upload your CSV to see real data")
    df = load_demo()

# ── FETCH LIVE PRICES ─────────────────────────────────────────────────────────
with st.spinner("🔄 Fetching live prices..."):
    rows = []
    for _, r in df.iterrows():
        info = fetch_stock(str(r["ticker"]).strip())
        day_chg = round(((info["price"] - info["prev"]) / info["prev"] * 100), 2) if info["prev"] > 0 else 0
        rows.append({
            "Company":       info["name"],
            "Ticker":        str(r["ticker"]).upper().replace(".T",""),
            "Shares":        r["shares"],
            "Avg Buy":       r["avg_price"],
            "Current Price": info["price"],
            "Market Value":  round(r["shares"] * info["price"], 0),
            "Cost Basis":    round(r["shares"] * r["avg_price"], 0),
            "Gain (¥)":      round((info["price"] - r["avg_price"]) * r["shares"], 0),
            "Gain (%)":      round(((info["price"] - r["avg_price"]) / r["avg_price"]) * 100, 2) if r["avg_price"] > 0 else 0,
            "Day (%)":       day_chg,
            "Ticker_raw":    str(r["ticker"]).strip()
        })

port = pd.DataFrame(rows)

# ── SUMMARY STATS ─────────────────────────────────────────────────────────────
total_val   = port["Market Value"].sum()
total_cost  = port["Cost Basis"].sum()
total_gain  = port["Gain (¥)"].sum()
gain_pct    = round((total_gain / total_cost * 100), 2) if total_cost > 0 else 0
winners     = len(port[port["Gain (%)"] > 0])
losers      = len(port[port["Gain (%)"] < 0])
best        = port.loc[port["Gain (%)"].idxmax()] if len(port) > 0 else None
worst       = port.loc[port["Gain (%)"].idxmin()] if len(port) > 0 else None

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    # Metrics
    st.markdown('<p class="section-title">PORTFOLIO SUMMARY</p>', unsafe_allow_html=True)
    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("Portfolio Value",  f"{SYM}{total_val:,.0f}")
    m2.metric("Total Cost",       f"{SYM}{total_cost:,.0f}")
    m3.metric("Total P&L",        f"{SYM}{total_gain:,.0f}", delta=f"{gain_pct}%")
    m4.metric("Positions",        f"{len(port)}")
    m5.metric("Winners / Losers", f"{winners}W · {losers}L")

    st.markdown("---")

    # Best / Worst
    if best is not None and worst is not None:
        st.markdown('<p class="section-title">TODAY\'S LEADERS</p>', unsafe_allow_html=True)
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("🏆 Best Gain",  best["Company"][:20],  delta=f"{best['Gain (%)']:.2f}%")
        b2.metric("📉 Worst Loss", worst["Company"][:20], delta=f"{worst['Gain (%)']:.2f}%")
        b3.metric("Top Holding",   port.loc[port["Market Value"].idxmax()]["Company"][:20],
                  f"{SYM}{port['Market Value'].max():,.0f}")
        b4.metric("Avg Position Size", f"{SYM}{total_val/len(port):,.0f}" if len(port) > 0 else "—")
    st.markdown("---")

    # Charts row
    c1, c2 = st.columns([3, 2])

    with c1:
        st.markdown('<p class="section-title">GAIN / LOSS BY POSITION</p>', unsafe_allow_html=True)
        port_sorted = port.sort_values("Gain (%)", ascending=True)
        colors = [GREEN if v >= 0 else RED for v in port_sorted["Gain (%)"]]
        fig_bar = go.Figure(go.Bar(
            x=port_sorted["Gain (%)"],
            y=port_sorted["Ticker"],
            orientation="h",
            marker_color=colors,
            text=[f"{v:.1f}%" for v in port_sorted["Gain (%)"]],
            textposition="outside",
            textfont=dict(size=9, color="#e2e8f0")
        ))
        fig_bar.update_layout(**PLOT_LAYOUT, height=max(300, len(port)*22))
        fig_bar.update_xaxis(ticksuffix="%")
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.markdown('<p class="section-title">ALLOCATION</p>', unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            values=port["Market Value"],
            labels=port["Company"].str[:20],
            hole=0.65,
            marker=dict(colors=PALETTE * (len(port)//len(PALETTE)+1), line=dict(color="#080b12", width=1)),
            textfont=dict(size=9),
            hovertemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>"
        ))
        fig_pie.update_layout(**PLOT_LAYOUT, height=360,
            legend=dict(bgcolor="#111827", font=dict(size=9, color="#64748b"), x=1.02))
        fig_pie.add_annotation(text=f"{len(port)}<br><span style='font-size:10px'>stocks</span>",
            x=0.5, y=0.5, showarrow=False, font=dict(color="#e2e8f0", size=16))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Treemap
    st.markdown('<p class="section-title">PORTFOLIO TREEMAP</p>', unsafe_allow_html=True)
    fig_tree = px.treemap(
        port, path=["Company"], values="Market Value",
        color="Gain (%)",
        color_continuous_scale=[[0, RED],[0.5,"#1e2d40"],[1, GREEN]],
        color_continuous_midpoint=0,
        hover_data={"Gain (%)": ":.2f"}
    )
    fig_tree.update_layout(**PLOT_LAYOUT, height=320, coloraxis_showscale=False)
    fig_tree.update_traces(textfont=dict(size=11, color="white"), marker=dict(line=dict(width=1, color="#080b12")))
    st.plotly_chart(fig_tree, use_container_width=True)

    # Scatter — position size vs performance
    st.markdown('<p class="section-title">POSITION SIZE vs PERFORMANCE</p>', unsafe_allow_html=True)
    fig_scatter = go.Figure(go.Scatter(
        x=port["Cost Basis"], y=port["Gain (%)"],
        mode="markers+text",
        text=port["Ticker"],
        textposition="top center",
        textfont=dict(size=8, color="#64748b"),
        marker=dict(
            size=port["Market Value"] / (port["Market Value"].max() / 30 + 1) + 6,
            color=port["Gain (%)"],
            colorscale=[[0, RED],[0.5,"#1e2d40"],[1, GREEN]],
            line=dict(color="#1e2d40", width=1),
            showscale=False
        ),
        hovertemplate="<b>%{text}</b><br>Cost: ¥%{x:,.0f}<br>Gain: %{y:.2f}%<extra></extra>"
    ))
    fig_scatter.add_hline(y=0, line_color="#1e2d40", line_dash="dash")
    fig_scatter.update_layout(**PLOT_LAYOUT, height=300,
        xaxis=dict(title="Cost Basis", tickprefix=SYM, gridcolor="#1e2d40"),
        yaxis=dict(title="Gain %", ticksuffix="%", gridcolor="#1e2d40"))
    st.plotly_chart(fig_scatter, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — HOLDINGS TABLE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-title">ALL POSITIONS</p>', unsafe_allow_html=True)

    # Search + sort
    sc1, sc2 = st.columns([3, 1])
    with sc1:
        search = st.text_input("🔍 Search company", placeholder="e.g. Toyota, NVIDIA...")
    with sc2:
        sort_by = st.selectbox("Sort by", ["Market Value","Gain (%)","Day (%)","Cost Basis","Gain (¥)"])

    filtered = port[port["Company"].str.contains(search, case=False, na=False)] if search else port
    filtered = filtered.sort_values(sort_by, ascending=False)
    filtered.index = range(1, len(filtered)+1)

    # Add TradingView chart links
    def tv_link(row):
        ticker = row["Ticker_raw"].replace(".T", "")
        prefix = "TSE:" if ".T" in row["Ticker_raw"] else ""
        return f'<a href="https://www.tradingview.com/chart/?symbol={prefix}{ticker}" target="_blank" style="color:#3b82f6;text-decoration:none;">📈 {row["Company"][:28]}</a>'

    display = filtered.copy()
    display["Company"] = display.apply(tv_link, axis=1)

    styled = display[["Company","Ticker","Shares","Avg Buy","Current Price","Market Value","Cost Basis","Gain (¥)","Gain (%)","Day (%)"]]\
        .style\
        .map(lambda v: f"color: {GREEN}; font-weight:700" if isinstance(v,(int,float)) and v > 0
             else (f"color: {RED}; font-weight:700" if isinstance(v,(int,float)) and v < 0 else ""),
             subset=["Gain (¥)","Gain (%)","Day (%)"])\
        .format({
            "Avg Buy":        f"{SYM}{{:,.2f}}",
            "Current Price":  f"{SYM}{{:,.2f}}",
            "Market Value":   f"{SYM}{{:,.0f}}",
            "Cost Basis":     f"{SYM}{{:,.0f}}",
            "Gain (¥)":       f"{SYM}{{:,.0f}}",
            "Gain (%)":       "{:.2f}%",
            "Day (%)":        "{:.2f}%",
        })\
        .set_properties(**{"background-color":"#111827","color":"#e2e8f0","border-color":"#1e2d40"})

    st.write(styled.to_html(escape=False), unsafe_allow_html=True)

    st.markdown("---")

    # Export
    csv = port.drop(columns=["Ticker_raw"]).to_csv(index=False)
    st.download_button("⬇ Export Holdings CSV", csv, "holdings_export.csv", "text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ACTIVITY
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-title">TRANSACTION ACTIVITY</p>', unsafe_allow_html=True)

    if hist_file:
        hist_df = pd.read_csv(hist_file, encoding="utf-8-sig")
        st.success(f"✅ Loaded {len(hist_df)} transactions")
        cols = list(hist_df.columns)
        st.caption(f"Detected columns: {', '.join(cols)}")
        if len(cols) >= 4:
            st.dataframe(hist_df.head(50), use_container_width=True, height=400)
    else:
        st.info("Upload your transaction history CSV in the sidebar to see real activity. Showing sample data.")
        months_demo = ["2025.03","2025.04","2025.05","2025.06","2025.07","2025.08",
                       "2025.09","2025.10","2025.11","2025.12","2026.01","2026.02","2026.03","2026.04"]
        buy_vals  = [527000,104531,51000,67000,40090,77000,10146,19,435000,92511,183155,119467,223928,66371]
        sell_vals = [132268,0,0,0,0,11000,0,0,411362,0,0,0,0,0]

        fig_act = go.Figure()
        fig_act.add_trace(go.Bar(name="Buy",  x=months_demo, y=buy_vals,  marker_color=GREEN, opacity=0.8))
        fig_act.add_trace(go.Bar(name="Sell", x=months_demo, y=sell_vals, marker_color=RED,   opacity=0.7))
        fig_act.update_layout(**PLOT_LAYOUT, height=280, barmode="group",
            legend=dict(bgcolor="#111827", font=dict(color="#64748b")),
            xaxis=dict(tickangle=45),
            yaxis=dict(tickprefix="¥", tickformat=","))
        st.plotly_chart(fig_act, use_container_width=True)

        st.markdown('<p class="section-title">RECENT TRANSACTIONS (SAMPLE)</p>', unsafe_allow_html=True)
        demo_tx = pd.DataFrame([
            {"Date":"2026.05.01","Type":"Buy",      "Company":"NVIDIA",              "Amount":"¥1,024"},
            {"Date":"2026.05.01","Type":"Buy",      "Company":"Meta Platforms",      "Amount":"¥1,000"},
            {"Date":"2026.04.30","Type":"Buy",      "Company":"PayPay ADS",          "Amount":"¥10,000"},
            {"Date":"2026.04.30","Type":"Dividend", "Company":"イオン",               "Amount":"¥24"},
            {"Date":"2026.04.10","Type":"Buy",      "Company":"Microsoft",           "Amount":"¥15,000"},
            {"Date":"2026.04.10","Type":"Buy",      "Company":"CrowdStrike",         "Amount":"¥30,000"},
            {"Date":"2026.03.31","Type":"Buy",      "Company":"Berkshire Hathaway",  "Amount":"¥57,500"},
            {"Date":"2026.02.28","Type":"Sell",     "Company":"TESLA",               "Amount":"¥10,000"},
            {"Date":"2026.01.27","Type":"Buy",      "Company":"SoftBank Group",      "Amount":"¥20,000"},
            {"Date":"2025.11.30","Type":"Sell",     "Company":"CrowdStrike Holdings","Amount":"¥80,000"},
        ])

        def color_type(val):
            if val == "Buy":      return f"color:{GREEN};font-weight:700"
            if val == "Sell":     return f"color:{RED};font-weight:700"
            if val == "Dividend": return f"color:{GOLD};font-weight:700"
            return ""

        styled_tx = demo_tx.style\
            .map(color_type, subset=["Type"])\
            .set_properties(**{"background-color":"#111827","color":"#e2e8f0","border-color":"#1e2d40"})
        st.write(styled_tx.to_html(escape=False), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — DIVIDENDS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-title">DIVIDEND & INCOME TRACKER</p>', unsafe_allow_html=True)

    d1, d2, d3 = st.columns(3)
    d1.metric("Dividend Payers",        f"{len(port[port['Gain (¥)'] >= 0])}")
    d2.metric("Estimated Annual Yield", "~1.2%", help="Based on current holdings")
    d3.metric("Total Received (Demo)",  "¥19,821")

    st.markdown("---")
    st.markdown('<p class="section-title">TOP DIVIDEND PAYERS — YOUR PORTFOLIO</p>', unsafe_allow_html=True)

    div_data = pd.DataFrame([
        {"Company":"Fidelity JP Dividend Fund","Received (¥)":2340,"Yield":"est. 4.8%"},
        {"Company":"Altria Group",             "Received (¥)":1800,"Yield":"~8.0%"},
        {"Company":"AT&T",                     "Received (¥)":1239,"Yield":"~6.5%"},
        {"Company":"Exxon Mobil",              "Received (¥)":1180,"Yield":"~3.5%"},
        {"Company":"3M",                       "Received (¥)":1116,"Yield":"~5.2%"},
        {"Company":"Toyota Motor",             "Received (¥)":912, "Yield":"~3.1%"},
        {"Company":"Coca-Cola",                "Received (¥)":841, "Yield":"~3.0%"},
        {"Company":"Vanguard VIG ETF",         "Received (¥)":704, "Yield":"~1.8%"},
        {"Company":"AbbVie",                   "Received (¥)":678, "Yield":"~3.6%"},
        {"Company":"Astellas Pharma",          "Received (¥)":672, "Yield":"~4.2%"},
        {"Company":"JPMorgan Chase",           "Received (¥)":620, "Yield":"~2.2%"},
        {"Company":"Philip Morris",            "Received (¥)":560, "Yield":"~5.5%"},
        {"Company":"Chevron",                  "Received (¥)":420, "Yield":"~3.8%"},
    ])

    fig_div = go.Figure(go.Bar(
        x=div_data["Received (¥)"],
        y=div_data["Company"],
        orientation="h",
        marker_color=GOLD,
        opacity=0.8,
        text=[f"¥{v:,}" for v in div_data["Received (¥)"]],
        textposition="outside",
        textfont=dict(size=10, color="#e2e8f0"),
    ))
    fig_div.update_layout(**PLOT_LAYOUT, height=380,
        xaxis=dict(tickprefix="¥", gridcolor="#1e2d40"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig_div, use_container_width=True)

    st.markdown('<p class="section-title">DIVIDEND DETAIL TABLE</p>', unsafe_allow_html=True)
    div_data.index = range(1, len(div_data)+1)
    styled_div = div_data.style\
        .format({"Received (¥)": "¥{:,.0f}"})\
        .set_properties(**{"background-color":"#111827","color":"#e2e8f0","border-color":"#1e2d40"})\
        .map(lambda v: f"color:{GOLD};font-weight:700", subset=["Received (¥)"])
    st.write(styled_div.to_html(escape=False), unsafe_allow_html=True)

    st.markdown("---")
    st.caption("💡 To track real dividend data: export your PayPay transaction history and upload via sidebar. Dividend rows will be auto-detected.")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p style="color:#64748b;font-size:11px;text-align:center;font-family:Space Mono,monospace;">Portfolio Intelligence · Data via Yahoo Finance · Prices delayed · Not financial advice</p>', unsafe_allow_html=True)
