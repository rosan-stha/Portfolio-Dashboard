"""yfinance wrapper with Streamlit caching.

All public functions accept a single ticker string and return either a DataFrame
(history) or a dict (quote / info). Failures return empty values rather than
raising, so callers can skip missing tickers without try/except boilerplate.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

import pandas as pd
import streamlit as st

from app.config import HISTORY_TTL, INFO_TTL, QUOTE_TTL


def _import_yf():
    """Lazy import so the module loads even before yfinance is installed."""
    import yfinance as yf  # noqa: WPS433
    return yf


@st.cache_data(ttl=HISTORY_TTL, show_spinner=False)
def get_history(ticker: str, start: Optional[date] = None) -> pd.DataFrame:
    """Daily OHLCV bars for `ticker` from `start` (default: 5 years back) to today.

    Returns an empty DataFrame on failure. Index is tz-naive DatetimeIndex.
    """
    if not ticker:
        return pd.DataFrame()
    try:
        yf = _import_yf()
        start_str = start.isoformat() if start else None
        df = yf.download(
            ticker,
            start=start_str,
            period=None if start_str else "5y",
            auto_adjust=False,
            progress=False,
            threads=False,
        )
        if df.empty:
            return df
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index).tz_localize(None)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=QUOTE_TTL, show_spinner=False)
def get_quote(ticker: str) -> dict:
    """Latest price + previous close for `ticker`.

    Returns: {"price": float, "prev_close": float, "currency": str}
    Empty dict on failure.
    """
    if not ticker:
        return {}
    try:
        yf = _import_yf()
        tk = yf.Ticker(ticker)
        fi = getattr(tk, "fast_info", None)
        if fi:
            price = float(fi.get("last_price") or fi.get("lastPrice") or 0) or None
            prev  = float(fi.get("previous_close") or fi.get("previousClose") or 0) or None
            cur   = fi.get("currency") or ""
            if price:
                return {"price": price, "prev_close": prev or price, "currency": cur}
        # Fallback to history
        hist = tk.history(period="5d", auto_adjust=False)
        if hist.empty:
            return {}
        price = float(hist["Close"].iloc[-1])
        prev  = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else price
        return {"price": price, "prev_close": prev, "currency": ""}
    except Exception:
        return {}


@st.cache_data(ttl=INFO_TTL, show_spinner=False)
def get_info(ticker: str) -> dict:
    """Company metadata — sector, industry, name, country.

    Empty dict on failure. yfinance .info is slow and rate-limited, so this is
    cached for 24 hours.
    """
    if not ticker:
        return {}
    try:
        yf = _import_yf()
        info = yf.Ticker(ticker).info or {}
        return {
            "name":     info.get("longName") or info.get("shortName") or ticker,
            "sector":   info.get("sector") or "Unknown",
            "industry": info.get("industry") or "Unknown",
            "country":  info.get("country") or "Unknown",
            "currency": info.get("currency") or "",
        }
    except Exception:
        return {}


def close_on(history: pd.DataFrame, when: datetime | pd.Timestamp) -> float:
    """Return the close price on or immediately before `when`. 0 if unavailable."""
    if history.empty or pd.isna(when):
        return 0.0
    ts = pd.Timestamp(when).tz_localize(None) if pd.Timestamp(when).tzinfo else pd.Timestamp(when)
    # Find the last available trading day on or before `ts`
    available = history.loc[history.index <= ts]
    if available.empty:
        # If trade predates available history, fall back to first available bar
        return float(history["Close"].iloc[0])
    return float(available["Close"].iloc[-1])
