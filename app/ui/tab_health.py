"""Health Score tab — overall gauge, subscore radar, recommendations panel."""
from typing import Callable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.analytics import health
from app.analytics import positions as pos
from app.config import BLUE, BORDER, CARD, GOLD, GREEN, MUTED, NOGRID, RED, TEXT
from app.data import tickers
from app.ui.components import chart_base, fmt_pct, kpi_card, label, section_hd


SUBSCORE_LABELS = {
    "diversification": "Diversification",
    "sector_balance":  "Sector Balance",
    "concentration":   "Concentration",
    "volatility":      "Volatility",
    "sharpe":          "Risk-Adj Return",
    "drawdown":        "Drawdown",
    "momentum":        "Momentum",
    "correlation":     "Correlation",
}

SEVERITY_COLORS = {
    "high":   RED,
    "medium": GOLD,
    "low":    BLUE,
    "info":   GREEN,
}


def _score_color(score: float) -> str:
    if score >= 75: return GREEN
    if score >= 50: return GOLD
    return RED


def _gauge(score: float) -> go.Figure:
    color = _score_color(score)
    grade, descriptor = health.score_grade(score)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"color": TEXT, "size": 56}, "suffix": ""},
        gauge={
            "axis":      {"range": [0, 100], "tickcolor": MUTED, "tickwidth": 1, "tickfont": {"color": MUTED, "size": 10}},
            "bar":       {"color": color, "thickness": 0.35},
            "bgcolor":   CARD,
            "borderwidth": 0,
            "steps": [
                {"range": [0,  50],  "color": "#3a1a22"},
                {"range": [50, 75],  "color": "#3a311a"},
                {"range": [75, 100], "color": "#1a3a2e"},
            ],
            "threshold": {"line": {"color": TEXT, "width": 3}, "thickness": 0.8, "value": score},
        },
        title={"text": f"<span style='font-size:0.8rem;color:{MUTED}'>{descriptor}  ·  Grade {grade}</span>",
               "font": {"color": MUTED}},
        domain={"x": [0, 1], "y": [0, 1]},
    ))
    fig.update_layout(**chart_base(height=300))
    return fig


def _radar(subscores: dict) -> go.Figure:
    categories = [SUBSCORE_LABELS[k] for k in subscores]
    values = list(subscores.values())
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor=f"rgba(41,98,255,0.20)",
        line=dict(color=BLUE, width=2),
        marker=dict(color=BLUE, size=6),
        hovertemplate="<b>%{theta}</b><br>%{r:.0f} / 100<extra></extra>",
    ))
    fig.update_layout(
        **chart_base(height=400),
        polar=dict(
            bgcolor=CARD,
            radialaxis=dict(
                range=[0, 100],
                color=MUTED, gridcolor=BORDER, linecolor=BORDER,
                tickfont=dict(color=MUTED, size=9),
            ),
            angularaxis=dict(
                color=TEXT, gridcolor=BORDER, linecolor=BORDER,
                tickfont=dict(color=TEXT, size=11),
            ),
        ),
    )
    return fig


def render(ps: pd.DataFrame, th: pd.DataFrame, money: Callable[[float], str]) -> None:
    ticker_map = tickers.all_mappings()
    if not ticker_map:
        st.info(
            "🎯 Map tickers in the **Tickers** tab to compute your Portfolio Health Score."
        )
        return

    with st.spinner("Scoring your portfolio…"):
        positions = pos.build_positions(ps, th, ticker_map)
        if positions.empty:
            st.warning("No live positions — check the Tickers tab.")
            return
        report = health.evaluate(positions, period="1Y")

    # ── Headline row: gauge + radar + raw KPIs ───────────────────────────────
    g_col, r_col = st.columns([1, 1])
    with g_col:
        st.markdown(section_hd("Portfolio Health Score", "Composite 8-factor model", "Health"), unsafe_allow_html=True)
        st.plotly_chart(_gauge(report.overall), use_container_width=True)
    with r_col:
        st.markdown(section_hd("Subscore Profile", "8-dimension radar", "Breakdown"), unsafe_allow_html=True)
        st.plotly_chart(_radar(report.subscores), use_container_width=True)

    st.markdown("---")

    # ── Subscore cards ───────────────────────────────────────────────────────
    label("Subscore Breakdown")
    cards_html = ""
    for key, val in report.subscores.items():
        vc = "kpi-value--pos" if val >= 75 else ("kpi-value--warn" if val >= 50 else "kpi-value--neg")
        cards_html += kpi_card(
            eyebrow_text=SUBSCORE_LABELS[key],
            value=f"{val:.0f}",
            value_class=vc,
            value_suffix=" / 100",
        )
    st.markdown(
        f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:14px">{cards_html}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Raw metrics strip ────────────────────────────────────────────────────
    st.markdown(section_hd("Raw Inputs", "Underlying metrics used in scoring", "Metrics"), unsafe_allow_html=True)
    raw = report.raw_metrics
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Volatility (ann.)",        fmt_pct(raw.get("volatility", 0)))
    k2.metric("Sharpe Ratio",              f"{raw.get('sharpe', 0):.2f}")
    k3.metric("Max Drawdown",              fmt_pct(raw.get("max_drawdown", 0)))
    k4.metric("Avg Pairwise Correlation",  f"{raw.get('avg_correlation', 0):.2f}")
    k5.metric("Top Position Weight",       fmt_pct(raw.get("top_weight", 0)))

    st.markdown("---")

    # ── Recommendations ──────────────────────────────────────────────────────
    st.markdown(section_hd("Recommendations", "Priority actions to improve portfolio health", "Actions"), unsafe_allow_html=True)
    for rec in report.recommendations:
        sev = rec["severity"]
        color = SEVERITY_COLORS.get(sev, BLUE)
        badge = sev.upper()
        st.markdown(
            f'<div class="card" style="border-left:3px solid {color};padding:14px 16px;margin-bottom:8px">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">'
            f'<span class="pill" style="background:rgba(0,0,0,0.3);color:{color};'
            f'border-color:{color}40;font-size:9px;padding:2px 7px;letter-spacing:0.10em">{badge}</span>'
            f'</div>'
            f'<div style="color:#CBD5E1;font-size:12.5px;line-height:1.55">{rec["text"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Highly correlated pairs (if any) ─────────────────────────────────────
    if report.high_corr_pairs:
        st.markdown("---")
        tbl = '<table class="ptable"><thead><tr>'
        for h in ["#", "Position A", "Position B", "Correlation"]:
            tbl += f"<th>{h}</th>"
        tbl += "</tr></thead><tbody>"
        for i, (a, b, c) in enumerate(report.high_corr_pairs, 1):
            comp_a = positions.loc[positions["ticker"] == a, "company"].iloc[0] if (positions["ticker"] == a).any() else a
            comp_b = positions.loc[positions["ticker"] == b, "company"].iloc[0] if (positions["ticker"] == b).any() else b
            tbl += (
                f'<tr><td style="color:{MUTED};font-size:0.7rem">{i}</td>'
                f'<td style="font-weight:600">{comp_a} <span style="color:{MUTED}">({a})</span></td>'
                f'<td style="font-weight:600">{comp_b} <span style="color:{MUTED}">({b})</span></td>'
                f'<td style="color:{RED};font-weight:700;text-align:right">{c:.3f}</td></tr>'
            )
        tbl += "</tbody></table>"
        st.markdown(
            f'<div class="card" style="padding:0;overflow:hidden">'
            f'<div class="card-hd-inner">'
            f'<div class="eyebrow">Correlation Risk</div>'
            f'<div class="card-title font-display">High-Correlation Pairs ({len(report.high_corr_pairs)})</div>'
            f'</div>'
            f'<div style="overflow-x:auto">{tbl}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
