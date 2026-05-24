"""Excel loader + demo-data generator.

The user's Excel file has three sheets — Portfolio Summary, Transaction History,
Dividend Tracker — with header names that vary between Japanese and English. The
column-resolver maps each acceptable variant to a single internal key.
"""
from io import BytesIO

import numpy as np
import pandas as pd
import streamlit as st


# ── Column-name resolvers (internal_key → list of acceptable Excel headers) ──
PS_MAP = {   # Portfolio Summary sheet
    "company":       ["Company / Fund Name", "Company name", "Company Name", "Company", "銘柄名", "銘柄"],
    "total_bought":  ["Total Bought (¥)", "Total Bought", "買付合計", "購入合計"],
    "total_sold":    ["Total Sold (¥)",   "Total Sold",   "売却合計"],
    "net_invested":  ["Net Invested (¥)", "Net Invested", "純投資額"],
    "dividends":     ["Dividends / Dist. (¥)", "Dividends (¥)", "Dividends", "配当金"],
    "buy_trades":    ["Buy Trades",       "買付回数"],
    "last_purchase": ["Last Purchase",    "最終購入日"],
}
TH_MAP = {   # Transaction History sheet
    "date":    ["Date", "日付", "取引日"],
    "tx_type": ["Transaction Type", "Type", "取引種別"],
    "company": ["Company / Fund", "Company/Fund", "Company", "Company Name", "銘柄名"],
    "amount":  ["Amount (¥)", "Amount", "金額"],
    "type_en": ["Type (EN)", "Type EN", "Type_EN"],
}
DT_MAP = {   # Dividend Tracker sheet
    "company":  ["Company / Fund", "Company/Fund", "Company", "Company Name", "銘柄名"],
    "received": ["Total Received (¥)", "Total Received", "配当合計"],
}


def remap(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    """Rename df columns using the first matching alias from col_map."""
    rename = {}
    for internal_key, aliases in col_map.items():
        for alias in aliases:
            if alias in df.columns:
                rename[alias] = internal_key
                break
    return df.rename(columns=rename)


@st.cache_data(show_spinner=False)
def load_excel(file_bytes: bytes):
    """Read the uploaded Excel file and return (ps, th, dt) DataFrames."""
    xls = pd.ExcelFile(BytesIO(file_bytes))

    # Portfolio Summary — row 4 (0-indexed: 3) is the header; rows 1-3 are title/subtitle/blank
    ps = remap(pd.read_excel(xls, sheet_name="Portfolio Summary", header=3), PS_MAP)
    for col in ["total_bought", "total_sold", "net_invested", "dividends", "buy_trades"]:
        if col in ps.columns:
            ps[col] = pd.to_numeric(ps[col], errors="coerce").fillna(0)
    ps = ps.dropna(subset=["company"]).reset_index(drop=True)
    # drop section-label and total rows (numeric columns are 0 for them after coercion)
    ps = ps[ps["company"].str.match(r"^(?!▶|TOTAL)", na=False)].reset_index(drop=True)

    # Transaction History — row 2 (0-indexed: 1) is the header; row 1 is the title
    th = remap(pd.read_excel(xls, sheet_name="Transaction History", header=1), TH_MAP)
    if "amount" in th.columns:
        th["amount"] = pd.to_numeric(th["amount"], errors="coerce").fillna(0)
    if "date" in th.columns:
        th["date"] = pd.to_datetime(th["date"], errors="coerce")
    if "type_en" not in th.columns and "tx_type" in th.columns:
        th["type_en"] = th["tx_type"]
    th = th.dropna(subset=["date"]).reset_index(drop=True)

    # Dividend Tracker — row 2 (0-indexed: 1) is the header; row 1 is the title
    dt = remap(pd.read_excel(xls, sheet_name="Dividend Tracker", header=1), DT_MAP)
    if "received" in dt.columns:
        dt["received"] = pd.to_numeric(dt["received"], errors="coerce").fillna(0)
    dt = (
        dt.dropna(subset=["company"])
        .sort_values("received", ascending=False)
        .reset_index(drop=True)
    )

    return ps, th, dt


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


def make_demo():
    """Return realistic sample DataFrames so the dashboard isn't empty."""
    rng = np.random.default_rng(42)

    companies = list(DEMO_COMPANIES_TICKERS.keys())
    n = len(companies)
    bought    = rng.integers(60_000, 600_000, size=n).astype(float)
    sold_mask = rng.random(n) > 0.65
    sold      = np.where(sold_mask, rng.integers(10_000, 300_000, size=n).astype(float), 0.0)
    net       = bought - sold
    divs      = np.round(net * rng.uniform(0.005, 0.03, size=n), 0)
    trades    = rng.integers(1, 18, size=n).astype(float)
    dates     = pd.date_range("2024-01-01", periods=n, freq="ME").strftime("%Y-%m-%d")

    ps = pd.DataFrame({
        "company": companies, "total_bought": bought, "total_sold": sold,
        "net_invested": net, "dividends": divs, "buy_trades": trades,
        "last_purchase": dates,
    })

    rows = []
    for c, b in zip(companies[:10], bought[:10]):
        k = int(rng.integers(2, 7))
        amounts = np.round(b / k * rng.uniform(0.8, 1.2, size=k), 0)
        for a in amounts:
            day = pd.Timestamp("2024-01-01") + pd.Timedelta(days=int(rng.integers(0, 480)))
            rows.append({"date": day, "type_en": "Buy", "company": c, "amount": a})
    for c, s in zip(companies[:5], sold[:5]):
        if s > 0:
            day = pd.Timestamp("2024-08-01") + pd.Timedelta(days=int(rng.integers(0, 120)))
            rows.append({"date": day, "type_en": "Sell", "company": c, "amount": s})
    for c, d in zip(companies[:7], divs[:7]):
        if d > 0:
            rows.append({"date": pd.Timestamp("2024-09-30"), "type_en": "Dividend", "company": c, "amount": d})
    th = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    dt = (
        ps[["company", "dividends"]]
        .rename(columns={"dividends": "received"})
        .query("received > 0")
        .sort_values("received", ascending=False)
        .reset_index(drop=True)
    )

    return ps, th, dt
