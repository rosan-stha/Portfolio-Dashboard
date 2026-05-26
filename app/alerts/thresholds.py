"""Threshold-based alert detection.

check_all_alerts() scans positions (and optionally a health report) and returns
a list of alert dicts following the shared output contract.
"""
from __future__ import annotations

import datetime
from typing import Optional

import pandas as pd

from app.analytics import correlation as corr_mod
from app.analytics import positions as pos_mod
from app.config import ALERT_THRESHOLDS


def _now_jst() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M JST")


def _position_alerts(positions: pd.DataFrame, weights: pd.Series) -> list[dict]:
    alerts = []
    for ticker, weight in weights.items():
        company = ""
        row = positions[positions["ticker"] == ticker]
        if not row.empty:
            company = str(row.iloc[0]["company"])

        # Concentration alert
        threshold = ALERT_THRESHOLDS["max_position_pct"]
        if weight > threshold:
            severity = "HIGH" if weight > threshold * 1.3 else "MEDIUM"
            alerts.append({
                "severity": severity,
                "type": "CONCENTRATION",
                "ticker": ticker,
                "company": company,
                "message": f"{company} is {weight:.1%} of the portfolio (threshold: {threshold:.0%}).",
                "current_value": float(weight),
                "threshold": threshold,
                "suggested_action": "Review position sizing in the Decisions tab.",
                "timestamp": _now_jst(),
            })

        # Daily move alert
        if not row.empty:
            day_move = abs(float(row.iloc[0].get("day_change_pct", 0)))
            mv_threshold = ALERT_THRESHOLDS["daily_move_pct"]
            if day_move > mv_threshold:
                severity = "HIGH" if day_move > mv_threshold * 1.5 else "MEDIUM"
                direction = "up" if float(row.iloc[0].get("day_change_pct", 0)) > 0 else "down"
                alerts.append({
                    "severity": severity,
                    "type": "VOLATILITY",
                    "ticker": ticker,
                    "company": company,
                    "message": f"{company} moved {direction} {day_move:.1%} today (threshold: {mv_threshold:.0%}).",
                    "current_value": float(day_move),
                    "threshold": mv_threshold,
                    "suggested_action": f"Review {ticker} position and check for news.",
                    "timestamp": _now_jst(),
                })
    return alerts


def _sector_alerts(positions: pd.DataFrame) -> list[dict]:
    alerts = []
    total_mv = float(positions["market_value"].sum())
    if total_mv <= 0:
        return alerts
    by_sector = positions.groupby("sector")["market_value"].sum()
    sector_w = by_sector / total_mv
    threshold = ALERT_THRESHOLDS["max_sector_pct"]
    for sector, w in sector_w.items():
        if w > threshold:
            severity = "HIGH" if w > threshold * 1.2 else "MEDIUM"
            alerts.append({
                "severity": severity,
                "type": "SECTOR",
                "ticker": "PORTFOLIO",
                "company": f"{sector} sector",
                "message": f"{sector} sector is {w:.1%} of the portfolio (threshold: {threshold:.0%}).",
                "current_value": float(w),
                "threshold": threshold,
                "suggested_action": "Diversify into underweight sectors.",
                "timestamp": _now_jst(),
            })
    return alerts


def _currency_alerts(positions: pd.DataFrame) -> list[dict]:
    alerts = []
    total_mv = float(positions["market_value"].sum())
    if total_mv <= 0:
        return alerts
    by_ccy = positions.groupby("currency")["market_value"].sum()
    ccy_w = by_ccy / total_mv
    threshold = ALERT_THRESHOLDS["max_currency_pct"]
    for ccy, w in ccy_w.items():
        if w > threshold:
            alerts.append({
                "severity": "MEDIUM",
                "type": "CONCENTRATION",
                "ticker": "PORTFOLIO",
                "company": f"{ccy} currency exposure",
                "message": f"{ccy} represents {w:.1%} of the portfolio (threshold: {threshold:.0%}).",
                "current_value": float(w),
                "threshold": threshold,
                "suggested_action": "Consider adding non-JPY or diversified positions.",
                "timestamp": _now_jst(),
            })
    return alerts


def _correlation_alerts(positions: pd.DataFrame) -> list[dict]:
    alerts = []
    threshold = ALERT_THRESHOLDS["max_correlation"]
    corr = corr_mod.correlation_matrix(positions, period="1Y")
    high_pairs = corr_mod.high_correlation_pairs(corr, threshold=threshold)
    for a, b, c in high_pairs[:5]:
        ticker_to_company = dict(zip(positions["ticker"], positions["company"]))
        ca = ticker_to_company.get(a, a)
        cb = ticker_to_company.get(b, b)
        alerts.append({
            "severity": "LOW",
            "type": "CORRELATION",
            "ticker": f"{a}/{b}",
            "company": f"{ca} / {cb}",
            "message": f"{ca} and {cb} have {c:.2f} correlation (threshold: {threshold:.2f}).",
            "current_value": float(c),
            "threshold": threshold,
            "suggested_action": "Consider reducing overlap to improve true diversification.",
            "timestamp": _now_jst(),
        })
    return alerts


def _health_alerts(health_report) -> list[dict]:
    """Requires a HealthReport object from health.evaluate(). Pass None to skip."""
    if health_report is None:
        return []
    alerts = []
    score = float(health_report.overall)
    threshold = ALERT_THRESHOLDS["min_health_score"]
    if score < threshold:
        severity = "HIGH" if score < threshold - 15 else "MEDIUM"
        alerts.append({
            "severity": severity,
            "type": "HEALTH",
            "ticker": "PORTFOLIO",
            "company": "Portfolio Health",
            "message": f"Health score is {score:.0f}/100, below the {threshold} threshold.",
            "current_value": score,
            "threshold": float(threshold),
            "suggested_action": "Review the Health Score tab for specific recommendations.",
            "timestamp": _now_jst(),
        })
    return alerts


def check_all_alerts(positions: pd.DataFrame, health_report=None) -> list[dict]:
    """
    Scan positions and return list of alert dicts sorted by severity.
    health_report: optional HealthReport from health.evaluate() — enables health alerts.
    """
    if positions.empty:
        return []

    weights = pos_mod.position_weights(positions)
    alerts = []
    alerts.extend(_position_alerts(positions, weights))
    alerts.extend(_sector_alerts(positions))
    alerts.extend(_currency_alerts(positions))
    alerts.extend(_correlation_alerts(positions))
    alerts.extend(_health_alerts(health_report))

    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    alerts.sort(key=lambda a: severity_order.get(a["severity"], 9))
    return alerts
