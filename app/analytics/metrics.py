"""Institutional risk/return metrics.

Pure functions. All annualization assumes daily returns with 252 trading
days per year. Risk-free rate `rf` defaults to 0 (raw Sharpe) but can be
supplied as a daily rate.
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np
import pandas as pd


PERIODS_PER_YEAR = 252


def total_return(prices: pd.Series) -> float:
    """Total return over the period: end / start - 1."""
    if prices.empty or prices.iloc[0] <= 0:
        return 0.0
    return float(prices.iloc[-1] / prices.iloc[0] - 1)


def cagr(prices: pd.Series) -> float:
    """Compound annual growth rate. Returns 0 if series too short."""
    if prices.empty or prices.iloc[0] <= 0:
        return 0.0
    days = (prices.index[-1] - prices.index[0]).days
    if days < 30:
        return 0.0
    years = days / 365.25
    return float((prices.iloc[-1] / prices.iloc[0]) ** (1 / years) - 1)


def volatility(returns: pd.Series, annualize: bool = True) -> float:
    """Standard deviation of returns. Annualized by default."""
    if returns.empty:
        return 0.0
    vol = float(returns.std(ddof=1))
    return vol * math.sqrt(PERIODS_PER_YEAR) if annualize else vol


def sharpe(returns: pd.Series, rf: float = 0.0) -> float:
    """Annualized Sharpe ratio. `rf` is a daily risk-free rate."""
    if returns.empty:
        return 0.0
    excess = returns - rf
    sd = float(excess.std(ddof=1))
    if sd <= 0:
        return 0.0
    return float(excess.mean() / sd * math.sqrt(PERIODS_PER_YEAR))


def sortino(returns: pd.Series, rf: float = 0.0) -> float:
    """Annualized Sortino ratio (downside-deviation-based)."""
    if returns.empty:
        return 0.0
    excess = returns - rf
    downside = excess[excess < 0]
    if downside.empty:
        return 0.0
    dd = float(downside.std(ddof=1))
    if dd <= 0:
        return 0.0
    return float(excess.mean() / dd * math.sqrt(PERIODS_PER_YEAR))


def max_drawdown(prices: pd.Series) -> float:
    """Maximum peak-to-trough drawdown as a negative fraction (e.g. -0.27)."""
    if prices.empty:
        return 0.0
    cummax = prices.cummax()
    dd = prices / cummax - 1.0
    return float(dd.min())


def drawdown_series(prices: pd.Series) -> pd.Series:
    """Drawdown at every point in time (fraction, <= 0)."""
    if prices.empty:
        return pd.Series(dtype=float)
    cummax = prices.cummax()
    return prices / cummax - 1.0


def var_95(returns: pd.Series) -> float:
    """Historical 1-day VaR at 95% confidence (negative fraction). Empty → 0."""
    if returns.empty:
        return 0.0
    return float(np.percentile(returns, 5))


def cvar_95(returns: pd.Series) -> float:
    """Conditional VaR (mean of the worst 5% returns). Negative fraction."""
    if returns.empty:
        return 0.0
    cutoff = np.percentile(returns, 5)
    tail = returns[returns <= cutoff]
    if tail.empty:
        return 0.0
    return float(tail.mean())


def beta(returns: pd.Series, market_returns: pd.Series) -> float:
    """Beta vs market returns (CAPM). 0 if no overlap or zero variance."""
    if returns.empty or market_returns.empty:
        return 0.0
    aligned = pd.concat([returns, market_returns], axis=1, join="inner").dropna()
    if len(aligned) < 30:
        return 0.0
    cov = float(aligned.cov().iloc[0, 1])
    var_m = float(aligned.iloc[:, 1].var(ddof=1))
    if var_m <= 0:
        return 0.0
    return cov / var_m


def alpha(returns: pd.Series, market_returns: pd.Series, rf: float = 0.0) -> float:
    """Annualized Jensen's alpha vs market (CAPM)."""
    if returns.empty or market_returns.empty:
        return 0.0
    b = beta(returns, market_returns)
    aligned = pd.concat([returns, market_returns], axis=1, join="inner").dropna()
    if aligned.empty:
        return 0.0
    rp = float(aligned.iloc[:, 0].mean()) - rf
    rm = float(aligned.iloc[:, 1].mean()) - rf
    daily_alpha = rp - b * rm
    return float(daily_alpha * PERIODS_PER_YEAR)


def summary(prices: pd.Series, market_prices: Optional[pd.Series] = None) -> dict:
    """One-shot helper: every metric in a single dict."""
    rets = prices.pct_change().dropna() if not prices.empty else pd.Series(dtype=float)
    result = {
        "total_return": total_return(prices),
        "cagr":         cagr(prices),
        "volatility":   volatility(rets),
        "sharpe":       sharpe(rets),
        "sortino":      sortino(rets),
        "max_drawdown": max_drawdown(prices),
        "var_95":       var_95(rets),
        "cvar_95":      cvar_95(rets),
    }
    if market_prices is not None and not market_prices.empty:
        mkt_rets = market_prices.pct_change().dropna()
        result["beta"]  = beta(rets, mkt_rets)
        result["alpha"] = alpha(rets, mkt_rets)
    else:
        result["beta"]  = 0.0
        result["alpha"] = 0.0
    return result
