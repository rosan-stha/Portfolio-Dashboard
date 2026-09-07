"""Excel loader for the single-sheet PayPay transaction log.

Expected exact column headers (all 8 must be present):
    Date | Security | Description | Account Type |
    Order Amount | Price | FX Rate | Amount (Shares)

Public API
----------
load_portfolio(file_bytes) -> dict
    summary      : DataFrame – company, total_bought, total_sold, net_invested,
                               dividends, buy_trades, last_purchase
    transactions : DataFrame – date, Transaction Type, Company/Fund, Amount (¥),
                               Type (EN), Account Type, Amount (Shares),
                               + aliases: type_en, company, amount
    dividends    : DataFrame – company, received
    loaded_at    : datetime
    row_counts   : dict {raw, valid, skipped}
    errors       : list[str]  — non-fatal warnings; does not include fatal errors
    is_valid     : bool

make_demo() -> (summary_df, transactions_df, dividends_df)
    Realistic sample data when no file is uploaded.
"""
from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

REQUIRED_COLUMNS = [
    "Date", "Security", "Description", "Account Type",
    "Order Amount", "Price", "FX Rate", "Amount (Shares)",
]

TYPE_MAP: dict[str, str] = {
    # Japanese transaction descriptions → English canonical type
    "買付":         "Buy",
    "積立買付":     "Buy",
    "売却":         "Sell",
    "売却（特定）": "Sell",
    "配当金入金":   "Dividend",
    # English passthroughs (future-proof for exports that already have English)
    "buy":          "Buy",
    "sell":         "Sell",
    "dividend":     "Dividend",
}


def _normalize_type(val: Any) -> str:
    if pd.isna(val):
        return "Other"
    s = str(val).strip()
    return TYPE_MAP.get(s, TYPE_MAP.get(s.lower(), s))


@st.cache_data(show_spinner=False)
def load_portfolio(file_bytes: bytes) -> dict:
    """Parse the single-sheet flat transaction log and return the standard dict."""
    errors: list[str] = []

    try:
        raw = pd.read_excel(BytesIO(file_bytes), sheet_name=0, header=0)
    except Exception as exc:
        return _invalid(f"Could not read Excel file: {exc}")

    # ── Column validation ────────────────────────────────────────────────────
    missing = [c for c in REQUIRED_COLUMNS if c not in raw.columns]
    if missing:
        return _invalid(f"Missing required columns: {missing!r}")

    df = raw[REQUIRED_COLUMNS].copy()

    # ── Date parsing ─────────────────────────────────────────────────────────
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    nat_rows = df["Date"].isna().sum()
    if nat_rows:
        errors.append(f"{nat_rows} row(s) had unparseable dates and were dropped.")
    df = df.dropna(subset=["Date"]).reset_index(drop=True)
    raw_count = len(df)

    # ── Numeric coercion ─────────────────────────────────────────────────────
    for col in ["Order Amount", "Price", "FX Rate", "Amount (Shares)"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── Cross-check: Price × Shares × FX Rate ≈ Order Amount (1% tolerance) ─
    check = (
        df["Price"].notna() & (df["Price"] != 0) &
        df["FX Rate"].notna() & (df["FX Rate"] != 0) &
        df["Amount (Shares)"].notna() & (df["Amount (Shares)"] != 0) &
        df["Order Amount"].notna() & (df["Order Amount"] != 0)
    )
    for idx in df[check].index:
        row = df.loc[idx]
        computed = row["Price"] * row["Amount (Shares)"] * row["FX Rate"]
        actual = row["Order Amount"]
        if abs(computed - actual) / abs(actual) > 0.01:
            errors.append(
                f"Cross-check mismatch {row['Date'].date()} / {row['Security']}: "
                f"Price×Shares×FX={computed:,.0f} vs Order Amount={actual:,.0f}"
            )

    # ── Normalize Description → canonical English type ────────────────────────
    df["type_en"] = df["Description"].apply(_normalize_type)
    company = df["Security"].str.strip()

    # ── transactions DataFrame ───────────────────────────────────────────────
    transactions = pd.DataFrame({
        "date":               df["Date"],
        "Transaction Type":   df["Description"],
        "Company/Fund":       company,
        "Amount (¥)":         df["Order Amount"].fillna(0),
        "Type (EN)":          df["type_en"],
        "Account Type":       df["Account Type"],
        "Amount (Shares)":    df["Amount (Shares)"],
    })
    # Aliases used by the analytics layer
    transactions["type_en"] = transactions["Type (EN)"]
    transactions["company"]  = transactions["Company/Fund"]
    transactions["amount"]   = transactions["Amount (¥)"]

    # ── summary DataFrame (one row per Security) ──────────────────────────────
    buy_tx  = transactions[transactions["type_en"] == "Buy"]
    sell_tx = transactions[transactions["type_en"] == "Sell"]
    div_tx  = transactions[transactions["type_en"] == "Dividend"]

    all_companies = company.unique()
    summary = (
        pd.DataFrame({"company": all_companies})
        .merge(buy_tx.groupby("company")["amount"].sum().rename("total_bought"),
               on="company", how="left")
        .merge(sell_tx.groupby("company")["amount"].sum().rename("total_sold"),
               on="company", how="left")
        .merge(div_tx.groupby("company")["amount"].sum().rename("dividends"),
               on="company", how="left")
        .merge(buy_tx.groupby("company").size().rename("buy_trades"),
               on="company", how="left")
        .merge(buy_tx.groupby("company")["date"].max().rename("last_purchase"),
               on="company", how="left")
    )
    for col in ["total_bought", "total_sold", "dividends"]:
        summary[col] = summary[col].fillna(0.0)
    summary["buy_trades"]   = summary["buy_trades"].fillna(0).astype(int)
    summary["net_invested"] = summary["total_bought"] - summary["total_sold"]
    summary["last_purchase"] = (
        pd.to_datetime(summary["last_purchase"]).dt.strftime("%Y.%m.%d")
    )
    summary = summary[[
        "company", "total_bought", "total_sold", "net_invested",
        "dividends", "buy_trades", "last_purchase",
    ]]

    # ── dividends DataFrame (one row per company) ─────────────────────────────
    dividends = (
        div_tx.groupby("company")["amount"]
        .sum()
        .reset_index()
        .rename(columns={"amount": "received"})
        .sort_values("received", ascending=False)
        .reset_index(drop=True)
    )

    return {
        "summary":      summary,
        "transactions": transactions,
        "dividends":    dividends,
        "loaded_at":    datetime.now(),
        "row_counts":   {"raw": raw_count, "valid": len(transactions), "skipped": int(nat_rows)},
        "errors":       errors,
        "is_valid":     True,
    }


def _invalid(msg: str) -> dict:
    return {
        "summary":      pd.DataFrame(),
        "transactions": pd.DataFrame(),
        "dividends":    pd.DataFrame(),
        "loaded_at":    datetime.now(),
        "row_counts":   {"raw": 0, "valid": 0, "skipped": 0},
        "errors":       [msg],
        "is_valid":     False,
    }


# ── Demo-data companies — Yahoo Finance tickers (Tokyo Stock Exchange) ──
DEMO_COMPANIES_TICKERS = {
    "Toyota Motor":          "7203.T",
    "SoftBank Group":        "9984.T",
    "Sony Group":            "6758.T",
    "Rakuten Group":         "4755.T",
    "KDDI Corp":             "9433.T",
    "Mitsubishi UFJ":        "8306.T",
    "Fast Retailing":        "9983.T",
    "Nintendo":              "7974.T",
    "Keyence Corp":          "6861.T",
    "Recruit Holdings":      "6098.T",
    "Shin-Etsu Chemical":    "4063.T",
    "Daikin Industries":     "6367.T",
    "Olympus Corp":          "7733.T",
    "Murata Manufacturing":  "6981.T",
    "TDK Corp":              "6762.T",
}


def make_demo() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return realistic sample (summary, transactions, dividends) DataFrames."""
    rng = np.random.default_rng(42)

    companies = list(DEMO_COMPANIES_TICKERS.keys())
    n = len(companies)
    bought    = rng.integers(60_000, 600_000, size=n).astype(float)
    sold_mask = rng.random(n) > 0.65
    sold      = np.where(sold_mask, rng.integers(10_000, 300_000, size=n).astype(float), 0.0)
    net       = bought - sold
    divs      = np.round(net * rng.uniform(0.005, 0.03, size=n), 0)
    trades    = rng.integers(1, 18, size=n).astype(float)
    dates     = pd.date_range("2024-01-01", periods=n, freq="ME").strftime("%Y.%m.%d")

    summary = pd.DataFrame({
        "company":       companies,
        "total_bought":  bought,
        "total_sold":    sold,
        "net_invested":  net,
        "dividends":     divs,
        "buy_trades":    trades,
        "last_purchase": dates,
    })

    rows = []
    for c, b in zip(companies[:10], bought[:10]):
        k = int(rng.integers(2, 7))
        amounts = np.round(b / k * rng.uniform(0.8, 1.2, size=k), 0)
        for a in amounts:
            day = pd.Timestamp("2024-01-01") + pd.Timedelta(days=int(rng.integers(0, 480)))
            rows.append({"date": day, "type_en": "Buy", "company": c, "amount": a,
                         "Type (EN)": "Buy", "Company/Fund": c, "Amount (¥)": a,
                         "Transaction Type": "Buy", "Account Type": "Taxable (Tokutei)",
                         "Amount (Shares)": None})
    for c, s in zip(companies[:5], sold[:5]):
        if s > 0:
            day = pd.Timestamp("2024-08-01") + pd.Timedelta(days=int(rng.integers(0, 120)))
            rows.append({"date": day, "type_en": "Sell", "company": c, "amount": s,
                         "Type (EN)": "Sell", "Company/Fund": c, "Amount (¥)": s,
                         "Transaction Type": "Sell", "Account Type": "Taxable (Tokutei)",
                         "Amount (Shares)": None})
    for c, d in zip(companies[:7], divs[:7]):
        if d > 0:
            rows.append({"date": pd.Timestamp("2024-09-30"), "type_en": "Dividend",
                         "company": c, "amount": d, "Type (EN)": "Dividend",
                         "Company/Fund": c, "Amount (¥)": d,
                         "Transaction Type": "配当金入金", "Account Type": "Taxable (Tokutei)",
                         "Amount (Shares)": None})

    transactions = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    dividends = (
        summary[["company", "dividends"]]
        .rename(columns={"dividends": "received"})
        .query("received > 0")
        .sort_values("received", ascending=False)
        .reset_index(drop=True)
    )

    return summary, transactions, dividends
