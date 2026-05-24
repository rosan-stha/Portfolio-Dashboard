# ─────────────────────────────────────────────────────────────────────────────
# portfolio.py — Portfolio Intelligence Platform  v3.1
# Streamlit entrypoint. All logic lives in the `app/` package.
# Run with:  streamlit run portfolio.py
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st

from app.config import DEFAULT_USD_JPY
from app.data import tickers
from app.data.excel_loader import load_excel, make_demo
from app.ui import theme
from app.ui.components import label, money_formatter, safe_sum
from app.ui.tab_activity import render as render_activity
from app.ui.tab_dividends import render as render_dividends
from app.ui.tab_health import render as render_health
from app.ui.tab_holdings import render as render_holdings
from app.ui.tab_overview import render as render_overview
from app.ui.tab_performance import render as render_performance
from app.ui.tab_positions import render as render_positions
from app.ui.tab_risk import render as render_risk
from app.ui.tab_tickers import render as render_tickers


# ─── Page config + theme ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Portfolio Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
theme.inject()


# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 Portfolio Intelligence")
    st.markdown('<p class="lbl">PayPay Securities · Japan Equities</p>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 📂 Upload Excel File")
    st.caption(
        "Your Excel must have three sheets:\n"
        "- **Portfolio Summary**\n"
        "- **Transaction History**\n"
        "- **Dividend Tracker**"
    )
    uploaded = st.file_uploader(
        "Select .xlsx file",
        type=["xlsx", "xls"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### 💱 Display Currency")
    currency = st.radio("Currency", ["JPY (¥)", "USD ($)"], index=0, label_visibility="collapsed")
    sym = "¥" if "JPY" in currency else "$"
    usd_rate = DEFAULT_USD_JPY
    if sym == "$":
        usd_rate = st.number_input(
            "JPY → USD exchange rate",
            value=DEFAULT_USD_JPY, min_value=1.0, step=0.5, format="%.1f",
        )

    st.markdown("---")
    st.caption(
        "Data: Excel upload + Yahoo Finance live prices.\n"
        "Not financial advice."
    )

money = money_formatter(sym, usd_rate)


# ─── Load data ──────────────────────────────────────────────────────────────
if uploaded is None:
    ps, th, dt = make_demo()
    st.info(
        "📂 **Demo mode** — upload your Excel file in the sidebar to see real data.",
        icon="ℹ️",
    )
else:
    try:
        with st.spinner("Reading your Excel file…"):
            ps, th, dt = load_excel(uploaded.read())
        st.success(
            f"✅ Loaded **{len(ps):,} positions** from your portfolio file.",
            icon="✅",
        )
    except Exception as e:
        st.error(f"❌ Could not read file: {e}")
        st.stop()

# Initialize ticker store (loads from disk on first call)
tickers.init()


# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown("## 📊 Portfolio Dashboard")
label("PayPay Securities · Japan Equities")
st.markdown("---")


# ─── Top KPI row (cost-basis view, always available) ────────────────────────
label("Portfolio At a Glance")
total_net    = safe_sum(ps, "net_invested")
total_bought = safe_sum(ps, "total_bought")
total_divs   = safe_sum(ps, "dividends")
total_trades = int(safe_sum(ps, "buy_trades"))
num_pos      = len(ps)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Net Invested",  money(total_net))
c2.metric("Total Gross Bought",  money(total_bought))
c3.metric("Total Dividends",     money(total_divs))
c4.metric("Positions",           f"{num_pos:,}")
c5.metric("Buy Trades",          f"{total_trades:,}")

st.markdown("---")


# ─── Tabs ───────────────────────────────────────────────────────────────────
tab_ov, tab_health, tab_pos, tab_risk, tab_perf, tab_hold, tab_act, tab_div, tab_tick = st.tabs([
    "📊  Overview",
    "🎯  Health",
    "💹  Positions",
    "⚠️  Risk",
    "📈  Performance",
    "📋  Holdings",
    "📜  Activity",
    "💰  Dividends",
    "🏷️  Tickers",
])

with tab_ov:
    render_overview(ps, th)

with tab_health:
    render_health(ps, th, money)

with tab_pos:
    render_positions(ps, th, money)

with tab_risk:
    render_risk(ps, th, money)

with tab_perf:
    render_performance(ps, th, money)

with tab_hold:
    render_holdings(ps, money)

with tab_act:
    render_activity(th, money)

with tab_div:
    render_dividends(dt, money)

with tab_tick:
    render_tickers(ps)


# ─── Footer ─────────────────────────────────────────────────────────────────
from app.config import MUTED
st.markdown("---")
st.markdown(
    f'<p style="color:{MUTED};font-size:0.75rem;text-align:center;">'
    "Data: Excel upload + Yahoo Finance &nbsp;·&nbsp; Not financial advice "
    "&nbsp;·&nbsp; Portfolio Intelligence v3.1"
    "</p>",
    unsafe_allow_html=True,
)
