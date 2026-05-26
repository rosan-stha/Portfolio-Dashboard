"""Overview tab — allocation donut, top-20 bar, treemap, monthly buy/sell."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.config import BLUE, CARD, GREEN, MUTED, NOGRID, RED, TEXT
from app.ui.components import chart_base, label, section_hd


def render(ps: pd.DataFrame, th: pd.DataFrame) -> None:
    # Row 1: donut | horizontal bar
    left, right = st.columns(2)

    # ── Donut — portfolio allocation ─────────────────────────────────────────
    with left:
        st.markdown(section_hd("Portfolio Allocation", "Net Invested", "Allocation"), unsafe_allow_html=True)

        top15 = ps.nlargest(15, "net_invested")
        others_val = ps.loc[~ps.index.isin(top15.index), "net_invested"].sum()
        donut_df = top15[["company", "net_invested"]].copy()
        if others_val > 0:
            donut_df = pd.concat(
                [donut_df, pd.DataFrame([{"company": "Others", "net_invested": others_val}])],
                ignore_index=True,
            )

        fig = px.pie(
            donut_df, values="net_invested", names="company",
            hole=0.55,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig.update_traces(
            textfont_color=TEXT,
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>Net Invested: ¥%{value:,.0f}<br>%{percent}<extra></extra>",
        )
        fig.update_layout(
            **chart_base(height=380, showlegend=True),
            legend=dict(bgcolor=CARD, font=dict(color=TEXT, size=9)),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Horizontal bar — Top 20 by Net Invested ──────────────────────────────
    with right:
        st.markdown(section_hd("Top 20 Holdings", "By Net Invested", "Sizing"), unsafe_allow_html=True)

        top20 = ps.nlargest(20, "net_invested").sort_values("net_invested")
        fig = go.Figure(go.Bar(
            x=top20["net_invested"],
            y=top20["company"],
            orientation="h",
            marker_color=BLUE,
            opacity=0.88,
            hovertemplate="<b>%{y}</b><br>Net Invested: ¥%{x:,.0f}<extra></extra>",
        ))
        fig.update_layout(**chart_base(
            height=380,
            xaxis=dict(color=MUTED, gridcolor=NOGRID, showgrid=False, tickprefix="¥"),
            yaxis=dict(color=MUTED, gridcolor=NOGRID, showgrid=False),
        ))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Row 2: treemap | monthly bar
    col_tree, col_month = st.columns(2)

    with col_tree:
        st.markdown(section_hd("Holdings Treemap", "Sized by Net Invested", "Treemap"), unsafe_allow_html=True)

        tree_df = ps[ps["net_invested"] > 0].copy()
        fig = px.treemap(
            tree_df,
            path=["company"],
            values="net_invested",
            color="net_invested",
            color_continuous_scale=[[0, CARD], [0.35, BLUE], [1, GREEN]],
        )
        fig.update_traces(
            textfont=dict(color=TEXT),
            hovertemplate="<b>%{label}</b><br>Net Invested: ¥%{value:,.0f}<extra></extra>",
        )
        fig.update_layout(**chart_base(height=360), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_month:
        st.markdown(section_hd("Monthly Volume", "Buy vs Sell", "Activity"), unsafe_allow_html=True)

        if "date" in th.columns and "type_en" in th.columns:
            th_m = th.dropna(subset=["date"]).copy()
            th_m["month"] = th_m["date"].dt.to_period("M").astype(str)

            buys  = th_m[th_m["type_en"].str.lower() == "buy" ].groupby("month")["amount"].sum()
            sells = th_m[th_m["type_en"].str.lower() == "sell"].groupby("month")["amount"].sum()
            months = sorted(set(buys.index) | set(sells.index))

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=months,
                y=[buys.get(mo, 0) for mo in months],
                name="Buy",
                marker_color=GREEN,
                hovertemplate="<b>%{x}</b><br>Buy: ¥%{y:,.0f}<extra></extra>",
            ))
            fig.add_trace(go.Bar(
                x=months,
                y=[sells.get(mo, 0) for mo in months],
                name="Sell",
                marker_color=RED,
                hovertemplate="<b>%{x}</b><br>Sell: ¥%{y:,.0f}<extra></extra>",
            ))
            fig.update_layout(**chart_base(
                height=360, showlegend=True, barmode="group",
                xaxis=dict(color=MUTED, gridcolor=NOGRID, showgrid=False),
                yaxis=dict(color=MUTED, gridcolor=NOGRID, showgrid=False, tickprefix="¥"),
            ), legend=dict(bgcolor=CARD, font=dict(color=TEXT)))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Transaction history not available for monthly chart.")
