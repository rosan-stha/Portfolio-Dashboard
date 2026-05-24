"""Multi-period trailing returns for positions and benchmarks.

Outperform/underperform = position trailing return − benchmark trailing return,
expressed in percentage points. Used by the Performance tab and the Health
Score's momentum subscore.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List

import pandas as pd

from app.analytics.returns import _aligned_price_jpy_series
from app.data import market


PERIODS = {
    "1W": 7,
    "1M": 30,
    "3M": 90,
    "6M": 180,
    "1Y": 365,
}

DEFAULT_BENCHMARKS = {
    "SPY":      "USD",   # S&P 500 ETF
    "QQQ":      "USD",   # Nasdaq 100 ETF
    "EWJ":      "USD",   # iShares MSCI Japan
    "1306.T":   "JPY",   # TOPIX ETF (Tokyo)
    "BTC-USD":  "USD",   # Bitcoin
    "GLD":      "USD",   # Gold ETF
}


def _trailing_return(prices: pd.Series, days: int) -> float:
    """Return over the last `days` calendar days. 0 if insufficient history."""
    if prices.empty:
        return 0.0
    cutoff = prices.index[-1] - pd.Timedelta(days=days)
    earlier = prices.loc[prices.index <= cutoff]
    if earlier.empty:
        return 0.0
    start_price = float(earlier.iloc[-1])
    end_price = float(prices.iloc[-1])
    if start_price <= 0:
        return 0.0
    return end_price / start_price - 1


def position_returns(positions: pd.DataFrame) -> pd.DataFrame:
    """Trailing returns per position for every period in PERIODS.

    Returns DataFrame indexed by ticker, columns = period labels.
    Includes a `company` column for display.
    """
    if positions.empty:
        return pd.DataFrame()

    longest_days = max(PERIODS.values())
    start = (pd.Timestamp.today() - pd.Timedelta(days=longest_days + 30)).date()

    rows: List[dict] = []
    for _, p in positions.iterrows():
        prices = _aligned_price_jpy_series(p["ticker"], p["currency"], start)
        if prices.empty:
            continue
        row = {
            "ticker":  p["ticker"],
            "company": p["company"],
            "sector":  p["sector"],
        }
        for label, days in PERIODS.items():
            row[label] = _trailing_return(prices, days)
        rows.append(row)

    return pd.DataFrame(rows).set_index("ticker") if rows else pd.DataFrame()


def benchmark_returns(
    benchmarks: Dict[str, str] = None,
) -> pd.DataFrame:
    """Trailing returns for each benchmark across PERIODS."""
    benchmarks = benchmarks or DEFAULT_BENCHMARKS
    longest_days = max(PERIODS.values())
    start = (pd.Timestamp.today() - pd.Timedelta(days=longest_days + 30)).date()

    rows: List[dict] = []
    for ticker, ccy in benchmarks.items():
        prices = _aligned_price_jpy_series(ticker, ccy, start)
        if prices.empty:
            continue
        row = {"ticker": ticker}
        for label, days in PERIODS.items():
            row[label] = _trailing_return(prices, days)
        rows.append(row)

    return pd.DataFrame(rows).set_index("ticker") if rows else pd.DataFrame()


def momentum_breadth(positions_returns_df: pd.DataFrame, period: str = "3M") -> float:
    """Fraction of positions with positive trailing return in `period`. 0-1."""
    if positions_returns_df.empty or period not in positions_returns_df.columns:
        return 0.0
    col = positions_returns_df[period].dropna()
    if col.empty:
        return 0.0
    return float((col > 0).mean())
