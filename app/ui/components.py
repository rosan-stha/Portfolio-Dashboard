"""Shared UI helpers — labels, money formatting, TV links, chart base."""
import urllib.parse

import pandas as pd
import streamlit as st

from app.config import BG2, BORDER, CARD, MUTED, TEXT


def label(text: str) -> None:
    """Render a small uppercase section heading."""
    st.markdown(f'<p class="lbl">{text}</p>', unsafe_allow_html=True)


def fmt_money(value, sym: str, rate: float = 1.0) -> str:
    """Format a number as currency string in JPY (¥) or USD ($)."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "—"
    if sym == "¥":
        return f"¥{v:,.0f}"
    return f"${v / rate:,.2f}"


def fmt_pct(value, decimals: int = 2) -> str:
    """Format a fractional value (0.123) as a percent string ("12.30%")."""
    try:
        return f"{float(value) * 100:.{decimals}f}%"
    except (TypeError, ValueError):
        return "—"


def tv_url(query: str) -> str:
    """Build a TradingView search URL for a company or ticker."""
    return f"https://www.tradingview.com/search/?query={urllib.parse.quote(str(query))}"


def safe_sum(df: pd.DataFrame, col: str) -> float:
    """Return column sum, or 0 if column is missing."""
    return float(df[col].sum()) if col in df.columns else 0.0


def chart_base(**extra) -> dict:
    """Shared Plotly layout — light theme, warm borders, no gridlines."""
    base = dict(
        paper_bgcolor=CARD,
        plot_bgcolor=BG2,
        font=dict(color=TEXT, size=11, family="IBM Plex Sans, IBM Plex Sans JP, system-ui"),
        margin=dict(t=30, b=20, l=20, r=20),
        showlegend=False,
        xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER, tickfont=dict(color=MUTED)),
        yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER, tickfont=dict(color=MUTED)),
    )
    base.update(extra)
    return base


def money_formatter(sym: str, usd_rate: float):
    """Return a closure that formats values with the current currency settings."""
    def _fmt(value) -> str:
        return fmt_money(value, sym, usd_rate)
    return _fmt
