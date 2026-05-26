"""Chat tab — LLM-powered portfolio assistant with daily briefing.

Uses the Anthropic API (ANTHROPIC_API_KEY env var). If the key is missing,
shows setup instructions without crashing. Conversation history is maintained
in st.session_state for the duration of the session.
"""
from __future__ import annotations

import datetime
import os
from typing import Callable

import pandas as pd
import streamlit as st

from app.analytics import health as health_mod
from app.analytics import positions as pos_mod
from app.alerts.thresholds import check_all_alerts
from app.analytics import decisions as dec_mod
from app.config import BLUE, CARD, GREEN, MUTED, RED, TEXT, WARN
from app.data import tickers
from app.ui.components import label, section_hd


_SESSION_HIST = "chat_history"
_API_KEY_NAME = "ANTHROPIC_API_KEY"
_MODEL        = "claude-haiku-4-5-20251001"
_MAX_TOKENS   = 500


def _api_key() -> str:
    return os.environ.get(_API_KEY_NAME, "")


def _timestamp() -> str:
    return datetime.datetime.now().strftime("%H:%M")


def _setup_warning() -> None:
    st.markdown(f"""
<div style="background:rgba(245,158,11,0.06);border:1px solid rgba(245,158,11,0.30);
            border-radius:10px;padding:20px;max-width:600px;margin:20px auto">
  <div style="font-size:14px;font-weight:600;color:#F59E0B;margin-bottom:10px">
    🔑 Anthropic API Key Required
  </div>
  <div style="font-size:12.5px;color:#CBD5E1;line-height:1.6">
    The chat assistant requires an Anthropic API key.<br><br>
    Set it as an environment variable:<br>
    <code style="background:rgba(0,0,0,0.3);padding:3px 8px;border-radius:4px;
                 font-family:'JetBrains Mono',monospace">ANTHROPIC_API_KEY=sk-ant-...</code><br><br>
    On Streamlit Cloud: add it in <strong>App Settings → Secrets</strong>.<br>
    Locally: export it in your shell or add to a <code>.env</code> file.
  </div>
</div>
""", unsafe_allow_html=True)


def _build_system_prompt(
    health: health_mod.HealthReport,
    positions: pd.DataFrame,
    alerts: list[dict],
    recommendations: list[dict],
) -> str:
    try:
        from app.agents.report_writer import build_chat_context
        return build_chat_context(health, positions, alerts, recommendations)
    except Exception:
        kpis = pos_mod.portfolio_kpis(positions)
        grade, _ = health_mod.score_grade(health.overall)
        top_rec = recommendations[0]["reason"] if recommendations else "No strong signals."
        return (
            f"You are a portfolio analyst. Portfolio: ¥{kpis['market_value']:,.0f}, "
            f"health {health.overall:.0f}/100 (Grade {grade}), "
            f"{len(alerts)} alerts. Top rec: {top_rec}. "
            f"Answer questions about this specific portfolio. Be concise."
        )


def _call_api(system: str, messages: list[dict]) -> str:
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=_api_key())
        response = client.messages.create(
            model=_MODEL,
            max_tokens=_MAX_TOKENS,
            system=system,
            messages=messages,
        )
        return response.content[0].text.strip()
    except Exception as exc:
        return f"⚠️ API error: {exc}"


def _render_message(role: str, content: str, ts: str) -> None:
    is_user = role == "user"
    align   = "flex-end" if is_user else "flex-start"
    bg      = "rgba(59,130,246,0.10)" if is_user else "var(--surface)"
    border  = "rgba(59,130,246,0.25)" if is_user else "var(--border)"
    name    = "You" if is_user else "Atlas AI"
    avatar  = "👤" if is_user else "🤖"

    st.markdown(
        f'<div style="display:flex;flex-direction:column;align-items:{align};margin-bottom:12px">'
        f'<div style="background:{bg};border:1px solid {border};border-radius:12px;'
        f'padding:12px 16px;max-width:75%">'
        f'<div class="eyebrow" style="margin-bottom:5px">{avatar} {name} · {ts}</div>'
        f'<div style="font-size:13px;color:var(--text);line-height:1.6">{content}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def render(ps: pd.DataFrame, th: pd.DataFrame, money: Callable) -> None:
    if _SESSION_HIST not in st.session_state:
        st.session_state[_SESSION_HIST] = []

    # ── Check API key ─────────────────────────────────────────────────────────
    if not _api_key():
        _setup_warning()
        st.markdown("---")

    # ── Load data ─────────────────────────────────────────────────────────────
    ticker_map = tickers.all_mappings()
    positions = pd.DataFrame()
    health_report = None
    alerts: list[dict] = []
    recommendations: list[dict] = []

    if ticker_map:
        with st.spinner("Loading portfolio context…"):
            positions = pos_mod.build_positions(ps, th, ticker_map)
        if not positions.empty:
            health_report = health_mod.evaluate(positions)
            alerts        = check_all_alerts(positions, health_report)
            recommendations = dec_mod.get_recommendations(positions, health_report)
    else:
        st.info("💡 Map tickers in the **Tickers** tab to unlock portfolio-aware responses.")

    # ── Morning briefing button ───────────────────────────────────────────────
    st.markdown(section_hd("Daily Briefing", "AI-generated portfolio morning report", "Briefing"), unsafe_allow_html=True)
    col_brief, col_status = st.columns([2, 3])
    with col_brief:
        gen_briefing = st.button("📋 Generate Morning Briefing", use_container_width=True)

    if gen_briefing and health_report is not None:
        with st.spinner("Generating briefing…"):
            try:
                from app.agents.report_writer import generate_daily_briefing, get_today_report
                existing = get_today_report()
                if existing:
                    briefing = existing
                else:
                    briefing = generate_daily_briefing(
                        health_report, positions, alerts, recommendations, {}
                    )
                st.session_state[_SESSION_HIST].append(
                    {"role": "assistant", "content": briefing, "ts": _timestamp()}
                )
            except Exception as exc:
                st.error(f"Briefing error: {exc}")
    elif gen_briefing:
        st.warning("Map tickers first to generate a briefing.")

    # Show link to today's saved report
    try:
        from app.agents.report_writer import get_today_report
        if get_today_report():
            st.caption(f"✅ Today's briefing has been generated and saved.")
    except Exception:
        pass

    st.markdown("---")

    # ── Context snapshot ──────────────────────────────────────────────────────
    if health_report is not None:
        grade, _ = health_mod.score_grade(health_report.overall)
        kpis = pos_mod.portfolio_kpis(positions)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Portfolio Value", money(kpis["market_value"]))
        c2.metric("Health Score",    f"{health_report.overall:.0f}/100 ({grade})")
        c3.metric("Active Alerts",   f"{len(alerts)}")
        c4.metric("Signals",         f"{len([r for r in recommendations if r['action'] != 'HOLD'])}")
        st.markdown("---")

    # ── Chat history ──────────────────────────────────────────────────────────
    st.markdown(section_hd("Portfolio Assistant", "Ask anything about your holdings", "Chat"), unsafe_allow_html=True)

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state[_SESSION_HIST]:
            _render_message(msg["role"], msg["content"], msg.get("ts", ""))

    # ── Input ─────────────────────────────────────────────────────────────────
    user_input = st.chat_input(
        "Ask about your portfolio… (e.g. 'What's my biggest risk?' 'Should I trim SoftBank?')"
    )

    if user_input:
        ts = _timestamp()
        st.session_state[_SESSION_HIST].append(
            {"role": "user", "content": user_input, "ts": ts}
        )

        if not _api_key():
            reply = (
                "⚠️ API key not set. Add `ANTHROPIC_API_KEY` to your environment "
                "to enable the chat assistant."
            )
        elif health_report is None:
            reply = (
                "I don't have live portfolio data yet. "
                "Please map your tickers in the Tickers tab first."
            )
        else:
            system = _build_system_prompt(health_report, positions, alerts, recommendations)
            api_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state[_SESSION_HIST]
                if m["role"] in ("user", "assistant")
            ]
            with st.spinner("Thinking…"):
                reply = _call_api(system, api_messages)

        st.session_state[_SESSION_HIST].append(
            {"role": "assistant", "content": reply, "ts": _timestamp()}
        )
        st.rerun()

    # ── Clear button ──────────────────────────────────────────────────────────
    if st.session_state[_SESSION_HIST]:
        if st.button("🗑 Clear conversation", key="chat_clear"):
            st.session_state[_SESSION_HIST] = []
            st.rerun()
