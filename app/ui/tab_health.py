"""Health Score tab — overall gauge, subscore radar, recommendations panel."""
from typing import Callable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.analytics import health
from app.analytics import positions as pos
from app.config import BLUE, BORDER, CARD, GOLD, GREEN, MUTED, NOGRID, RED, TEXT
from app.data import tickers
from app.ui.components import chart_base, fmt_pct, label


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
        label("Portfolio Health Score")
        st.plotly_chart(_gauge(report.overall), use_container_width=True)
    with r_col:
        label("Subscore Profile")
        st.plotly_chart(_radar(report.subscores), use_container_width=True)

    st.markdown("---")

    # ── Subscore cards ───────────────────────────────────────────────────────
    label("Subscore Breakdown")
    cols = st.columns(4)
    items = list(report.subscores.items())
    for i, (key, val) in enumerate(items):
        with cols[i % 4]:
            color = _score_color(val)
            st.markdown(
                f"""<div style="background:{CARD};border:1px solid {BORDER};border-radius:8px;
                padding:14px 16px;margin-bottom:10px">
                  <div style="color:{MUTED};font-size:0.65rem;text-transform:uppercase;
                              letter-spacing:0.08em;margin-bottom:6px">{SUBSCORE_LABELS[key]}</div>
                  <div style="color:{color};font-size:1.6rem;font-weight:700">{val:.0f}<span style="color:{MUTED};font-size:0.8rem;font-weight:400"> / 100</span></div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── Raw metrics strip ────────────────────────────────────────────────────
    label("Raw Inputs")
    raw = report.raw_metrics
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Volatility (ann.)",        fmt_pct(raw.get("volatility", 0)))
    k2.metric("Sharpe Ratio",              f"{raw.get('sharpe', 0):.2f}")
    k3.metric("Max Drawdown",              fmt_pct(raw.get("max_drawdown", 0)))
    k4.metric("Avg Pairwise Correlation",  f"{raw.get('avg_correlation', 0):.2f}")
    k5.metric("Top Position Weight",       fmt_pct(raw.get("top_weight", 0)))

    st.markdown("---")

    # ── Recommendations ──────────────────────────────────────────────────────
    label("Recommendations")
    for rec in report.recommendations:
        sev = rec["severity"]
        color = SEVERITY_COLORS.get(sev, BLUE)
        badge = sev.upper()
        st.markdown(
            f"""<div style="background:{CARD};border-left:3px solid {color};
            border-radius:6px;padding:12px 16px;margin-bottom:8px">
              <span style="background:{color};color:{CARD};font-size:0.65rem;
                          font-weight:700;padding:2px 8px;border-radius:4px;
                          margin-right:10px;letter-spacing:0.05em">{badge}</span>
              <span style="color:{TEXT};font-size:0.92rem">{rec["text"]}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    # ── Highly correlated pairs (if any) ─────────────────────────────────────
    if report.high_corr_pairs:
        st.markdown("---")
        label(f"High-Correlation Pairs ({len(report.high_corr_pairs)})")
        html = '<table class="ptable"><thead><tr>'
        for h in ["#", "Position A", "Position B", "Correlation"]:
            html += f"<th>{h}</th>"
        html += "</tr></thead><tbody>"
        for i, (a, b, c) in enumerate(report.high_corr_pairs, 1):
            comp_a = positions.loc[positions["ticker"] == a, "company"].iloc[0] if (positions["ticker"] == a).any() else a
            comp_b = positions.loc[positions["ticker"] == b, "company"].iloc[0] if (positions["ticker"] == b).any() else b
            html += (
                f'<tr><td style="color:{MUTED};font-size:0.7rem">{i}</td>'
                f'<td style="font-weight:600">{comp_a} <span style="color:{MUTED}">({a})</span></td>'
                f'<td style="font-weight:600">{comp_b} <span style="color:{MUTED}">({b})</span></td>'
                f'<td style="color:{RED};font-weight:700;text-align:right">{c:.3f}</td></tr>'
            )
        html += "</tbody></table>"
        st.write(html, unsafe_allow_html=True)
