"""Dividends tab — summary, ranked payers, top-20 chart, CSV export."""
from typing import Callable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.config import GOLD, MUTED, NOGRID, TEXT
from app.ui.components import chart_base, label, safe_sum, section_hd


def render(dt: pd.DataFrame, money: Callable[[float], str]) -> None:
    if dt.empty or safe_sum(dt, "received") == 0:
        st.info("No dividend data found in the uploaded file.")
        return

    st.markdown(section_hd("Dividend Income", "Total received across all holdings", "Income"), unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    d1.metric("Total Dividend Income", money(safe_sum(dt, "received")))
    d2.metric("Paying Companies",      f"{len(dt):,}")
    d3.metric("Average per Company",   money(dt["received"].mean()))

    st.markdown("---")

    total_recv = safe_sum(dt, "received")

    tbl = '<table class="ptable"><thead><tr>'
    for h in ["#", "Company / Fund", "Total Received", "Share"]:
        tbl += f"<th>{h}</th>"
    tbl += "</tr></thead><tbody>"

    for i, (_, r) in enumerate(dt.iterrows(), 1):
        pct = r["received"] / total_recv * 100 if total_recv > 0 else 0
        bar_px = max(4, int(pct * 2.5))

        tbl += (
            f"<tr>"
            f'<td style="color:{MUTED};font-size:0.7rem">{i}</td>'
            f'<td style="font-weight:600">{r["company"]}</td>'
            f'<td style="color:{GOLD};font-weight:700;text-align:right">{money(r["received"])}</td>'
            f'<td>'
            f'  <span style="font-size:0.75rem;color:{MUTED}">{pct:.1f}%</span>&nbsp;'
            f'  <span style="display:inline-block;width:{bar_px}px;height:6px;'
            f'background:{GOLD};border-radius:3px;vertical-align:middle;opacity:0.7"></span>'
            f'</td>'
            f"</tr>"
        )

    tbl += (
        f'<tr class="tot">'
        f'<td colspan="2">TOTAL</td>'
        f'<td style="text-align:right;color:{GOLD}">{money(total_recv)}</td>'
        f"<td>100%</td>"
        f"</tr>"
    )
    tbl += "</tbody></table>"

    st.markdown(
        f'<div class="card" style="padding:0;overflow:hidden">'
        f'<div class="card-hd-inner">'
        f'<div class="eyebrow">Dividend Payers</div>'
        f'<div class="card-title font-display">Ranked by Total Received</div>'
        f'</div>'
        f'<div style="overflow-x:auto">{tbl}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown(section_hd("Top 20 Payers", "Bar chart — sorted by total received", "Chart"), unsafe_allow_html=True)
    top20 = dt.nlargest(20, "received").sort_values("received")

    fig = go.Figure(go.Bar(
        x=top20["received"],
        y=top20["company"],
        orientation="h",
        marker_color=GOLD,
        opacity=0.88,
        text=[money(v) for v in top20["received"]],
        textposition="outside",
        textfont=dict(color=TEXT, size=10),
        hovertemplate="<b>%{y}</b><br>Received: ¥%{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **chart_base(height=max(280, len(top20) * 32)),
        xaxis=dict(color=MUTED, gridcolor=NOGRID, showgrid=False, tickprefix="¥"),
        yaxis=dict(color=MUTED, gridcolor=NOGRID, showgrid=False),
    )
    st.plotly_chart(fig, use_container_width=True)

    csv_div = dt.rename(columns={"company": "Company", "received": "Total Received"}).to_csv(index=False)
    st.download_button("⬇ Export Dividends CSV", csv_div, "dividends.csv", "text/csv")
