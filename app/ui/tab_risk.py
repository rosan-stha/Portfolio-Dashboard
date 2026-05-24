"""Risk Exposure tab — sector/country/currency/cap breakdowns + correlation heatmap."""
from typing import Callable

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.analytics import correlation as corr_mod
from app.analytics import positions as pos
from app.config import BLUE, BORDER, CARD, GOLD, GREEN, MUTED, NOGRID, RED, TEXT
from app.data import market, tickers
from app.ui.components import chart_base, label


def _exposure_pie(df: pd.DataFrame, group_col: str, title: str):
    label(title)
    if df.empty or df[group_col].isna().all():
        st.info("No data available.")
        return
    agg = df.groupby(group_col, as_index=False)["market_value"].sum()
    agg = agg.sort_values("market_value", ascending=False)
    fig = px.pie(
        agg, values="market_value", names=group_col,
        hole=0.55,
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig.update_traces(
        textfont_color=TEXT,
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>¥%{value:,.0f}<br>%{percent}<extra></extra>",
    )
    fig.update_layout(
        **chart_base(height=340, showlegend=True),
        legend=dict(bgcolor=CARD, font=dict(color=TEXT, size=9), orientation="v"),
    )
    st.plotly_chart(fig, use_container_width=True)


def _market_cap_bucket(market_cap: float) -> str:
    """Bucket market cap (USD) into Mega/Large/Mid/Small/Micro."""
    if not market_cap or market_cap <= 0:
        return "Unknown"
    if market_cap >= 200e9: return "Mega Cap (>$200B)"
    if market_cap >= 10e9:  return "Large Cap ($10B–$200B)"
    if market_cap >= 2e9:   return "Mid Cap ($2B–$10B)"
    if market_cap >= 300e6: return "Small Cap ($300M–$2B)"
    return "Micro Cap (<$300M)"


def _enrich_market_cap(positions: pd.DataFrame) -> pd.DataFrame:
    """Add `market_cap_bucket` column by re-querying yfinance info (cached)."""
    if positions.empty:
        return positions
    buckets = []
    for _, r in positions.iterrows():
        info = market.get_info(r["ticker"])
        mc = info.get("market_cap") if isinstance(info, dict) else None
        # market.get_info doesn't currently return market_cap — fall back to direct fetch
        if mc is None:
            try:
                import yfinance as yf
                raw = yf.Ticker(r["ticker"]).info or {}
                mc = raw.get("marketCap")
            except Exception:
                mc = None
        buckets.append(_market_cap_bucket(mc))
    out = positions.copy()
    out["market_cap_bucket"] = buckets
    return out


def render(ps: pd.DataFrame, th: pd.DataFrame, money: Callable[[float], str]) -> None:
    ticker_map = tickers.all_mappings()
    if not ticker_map:
        st.info("🎯 Map tickers in the **Tickers** tab to compute risk exposure.")
        return

    with st.spinner("Analyzing exposure…"):
        positions = pos.build_positions(ps, th, ticker_map)
        if positions.empty:
            st.warning("No live positions — check the Tickers tab.")
            return

    # ── Headline risk KPIs ───────────────────────────────────────────────────
    weights = pos.position_weights(positions)
    total_mv = float(positions["market_value"].sum())
    n_sectors = positions["sector"].nunique()
    n_countries = positions["country"].nunique()
    top_w = float(weights.iloc[0]) if not weights.empty else 0.0
    sector_w = positions.groupby("sector")["market_value"].sum() / total_mv if total_mv else pd.Series()
    top_sector_w = float(sector_w.max()) if not sector_w.empty else 0.0

    label("Exposure Snapshot")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Positions",       f"{len(positions):,}")
    k2.metric("Sectors",         f"{n_sectors}")
    k3.metric("Top Position",    f"{top_w * 100:.1f}%")
    k4.metric("Top Sector",      f"{top_sector_w * 100:.1f}%")

    st.markdown("---")

    # ── Exposure breakdowns ─────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        _exposure_pie(positions, "sector",   "Sector Exposure")
    with c2:
        _exposure_pie(positions, "country",  "Country Exposure")

    c3, c4 = st.columns(2)
    with c3:
        _exposure_pie(positions, "currency", "Currency Exposure")
    with c4:
        with st.spinner("Loading market-cap classifications…"):
            enriched = _enrich_market_cap(positions)
        _exposure_pie(enriched, "market_cap_bucket", "Market-Cap Buckets")

    st.markdown("---")

    # ── Treemap: sector → company ───────────────────────────────────────────
    label("Sector × Position Treemap")
    fig = px.treemap(
        positions,
        path=["sector", "company"],
        values="market_value",
        color="market_value",
        color_continuous_scale=[[0, CARD], [0.35, BLUE], [1, GREEN]],
    )
    fig.update_traces(
        textfont=dict(color=TEXT),
        hovertemplate="<b>%{label}</b><br>¥%{value:,.0f}<extra></extra>",
    )
    fig.update_layout(**chart_base(height=460), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Correlation heatmap ─────────────────────────────────────────────────
    label("Position Correlation Matrix — 1-Year Daily Returns")
    period_choice = st.select_slider(
        "Lookback window",
        options=["3M", "6M", "1Y", "2Y", "5Y"],
        value="1Y",
        key="risk_corr_period",
    )

    with st.spinner("Computing correlations…"):
        corr = corr_mod.correlation_matrix(positions, period=period_choice)

    if corr.empty or len(corr) < 2:
        st.info("Need at least 2 positions with overlapping price history for correlation analysis.")
        return

    # Map tickers → company names for labels
    ticker_to_company = dict(zip(positions["ticker"], positions["company"]))
    labels = [ticker_to_company.get(t, t) for t in corr.index]

    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=labels, y=labels,
        zmin=-1, zmax=1,
        colorscale=[
            [0.0, RED], [0.5, CARD], [1.0, GREEN],
        ],
        hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>Correlation: %{z:.3f}<extra></extra>",
        colorbar=dict(
            tickfont=dict(color=MUTED, size=10),
            outlinewidth=0,
            thickness=12,
        ),
    ))
    h = max(420, len(labels) * 28)
    fig.update_layout(
        **chart_base(height=h),
        xaxis=dict(color=MUTED, side="bottom", tickangle=-40),
        yaxis=dict(color=MUTED, autorange="reversed"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Summary stats
    avg_corr = corr_mod.average_pairwise_correlation(corr)
    high_pairs = corr_mod.high_correlation_pairs(corr)
    cstat1, cstat2 = st.columns(2)
    cstat1.metric("Avg Pairwise Correlation", f"{avg_corr:.3f}")
    cstat2.metric("Highly Correlated Pairs (>0.85)", f"{len(high_pairs)}")

    if high_pairs:
        label(f"Top Correlated Pairs")
        html = '<table class="ptable"><thead><tr>'
        for h in ["#", "Position A", "Position B", "Correlation"]:
            html += f"<th>{h}</th>"
        html += "</tr></thead><tbody>"
        for i, (a, b, c) in enumerate(high_pairs[:15], 1):
            ca = ticker_to_company.get(a, a)
            cb = ticker_to_company.get(b, b)
            html += (
                f'<tr><td style="color:{MUTED};font-size:0.7rem">{i}</td>'
                f'<td style="font-weight:600">{ca} <span style="color:{MUTED}">({a})</span></td>'
                f'<td style="font-weight:600">{cb} <span style="color:{MUTED}">({b})</span></td>'
                f'<td style="color:{RED};font-weight:700;text-align:right">{c:.3f}</td></tr>'
            )
        html += "</tbody></table>"
        st.write(html, unsafe_allow_html=True)
