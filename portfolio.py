# ─────────────────────────────────────────────────────────────────────────────
# portfolio.py — Atlas Terminal  v4.0
# Premium dark navy institutional portfolio dashboard.
# Run with:  streamlit run portfolio.py
# ─────────────────────────────────────────────────────────────────────────────

import datetime

import streamlit as st

from app.config import DEFAULT_USD_JPY
from app.data import tickers
from app.data.excel_loader import load_excel, make_demo
from app.ui import theme
from app.ui.components import (
    ai_insight_card,
    kpi_card,
    label,
    money_formatter,
    news_ticker,
    safe_sum,
)
from app.ui.tab_activity import render as render_activity
from app.ui.tab_chat import render as render_chat
from app.ui.tab_decisions import render as render_decisions
from app.ui.tab_dividends import render as render_dividends
from app.ui.tab_health import render as render_health
from app.ui.tab_holdings import render as render_holdings
from app.ui.tab_overview import render as render_overview
from app.ui.tab_performance import render as render_performance
from app.ui.tab_positions import render as render_positions
from app.ui.tab_risk import render as render_risk
from app.ui.tab_tickers import render as render_tickers


# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Atlas Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
theme.inject()


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER RENDERERS  (must be defined before the routing block calls them)
# ═══════════════════════════════════════════════════════════════════════════════

def _render_kpi_row(ps, money, sym, usd_rate, num_pos):
    """6-card hero KPI row in the terminal style."""
    total_buys = safe_sum(ps, "total_bought")
    total_net  = safe_sum(ps, "net_invested")
    total_divs = safe_sum(ps, "dividends")
    total_sold = safe_sum(ps, "total_sold")
    total_trades = int(safe_sum(ps, "buy_trades"))

    net_sign = ("+" if total_net >= 0 else "−") + money(abs(total_net))
    div_yld  = f'+{total_divs/total_buys*100:.2f}% yield on cost' if total_buys else ""

    cards_html = "".join([
        kpi_card(
            eyebrow_text="Total Portfolio Value",
            jp_label="総資産",
            value=money(total_buys),
            value_class="kpi-value--cyan",
            delta_str=(
                f'<span class="pos">{net_sign}</span> '
                f'<span style="color:#64748B">net invested</span>'
            ),
            featured=True,
            glow=True,
        ),
        kpi_card(
            eyebrow_text="Total Net Invested",
            jp_label="純投資額",
            value=money(total_net),
            delta_str=f'{num_pos} positions',
        ),
        kpi_card(
            eyebrow_text="Total Dividends",
            jp_label="配当合計",
            value=money(total_divs),
            value_class="kpi-value--pos",
            delta_str=f'<span class="pos">{div_yld}</span>' if div_yld else "",
        ),
        kpi_card(
            eyebrow_text="Buy Trades",
            jp_label="買付回数",
            value=f"{total_trades:,}",
            value_class="kpi-value--cyan",
            badge="YTD",
            badge_class="pill-cyan",
        ),
        kpi_card(
            eyebrow_text="Positions",
            jp_label="保有銘柄数",
            value=f"{num_pos}",
            delta_str="active holdings",
        ),
        kpi_card(
            eyebrow_text="Total Sold",
            jp_label="売却合計",
            value=money(total_sold),
            value_class="kpi-value--warn",
        ),
    ])

    st.markdown(
        '<div style="display:grid;grid-template-columns:1.4fr 1fr 1.1fr 1fr 1fr 1.1fr;'
        f'gap:14px;margin-bottom:14px">{cards_html}</div>',
        unsafe_allow_html=True,
    )


def _render_ai_insights():
    """AI insights panel with severity-coded cards."""
    insights = [
        ("risk",        "warn", "Review position concentration",
         "Ensure no single position exceeds 20% of portfolio. "
         "Diversification across sectors reduces drawdown risk significantly.",
         "Review weights"),
        ("opportunity", "ok",   "NISA quota headroom available",
         "Check annual NISA contribution limits. Moving taxable gains "
         "to NISA growth slots eliminates 20.315% withholding on future gains.",
         "Plan transfer"),
        ("alert",       "info", "Upcoming ex-dividend events",
         "Review your holdings calendar for ex-dividend dates in the next "
         "30 days to ensure positions are held before the cut-off date.",
         "View calendar"),
        ("performance", "pos",  "Benchmark your returns",
         "Compare your portfolio against TOPIX and Nikkei 225. "
         "Use the Analytics tab for full performance attribution and Sharpe ratio.",
         "View analytics"),
    ]

    cards_html = "".join(ai_insight_card(*i) for i in insights)
    st.markdown(f"""
<div class="card" style="padding:0;overflow:hidden">
  <div style="padding:14px 16px 12px;border-bottom:1px solid rgba(148,163,184,0.10);
              display:flex;align-items:center;justify-content:space-between;
              background:linear-gradient(90deg,rgba(6,182,212,0.06),transparent 60%)">
    <div style="display:flex;align-items:center;gap:10px">
      <div style="width:32px;height:32px;border-radius:8px;
                  background:linear-gradient(135deg,#3B82F6,#06B6D4);
                  display:grid;place-items:center;
                  box-shadow:0 0 16px -2px rgba(6,182,212,0.5)">
        <svg viewBox="0 0 20 20" width="16" height="16" fill="none">
          <path d="M10 2L11.5 7L16 8L11.5 9L10 14L8.5 9L4 8L8.5 7Z" fill="white"/>
          <circle cx="16" cy="3" r="1" fill="white"/>
        </svg>
      </div>
      <div>
        <div class="font-display" style="font-size:15px;font-weight:600;color:#F8FAFC;
             display:flex;align-items:center;gap:8px">
          AI Insights
          <span class="pill pill-cyan" style="font-size:9px;padding:2px 6px">BETA</span>
        </div>
        <div style="font-size:11px;color:#64748B;margin-top:1px">{len(insights)} active signals</div>
      </div>
    </div>
  </div>
  <div style="padding:12px">{cards_html}</div>
</div>
""", unsafe_allow_html=True)


def _render_market_overview():
    """Static market overview panel (8-tile grid)."""
    items = [
        ("JP",   "TOPIX",       2842.18,  +0.0042),
        ("JP",   "Nikkei 225",  39218.4,  +0.0061),
        ("JP",   "Mothers",       742.31, -0.0083),
        ("US",   "S&P 500",     5842.12,  +0.0029),
        ("FX",   "USD/JPY",       156.42, -0.0018),
        ("US",   "VIX",            14.82, +0.0210),
        ("Rate", "JGB 10Y",         1.43, +0.0140),
        ("Comm", "Gold (¥/g)",  14852,    +0.0034),
    ]
    region_clr = {
        "JP": "#06B6D4", "US": "#3B82F6",
        "FX": "#F59E0B", "Rate": "#A78BFA", "Comm": "#F97316",
    }
    tiles = ""
    for i, (region, name, last, day) in enumerate(items):
        br = "border-right:1px solid rgba(148,163,184,0.08);" if i % 2 == 0 else ""
        bb = "border-bottom:1px solid rgba(148,163,184,0.08);" if i < len(items) - 2 else ""
        clr  = "#22C55E" if day >= 0 else "#EF4444"
        sign = "+" if day >= 0 else ""
        rc   = region_clr.get(region, "#64748B")
        lf   = f"{last:,.2f}" if last < 100 else f"{last:,.0f}"
        tiles += (
            f'<div style="padding:11px 13px;{br}{bb}">'
            f'<div style="display:flex;align-items:center;gap:5px;margin-bottom:3px">'
            f'<span style="font-size:9px;font-weight:700;color:{rc};letter-spacing:.08em;text-transform:uppercase">{region}</span>'
            f'<span style="font-size:12px;font-weight:500;color:#F8FAFC">{name}</span>'
            f'</div>'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-end">'
            f'<span class="mono" style="font-size:16px;font-weight:500">{lf}</span>'
            f'<span class="mono" style="font-size:11.5px;color:{clr}">{sign}{day*100:.2f}%</span>'
            f'</div></div>'
        )

    st.markdown(f"""
<div class="card" style="padding:0;overflow:hidden">
  <div style="padding:13px 16px 11px;border-bottom:1px solid rgba(148,163,184,0.10)">
    <div class="eyebrow">Markets</div>
    <div class="card-title font-display">Market Overview</div>
    <div class="card-sub">Indices · FX · Rates</div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr">{tiles}</div>
</div>
""", unsafe_allow_html=True)


def _render_footer():
    now_str = datetime.datetime.now().strftime("%d %b %Y %H:%M")
    st.markdown(f"""
<div class="term-footer">
  <div style="display:flex;align-items:center;gap:12px">
    <span style="display:inline-flex;align-items:center;gap:6px">
      <span class="live-dot"></span>
      <span style="color:#CBD5E1">All systems operational</span>
    </span>
    <span style="color:#475569">·</span>
    <span>Data: Yahoo Finance + Excel</span>
    <span style="color:#475569">·</span>
    <span style="color:#F59E0B;font-weight:500">Not financial advice</span>
  </div>
  <div class="mono" style="font-size:10.5px">Atlas Terminal v4.0 · As of {now_str} JST</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
<div class="brand-bar">
  <div class="brand-logo">
    <svg viewBox="0 0 20 20" width="18" height="18" fill="none">
      <path d="M3 14L7 9L11 12L17 5" stroke="white" stroke-width="2"
            stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="17" cy="5" r="1.5" fill="white"/>
    </svg>
  </div>
  <div>
    <div class="brand-title">Atlas</div>
    <div class="brand-sub">Terminal · v4.0</div>
  </div>
</div>
<div class="eyebrow" style="padding:0 8px 6px;font-size:9.5px">Navigation</div>
""", unsafe_allow_html=True)

    NAV_ITEMS = {
        "Dashboard":    "📊  Dashboard",
        "Portfolio":    "💼  Portfolio",
        "Analytics":    "📈  Analytics",
        "Health Score": "❤️   Health Score",
        "Risk":         "⚠️   Risk",
        "Decisions":    "🎯  Decisions",
        "Chat":         "💬  Chat",
        "Watchlist":    "👁   Watchlist",
        "AI Insights":  "🤖  AI Insights",
        "Backtesting":  "🔬  Backtesting",
        "Settings":     "⚙️   Settings",
    }
    active_page = st.radio(
        "",
        list(NAV_ITEMS.keys()),
        format_func=lambda k: NAV_ITEMS[k],
        label_visibility="collapsed",
        key="nav",
    )

    st.markdown("<div style='min-height:20px'></div>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<div class="eyebrow" style="margin-bottom:6px">Data Source</div>',
                unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload Excel (.xlsx)", type=["xlsx", "xls"],
        label_visibility="visible",
    )

    st.markdown("---")
    st.markdown('<div class="eyebrow" style="margin-bottom:6px">Currency</div>',
                unsafe_allow_html=True)
    currency = st.radio("Currency", ["JPY (¥)", "USD ($)"], index=0,
                        label_visibility="collapsed", horizontal=True)
    sym = "¥" if "JPY" in currency else "$"
    usd_rate = DEFAULT_USD_JPY
    if sym == "$":
        usd_rate = st.number_input(
            "JPY → USD rate",
            value=DEFAULT_USD_JPY, min_value=1.0, step=0.5, format="%.1f",
        )

    st.markdown("---")
    st.markdown("""
<div class="card" style="padding:12px;margin-top:4px">
  <div style="display:flex;align-items:center;gap:10px">
    <div style="width:34px;height:34px;border-radius:8px;
                background:linear-gradient(135deg,#1E40AF,#06B6D4);
                display:grid;place-items:center;font-weight:700;
                font-size:13px;color:white;
                box-shadow:0 4px 14px -4px rgba(6,182,212,0.5)">A</div>
    <div>
      <div style="font-size:12.5px;font-weight:600;line-height:1.2;color:#F8FAFC">Atlas User</div>
      <div style="font-size:10.5px;color:#64748B">PayPay Securities</div>
    </div>
  </div>
  <div style="margin-top:10px;padding-top:10px;border-top:1px solid rgba(148,163,184,0.10);
              display:flex;justify-content:space-between;font-size:10.5px">
    <span style="color:#64748B">Live sync</span>
    <span style="display:inline-flex;align-items:center;gap:5px">
      <span class="live-dot"></span>
      <span style="color:#22C55E">Active</span>
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

money = money_formatter(sym, usd_rate)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOAD
# ═══════════════════════════════════════════════════════════════════════════════

is_demo = uploaded is None
if is_demo:
    ps, th, dt = make_demo()
else:
    try:
        with st.spinner("Reading your Excel file…"):
            ps, th, dt = load_excel(uploaded.read())
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

tickers.init()
num_pos = len(ps)


# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════

now      = datetime.datetime.now()
time_str = now.strftime("%H:%M:%S")
date_str = now.strftime("%d %b %Y")
demo_badge = (
    '<span style="background:rgba(6,182,212,0.12);border:1px solid rgba(6,182,212,0.30);'
    'color:#06B6D4;font-size:10px;font-weight:700;letter-spacing:0.08em;'
    'padding:3px 9px;border-radius:4px;margin-left:8px">DEMO</span>'
    if is_demo else ""
)

st.markdown(f"""
<div class="term-header">
  <div style="display:flex;align-items:center;gap:18px">
    <div>
      <div class="eyebrow" style="font-size:9.5px;margin-bottom:2px">{active_page}</div>
      <div class="font-display"
           style="font-size:20px;font-weight:600;letter-spacing:-0.02em;color:#F8FAFC">
        Portfolio Overview
      </div>
    </div>
    <div style="height:32px;width:1px;background:rgba(148,163,184,0.10)"></div>
    <div style="display:flex;align-items:center;gap:8px;font-size:11.5px;color:#64748B">
      <span class="live-dot"></span>
      <span class="mono" style="color:#CBD5E1;letter-spacing:0.05em">LIVE · {time_str} JST</span>
      <span style="color:#475569">·</span>
      <span>{date_str}</span>
      {demo_badge}
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:10px">
    <span style="font-size:11px;color:#64748B">
      Data: Excel + Yahoo Finance &nbsp;·&nbsp;
      <span style="color:#F59E0B;font-weight:500">Not financial advice</span>
    </span>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# NEWS TICKER
# ═══════════════════════════════════════════════════════════════════════════════

news_ticker([
    ("14:28", "Nikkei",    "BOJ holds rate, signals October normalization path"),
    ("13:55", "Reuters",   "Toyota raises FY guidance on stronger Q4 US sales"),
    ("13:12", "Bloomberg", "Tokyo Electron up 3.2% as ASML deliveries beat"),
    ("12:48", "Nikkei",    "Yen weakens past 156 as US yields climb"),
    ("11:30", "Reuters",   "SoftBank Group to spin out Arm China unit"),
])


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE ROUTING
# ═══════════════════════════════════════════════════════════════════════════════

if active_page == "Dashboard":
    _render_kpi_row(ps, money, sym, usd_rate, num_pos)

    # Row 1: AI Insights + Market Overview (neither creates nested columns)
    c_ai, c_mkt = st.columns([3, 2])
    with c_ai:
        _render_ai_insights()
    with c_mkt:
        _render_market_overview()

    st.markdown("---")
    label("Holdings")
    render_holdings(ps, money)

    st.markdown("---")
    label("Sector Allocation")
    render_overview(ps, th)

    st.markdown("---")
    label("Activity & Dividends")
    c_act, c_div = st.columns(2)
    with c_act:
        render_activity(th, money)
    with c_div:
        render_dividends(dt, money)

    _render_footer()


elif active_page == "Portfolio":
    _render_kpi_row(ps, money, sym, usd_rate, num_pos)
    st.markdown("---")
    label("Holdings")
    render_holdings(ps, money)
    st.markdown("---")
    label("Positions Detail")
    render_positions(ps, th, money)
    st.markdown("---")
    label("Sector Allocation")
    render_overview(ps, th)
    _render_footer()


elif active_page == "Analytics":
    _render_kpi_row(ps, money, sym, usd_rate, num_pos)
    st.markdown("---")
    render_performance(ps, th, money)
    _render_footer()


elif active_page == "Risk":
    _render_kpi_row(ps, money, sym, usd_rate, num_pos)
    st.markdown("---")
    render_risk(ps, th, money)
    _render_footer()


elif active_page == "Health Score":
    _render_kpi_row(ps, money, sym, usd_rate, num_pos)
    st.markdown("---")
    render_health(ps, th, money)
    _render_footer()


elif active_page == "Decisions":
    _render_kpi_row(ps, money, sym, usd_rate, num_pos)
    st.markdown("---")
    render_decisions(ps, th, money)
    _render_footer()


elif active_page == "Chat":
    render_chat(ps, th, money)
    _render_footer()


elif active_page == "Watchlist":
    c_wl, c_mkt = st.columns([2, 1])
    with c_wl:
        label("Ticker Watchlist")
        render_tickers(ps)
    with c_mkt:
        _render_market_overview()
    _render_footer()


elif active_page == "AI Insights":
    _render_ai_insights()
    st.markdown("---")
    _render_kpi_row(ps, money, sym, usd_rate, num_pos)
    _render_footer()


elif active_page == "Backtesting":
    st.markdown("""
<div style="max-width:560px;margin:40px auto">
<div class="card" style="padding:40px;text-align:center">
  <div style="width:52px;height:52px;border-radius:14px;
              background:linear-gradient(135deg,#3B82F6,#06B6D4);
              display:grid;place-items:center;margin:0 auto 18px;
              box-shadow:0 0 28px -4px rgba(6,182,212,0.55)">
    <svg viewBox="0 0 20 20" width="24" height="24" fill="none">
      <path d="M3 4h14v12H3zM3 8h14M7 4v12M11 11l2 2 4-4"
            stroke="white" stroke-width="1.4" stroke-linejoin="round"/>
    </svg>
  </div>
  <div class="font-display" style="font-size:20px;font-weight:600;margin-bottom:8px;color:#F8FAFC">
    Backtesting Engine
  </div>
  <div style="font-size:13px;color:#64748B;line-height:1.6;max-width:400px;margin:0 auto">
    Replay strategies against your historical Excel data with realistic
    transaction costs and Japanese tax modeling (20.315% 特定口座).
  </div>
  <div style="margin-top:22px">
    <span style="display:inline-block;padding:10px 22px;
                 background:linear-gradient(180deg,#1E40AF,#1E3A8A);
                 border:1px solid rgba(59,130,246,0.4);border-radius:8px;
                 font-size:13px;font-weight:500;color:#F8FAFC;
                 box-shadow:0 6px 20px -6px rgba(59,130,246,0.5)">
      Coming soon
    </span>
  </div>
</div>
</div>
""", unsafe_allow_html=True)
    _render_footer()


elif active_page == "Settings":
    st.markdown(
        '<div class="font-display" style="font-size:22px;font-weight:600;'
        'margin-bottom:18px;color:#F8FAFC">Preferences</div>',
        unsafe_allow_html=True,
    )
    rows = [
        ("Default currency",    currency),
        ("JPY → USD rate",      f"{usd_rate:.2f}"),
        ("Excel schema",        "PayPay Securities v3.1"),
        ("Price source",        "Yahoo Finance + 15-min delayed fallback"),
        ("Tax rate (特定口座)", "20.315% (income + reconstruction surtax)"),
        ("Cache refresh",       "Every 5 minutes during market hours"),
        ("Risk-free rate",      "JGB 10Y · 1.428%"),
        ("Benchmark",           "TOPIX (primary), Nikkei 225 (secondary)"),
    ]
    rows_html = "".join(
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'padding:12px 0;border-bottom:1px solid rgba(148,163,184,0.08)">'
        f'<span style="color:#CBD5E1">{l}</span>'
        f'<span class="mono" style="color:#F8FAFC">{v}</span></div>'
        for l, v in rows
    )
    st.markdown(
        f'<div class="card" style="padding:20px;max-width:720px">{rows_html}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    label("Ticker Mappings")
    render_tickers(ps)
    _render_footer()
