"""Holdings tab — filterable table of all positions with CSV export."""
from typing import Callable

import pandas as pd
import streamlit as st

from app.config import BLUE, GOLD, GREEN, MUTED
from app.ui.components import label, safe_sum, tv_url


def render(ps: pd.DataFrame, money: Callable[[float], str]) -> None:
    # Filters
    fc1, fc2, fc3 = st.columns([3, 2, 2])

    with fc1:
        search = st.text_input(
            "🔍 Search company", placeholder="Type a company name…", key="h_search"
        )
    with fc2:
        view = st.radio(
            "Show",
            ["All", "Top 10", "Top 20", "Dividends Only"],
            horizontal=True,
            key="h_view",
        )
    with fc3:
        sort_col = st.selectbox(
            "Sort by",
            options=["net_invested", "total_bought", "total_sold", "dividends", "buy_trades"],
            format_func=lambda x: {
                "net_invested": "Net Invested",
                "total_bought": "Total Bought",
                "total_sold":   "Total Sold",
                "dividends":    "Dividends",
                "buy_trades":   "Buy Trades",
            }[x],
            key="h_sort",
        )

    view_h = ps.copy()
    if search:
        view_h = view_h[view_h["company"].str.contains(search, case=False, na=False)]
    if view == "Top 10":
        view_h = view_h.nlargest(10, "net_invested")
    elif view == "Top 20":
        view_h = view_h.nlargest(20, "net_invested")
    elif view == "Dividends Only" and "dividends" in view_h.columns:
        view_h = view_h[view_h["dividends"] > 0]

    view_h = view_h.sort_values(sort_col, ascending=False).reset_index(drop=True)

    label(f"Holdings — {len(view_h):,} positions")

    html = '<table class="ptable"><thead><tr>'
    for col_hdr in ["#", "Company", "Total Bought", "Total Sold",
                    "Net Invested", "Dividends", "Buy Trades", "Last Purchase", "TV"]:
        html += f"<th>{col_hdr}</th>"
    html += "</tr></thead><tbody>"

    for i, (_, row) in enumerate(view_h.iterrows(), 1):
        ni  = row.get("net_invested", 0)
        div = row.get("dividends", 0)
        ts  = row.get("total_sold", 0)
        bt  = row.get("buy_trades", 0)
        lp  = str(row.get("last_purchase", "—"))[:10]

        html += (
            f"<tr>"
            f'<td style="color:{MUTED};font-size:0.7rem">{i}</td>'
            f"<td style=\"font-weight:600\">{row['company']}</td>"
            f"<td>{money(row.get('total_bought', 0))}</td>"
            f"<td>{money(ts)}</td>"
            f'<td style="color:{GREEN};font-weight:700">{money(ni)}</td>'
            f'<td style="color:{GOLD};font-weight:700">{money(div)}</td>'
            f'<td style="text-align:center">{int(bt)}</td>'
            f'<td style="color:{MUTED}">{lp}</td>'
            f'<td><a href="{tv_url(row["company"])}" target="_blank" '
            f'style="color:{BLUE};text-decoration:none">📊</a></td>'
            f"</tr>"
        )

    html += (
        f'<tr class="tot">'
        f'<td colspan="2">TOTAL  ({len(view_h):,} positions)</td>'
        f"<td>{money(safe_sum(view_h, 'total_bought'))}</td>"
        f"<td>{money(safe_sum(view_h, 'total_sold'))}</td>"
        f'<td style="color:{GREEN};font-weight:700">{money(safe_sum(view_h, "net_invested"))}</td>'
        f'<td style="color:{GOLD};font-weight:700">{money(safe_sum(view_h, "dividends"))}</td>'
        f'<td style="text-align:center">{int(safe_sum(view_h, "buy_trades"))}</td>'
        f'<td colspan="2"></td>'
        f"</tr>"
    )
    html += "</tbody></table>"
    st.write(html, unsafe_allow_html=True)

    st.markdown("")
    export_cols = {
        "company": "Company", "total_bought": "Total Bought", "total_sold": "Total Sold",
        "net_invested": "Net Invested", "dividends": "Dividends",
        "buy_trades": "Buy Trades", "last_purchase": "Last Purchase",
    }
    export_h = view_h.rename(columns=export_cols)[
        [v for k, v in export_cols.items() if k in view_h.columns]
    ]
    st.download_button(
        "⬇ Export Holdings CSV",
        export_h.to_csv(index=False),
        "holdings.csv",
        "text/csv",
    )
