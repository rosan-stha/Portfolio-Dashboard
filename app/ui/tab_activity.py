"""Activity tab — transaction history with type/colour filters and CSV export."""
from typing import Callable

import pandas as pd
import streamlit as st

from app.config import GOLD, GREEN, MUTED, RED
from app.ui.components import label, safe_sum, section_hd


def _tx_color(t: str) -> str:
    t = str(t).lower()
    if "buy"      in t: return GREEN
    if "sell"     in t: return RED
    if "dividend" in t or "distribution" in t: return GOLD
    return MUTED


def render(th: pd.DataFrame, money: Callable[[float], str]) -> None:
    st.markdown(section_hd("Activity", "Transaction history — buy · sell · dividend", "History"), unsafe_allow_html=True)
    af1, af2, af3 = st.columns([2, 3, 2])

    with af1:
        type_opts = ["All"]
        if "type_en" in th.columns:
            type_opts += sorted(th["type_en"].dropna().unique().tolist())
        a_type = st.selectbox("Transaction type", type_opts, key="a_type")
    with af2:
        a_search = st.text_input(
            "🔍 Search company", placeholder="e.g. Toyota…", key="a_search"
        )
    with af3:
        a_sort = st.selectbox("Sort", ["Newest first", "Oldest first"], key="a_sort")

    view = th.copy()
    if a_type != "All" and "type_en" in view.columns:
        view = view[view["type_en"] == a_type]
    if a_search and "company" in view.columns:
        view = view[view["company"].str.contains(a_search, case=False, na=False)]
    if "date" in view.columns:
        view = view.sort_values("date", ascending=(a_sort == "Oldest first"))

    tbl = '<table class="ptable"><thead><tr>'
    for h in ["#", "Date", "Type", "Company / Fund", "Amount"]:
        tbl += f"<th>{h}</th>"
    tbl += "</tr></thead><tbody>"

    for i, (_, r) in enumerate(view.iterrows(), 1):
        date_str = r["date"].strftime("%Y-%m-%d") if pd.notna(r.get("date")) else "—"
        t_type   = str(r.get("type_en", r.get("tx_type", "—")))
        company  = str(r.get("company", "—"))
        amt      = r.get("amount", 0)
        tc       = _tx_color(t_type)

        tbl += (
            f"<tr>"
            f'<td style="color:{MUTED};font-size:0.7rem">{i}</td>'
            f"<td>{date_str}</td>"
            f'<td><span style="color:{tc};font-weight:700">{t_type}</span></td>'
            f"<td>{company}</td>"
            f'<td style="text-align:right;font-weight:600">{money(amt)}</td>'
            f"</tr>"
        )

    tbl += (
        f'<tr class="tot">'
        f'<td colspan="4">TOTAL — {len(view):,} transactions</td>'
        f'<td style="text-align:right">{money(safe_sum(view, "amount"))}</td>'
        f"</tr>"
    )
    tbl += "</tbody></table>"

    st.markdown(
        f'<div class="card" style="padding:0;overflow:hidden">'
        f'<div class="card-hd-inner">'
        f'<div class="eyebrow">Transaction History</div>'
        f'<div class="card-title font-display">{len(view):,} Records</div>'
        f'</div>'
        f'<div style="overflow-x:auto">{tbl}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("")
    csv_tx = view.rename(columns={
        "date": "Date", "type_en": "Type", "tx_type": "Transaction Type",
        "company": "Company", "amount": "Amount",
    }).to_csv(index=False)
    st.download_button("⬇ Export Transactions CSV", csv_tx, "transactions.csv", "text/csv")
