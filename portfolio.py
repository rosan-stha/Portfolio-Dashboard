import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Portfolio Dashboard",
    page_icon="📈",
    layout="wide"
)

# ── TRADINGVIEW DARK THEME ────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Base */
    html, body, [class*="css"] {
        font-family: 'Trebuchet MS', sans-serif;
        background-color: #131722;
        color: #d1d4dc;
    }
    .stApp { background-color: #131722; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: #1e2130;
        border: 1px solid #2a2e39;
        border-radius: 8px;
        padding: 16px;
    }
    [data-testid="stMetricValue"] { color: #d1d4dc; font-size: 1.4rem; }
    [data-testid="stMetricDelta"] { font-size: 0.9rem; }

    /* Tables */
    .stDataFrame { background-color: #1e2130; border-radius: 8px; }
    thead tr th {
        background-color: #2a2e39 !important;
        color: #787b86 !important;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    tbody tr:hover { background-color: #2a2e39 !important; }

    /* Upload box */
    [data-testid="stFileUploadDropzone"] {
        background-color: #1e2130;
        border: 1px dashed #2962ff;
        border-radius: 8px;
    }

    /* Headers */
    h1, h2, h3 { color: #d1d4dc; font-weight: 600; }
    .section-title {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #787b86;
        margin-bottom: 8px;
    }

    /* Divider */
    hr { border-color: #2a2e39; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1e2130; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
_, col_title = st.columns([1, 8])
with col_title:
    st.markdown("## 📊 Portfolio Dashboard")
    st.markdown('<p class="section-title">PayPay Securities · Powered by Yahoo Finance</p>', unsafe_allow_html=True)

st.markdown("---")

# ── SIDEBAR: COLUMN MAPPER ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ CSV Column Mapping")
    st.markdown('<p class="section-title">Match your PayPay CSV columns</p>', unsafe_allow_html=True)
    st.info("After uploading your CSV, map each column to the correct field below.")

    col_ticker   = st.text_input("Ticker column name",       value="ticker")
    col_shares   = st.text_input("Shares / Units column",    value="shares")
    col_avgprice = st.text_input("Average Buy Price column", value="avg_price")

    st.markdown("---")
    st.markdown("### 💱 Currency")
    currency = st.selectbox("Display currency", ["JPY (¥)", "USD ($)"])
    symbol = "¥" if "JPY" in currency else "$"

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("Upload your PayPay Securities CSV export. This app fetches live prices from Yahoo Finance and displays your portfolio in English.")

# ── FILE UPLOAD ───────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload your PayPay Securities CSV export",
    type=["csv"],
    help="Export from PayPay Securities → My Page → Portfolio → Download CSV"
)

# ── DEMO DATA (if no file uploaded) ──────────────────────────────────────────
def load_demo_data():
    return pd.DataFrame({
        "ticker":    ["7203.T", "9984.T", "6758.T", "4755.T", "9433.T"],
        "shares":    [10, 5, 8, 20, 15],
        "avg_price": [2100, 7800, 12500, 1800, 4200]
    })

# ── FETCH STOCK DATA ──────────────────────────────────────────────────────────
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info
        hist  = stock.history(period="5d")
        price = hist["Close"].iloc[-1] if not hist.empty else (info.get("currentPrice") or 0)
        name  = info.get("longName") or info.get("shortName") or ticker
        return {
            "name":          name,
            "current_price": round(price, 2),
            "currency":      info.get("currency", "JPY")
        }
    except Exception:
        return {"name": ticker, "current_price": 0, "currency": "JPY"}

# ── MAIN APP LOGIC ────────────────────────────────────────────────────────────
if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
    st.markdown("#### 👀 Raw CSV Preview")
    st.dataframe(raw_df.head(5), use_container_width=True)

    # Rename columns based on sidebar mapping
    try:
        df = raw_df.rename(columns={
            col_ticker:   "ticker",
            col_shares:   "shares",
            col_avgprice: "avg_price"
        })[["ticker", "shares", "avg_price"]]
    except KeyError as e:
        st.error(f"Column not found: {e}. Check your column mapping in the sidebar.")
        st.stop()
else:
    st.info("📂 No file uploaded — showing demo data. Upload your CSV to see real portfolio.")
    df = load_demo_data()

# ── FETCH LIVE DATA ───────────────────────────────────────────────────────────
with st.spinner("🔄 Fetching live prices from Yahoo Finance..."):
    results = []
    for _, row in df.iterrows():
        info = fetch_stock_info(str(row["ticker"]).strip())
        results.append({
            "Company":        info["name"],
            "Ticker":         str(row["ticker"]).upper(),
            "Shares":         row["shares"],
            "Avg Buy Price":  row["avg_price"],
            "Current Price":  info["current_price"],
            "Market Value":   round(row["shares"] * info["current_price"], 0),
            "Cost Basis":     round(row["shares"] * row["avg_price"], 0),
            "Gain/Loss":      round((info["current_price"] - row["avg_price"]) * row["shares"], 0),
            "Gain/Loss (%)":  round(((info["current_price"] - row["avg_price"]) / row["avg_price"]) * 100, 2) if row["avg_price"] > 0 else 0
        })

portfolio_df = pd.DataFrame(results)

# ── SUMMARY METRICS ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-title">Portfolio Summary</p>', unsafe_allow_html=True)

total_value    = portfolio_df["Market Value"].sum()
total_cost     = portfolio_df["Cost Basis"].sum()
total_gain     = portfolio_df["Gain/Loss"].sum()
total_gain_pct = round(((total_value - total_cost) / total_cost) * 100, 2) if total_cost > 0 else 0
num_positions  = len(portfolio_df)
winners        = len(portfolio_df[portfolio_df["Gain/Loss (%)"] > 0])
losers         = len(portfolio_df[portfolio_df["Gain/Loss (%)"] < 0])

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Portfolio Value",  f"{symbol}{total_value:,.0f}")
m2.metric("Total Cost Basis",       f"{symbol}{total_cost:,.0f}")
m3.metric("Total Gain / Loss",      f"{symbol}{total_gain:,.0f}",    delta=f"{total_gain_pct}%")
m4.metric("Positions",              f"{num_positions}")
m5.metric("Winners / Losers",       f"{winners}W · {losers}L")

# ── HOLDINGS TABLE ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-title">Holdings</p>', unsafe_allow_html=True)

def color_gainloss(val):
    if isinstance(val, (int, float)):
        color = "#089981" if val > 0 else "#f23645" if val < 0 else "#d1d4dc"
        return f"color: {color}; font-weight: 600"
    return ""

# Fix index to start from 1
portfolio_df.index = range(1, len(portfolio_df) + 1)

# Remove .T from display ticker
portfolio_df["Ticker"] = portfolio_df["Ticker"].str.replace(".T", "", regex=False)

# Add TradingView link to Company name
portfolio_df["Company"] = portfolio_df.apply(
    lambda row: f'<a href="https://www.tradingview.com/chart/?symbol=TSE:{row["Ticker"]}" target="_blank" style="color:#2962ff; text-decoration:none;">{row["Company"]}</a>',
    axis=1
)

styled_df = portfolio_df.style\
    .map(color_gainloss, subset=["Gain/Loss", "Gain/Loss (%)"])\
    .format({
        "Avg Buy Price":  f"{symbol}{{:,.2f}}",
        "Current Price":  f"{symbol}{{:,.2f}}",
        "Market Value":   f"{symbol}{{:,.0f}}",
        "Cost Basis":     f"{symbol}{{:,.0f}}",
        "Gain/Loss":      f"{symbol}{{:,.0f}}",
        "Gain/Loss (%)":  "{:.2f}%"
    })\
    .set_properties(**{
        "background-color": "#1e2130",
        "color":            "#d1d4dc",
        "border-color":     "#2a2e39"
    })

st.write(styled_df.to_html(escape=False), unsafe_allow_html=True)

# ── CHARTS ROW ────────────────────────────────────────────────────────────────
st.markdown("---")
chart1, chart2 = st.columns(2)

# Pie chart — Portfolio Allocation
with chart1:
    st.markdown('<p class="section-title">Portfolio Allocation</p>', unsafe_allow_html=True)
    fig_pie = px.pie(
        portfolio_df,
        values="Market Value",
        names="Company",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_pie.update_layout(
        paper_bgcolor="#1e2130",
        plot_bgcolor="#1e2130",
        font_color="#d1d4dc",
        legend=dict(bgcolor="#1e2130", font=dict(color="#d1d4dc")),
        margin=dict(t=20, b=20, l=20, r=20)
    )
    fig_pie.update_traces(textfont_color="#d1d4dc")
    st.plotly_chart(fig_pie, use_container_width=True)

# Bar chart — Gain/Loss per stock
with chart2:
    st.markdown('<p class="section-title">Gain / Loss by Position</p>', unsafe_allow_html=True)
    bar_colors = ["#089981" if v >= 0 else "#f23645" for v in portfolio_df["Gain/Loss (%)"]]
    fig_bar = go.Figure(go.Bar(
        x=portfolio_df["Ticker"],
        y=portfolio_df["Gain/Loss (%)"],
        marker_color=bar_colors,
        text=[f"{v:.2f}%" for v in portfolio_df["Gain/Loss (%)"]],
        textposition="outside",
        textfont=dict(color="#d1d4dc")
    ))
    fig_bar.update_layout(
        paper_bgcolor="#1e2130",
        plot_bgcolor="#1e2130",
        font_color="#d1d4dc",
        xaxis=dict(gridcolor="#2a2e39", color="#787b86"),
        yaxis=dict(gridcolor="#2a2e39", color="#787b86", ticksuffix="%"),
        margin=dict(t=20, b=20, l=20, r=20),
        showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p style="color:#787b86; font-size:0.75rem; text-align:center;">Data sourced from Yahoo Finance · Prices delayed · Not financial advice</p>', unsafe_allow_html=True)