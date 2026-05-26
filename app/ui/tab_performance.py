"""Performance tab — equity curve vs benchmarks, drawdown, institutional metrics,
multi-period returns heatmap, relative strength comparison."""
from typing import Callable, Dict

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.analytics import metrics as met
from app.analytics import positions as pos
from app.analytics import relative_strength as rs
from app.analytics import returns as ret
from app.config import BLUE, BORDER, CARD, GOLD, GREEN, MUTED, NOGRID, RED, TEXT
from app.data import tickers
from app.ui.components import chart_base, fmt_pct, label, section_hd


BENCHMARK_OPTIONS = {
    "S&P 500 (SPY)":    ("SPY",     "USD"),
    "Nasdaq 100 (QQQ)": ("QQQ",     "USD"),
    "Japan (EWJ)":      ("EWJ",     "USD"),
    "TOPIX (1306.T)":   ("1306.T",  "JPY"),
    "Bitcoin":          ("BTC-USD", "USD"),
    "Gold (GLD)":       ("GLD",     "USD"),
}


def _rebased(series: pd.Series, base: float = 100.0) -> pd.Series:
    if series.empty or series.iloc[0] <= 0:
        return series
    return series / series.iloc[0] * base


def _equity_curve(
    portfolio: pd.Series,
    benchmarks: Dict[str, pd.Series],
) -> go.Figure:
    fig = go.Figure()

    if not portfolio.empty:
        fig.add_trace(go.Scatter(
            x=portfolio.index, y=_rebased(portfolio),
            mode="lines", name="Portfolio",
            line=dict(color=BLUE, width=2.5),
            hovertemplate="<b>Portfolio</b><br>%{x|%Y-%m-%d}: %{y:.1f}<extra></extra>",
        ))

    colors = [GOLD, GREEN, RED, "#9b6bff", "#27c8ff", "#ff8a3d"]
    for i, (name, series) in enumerate(benchmarks.items()):
        if series.empty:
            continue
        fig.add_trace(go.Scatter(
            x=series.index, y=_rebased(series),
            mode="lines", name=name,
            line=dict(color=colors[i % len(colors)], width=1.5, dash="dot"),
            hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}: %{{y:.1f}}<extra></extra>",
        ))

    fig.update_layout(**chart_base(
        height=400, showlegend=True, hovermode="x unified",
        xaxis=dict(color=MUTED, gridcolor=BORDER, showgrid=True),
        yaxis=dict(color=MUTED, gridcolor=BORDER, showgrid=True, title="Indexed to 100"),
    ), legend=dict(bgcolor=CARD, font=dict(color=TEXT, size=10),
                   orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig


def _drawdown_curve(portfolio: pd.Series) -> go.Figure:
    dd = met.drawdown_series(portfolio) * 100
    fig = go.Figure(go.Scatter(
        x=dd.index, y=dd,
        mode="lines", fill="tozeroy",
        line=dict(color=RED, width=1.5),
        fillcolor="rgba(242,54,69,0.25)",
        hovertemplate="%{x|%Y-%m-%d}: %{y:.2f}%<extra></extra>",
    ))
    fig.update_layout(**chart_base(
        height=240,
        xaxis=dict(color=MUTED, gridcolor=BORDER, showgrid=True),
        yaxis=dict(color=MUTED, gridcolor=BORDER, showgrid=True, ticksuffix="%", title="Drawdown"),
    ))
    return fig


def _returns_heatmap(rs_df: pd.DataFrame) -> go.Figure:
    if rs_df.empty:
        return go.Figure()
    periods = list(rs.PERIODS.keys())
    available = [p for p in periods if p in rs_df.columns]
    z = rs_df[available].values * 100  # convert to %
    labels = [f"{c}" for c in rs_df["company"].tolist()]
    fig = go.Figure(go.Heatmap(
        z=z,
        x=available,
        y=labels,
        zmid=0,
        colorscale=[[0.0, RED], [0.5, CARD], [1.0, GREEN]],
        text=[[f"{v:+.1f}%" for v in row] for row in z],
        texttemplate="%{text}",
        textfont=dict(color=TEXT, size=10),
        hovertemplate="<b>%{y}</b> · %{x}<br>%{z:.2f}%<extra></extra>",
        colorbar=dict(tickfont=dict(color=MUTED, size=10),
                      outlinewidth=0, thickness=12, ticksuffix="%"),
    ))
    h = max(360, len(labels) * 28)
    fig.update_layout(**chart_base(
        height=h,
        xaxis=dict(color=MUTED, side="bottom"),
        yaxis=dict(color=MUTED, autorange="reversed"),
    ))
    return fig


def render(ps: pd.DataFrame, th: pd.DataFrame, money: Callable[[float], str]) -> None:
    ticker_map = tickers.all_mappings()
    if not ticker_map:
        st.info("🎯 Map tickers in the **Tickers** tab to compute performance metrics.")
        return

    with st.spinner("Building portfolio time series…"):
        positions = pos.build_positions(ps, th, ticker_map)
        if positions.empty:
            st.warning("No live positions — check the Tickers tab.")
            return

    # ── Controls ─────────────────────────────────────────────────────────────
    ctl1, ctl2 = st.columns([1, 3])
    with ctl1:
        period = st.selectbox(
            "Period",
            options=["3M", "6M", "1Y", "2Y", "5Y", "MAX"],
            index=2,
            key="perf_period",
        )
    with ctl2:
        bench_choice = st.multiselect(
            "Benchmarks (rebased to 100 at period start)",
            options=list(BENCHMARK_OPTIONS.keys()),
            default=["S&P 500 (SPY)", "TOPIX (1306.T)"],
            key="perf_benchmarks",
        )

    with st.spinner("Fetching market data…"):
        portfolio_value = ret.portfolio_value_series(positions, period=period)
        benchmarks = {
            name: ret.benchmark_series(BENCHMARK_OPTIONS[name][0], period=period,
                                       currency=BENCHMARK_OPTIONS[name][1])
            for name in bench_choice
        }

    if portfolio_value.empty:
        st.warning(
            "Could not build a portfolio time series. Likely cause: yfinance "
            "returned no overlapping history for your mapped tickers."
        )
        return

    # ── Headline metrics ────────────────────────────────────────────────────
    primary_bench = next((s for s in benchmarks.values() if not s.empty), pd.Series(dtype=float))
    summary = met.summary(portfolio_value, primary_bench if not primary_bench.empty else None)

    st.markdown(section_hd("Performance Metrics", f"Period: {period} · vs {len(bench_choice)} benchmark(s)", "Analytics"), unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Return",     fmt_pct(summary["total_return"]))
    k2.metric("CAGR",             fmt_pct(summary["cagr"]))
    k3.metric("Volatility (ann.)", fmt_pct(summary["volatility"]))
    k4.metric("Max Drawdown",     fmt_pct(summary["max_drawdown"]))

    k5, k6, k7, k8 = st.columns(4)
    k5.metric("Sharpe Ratio",     f"{summary['sharpe']:.2f}")
    k6.metric("Sortino Ratio",    f"{summary['sortino']:.2f}")
    k7.metric("Beta",             f"{summary['beta']:.2f}")
    k8.metric("Alpha (ann.)",     fmt_pct(summary["alpha"]))

    k9, k10, _, _ = st.columns(4)
    k9.metric("VaR 95% (1-day)",  fmt_pct(summary["var_95"]))
    k10.metric("CVaR 95% (1-day)", fmt_pct(summary["cvar_95"]))

    st.markdown("---")

    # ── Equity curve ────────────────────────────────────────────────────────
    st.markdown(section_hd("Equity Curve", "Portfolio vs Benchmarks · Rebased to 100", "Returns"), unsafe_allow_html=True)
    st.plotly_chart(_equity_curve(portfolio_value, benchmarks), use_container_width=True)

    # ── Drawdown curve ──────────────────────────────────────────────────────
    st.markdown(section_hd("Drawdown", "Peak-to-Trough Decline", "Risk"), unsafe_allow_html=True)
    st.plotly_chart(_drawdown_curve(portfolio_value), use_container_width=True)

    st.markdown("---")

    # ── Multi-period returns heatmap ────────────────────────────────────────
    st.markdown(section_hd("Relative Strength", "Trailing Returns by Position", "Heatmap"), unsafe_allow_html=True)
    with st.spinner("Computing trailing returns…"):
        pos_rs = rs.position_returns(positions)
    if pos_rs.empty:
        st.info("No position-level returns available.")
    else:
        pos_rs_sorted = pos_rs.sort_values("1Y", ascending=False) if "1Y" in pos_rs.columns else pos_rs
        st.plotly_chart(_returns_heatmap(pos_rs_sorted), use_container_width=True)

    st.markdown("---")

    # ── Benchmark comparison table ──────────────────────────────────────────
    label("Benchmark Comparison")
    with st.spinner("Loading benchmarks…"):
        bench_rs = rs.benchmark_returns()

    if bench_rs.empty:
        st.info("Benchmark data unavailable.")
        return

    p_series_full = ret.portfolio_value_series(positions, period="2Y")
    portfolio_row = {p: rs._trailing_return(p_series_full, d) for p, d in rs.PERIODS.items()}

    tbl = '<table class="ptable"><thead><tr>'
    for h in ["Asset", *rs.PERIODS.keys()]:
        tbl += f"<th>{h}</th>"
    tbl += "</tr></thead><tbody>"

    tbl += f'<tr style="background:rgba(59,130,246,0.06)"><td style="font-weight:700;color:{BLUE}">Your Portfolio</td>'
    for p in rs.PERIODS.keys():
        v = portfolio_row.get(p, 0)
        c = GREEN if v > 0 else (RED if v < 0 else MUTED)
        tbl += f'<td style="color:{c};font-weight:700;text-align:right">{v * 100:+.2f}%</td>'
    tbl += "</tr>"

    for ticker, row in bench_rs.iterrows():
        tbl += f'<tr><td style="font-weight:600">{ticker}</td>'
        for p in rs.PERIODS.keys():
            v = row.get(p, 0)
            c = GREEN if v > 0 else (RED if v < 0 else MUTED)
            tbl += f'<td style="color:{c};font-weight:600;text-align:right">{v * 100:+.2f}%</td>'
        tbl += "</tr>"

    tbl += "</tbody></table>"

    st.markdown(
        f'<div class="card" style="padding:0;overflow:hidden">'
        f'<div class="card-hd-inner">'
        f'<div class="eyebrow">Trailing Returns</div>'
        f'<div class="card-title font-display">Portfolio vs Benchmarks</div>'
        f'</div>'
        f'<div style="overflow-x:auto">{tbl}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
