"""Shared UI helpers — labels, money formatting, TV links, chart base."""
import urllib.parse
from typing import Optional

import pandas as pd
import streamlit as st

from app.config import (
    BG2, BLUE, BORDER, CARD, CYAN, MUTED, NEG, POS, TEXT, WARN
)


# ── Text helpers ─────────────────────────────────────────────────────────────

def label(text: str) -> None:
    """Render a small uppercase section heading."""
    st.markdown(f'<p class="lbl">{text}</p>', unsafe_allow_html=True)


def eyebrow(text: str) -> None:
    """Render an eyebrow label (smaller, more muted)."""
    st.markdown(f'<div class="eyebrow">{text}</div>', unsafe_allow_html=True)


# ── Money / percent formatters ────────────────────────────────────────────────

def fmt_money(value, sym: str, rate: float = 1.0) -> str:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "—"
    if sym == "¥":
        return f"¥{v:,.0f}"
    return f"${v / rate:,.2f}"


def fmt_money_compact(value, sym: str = "¥", rate: float = 1.0) -> str:
    try:
        v = float(value) / rate
    except (TypeError, ValueError):
        return "—"
    if sym == "¥":
        if abs(v) >= 1e8: return f"¥{v/1e8:.2f}B"
        if abs(v) >= 1e6: return f"¥{v/1e6:.2f}M"
        if abs(v) >= 1e3: return f"¥{v/1e3:.1f}K"
        return f"¥{round(v):,}"
    else:
        if abs(v) >= 1e6: return f"${v/1e6:.2f}M"
        if abs(v) >= 1e3: return f"${v/1e3:.1f}K"
        return f"${v:.0f}"


def fmt_pct(value, decimals: int = 2) -> str:
    try:
        return f"{float(value) * 100:.{decimals}f}%"
    except (TypeError, ValueError):
        return "—"


def fmt_sign(value, sym: str = "¥", rate: float = 1.0, compact: bool = False) -> str:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "—"
    sign = "+" if v >= 0 else "−"
    abs_str = fmt_money_compact(abs(v), sym, rate) if compact else fmt_money(abs(v), sym, rate)
    return sign + abs_str


def tv_url(query: str) -> str:
    return f"https://www.tradingview.com/search/?query={urllib.parse.quote(str(query))}"


def safe_sum(df: pd.DataFrame, col: str) -> float:
    return float(df[col].sum()) if col in df.columns else 0.0


# ── Chart base ────────────────────────────────────────────────────────────────

def chart_base(**extra) -> dict:
    """Dark terminal Plotly layout."""
    base = dict(
        paper_bgcolor="rgba(11,18,32,0.0)",
        plot_bgcolor="rgba(11,18,32,0.0)",
        font=dict(color="#CBD5E1", size=11, family="JetBrains Mono, Inter, system-ui"),
        margin=dict(t=30, b=30, l=20, r=20),
        showlegend=False,
        xaxis=dict(
            gridcolor="rgba(148,163,184,0.06)",
            zerolinecolor="rgba(148,163,184,0.10)",
            linecolor="rgba(148,163,184,0.08)",
            tickfont=dict(color="#64748B", size=10, family="JetBrains Mono, monospace"),
        ),
        yaxis=dict(
            gridcolor="rgba(148,163,184,0.06)",
            zerolinecolor="rgba(148,163,184,0.10)",
            linecolor="rgba(148,163,184,0.08)",
            tickfont=dict(color="#64748B", size=10, family="JetBrains Mono, monospace"),
        ),
    )
    base.update(extra)
    return base


def money_formatter(sym: str, usd_rate: float):
    def _fmt(value) -> str:
        return fmt_money(value, sym, usd_rate)
    return _fmt


# ── KPI Card ──────────────────────────────────────────────────────────────────

def kpi_card(
    eyebrow_text: str,
    value: str,
    value_class: str = "",      # "kpi-value--cyan", "--pos", "--neg", "--warn"
    delta_str: str = "",
    delta_class: str = "",      # "pos", "neg", "warn", "cyan"
    badge: str = "",
    badge_class: str = "pill-cyan",
    breakdown: Optional[list] = None,  # list of (label, value) tuples
    jp_label: str = "",
    featured: bool = False,
    glow: bool = False,
    value_suffix: str = "",
) -> str:
    card_cls = "kpi-card"
    if featured: card_cls += " kpi-card--featured"
    if glow:     card_cls += " kpi-card--glow"

    badge_html = ""
    if badge:
        badge_html = f'<span class="pill {badge_class}" style="font-size:10px;padding:2px 7px">{badge}</span>'

    jp_html = f'<div class="kpi-jp">{jp_label}</div>' if jp_label else ""
    suffix_html = f'<span style="font-size:14px;color:#64748B;margin-left:4px;font-weight:400">{value_suffix}</span>' if value_suffix else ""

    delta_html = ""
    if delta_str:
        delta_html = f'<div class="kpi-delta {delta_class}" style="margin-top:4px">{delta_str}</div>'

    breakdown_html = ""
    if breakdown:
        items = "".join(
            f'<div><div class="kpi-breakdown-item-label">{l}</div>'
            f'<div class="kpi-breakdown-item-value">{v}</div></div>'
            for l, v in breakdown
        )
        breakdown_html = f'<div class="kpi-breakdown">{items}</div>'

    value_size = "kpi-value--lg" if featured else ""

    return f"""
<div class="{card_cls}">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:8px">
    <div>
      <div class="kpi-eyebrow">{eyebrow_text}</div>
      {jp_html}
    </div>
    {badge_html}
  </div>
  <div class="kpi-value {value_size} {value_class}">{value}{suffix_html}</div>
  {delta_html}
  {breakdown_html}
</div>
"""


# ── Terminal section header ───────────────────────────────────────────────────

def section_hd(title: str, sub: str = "", eyebrow_text: str = "") -> str:
    ey = f'<div class="eyebrow" style="margin-bottom:4px">{eyebrow_text}</div>' if eyebrow_text else ""
    sb = f'<div class="card-sub">{sub}</div>' if sub else ""
    return f"""
<div class="card-hd">
  <div>
    {ey}
    <div class="card-title font-display">{title}</div>
    {sb}
  </div>
</div>
"""


# ── News ticker ───────────────────────────────────────────────────────────────

def news_ticker(items: list) -> None:
    """Render a scrolling news ticker. items = list of (time, source, text)."""
    news_html = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:8px;font-size:12px">'
        f'<span class="news-item-time">{t}</span>'
        f'<span class="news-item-src">{s.upper()}</span>'
        f'<span class="news-item-text">{txt}</span>'
        f'</span>'
        for t, s, txt in (items + items)  # duplicate for seamless loop
    )
    st.markdown(f"""
<div class="news-ticker-wrap">
  <div style="display:flex;align-items:center;gap:6px;flex-shrink:0">
    <span class="live-dot-red"></span>
    <span style="font-size:10px;font-weight:700;letter-spacing:0.12em;color:#EF4444">LIVE</span>
  </div>
  <div class="news-ticker-scroll">
    <div class="news-ticker-inner" style="gap:40px">{news_html}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── AI Insight card ───────────────────────────────────────────────────────────

def ai_insight_card(kind: str, severity: str, title: str, body: str, action: str) -> str:
    sev_map = {
        "warn": ("warn",   "#F59E0B", "RISK"),
        "ok":   ("ok",     "#06B6D4", "OPPORTUNITY"),
        "info": ("info",   "#3B82F6", "ALERT"),
        "pos":  ("perf",   "#22C55E", "PERFORMANCE"),
    }
    cls, color, badge_label = sev_map.get(severity, ("info", "#3B82F6", "ALERT"))
    return f"""
<div class="ai-card ai-card--{cls}">
  <span class="ai-badge" style="color:{color};border:1px solid {color}40">{badge_label}</span>
  <div class="ai-title">{title}</div>
  <div class="ai-body">{body}</div>
  <div class="ai-action">Action · <span style="color:{color};font-weight:500">{action}</span></div>
</div>
"""


# ── Mini sparkline (pure SVG) ─────────────────────────────────────────────────

def spark_svg(values: list, width: int = 80, height: int = 24,
              color: str = "#06B6D4", stroke: float = 1.5,
              filled: bool = True, glow: bool = True) -> str:
    if not values or len(values) < 2:
        return ""
    mn, mx = min(values), max(values)
    rng = (mx - mn) or 1
    step = width / (len(values) - 1)
    pts = [(i * step, height - ((v - mn) / rng) * (height - 4) - 2) for i, v in enumerate(values)]
    d = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f} {y:.1f}" for i, (x, y) in enumerate(pts))
    fill_d = d + f" L {pts[-1][0]:.1f} {height} L 0 {height} Z"
    glow_filter = f'filter: drop-shadow(0 0 4px {color});' if glow else ""
    fill_part = f'<path d="{fill_d}" fill="{color}" fill-opacity="0.18" />' if filled else ""
    uid = f"sg{abs(hash(str(values[:3]))) % 99999}"
    return (
        f'<svg width="{width}" height="{height}" style="display:block;overflow:visible">'
        f'{fill_part}'
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{stroke}" '
        f'stroke-linejoin="round" stroke-linecap="round" style="{glow_filter}" />'
        f'</svg>'
    )


# ── Mini meter bar ─────────────────────────────────────────────────────────────

def mini_meter(value: float, max_val: float, color: str = "#06B6D4", height: int = 3) -> str:
    pct = min(1.0, max(0.0, value / max_val)) * 100
    return (
        f'<div style="width:100%;height:{height}px;background:rgba(148,163,184,0.10);'
        f'border-radius:{height//2}px;overflow:hidden">'
        f'<div style="width:{pct:.1f}%;height:100%;background:{color};'
        f'box-shadow:0 0 8px {color}"></div>'
        f'</div>'
    )
