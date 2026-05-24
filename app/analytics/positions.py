"""Derive shares held, cost basis, current value, and unrealized P&L.

Approach: for each mapped company, walk its transactions chronologically and
derive shares = ¥amount / (close-on-trade-date × FX-on-trade-date). For
JPY-denominated tickers the FX factor is 1.0, so the math reduces to
¥amount / close. For non-JPY tickers (e.g. AAPL in USD), historical FX bars
convert the native close into JPY-equivalent per-share cost.

All output values are in JPY. There is no longer a currency mismatch
suppression — every mapped ticker contributes to the portfolio totals.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import pandas as pd

from app.data import fx, market


def _company_transactions(th: pd.DataFrame, company: str) -> pd.DataFrame:
    """Buy/Sell transactions for a single company, sorted by date."""
    if th.empty or "company" not in th.columns:
        return th.iloc[0:0]
    sub = th[th["company"] == company].copy()
    if "type_en" in sub.columns:
        sub = sub[sub["type_en"].str.lower().isin(["buy", "sell"])]
    if "date" in sub.columns:
        sub = sub.sort_values("date")
    return sub.reset_index(drop=True)


def _derive_shares(
    tx: pd.DataFrame,
    history: pd.DataFrame,
    fx_series: pd.Series,
) -> float:
    """Walk transactions; +shares on Buy, -shares on Sell. JPY-aware.

    shares_delta = ¥amount ÷ (price_native × fx_at_trade)
    For JPY tickers, fx_series is empty and factor_on() returns 1.0.
    """
    shares = 0.0
    if tx.empty or history.empty:
        return shares
    for _, t in tx.iterrows():
        close = market.close_on(history, t["date"])
        if close <= 0:
            continue
        fx_factor = fx.factor_on(fx_series, t["date"])
        if fx_factor <= 0:
            continue
        amount = float(t.get("amount", 0))
        if amount <= 0:
            continue
        effective_price_jpy = close * fx_factor
        if effective_price_jpy <= 0:
            continue
        t_type = str(t.get("type_en", "")).lower()
        if "buy" in t_type:
            shares += amount / effective_price_jpy
        elif "sell" in t_type:
            shares -= amount / effective_price_jpy
    return shares


def build_positions(
    ps: pd.DataFrame,
    th: pd.DataFrame,
    ticker_map: Dict[str, str],
) -> pd.DataFrame:
    """Build the positions table — one row per mapped company with live data.

    Returns DataFrame with columns:
        company, ticker, sector, currency, fx_rate, shares, cost_basis, avg_cost,
        current_price, current_price_jpy, prev_close, prev_close_jpy,
        day_change_pct, market_value, unrealized_pl, unrealized_pct
    """
    rows: List[dict] = []
    if ps.empty:
        return pd.DataFrame(rows)

    for _, ps_row in ps.iterrows():
        company = ps_row["company"]
        ticker = ticker_map.get(company, "").strip()
        if not ticker:
            continue

        tx = _company_transactions(th, company)
        if tx.empty:
            continue

        start = tx["date"].min().date() if pd.notna(tx["date"].min()) else None
        history = market.get_history(ticker, start)
        if history.empty:
            continue

        # Determine currency before deriving shares (FX history needed for non-JPY)
        quote = market.get_quote(ticker)
        currency = (quote.get("currency", "") or "JPY").upper() or "JPY"
        fx_series = fx.jpy_factor_series(currency, start)
        fx_rate_now = fx.get_rate(currency)
        if fx_rate_now <= 0:
            # FX unavailable — can't price non-JPY position; skip
            if currency != "JPY":
                continue
            fx_rate_now = 1.0

        shares = _derive_shares(tx, history, fx_series)
        if shares <= 1e-6:
            continue  # closed or never held

        cost_basis = float(ps_row.get("net_invested", 0))
        if cost_basis <= 0:
            cost_basis = float(ps_row.get("total_bought", 0)) - float(ps_row.get("total_sold", 0))

        price_native = quote.get("price", 0) or 0
        prev_close_native = quote.get("prev_close", price_native) or price_native

        price_jpy = price_native * fx_rate_now
        prev_close_jpy = prev_close_native * fx_rate_now

        info = market.get_info(ticker)

        market_value = shares * price_jpy
        unrealized_pl = market_value - cost_basis
        unrealized_pct = (unrealized_pl / cost_basis) if cost_basis > 0 else 0.0

        day_change_pct = (price_native - prev_close_native) / prev_close_native if prev_close_native else 0.0
        avg_cost = cost_basis / shares if shares else 0.0

        rows.append({
            "company":           company,
            "ticker":            ticker,
            "sector":            info.get("sector", "Unknown"),
            "industry":          info.get("industry", "Unknown"),
            "country":           info.get("country", "Unknown"),
            "currency":          currency,
            "fx_rate":           fx_rate_now,
            "shares":            shares,
            "cost_basis":        cost_basis,
            "avg_cost":          avg_cost,
            "current_price":     price_native,
            "current_price_jpy": price_jpy,
            "prev_close":        prev_close_native,
            "prev_close_jpy":    prev_close_jpy,
            "day_change_pct":    day_change_pct,
            "market_value":      market_value,
            "unrealized_pl":     unrealized_pl,
            "unrealized_pct":    unrealized_pct,
        })

    return pd.DataFrame(rows)


def portfolio_kpis(positions: pd.DataFrame) -> dict:
    """Aggregate JPY KPIs across all positions."""
    if positions.empty:
        return {"market_value": 0, "cost_basis": 0, "unrealized_pl": 0,
                "unrealized_pct": 0, "day_change": 0, "day_change_pct": 0,
                "n_positions": 0}

    mv  = float(positions["market_value"].sum())
    cb  = float(positions["cost_basis"].sum())
    upl = mv - cb
    prev_value = float((positions["shares"] * positions["prev_close_jpy"]).sum())
    day_change = mv - prev_value
    return {
        "market_value":   mv,
        "cost_basis":     cb,
        "unrealized_pl":  upl,
        "unrealized_pct": (upl / cb) if cb > 0 else 0.0,
        "day_change":     day_change,
        "day_change_pct": (day_change / prev_value) if prev_value > 0 else 0.0,
        "n_positions":    len(positions),
    }


def position_weights(positions: pd.DataFrame) -> pd.Series:
    """Market-value weights per position, indexed by ticker. Sums to ~1.0."""
    if positions.empty:
        return pd.Series(dtype=float)
    total = float(positions["market_value"].sum())
    if total <= 0:
        return pd.Series(dtype=float)
    return (positions.set_index("ticker")["market_value"] / total).sort_values(ascending=False)
