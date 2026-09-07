"""Holdings tab — live positions grouped by asset category.

Shows only nonzero-share positions (build_positions already filters those out).
Groups by category in fixed display order; within each group sorts by % of portfolio.
Reuses build_positions() from app/analytics/positions.py — does not duplicate P&L math.
"""
from __future__ import annotations

from typing import Callable

import pandas as pd
import streamlit as st

from app.analytics import positions as pos
from app.config import BLUE, GREEN, MUTED, RED
from app.data import tickers
from app.ui.components import fmt_pct, kpi_card, section_hd, ticker_link

CATEGORY_ORDER = ["American Stock", "Japanese Stock", "ETF", "Mutual Fund", "Other"]


def _color(v: float) -> str:
    if v > 0: return GREEN
    if v < 0: return RED
    return MUTED


def _sign(v: float, money: Callable[[float], str]) -> str:
    s = money(abs(v))
    return f"+{s}" if v >= 0 else f"−{s}"


def render(ps: pd.DataFrame, th: pd.DataFrame, money: Callable[[float], str]) -> None:
    st.markdown(
        section_hd("Holdings", "Live positions grouped by asset category", "Portfolio"),
        unsafe_allow_html=True,
    )

    ticker_map = tickers.all_mappings()
    meta_map   = tickers.all_meta()

    if not ticker_map:
        st.info(
            "🎯 **No tickers mapped.** Open the **Tickers** tab to link companies "
            "to Yahoo Finance symbols. Once mapped, this tab shows live % of portfolio, "
            "gain/loss, and TradingView links."
        )
        return

    with st.spinner("Fetching live market data…"):
        positions = pos.build_positions(ps, th, ticker_map)

    if positions.empty:
        st.warning(
            "No live positions found. Check the Tickers tab — tickers may be invalid "
            "or no Buy transactions exist for mapped companies."
        )
        return

    # Enrich with category and exchange from tickers.json meta
    positions = positions.copy()
    positions["category"] = positions["company"].map(
        lambda c: meta_map.get(c, {}).get("category", "Other")
    )
    positions["exchange"] = positions["company"].map(
        lambda c: meta_map.get(c, {}).get("exchange", "")
    )

    total_mv = float(positions["market_value"].sum())
    positions["pct_portfolio"] = (
        positions["market_value"] / total_mv if total_mv > 0 else 0.0
    )

    # ── Category summary strip ────────────────────────────────────────────────
    active_cats = [
        cat for cat in CATEGORY_ORDER
        if not positions[positions["category"] == cat].empty
    ]
    # Bucket anything not in the fixed list into "Other"
    positions.loc[~positions["category"].isin(CATEGORY_ORDER), "category"] = "Other"
    if "Other" not in active_cats and not positions[positions["category"] == "Other"].empty:
        active_cats.append("Other")

    cat_stats: dict[str, dict] = {}
    for cat in active_cats:
        sub = positions[positions["category"] == cat]
        mv  = float(sub["market_value"].sum())
        cb  = float(sub["cost_basis"].sum())
        cat_stats[cat] = {
            "mv":       mv,
            "pct":      mv / total_mv if total_mv > 0 else 0.0,
            "gain_pct": (mv - cb) / cb if cb > 0 else 0.0,
        }

    if active_cats:
        cols = st.columns(len(active_cats))
        for col, cat in zip(cols, active_cats):
            info      = cat_stats[cat]
            gain_pct  = info["gain_pct"]
            delta_cls = "pos" if gain_pct >= 0 else "neg"
            sign      = "+" if gain_pct >= 0 else ""
            with col:
                st.markdown(
                    kpi_card(
                        eyebrow_text=cat,
                        value=f"{info['pct'] * 100:.1f}%",
                        delta_str=f"{sign}{gain_pct * 100:.1f}% total gain",
                        delta_class=delta_cls,
                    ),
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    # ── Per-category holding tables ───────────────────────────────────────────
    for cat in active_cats:
        sub = (
            positions[positions["category"] == cat]
            .sort_values("pct_portfolio", ascending=False)
            .reset_index(drop=True)
        )

        st.markdown(
            f'<div class="eyebrow" style="margin:16px 0 8px">'
            f'{cat} &nbsp;·&nbsp; {len(sub)} position{"s" if len(sub) != 1 else ""}'
            f'</div>',
            unsafe_allow_html=True,
        )

        tbl = '<table class="ptable"><thead><tr>'
        for h in ["#", "Company", "Ticker", "% of Portfolio", "Gain (¥)", "Gain (%)"]:
            tbl += f"<th>{h}</th>"
        tbl += "</tr></thead><tbody>"

        for i, (_, r) in enumerate(sub.iterrows(), 1):
            gain_jpy = r["unrealized_pl"]
            gain_pct = r["unrealized_pct"]
            gc       = _color(gain_jpy)

            tbl += (
                f"<tr>"
                f'<td style="color:{MUTED};font-size:0.7rem">{i}</td>'
                f'<td>{ticker_link(r["company"], r["ticker"], r["exchange"])}</td>'
                f'<td style="color:{BLUE};font-weight:600">{r["ticker"]}</td>'
                f'<td style="text-align:right;font-weight:600">{r["pct_portfolio"] * 100:.1f}%</td>'
                f'<td style="color:{gc};font-weight:700;text-align:right">{_sign(gain_jpy, money)}</td>'
                f'<td style="color:{gc};font-weight:700;text-align:right">{fmt_pct(gain_pct)}</td>'
                f"</tr>"
            )

        tbl += "</tbody></table>"
        st.markdown(
            f'<div class="card" style="padding:0;overflow:hidden;margin-bottom:14px">'
            f'<div style="overflow-x:auto">{tbl}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
