"""What-If trade simulator.

simulate_trade() takes a hypothetical buy/sell/trim and re-computes the
structure-based health subscores (diversification, concentration, sector_balance).
Speed-sensitive subscores (volatility, sharpe, drawdown, momentum, correlation)
are carried forward unchanged since they depend on historical price series.
"""
from __future__ import annotations

import pandas as pd

from app.analytics import health as health_mod
from app.analytics import positions as pos_mod
from app.analytics.health import (
    SCORE_WEIGHTS,
    _concentration,
    _diversification,
    _sector_balance,
)


def simulate_trade(
    positions: pd.DataFrame,
    ticker: str,
    action: str,
    amount_jpy: float,
    current_health: health_mod.HealthReport,
) -> dict:
    """
    Project the health score impact of buying or selling `amount_jpy` of `ticker`.

    Returns:
        {
            "new_health_score":      float,
            "new_concentration_pct": float,   # top-position weight after trade
            "new_sector_balance":    dict,    # {sector: weight}
            "health_delta":          float,   # positive = improvement
            "recommendation":        str,
        }
    """
    if positions.empty or amount_jpy <= 0:
        return {
            "new_health_score":      current_health.overall,
            "new_concentration_pct": 0.0,
            "new_sector_balance":    {},
            "health_delta":          0.0,
            "recommendation":        "Enter an amount to run the simulation.",
        }

    sim = positions.copy()
    total_mv = float(sim["market_value"].sum())
    mask = sim["ticker"] == ticker

    if not mask.any():
        return {
            "new_health_score":      current_health.overall,
            "new_concentration_pct": 0.0,
            "new_sector_balance":    {},
            "health_delta":          0.0,
            "recommendation":        f"Ticker {ticker} not found in current positions.",
        }

    idx = sim[mask].index[0]
    current_mv = float(sim.loc[idx, "market_value"])
    current_cb = float(sim.loc[idx, "cost_basis"])

    action_upper = action.upper()
    if action_upper == "BUY":
        sim.loc[idx, "market_value"] = current_mv + amount_jpy
        sim.loc[idx, "cost_basis"]   = current_cb + amount_jpy
        new_total = total_mv + amount_jpy
    elif action_upper in ("SELL", "TRIM"):
        trim = min(amount_jpy, current_mv)
        ratio = (current_mv - trim) / current_mv if current_mv > 0 else 0
        sim.loc[idx, "market_value"] = current_mv - trim
        sim.loc[idx, "cost_basis"]   = current_cb * ratio
        new_total = total_mv - trim
        # Remove position if fully sold
        if sim.loc[idx, "market_value"] <= 0:
            sim = sim.drop(index=idx).reset_index(drop=True)
    else:
        new_total = total_mv

    if new_total <= 0:
        return {
            "new_health_score":      0.0,
            "new_concentration_pct": 0.0,
            "new_sector_balance":    {},
            "health_delta":          -current_health.overall,
            "recommendation":        "Portfolio would be empty after this trade.",
        }

    # Recompute structure-based subscores
    new_weights = pos_mod.position_weights(sim)
    new_conc_pct = float(new_weights.iloc[0]) if not new_weights.empty else 0.0

    sector_mv = sim.groupby("sector")["market_value"].sum()
    new_sector_balance = (
        (sector_mv / float(sector_mv.sum())).to_dict()
        if sector_mv.sum() > 0 else {}
    )

    new_subscores = dict(current_health.subscores)
    new_subscores["diversification"] = _diversification(new_weights)
    new_subscores["concentration"]   = _concentration(new_weights)
    new_subscores["sector_balance"]  = _sector_balance(sim)

    new_overall = sum(new_subscores[k] * w for k, w in SCORE_WEIGHTS.items())
    delta = new_overall - current_health.overall

    if delta > 5:
        rec = f"This trade improves the health score by {delta:+.1f} pts. Recommended."
    elif delta > 0:
        rec = f"Slight improvement ({delta:+.1f} pts). Neutral signal."
    elif delta > -5:
        rec = f"Minor health impact ({delta:+.1f} pts). Monitor closely."
    else:
        rec = f"This trade reduces the health score by {abs(delta):.1f} pts. Review carefully."

    return {
        "new_health_score":      round(new_overall, 1),
        "new_concentration_pct": new_conc_pct,
        "new_sector_balance":    new_sector_balance,
        "health_delta":          round(delta, 1),
        "recommendation":        rec,
    }
