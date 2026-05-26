"""Decisions tab — ranked buy/sell/trim/rebalance recommendations with What-If simulator."""
from typing import Callable

import pandas as pd
import streamlit as st

from app.analytics import decisions as dec_mod
from app.analytics import health as health_mod
from app.analytics import positions as pos_mod
from app.analytics import simulator as sim_mod
from app.config import BLUE, CARD, GOLD, GREEN, MUTED, RED, TEXT
from app.data import tickers
from app.ui.components import chart_base, label, section_hd


# ── Action badge styling ──────────────────────────────────────────────────────

_ACTION_COLORS = {
    "BUY":       GREEN,
    "SELL":      RED,
    "TRIM":      RED,
    "HOLD":      MUTED,
    "REBALANCE": GOLD,
}

_ACTION_BG = {
    "BUY":       "rgba(34,197,94,0.12)",
    "SELL":      "rgba(239,68,68,0.12)",
    "TRIM":      "rgba(239,68,68,0.12)",
    "HOLD":      "rgba(100,116,139,0.10)",
    "REBALANCE": "rgba(245,158,11,0.12)",
}


def _badge(action: str) -> str:
    color = _ACTION_COLORS.get(action, MUTED)
    bg    = _ACTION_BG.get(action, "rgba(100,116,139,0.10)")
    return (
        f'<span style="background:{bg};border:1px solid {color}40;color:{color};'
        f'font-size:10px;font-weight:700;letter-spacing:0.10em;'
        f'padding:3px 10px;border-radius:4px">{action}</span>'
    )


def _confidence_bar(confidence: float, color: str) -> str:
    pct = confidence * 100
    return (
        f'<div style="margin-top:6px">'
        f'<div style="font-size:9.5px;color:{MUTED};letter-spacing:0.08em;'
        f'text-transform:uppercase;margin-bottom:3px">Confidence</div>'
        f'<div style="display:flex;align-items:center;gap:8px">'
        f'<div style="flex:1;height:4px;background:rgba(148,163,184,0.10);border-radius:2px">'
        f'<div style="width:{pct:.0f}%;height:100%;background:{color};'
        f'box-shadow:0 0 6px {color};border-radius:2px"></div></div>'
        f'<span style="font-size:10.5px;color:{color};font-weight:600">{pct:.0f}%</span>'
        f'</div></div>'
    )


def _render_card(rec: dict, positions: pd.DataFrame, health_report: health_mod.HealthReport, money: Callable, key_prefix: str) -> None:
    action  = rec["action"]
    color   = _ACTION_COLORS.get(action, MUTED)
    company = rec["company"]
    ticker  = rec["ticker"]
    reason  = rec["reason"]
    signals = rec["signals"]
    conf    = rec["confidence"]
    priority= rec["priority"]
    amt_jpy = rec["suggested_amount_jpy"]

    signals_html = "".join(
        f'<div style="font-size:11px;color:{MUTED};padding:2px 0">'
        f'· {s}</div>' for s in signals
    )

    amt_html = (
        f'<div style="margin-top:10px;padding-top:10px;border-top:1px solid var(--border);'
        f'font-size:11px;color:{GOLD}">'
        f'Suggested amount: <span style="font-family:\'JetBrains Mono\',monospace;font-weight:600">'
        f'{money(amt_jpy)}</span></div>'
    ) if amt_jpy > 0 else ""

    st.markdown(
        f'<div class="card" style="border-left:3px solid {color};padding:16px;margin-bottom:10px">'
        f'<div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:10px">'
        f'<div style="display:flex;align-items:center;gap:10px">'
        f'{_badge(action)}'
        f'<span style="font-size:14px;font-weight:600;color:var(--text)">{company}</span>'
        f'<span style="font-size:11px;color:var(--muted)">#{priority} priority</span>'
        f'</div>'
        f'<span class="mono" style="font-size:11px;color:var(--muted)">{ticker}</span>'
        f'</div>'
        f'<div style="font-size:12.5px;color:var(--text-2);line-height:1.55;margin-bottom:8px">{reason}</div>'
        f'<div style="margin-bottom:10px">{signals_html}</div>'
        f'{_confidence_bar(conf, color)}'
        f'{amt_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # What-If expander
    if ticker != "PORTFOLIO" and action in ("BUY", "SELL", "TRIM"):
        with st.expander(f"🔬 Run What-If for {company}"):
            sim_action = st.selectbox(
                "Action", ["BUY", "TRIM"], key=f"{key_prefix}_action"
            )
            max_val = int(float(positions[positions["ticker"] == ticker]["market_value"].iloc[0])) if not positions[positions["ticker"] == ticker].empty else 5_000_000
            sim_amt = st.slider(
                "Amount (¥)",
                min_value=10_000,
                max_value=max(max_val, 10_000),
                value=min(amt_jpy, max_val) if amt_jpy > 0 else 100_000,
                step=10_000,
                key=f"{key_prefix}_amt",
                format="¥%d",
            )
            if st.button("Calculate Impact", key=f"{key_prefix}_calc"):
                result = sim_mod.simulate_trade(
                    positions, ticker, sim_action, float(sim_amt), health_report
                )
                delta = result["health_delta"]
                delta_color = GREEN if delta > 0 else (RED if delta < 0 else MUTED)
                c1, c2, c3 = st.columns(3)
                c1.metric("New Health Score",    f"{result['new_health_score']:.0f}/100",
                          delta=f"{delta:+.1f} pts")
                c2.metric("New Top Concentration",
                          f"{result['new_concentration_pct']:.1%}")
                c3.metric("Health Delta", f"{delta:+.1f}",
                          delta_color="normal")
                st.caption(result["recommendation"])


# ── Public entry point ────────────────────────────────────────────────────────

def render(ps: pd.DataFrame, th: pd.DataFrame, money: Callable) -> None:
    ticker_map = tickers.all_mappings()
    if not ticker_map:
        st.info(
            "🎯 **No tickers mapped yet.** Open the **Tickers** tab to link your "
            "company names to Yahoo Finance symbols. Decisions require live price data."
        )
        return

    with st.spinner("Building positions…"):
        positions = pos_mod.build_positions(ps, th, ticker_map)

    if positions.empty:
        st.warning("No live positions — check the Tickers tab.")
        return

    with st.spinner("Scoring portfolio…"):
        health_report = health_mod.evaluate(positions)

    with st.spinner("Analyzing signals…"):
        recommendations = dec_mod.get_recommendations(positions, health_report)

    # ── Summary KPIs ─────────────────────────────────────────────────────────
    actionable = [r for r in recommendations if r["action"] not in ("HOLD",)]
    buys  = [r for r in actionable if r["action"] == "BUY"]
    trims = [r for r in actionable if r["action"] in ("TRIM", "SELL")]
    rebal = [r for r in actionable if r["action"] == "REBALANCE"]

    st.markdown(section_hd("Decision Summary", "Ranked signals across all positions", "Signals"), unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Signals",   f"{len(actionable)}")
    k2.metric("Buy Signals",     f"{len(buys)}",  delta=f"{len(buys)} actionable"  if buys  else None)
    k3.metric("Trim / Sell",     f"{len(trims)}", delta=f"{len(trims)} actionable" if trims else None)
    k4.metric("Rebalance",       f"{len(rebal)}")

    st.markdown("---")

    # ── Filter controls ───────────────────────────────────────────────────────
    st.markdown(section_hd("Recommendations", "Buy · Trim · Rebalance · Hold", "Actions"), unsafe_allow_html=True)
    col_filter, _ = st.columns([2, 3])
    with col_filter:
        filter_action = st.multiselect(
            "Filter by action",
            options=["BUY", "TRIM", "REBALANCE", "HOLD"],
            default=["BUY", "TRIM", "REBALANCE"],
            key="dec_filter",
        )

    visible = [r for r in recommendations if r["action"] in filter_action]

    if not visible:
        st.info("No recommendations match the current filter.")
        return

    # ── Render cards ──────────────────────────────────────────────────────────
    for i, rec in enumerate(visible):
        _render_card(rec, positions, health_report, money, key_prefix=f"rec_{i}")

    st.markdown("---")

    # ── Full signals table ────────────────────────────────────────────────────
    with st.expander("📋 View all signals as table"):
        rows = []
        for r in recommendations:
            rows.append({
                "Action":     r["action"],
                "Company":    r["company"],
                "Ticker":     r["ticker"],
                "Confidence": f"{r['confidence'] * 100:.0f}%",
                "Priority":   r["priority"],
                "Reason":     r["reason"][:80] + "…" if len(r["reason"]) > 80 else r["reason"],
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
