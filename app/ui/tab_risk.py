"""Risk Exposure tab — sector/country/currency/cap breakdowns + correlation heatmap + alerts."""
from typing import Callable

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.alerts.thresholds import check_all_alerts
from app.analytics import correlation as corr_mod
from app.analytics import positions as pos
from app.config import ALERT_THRESHOLDS, BLUE, BORDER, CARD, GOLD, GREEN, MUTED, NOGRID, RED, TEXT
from app.data import market, tickers
from app.ui.components import chart_base, label, section_hd


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
    """Add `market_cap_bucket` column using cached market.get_info()."""
    if positions.empty:
        return positions
    buckets = []
    for _, r in positions.iterrows():
        info = market.get_info(r["ticker"])
        mc   = info.get("market_cap", 0) if isinstance(info, dict) else 0
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

    st.markdown(section_hd("Exposure Snapshot", "Real-time position breakdown", "Risk"), unsafe_allow_html=True)
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
    st.markdown(section_hd("Sector × Position Treemap", "Market value by sector and company", "Treemap"), unsafe_allow_html=True)
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
    st.markdown(section_hd("Correlation Matrix", "Daily returns — select lookback window below", "Correlation"), unsafe_allow_html=True)
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
        tbl = '<table class="ptable"><thead><tr>'
        for h in ["#", "Position A", "Position B", "Correlation"]:
            tbl += f"<th>{h}</th>"
        tbl += "</tr></thead><tbody>"
        for i, (a, b, c) in enumerate(high_pairs[:15], 1):
            ca = ticker_to_company.get(a, a)
            cb = ticker_to_company.get(b, b)
            tbl += (
                f'<tr><td style="color:{MUTED};font-size:0.7rem">{i}</td>'
                f'<td style="font-weight:600">{ca} <span style="color:{MUTED}">({a})</span></td>'
                f'<td style="font-weight:600">{cb} <span style="color:{MUTED}">({b})</span></td>'
                f'<td style="color:{RED};font-weight:700;text-align:right">{c:.3f}</td></tr>'
            )
        tbl += "</tbody></table>"
        st.markdown(
            f'<div class="card" style="padding:0;overflow:hidden;margin-top:8px">'
            f'<div class="card-hd-inner">'
            f'<div class="eyebrow">Concentration Risk</div>'
            f'<div class="card-title font-display">Top Correlated Pairs</div>'
            f'</div>'
            f'<div style="overflow-x:auto">{tbl}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Active alerts panel ──────────────────────────────────────────────────
    st.markdown(section_hd("Active Risk Alerts", "Threshold breach monitoring", "Alerts"), unsafe_allow_html=True)
    with st.spinner("Checking thresholds…"):
        alerts = check_all_alerts(positions)

    if not alerts:
        st.markdown(
            f'<div class="card" style="border-left:3px solid {GREEN};padding:14px 16px;'
            f'color:{GREEN};display:flex;align-items:center;gap:10px">'
            f'<span style="font-size:16px">✅</span>'
            f'<span>No threshold breaches detected across all risk dimensions.</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        sev_color = {"HIGH": RED, "MEDIUM": GOLD, "LOW": BLUE}
        sev_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🔵"}
        for alert in alerts[:10]:
            sev   = alert.get("severity", "LOW")
            color = sev_color.get(sev, BLUE)
            emoji = sev_emoji.get(sev, "🔵")
            st.markdown(
                f'<div class="card" style="border-left:3px solid {color};padding:14px 16px;margin-bottom:8px">'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">'
                f'<span>{emoji}</span>'
                f'<span class="pill" style="background:rgba(0,0,0,0.3);color:{color};'
                f'border-color:{color}40;font-size:9px;padding:2px 7px;letter-spacing:0.10em">'
                f'{sev} · {alert.get("type","")}</span>'
                f'<span style="font-size:10px;color:{MUTED}">{alert.get("timestamp","")}</span>'
                f'</div>'
                f'<div style="font-size:12.5px;color:#CBD5E1;line-height:1.5">{alert.get("message","")}</div>'
                f'<div style="font-size:11px;color:{MUTED};margin-top:6px">'
                f'Suggested: {alert.get("suggested_action","")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        if len(alerts) > 10:
            st.caption(f"… {len(alerts) - 10} more alerts not shown.")

    st.markdown("---")

    # ── Threshold reference ───────────────────────────────────────────────────
    st.markdown(section_hd("Alert Thresholds", "Configurable in app/config.py", "Config"), unsafe_allow_html=True)
    thresh_rows = [
        ("Max single position", f"{ALERT_THRESHOLDS['max_position_pct']:.0%}"),
        ("Max sector exposure", f"{ALERT_THRESHOLDS['max_sector_pct']:.0%}"),
        ("Max currency exposure", f"{ALERT_THRESHOLDS['max_currency_pct']:.0%}"),
        ("Max pairwise correlation", f"{ALERT_THRESHOLDS['max_correlation']:.2f}"),
        ("Daily move alert", f"±{ALERT_THRESHOLDS['daily_move_pct']:.0%}"),
        ("Min health score", f"{ALERT_THRESHOLDS['min_health_score']}/100"),
    ]
    rows_html = "".join(
        f'<div style="display:flex;justify-content:space-between;padding:9px 0;'
        f'border-bottom:1px solid rgba(148,163,184,0.08)">'
        f'<span style="color:#CBD5E1">{lbl}</span>'
        f'<span style="font-family:\'JetBrains Mono\',monospace;color:#F8FAFC">{val}</span>'
        f'</div>'
        for lbl, val in thresh_rows
    )
    st.markdown(
        f'<div style="background:{CARD};border:1px solid rgba(148,163,184,0.10);'
        f'border-radius:10px;padding:16px;max-width:480px">{rows_html}</div>',
        unsafe_allow_html=True,
    )
