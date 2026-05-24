"""Portfolio Health Score — weighted composite of 8 subscores (0-100).

The score is meant to be glanceable, not optimization-grade. Recommendations
are rule-based strings, deliberately conservative: surface what's clearly
broken, don't fabricate signals from noise.

Subscores:
    diversification     — 1 - HHI on position weights
    sector_balance      — 1 - HHI on sector weights
    concentration       — penalizes max single position weight
    volatility          — lower annualized vol = higher score
    sharpe              — risk-adjusted return
    drawdown            — smaller max drawdown = higher score
    momentum            — % of positions with positive 3M return
    correlation         — lower avg pairwise correlation = higher score
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import pandas as pd

from app.analytics import correlation as corr_mod
from app.analytics import metrics as met
from app.analytics import relative_strength as rs
from app.analytics import returns as ret
from app.analytics.positions import position_weights


# ── Subscore weights (must sum to 1.0) ───────────────────────────────────────
SCORE_WEIGHTS = {
    "diversification": 0.15,
    "sector_balance":  0.15,
    "concentration":   0.15,
    "volatility":      0.12,
    "sharpe":          0.12,
    "drawdown":        0.13,
    "momentum":        0.08,
    "correlation":     0.10,
}


# ── Per-subscore mapping functions (each returns 0-100) ──────────────────────

def _diversification(weights: pd.Series) -> float:
    """1 - Herfindahl-Hirschman Index, mapped to 0-100.
    Single position → 0. Equal across 20+ → ~95."""
    if weights.empty:
        return 0.0
    hhi = float((weights ** 2).sum())
    return max(0.0, min(100.0, (1 - hhi) * 100))


def _concentration(weights: pd.Series) -> float:
    """100 if no position > 20%. Linearly down to 0 at max ≥ 50%."""
    if weights.empty:
        return 0.0
    max_w = float(weights.max())
    if max_w <= 0.20:
        return 100.0
    if max_w >= 0.50:
        return 0.0
    return float((0.50 - max_w) / 0.30 * 100)


def _sector_balance(positions: pd.DataFrame) -> float:
    """1 - HHI on sector weights, mapped to 0-100."""
    if positions.empty:
        return 0.0
    by_sector = positions.groupby("sector")["market_value"].sum()
    total = float(by_sector.sum())
    if total <= 0:
        return 0.0
    sector_w = by_sector / total
    hhi = float((sector_w ** 2).sum())
    return max(0.0, min(100.0, (1 - hhi) * 100))


def _volatility(vol: float) -> float:
    """100 at vol ≤ 10%, 0 at vol ≥ 35% (annualized)."""
    if vol <= 0.10:
        return 100.0
    if vol >= 0.35:
        return 0.0
    return float((0.35 - vol) / 0.25 * 100)


def _sharpe(s: float) -> float:
    """100 at Sharpe ≥ 2.0, 50 at 1.0, 0 at ≤ 0."""
    return max(0.0, min(100.0, s * 50))


def _drawdown(max_dd: float) -> float:
    """max_dd is negative. 100 if dd ≥ -10%, 0 if dd ≤ -50%."""
    if max_dd >= -0.10:
        return 100.0
    if max_dd <= -0.50:
        return 0.0
    return float((max_dd + 0.50) / 0.40 * 100)


def _momentum(breadth: float) -> float:
    """breadth is fraction in [0,1] — just scale to 0-100."""
    return max(0.0, min(100.0, breadth * 100))


def _correlation(avg_corr: float) -> float:
    """100 at avg_corr = -1, 50 at 0, 0 at 1."""
    return max(0.0, min(100.0, (1 - avg_corr) * 50))


# ── Recommendation rules ────────────────────────────────────────────────────

def _recommendations(
    positions: pd.DataFrame,
    weights: pd.Series,
    sector_weights: pd.Series,
    vol: float,
    sharpe: float,
    max_dd: float,
    breadth: float,
    avg_corr: float,
    high_pairs: list,
) -> List[Dict[str, str]]:
    """Generate rule-based recommendations. Each item: {severity, text}."""
    recs: List[Dict[str, str]] = []

    if not weights.empty:
        top_ticker = weights.index[0]
        top_w = float(weights.iloc[0])
        if top_w > 0.30:
            top_company = positions.loc[positions["ticker"] == top_ticker, "company"].iloc[0]
            recs.append({
                "severity": "high",
                "text":     f"**{top_company}** is **{top_w:.0%}** of the portfolio. "
                            f"Consider trimming to reduce single-name risk.",
            })
        elif top_w > 0.20:
            top_company = positions.loc[positions["ticker"] == top_ticker, "company"].iloc[0]
            recs.append({
                "severity": "medium",
                "text":     f"**{top_company}** is **{top_w:.0%}** of the portfolio — "
                            f"monitor for concentration risk.",
            })

    if not sector_weights.empty:
        top_sec = sector_weights.index[0]
        top_sec_w = float(sector_weights.iloc[0])
        if top_sec_w > 0.50:
            recs.append({
                "severity": "high",
                "text":     f"Sector exposure to **{top_sec}** is **{top_sec_w:.0%}**. "
                            f"Diversify across sectors.",
            })
        elif top_sec_w > 0.35:
            recs.append({
                "severity": "medium",
                "text":     f"Sector exposure to **{top_sec}** is **{top_sec_w:.0%}** — heavy concentration.",
            })

    if vol > 0.30:
        recs.append({
            "severity": "medium",
            "text":     f"Annualized volatility is **{vol:.1%}** — elevated. "
                        f"Adding lower-vol assets would smooth returns.",
        })

    if sharpe < 0.5 and sharpe != 0:
        recs.append({
            "severity": "medium",
            "text":     f"Sharpe ratio is **{sharpe:.2f}** — risk-adjusted returns are weak. "
                        f"Review underperformers.",
        })

    if max_dd <= -0.25:
        recs.append({
            "severity": "medium",
            "text":     f"Max drawdown over the lookback period was **{max_dd:.1%}**. "
                        f"Consider hedging or reducing cyclicals.",
        })

    if breadth > 0 and breadth < 0.40:
        recs.append({
            "severity": "low",
            "text":     f"Only **{breadth:.0%}** of positions show positive 3-month momentum. "
                        f"Market may be in a risk-off regime.",
        })

    if avg_corr > 0.70:
        recs.append({
            "severity": "high",
            "text":     f"Average pairwise correlation is **{avg_corr:.2f}** — holdings move together. "
                        f"True diversification is limited.",
        })
    elif avg_corr > 0.55:
        recs.append({
            "severity": "medium",
            "text":     f"Average pairwise correlation is **{avg_corr:.2f}** — moderately correlated holdings.",
        })

    if len(high_pairs) >= 3:
        sample = ", ".join(f"{a}↔{b}" for a, b, _ in high_pairs[:3])
        recs.append({
            "severity": "medium",
            "text":     f"**{len(high_pairs)}** highly-correlated pairs detected (e.g. {sample}). "
                        f"Pruning duplicates would improve diversification.",
        })

    if not recs:
        recs.append({
            "severity": "info",
            "text":     "No notable risk concentrations detected — portfolio appears balanced.",
        })

    return recs


# ── Public entrypoint ───────────────────────────────────────────────────────

@dataclass
class HealthReport:
    overall:        float
    subscores:      Dict[str, float]
    raw_metrics:    Dict[str, float]
    recommendations: List[Dict[str, str]]
    high_corr_pairs: list = field(default_factory=list)


def evaluate(positions: pd.DataFrame, period: str = "1Y") -> HealthReport:
    """Compute the full Health Score, subscores, and recommendations."""
    if positions.empty:
        return HealthReport(
            overall=0.0,
            subscores={k: 0.0 for k in SCORE_WEIGHTS},
            raw_metrics={},
            recommendations=[{
                "severity": "info",
                "text": "No positions yet. Map tickers to start scoring your portfolio.",
            }],
            high_corr_pairs=[],
        )

    weights = position_weights(positions)
    sector_w = positions.groupby("sector")["market_value"].sum().sort_values(ascending=False)
    sector_w = sector_w / sector_w.sum() if sector_w.sum() > 0 else sector_w

    # Returns-based metrics
    value_series = ret.portfolio_value_series(positions, period=period)
    rets = ret.daily_returns(value_series)
    vol  = met.volatility(rets)
    shp  = met.sharpe(rets)
    mdd  = met.max_drawdown(value_series)

    # Momentum (breadth of positive 3M returns)
    pos_rets = rs.position_returns(positions)
    breadth = rs.momentum_breadth(pos_rets, period="3M") if not pos_rets.empty else 0.0

    # Correlation
    corr = corr_mod.correlation_matrix(positions, period=period)
    avg_corr = corr_mod.average_pairwise_correlation(corr)
    high_pairs = corr_mod.high_correlation_pairs(corr)

    subscores = {
        "diversification": _diversification(weights),
        "sector_balance":  _sector_balance(positions),
        "concentration":   _concentration(weights),
        "volatility":      _volatility(vol),
        "sharpe":          _sharpe(shp),
        "drawdown":        _drawdown(mdd),
        "momentum":        _momentum(breadth),
        "correlation":     _correlation(avg_corr),
    }

    overall = sum(subscores[k] * w for k, w in SCORE_WEIGHTS.items())

    recs = _recommendations(
        positions, weights, sector_w,
        vol, shp, mdd, breadth, avg_corr, high_pairs,
    )

    return HealthReport(
        overall=round(overall, 1),
        subscores={k: round(v, 1) for k, v in subscores.items()},
        raw_metrics={
            "volatility":  vol,
            "sharpe":      shp,
            "max_drawdown": mdd,
            "momentum_breadth": breadth,
            "avg_correlation":  avg_corr,
            "top_weight": float(weights.iloc[0]) if not weights.empty else 0.0,
            "top_sector_weight": float(sector_w.iloc[0]) if not sector_w.empty else 0.0,
        },
        recommendations=recs,
        high_corr_pairs=high_pairs,
    )


def score_grade(score: float) -> tuple[str, str]:
    """Map a 0-100 score to (letter_grade, descriptor)."""
    if score >= 85: return ("A", "Excellent")
    if score >= 75: return ("B", "Strong")
    if score >= 65: return ("C", "Adequate")
    if score >= 50: return ("D", "Needs attention")
    return ("F", "High risk")
