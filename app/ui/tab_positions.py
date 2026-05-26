"""Positions tab — live prices, market value, unrealized P&L, sector tags.

All values shown in JPY. Non-JPY tickers are converted via live FX rates
(see app/data/fx.py), so e.g. AAPL holdings are priced as
shares × USD-price × USDJPY.
"""
from typing import Callable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.analytics import positions as pos
from app.config import BLUE, CARD, GOLD, GREEN, MUTED, NOGRID, RED, TEXT
from app.data import tickers
from app.ui.components import chart_base, fmt_pct, label, section_hd, tv_url


def _color(value: float) -> str:
    if value > 0: return GREEN
    if value < 0: return RED
    return MUTED


def _signed(value: float, formatter: Callable[[float], str]) -> str:
    s = formatter(abs(value))
    if value > 0: return f"+{s}"
    if value < 0: return f"−{s}"
    return s


def render(ps: pd.DataFrame, th: pd.DataFrame, money: Callable[[float], str]) -> None:
    ticker_map = tickers.all_mappings()

    if not ticker_map:
        st.info(
            "🎯 **No tickers mapped yet.** Open the **Tickers** tab to link your "
            "company names to Yahoo Finance symbols (e.g. `Toyota Motor` → `7203.T`). "
            "Once mapped, this tab will show live prices, market value, and P&L."
        )
        return

    with st.spinner("Fetching live market data…"):
        positions = pos.build_positions(ps, th, ticker_map)

    if positions.empty:
        st.warning(
            "Could not build positions. Common causes: tickers are invalid, "
            "no Buy/Sell transactions exist for mapped companies, or yfinance "
            "returned no history. Check the Tickers tab."
        )
        return

    multi_ccy = positions["currency"].nunique() > 1
    if multi_ccy:
        ccys = ", ".join(sorted(positions["currency"].unique()))
        st.caption(f"💱 Multi-currency portfolio ({ccys}) — all values converted to JPY at live FX rates.")

    # ── KPI row ──────────────────────────────────────────────────────────────
    k = pos.portfolio_kpis(positions)
    st.markdown(section_hd("Live Portfolio", "Real-time market value and P&L", "Positions"), unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Market Value",      money(k["market_value"]))
    c2.metric("Cost Basis",        money(k["cost_basis"]))
    c3.metric(
        "Unrealized P&L",
        money(k["unrealized_pl"]),
        delta=fmt_pct(k["unrealized_pct"]),
    )
    c4.metric(
        "Today's Change",
        money(k["day_change"]),
        delta=fmt_pct(k["day_change_pct"]),
    )
    c5.metric("Live Positions", f"{k['n_positions']:,}")

    st.markdown("---")

    # ── Positions table ──────────────────────────────────────────────────────
    view = positions.sort_values("market_value", ascending=False).reset_index(drop=True)

    tbl = '<table class="ptable"><thead><tr>'
    for h in ["#", "Company", "Ticker", "Sector", "CCY", "Shares", "Avg Cost",
              "Price (JPY)", "Day %", "Market Value", "Cost Basis", "Unrealized P&L", "Return", "TV"]:
        tbl += f"<th>{h}</th>"
    tbl += "</tr></thead><tbody>"

    for i, (_, r) in enumerate(view.iterrows(), 1):
        pl_color    = _color(r["unrealized_pl"])
        day_color   = _color(r["day_change_pct"])
        day_display = f"{r['day_change_pct'] * 100:+.2f}%"

        tbl += (
            f"<tr>"
            f'<td style="color:{MUTED};font-size:0.7rem">{i}</td>'
            f'<td style="font-weight:600">{r["company"]}</td>'
            f'<td style="color:{BLUE};font-weight:600">{r["ticker"]}</td>'
            f'<td style="color:{MUTED}">{r["sector"]}</td>'
            f'<td style="color:{MUTED};font-size:0.75rem">{r["currency"]}</td>'
            f'<td style="text-align:right">{r["shares"]:,.2f}</td>'
            f"<td>{money(r['avg_cost'])}</td>"
            f"<td>{money(r['current_price_jpy'])}</td>"
            f'<td style="color:{day_color};font-weight:600;text-align:right">{day_display}</td>'
            f'<td style="font-weight:700">{money(r["market_value"])}</td>'
            f"<td>{money(r['cost_basis'])}</td>"
            f'<td style="color:{pl_color};font-weight:700">{_signed(r["unrealized_pl"], money)}</td>'
            f'<td style="color:{pl_color};font-weight:700;text-align:right">{fmt_pct(r["unrealized_pct"])}</td>'
            f'<td><a href="{tv_url(r["ticker"])}" target="_blank" '
            f'style="color:{BLUE};text-decoration:none">📊</a></td>'
            f"</tr>"
        )

    tbl += (
        f'<tr class="tot">'
        f'<td colspan="9">TOTAL — {k["n_positions"]:,} live positions</td>'
        f"<td>{money(k['market_value'])}</td>"
        f"<td>{money(k['cost_basis'])}</td>"
        f'<td style="color:{_color(k["unrealized_pl"])};font-weight:700">'
        f'{_signed(k["unrealized_pl"], money)}</td>'
        f'<td style="color:{_color(k["unrealized_pl"])};font-weight:700;text-align:right">'
        f'{fmt_pct(k["unrealized_pct"])}</td>'
        f"<td></td>"
        f"</tr>"
    )
    tbl += "</tbody></table>"

    st.markdown(
        f'<div class="card" style="padding:0;overflow:hidden">'
        f'<div class="card-hd-inner">'
        f'<div class="eyebrow">Live Holdings</div>'
        f'<div class="card-title font-display">{k["n_positions"]:,} Positions</div>'
        f'</div>'
        f'<div style="overflow-x:auto">{tbl}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Sector exposure ──────────────────────────────────────────────────────
    if positions["sector"].nunique() > 0:
        col_pie, col_bar = st.columns(2)

        with col_pie:
            st.markdown(section_hd("Sector Exposure", "By market value", "Sectors"), unsafe_allow_html=True)
            sec = positions.groupby("sector", as_index=False)["market_value"].sum()
            sec = sec.sort_values("market_value", ascending=False)
            fig = px.pie(
                sec, values="market_value", names="sector",
                hole=0.55,
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig.update_traces(
                textfont_color=TEXT,
                textinfo="percent",
                hovertemplate="<b>%{label}</b><br>¥%{value:,.0f}<br>%{percent}<extra></extra>",
            )
            fig.update_layout(
                **chart_base(height=380, showlegend=True),
                legend=dict(bgcolor=CARD, font=dict(color=TEXT, size=9)),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_bar:
            st.markdown(section_hd("Position Sizing", "Top 20 by market value", "Sizing"), unsafe_allow_html=True)
            top = positions.nlargest(20, "market_value").sort_values("market_value")
            fig = go.Figure(go.Bar(
                x=top["market_value"], y=top["company"],
                orientation="h",
                marker_color=GREEN, opacity=0.88,
                hovertemplate="<b>%{y}</b><br>Market Value: ¥%{x:,.0f}<extra></extra>",
            ))
            fig.update_layout(**chart_base(
                height=380,
                xaxis=dict(color=MUTED, gridcolor=NOGRID, showgrid=False, tickprefix="¥"),
                yaxis=dict(color=MUTED, gridcolor=NOGRID, showgrid=False),
            ))
            st.plotly_chart(fig, use_container_width=True)

    # ── CSV export ───────────────────────────────────────────────────────────
    csv_pos = positions.rename(columns={
        "company": "Company", "ticker": "Ticker", "sector": "Sector",
        "industry": "Industry", "country": "Country", "currency": "Currency",
        "fx_rate": "FX→JPY", "shares": "Shares", "cost_basis": "Cost Basis (¥)",
        "avg_cost": "Avg Cost (¥)", "current_price": "Current Price",
        "current_price_jpy": "Current Price (¥)", "prev_close": "Previous Close",
        "prev_close_jpy": "Previous Close (¥)", "day_change_pct": "Day Change %",
        "market_value": "Market Value (¥)", "unrealized_pl": "Unrealized P&L (¥)",
        "unrealized_pct": "Unrealized %",
    }).to_csv(index=False)
    st.download_button("⬇ Export Positions CSV", csv_pos, "positions.csv", "text/csv")
