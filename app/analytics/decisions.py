"""Buy / Sell / Trim / Rebalance recommendations.

Scans each position against technical signals and risk thresholds, then returns
a ranked list of decision dicts following the shared output contract.

All historical data comes through market.get_history() (cached) so repeated
calls in the same session add no network round-trips.
"""
from __future__ import annotations

from typing import List

import pandas as pd

from app.analytics import health as health_mod
from app.analytics import positions as pos_mod
from app.config import ALERT_THRESHOLDS
from app.data import market


# ── Technical helpers ─────────────────────────────────────────────────────────

def _rsi(prices: pd.Series, period: int = 14) -> float:
    """Wilder's RSI on closing prices. Returns 50 on insufficient data."""
    if prices.empty or len(prices) < period + 1:
        return 50.0
    delta = prices.diff().dropna()
    gains  = delta.clip(lower=0)
    losses = (-delta).clip(lower=0)
    avg_gain = gains.ewm(alpha=1 / period, min_periods=period).mean()
    avg_loss = losses.ewm(alpha=1 / period, min_periods=period).mean()
    last_loss = float(avg_loss.iloc[-1])
    if last_loss == 0:
        return 100.0
    rs = float(avg_gain.iloc[-1]) / last_loss
    return round(100 - (100 / (1 + rs)), 2)


def _trailing_return(prices: pd.Series, days: int) -> float:
    """Return over the last N calendar days. 0 if history is too short."""
    if prices.empty:
        return 0.0
    cutoff = prices.index[-1] - pd.Timedelta(days=days)
    earlier = prices[prices.index <= cutoff]
    if earlier.empty:
        return 0.0
    start = float(earlier.iloc[-1])
    end   = float(prices.iloc[-1])
    return (end / start - 1) if start > 0 else 0.0


def _vs_52w_low(prices: pd.Series) -> float:
    """How far current price is above the 52-week low (fraction). 0 if no data."""
    if prices.empty:
        return 1.0
    year_ago = prices.index[-1] - pd.Timedelta(days=365)
    year_prices = prices[prices.index >= year_ago]
    if year_prices.empty:
        return 1.0
    low = float(year_prices.min())
    current = float(prices.iloc[-1])
    return (current - low) / low if low > 0 else 1.0


# ── Signal evaluation ─────────────────────────────────────────────────────────

def _evaluate_position(
    row: pd.Series,
    weight: float,
    total_mv: float,
    prices: pd.Series,
    health_report: health_mod.HealthReport,
) -> dict:
    ticker  = str(row["ticker"])
    company = str(row["company"])
    mv      = float(row["market_value"])

    rsi_val   = _rsi(prices)
    ret_30d   = _trailing_return(prices, 30)
    above_low = _vs_52w_low(prices)

    conc_score = health_report.subscores.get("concentration", 100)
    mom_score  = health_report.subscores.get("momentum", 50)

    signals: list[str] = []
    action     = "HOLD"
    reason     = f"{company} shows no actionable signals at current levels."
    confidence = 0.35
    priority   = 5

    # ── Sell / Trim hierarchy ────────────────────────────────────────────────
    max_pct = ALERT_THRESHOLDS["max_position_pct"]
    if weight > max_pct:
        signals.append(f"Position is {weight:.1%} of portfolio (limit: {max_pct:.0%})")
        action     = "TRIM"
        confidence = min(0.88, 0.60 + (weight - max_pct) * 2)
        priority   = 1
        target_mv  = total_mv * (max_pct * 0.75)
        trim_amt   = max(0, int(mv - target_mv))
        reason     = (
            f"{company} is {weight:.1%} of the portfolio, above the {max_pct:.0%} limit. "
            f"Trim ~¥{trim_amt:,} to restore balance."
        )

    if rsi_val > 75:
        signals.append(f"RSI-14 = {rsi_val:.1f} (overbought)")
        if action == "HOLD":
            action     = "TRIM"
            confidence = min(0.75, 0.45 + (rsi_val - 75) / 50)
            priority   = 2
            reason     = (
                f"{company} RSI-14 is {rsi_val:.1f} — overbought territory. "
                f"Consider taking partial profits."
            )

    if ret_30d > 0.40:
        signals.append(f"30-day return = {ret_30d:.1%} (take-profit zone)")
        if action == "HOLD":
            action     = "TRIM"
            confidence = min(0.70, 0.50 + ret_30d - 0.40)
            priority   = 2
            reason     = (
                f"{company} is up {ret_30d:.1%} in 30 days. "
                f"Consider trimming to lock in gains."
            )

    if conc_score < 40 and weight > 0.15 and action == "HOLD":
        signals.append(
            f"Portfolio concentration score {conc_score:.0f}/100 — "
            f"position is {weight:.1%}"
        )
        action     = "TRIM"
        confidence = 0.55
        priority   = 3
        reason     = (
            f"Portfolio concentration score is {conc_score:.0f}/100 and "
            f"{company} is {weight:.1%} of holdings."
        )

    # ── Buy hierarchy ────────────────────────────────────────────────────────
    if rsi_val < 30 and action == "HOLD":
        signals.append(f"RSI-14 = {rsi_val:.1f} (oversold)")
        action     = "BUY"
        confidence = min(0.75, 0.50 + (30 - rsi_val) / 60)
        priority   = 2
        reason     = (
            f"{company} RSI-14 is {rsi_val:.1f} — oversold. "
            f"Potential entry or accumulation point."
        )

    if above_low <= 0.05 and action == "HOLD" and not prices.empty:
        signals.append(f"Price is within {above_low:.1%} of 52-week low")
        action     = "BUY"
        confidence = 0.55
        priority   = 3
        reason     = (
            f"{company} is trading near its 52-week low "
            f"({above_low:.1%} above). Potential accumulation zone."
        )

    if ret_30d > 0 and mom_score < 50 and action == "HOLD":
        signals.append(
            f"Positive 30d return ({ret_30d:.1%}) while portfolio momentum "
            f"score is {mom_score:.0f}/100"
        )
        action     = "BUY"
        confidence = 0.50
        priority   = 4
        reason     = (
            f"{company} shows positive momentum while overall portfolio "
            f"momentum is weak — a relative outperformer."
        )

    # Suggested trade size
    if action == "TRIM":
        target = total_mv * (max_pct * 0.75)
        suggested = max(0, int(mv - target))
    elif action == "BUY":
        suggested = int(total_mv * 0.05)
    else:
        suggested = 0

    return {
        "action":               action,
        "ticker":               ticker,
        "company":              company,
        "reason":               reason,
        "signals":              signals if signals else ["No strong signals detected."],
        "confidence":           round(confidence, 3),
        "priority":             priority,
        "simulated_impact":     {},
        "suggested_amount_jpy": suggested,
    }


# ── Rebalance signals ─────────────────────────────────────────────────────────

def _sector_rebalance_signals(positions: pd.DataFrame) -> list[dict]:
    total_mv = float(positions["market_value"].sum())
    if total_mv <= 0:
        return []
    sector_w = positions.groupby("sector")["market_value"].sum() / total_mv
    results = []
    threshold = ALERT_THRESHOLDS["max_sector_pct"]
    for sector, w in sector_w.items():
        if w > threshold:
            results.append({
                "action":    "REBALANCE",
                "ticker":    "PORTFOLIO",
                "company":   f"{sector} sector",
                "reason":    (
                    f"{sector} is {w:.1%} of the portfolio "
                    f"(limit: {threshold:.0%}). "
                    f"Rebalance toward underweight sectors."
                ),
                "signals":              [f"{sector} sector weight {w:.1%} exceeds {threshold:.0%} limit"],
                "confidence":           0.70,
                "priority":             2,
                "simulated_impact":     {},
                "suggested_amount_jpy": 0,
            })
    return results


# ── Public API ────────────────────────────────────────────────────────────────

def get_recommendations(
    positions: pd.DataFrame,
    health_report: health_mod.HealthReport,
) -> List[dict]:
    """
    Analyze positions against signals and risk thresholds.
    Returns a list of decision dicts sorted by priority (1 = highest).
    """
    if positions.empty:
        return []

    weights  = pos_mod.position_weights(positions)
    total_mv = float(positions["market_value"].sum())

    results: list[dict] = []
    for _, row in positions.iterrows():
        ticker = str(row["ticker"])
        weight = float(weights.get(ticker, 0))

        history = market.get_history(ticker)
        prices  = (
            history["Close"].dropna()
            if not history.empty and "Close" in history.columns
            else pd.Series(dtype=float)
        )

        dec = _evaluate_position(row, weight, total_mv, prices, health_report)
        results.append(dec)

    results.extend(_sector_rebalance_signals(positions))

    # Sort: priority asc, confidence desc; push HOLDs to the back
    results.sort(key=lambda d: (0 if d["action"] != "HOLD" else 1, d["priority"], -d["confidence"]))
    return results
