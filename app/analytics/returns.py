"""Portfolio time series reconstruction.

Models the portfolio as if today's share counts were held throughout history.
This is the standard "buy-and-hold from today's weights" attribution view
used by most retail platforms — it lets us compute Sharpe / drawdown /
correlation against benchmarks without needing per-trade lot tracking.

Limitation: it does NOT account for actual trade timing. A position bought
last week will appear in the equity curve five years back. Real lot-aware
performance attribution is a Phase 4 item.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable

import pandas as pd

from app.data import fx, market


PERIOD_DAYS = {
    "1M":  30,
    "3M":  90,
    "6M":  180,
    "1Y":  365,
    "2Y":  730,
    "5Y":  365 * 5,
    "MAX": 365 * 10,
}


def _aligned_price_jpy_series(ticker: str, currency: str, start: date) -> pd.Series:
    """Daily close series for `ticker`, converted to JPY. Empty Series on failure."""
    hist = market.get_history(ticker, start)
    if hist.empty or "Close" not in hist.columns:
        return pd.Series(dtype=float)

    series = hist["Close"].copy()

    if currency and currency.upper() != "JPY":
        fx_series = fx.jpy_factor_series(currency, start)
        if fx_series.empty:
            return pd.Series(dtype=float)
        # Align FX to price dates using forward-fill (weekends/holidays)
        fx_aligned = fx_series.reindex(series.index, method="ffill")
        fx_aligned = fx_aligned.bfill()  # in case the first dates are missing
        series = series * fx_aligned

    return series.dropna()


def portfolio_value_series(
    positions: pd.DataFrame,
    period: str = "1Y",
) -> pd.Series:
    """Reconstruct portfolio JPY value over time.

    For each position: shares × historical_price × historical_FX, summed
    across positions on aligned dates.

    Returns: pd.Series indexed by date, values in JPY. Empty if no positions.
    """
    if positions.empty:
        return pd.Series(dtype=float)

    days = PERIOD_DAYS.get(period, 365)
    start = (pd.Timestamp.today() - pd.Timedelta(days=days)).date()

    per_position = []
    for _, row in positions.iterrows():
        price_jpy = _aligned_price_jpy_series(row["ticker"], row["currency"], start)
        if price_jpy.empty:
            continue
        per_position.append(price_jpy * float(row["shares"]))

    if not per_position:
        return pd.Series(dtype=float)

    df = pd.concat(per_position, axis=1)
    df = df.ffill().bfill()
    return df.sum(axis=1).dropna()


def daily_returns(value_series: pd.Series) -> pd.Series:
    """Daily pct-change returns from a value series. NaN-safe."""
    if value_series.empty:
        return pd.Series(dtype=float)
    return value_series.pct_change().dropna()


def position_price_matrix(
    positions: pd.DataFrame,
    period: str = "1Y",
) -> pd.DataFrame:
    """JPY close prices for every position, columns = tickers, index = dates.

    Used by the correlation engine and per-position returns calculations.
    Returns empty DataFrame if no usable data.
    """
    if positions.empty:
        return pd.DataFrame()

    days = PERIOD_DAYS.get(period, 365)
    start = (pd.Timestamp.today() - pd.Timedelta(days=days)).date()

    cols = {}
    for _, row in positions.iterrows():
        s = _aligned_price_jpy_series(row["ticker"], row["currency"], start)
        if not s.empty:
            cols[row["ticker"]] = s

    if not cols:
        return pd.DataFrame()

    df = pd.DataFrame(cols)
    return df.ffill().dropna(how="all")


def benchmark_series(ticker: str, period: str = "1Y", currency: str = "USD") -> pd.Series:
    """JPY-converted close series for a benchmark ticker (SPY, QQQ, BTC-USD…)."""
    days = PERIOD_DAYS.get(period, 365)
    start = (pd.Timestamp.today() - pd.Timedelta(days=days)).date()
    return _aligned_price_jpy_series(ticker, currency, start)
