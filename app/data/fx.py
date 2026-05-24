"""FX rate fetching via Yahoo Finance.

Yahoo encodes FX pairs as `<BASE><QUOTE>=X` (e.g. `USDJPY=X`). All helpers in
this module are JPY-quote-oriented since the user's cost basis is in JPY.

Conventions:
    currency  — 3-letter ISO code, uppercased (e.g. "USD")
    pair      — Yahoo symbol with `=X` suffix (e.g. "USDJPY=X")
    factor    — multiplier that converts native price → JPY  (price_jpy = price_native × factor)
"""
from __future__ import annotations

from datetime import date
from typing import Optional

import pandas as pd
import streamlit as st

from app.config import HISTORY_TTL, QUOTE_TTL


def _import_yf():
    import yfinance as yf  # noqa: WPS433
    return yf


def pair_for(currency: str) -> str:
    """Yahoo pair symbol for converting `currency` → JPY. Empty if input is JPY."""
    c = (currency or "").upper().strip()
    if not c or c == "JPY":
        return ""
    return f"{c}JPY=X"


@st.cache_data(ttl=QUOTE_TTL, show_spinner=False)
def get_rate(currency: str) -> float:
    """Current `currency` → JPY rate. JPY returns 1.0; failure returns 0.0."""
    pair = pair_for(currency)
    if not pair:
        return 1.0
    try:
        yf = _import_yf()
        tk = yf.Ticker(pair)
        fi = getattr(tk, "fast_info", None)
        if fi:
            rate = float(fi.get("last_price") or fi.get("lastPrice") or 0)
            if rate > 0:
                return rate
        hist = tk.history(period="5d", auto_adjust=False)
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception:
        pass
    return 0.0


@st.cache_data(ttl=HISTORY_TTL, show_spinner=False)
def get_history(currency: str, start: Optional[date] = None) -> pd.DataFrame:
    """Daily FX bars for `currency` → JPY. Empty DataFrame on failure or JPY input."""
    pair = pair_for(currency)
    if not pair:
        return pd.DataFrame()
    try:
        yf = _import_yf()
        start_str = start.isoformat() if start else None
        df = yf.download(
            pair,
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


def to_jpy(amount: float, currency: str) -> float:
    """Convert an amount in `currency` to JPY at the current rate."""
    rate = get_rate(currency)
    return amount * rate if rate else 0.0


def jpy_factor_series(currency: str, start: Optional[date] = None) -> pd.Series:
    """A series of `currency → JPY` factors, indexed by date.

    For JPY input, returns an empty Series — callers should treat that as
    "no conversion needed" and use a factor of 1.0.
    """
    if not currency or currency.upper() == "JPY":
        return pd.Series(dtype=float)
    hist = get_history(currency, start)
    if hist.empty:
        return pd.Series(dtype=float)
    return hist["Close"].copy()


def factor_on(factor_series: pd.Series, when: pd.Timestamp) -> float:
    """Look up the FX factor on or before `when`. Returns 1.0 if series empty."""
    if factor_series.empty:
        return 1.0
    ts = pd.Timestamp(when).tz_localize(None) if pd.Timestamp(when).tzinfo else pd.Timestamp(when)
    available = factor_series.loc[factor_series.index <= ts]
    if available.empty:
        return float(factor_series.iloc[0])
    return float(available.iloc[-1])
