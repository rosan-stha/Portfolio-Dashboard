"""Daily briefing generator and chat context builder.

This is the only module that calls the Anthropic API.
All other agents produce structured data; this one produces words.

Set ANTHROPIC_API_KEY in your environment to enable AI generation.
Falls back to a template-formatted string when the API is unavailable.
"""
from __future__ import annotations

import datetime
import os
from pathlib import Path

import pandas as pd

from app.analytics import health as health_mod
from app.analytics import positions as pos_mod

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
MODEL        = "claude-haiku-4-5-20251001"
MAX_TOKENS   = 500


def _load_template(name: str) -> str:
    path = PROMPTS_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _render_template(template: str, context: dict) -> str:
    """Minimal Jinja2 render with graceful fallback."""
    try:
        from jinja2 import Template
        return Template(template).render(**context)
    except Exception:
        result = template
        for key, val in context.items():
            result = result.replace(f"{{{{ {key} }}}}", str(val))
        return result


def _briefing_context(
    health: health_mod.HealthReport,
    positions: pd.DataFrame,
    alerts: list[dict],
    recommendations: list[dict],
    market: dict,
) -> dict:
    kpis = pos_mod.portfolio_kpis(positions)
    grade, _ = health_mod.score_grade(health.overall)
    top_rec = ""
    if recommendations:
        r = recommendations[0]
        top_rec = f"{r['action']} {r['company']} — {r['reason']}"

    return {
        "user_name":       "Atlas User",
        "date":            datetime.date.today().strftime("%d %b %Y"),
        "total_value_jpy": f"{kpis['market_value']:,.0f}",
        "day_change_jpy":  f"{kpis['day_change']:+,.0f}",
        "day_change_pct":  f"{kpis['day_change_pct'] * 100:+.2f}%",
        "health_score":    f"{health.overall:.0f}",
        "grade":           grade,
        "health_delta":    "",
        "alert_count":     len(alerts),
        "alerts":          alerts,
        "top_recommendation": top_rec or "No strong signals today.",
        "nikkei":          market.get("nikkei", "—"),
        "sp500":           market.get("sp500", "—"),
        "usdjpy":          market.get("usdjpy", "—"),
        "n_positions":     kpis["n_positions"],
    }


def generate_daily_briefing(
    health: health_mod.HealthReport,
    positions: pd.DataFrame,
    alerts: list[dict],
    recommendations: list[dict],
    market: dict,
) -> str:
    """
    Generate a morning briefing. Returns a markdown string.
    Also saves to app/reports/YYYY-MM-DD.md.
    """
    context = _briefing_context(health, positions, alerts, recommendations, market)
    template = _load_template("daily_briefing.j2")
    prompt = _render_template(template, context)

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    content = ""

    if api_key:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.content[0].text.strip()
        except Exception as exc:
            content = f"*AI generation failed: {exc}. Showing template summary.*\n\n"

    if not content:
        # Rule-based fallback
        kpis  = pos_mod.portfolio_kpis(positions)
        grade, descriptor = health_mod.score_grade(health.overall)
        top_alert = alerts[0]["message"] if alerts else "No active alerts."
        top_rec   = context["top_recommendation"]
        content = (
            f"### Morning Briefing — {context['date']}\n\n"
            f"**Portfolio:** ¥{kpis['market_value']:,.0f} · "
            f"Today {kpis['day_change_pct'] * 100:+.2f}%\n\n"
            f"**Health Score:** {health.overall:.0f}/100 — Grade {grade} ({descriptor})\n\n"
            f"**Top Alert:** {top_alert}\n\n"
            f"**Recommendation:** {top_rec}\n\n"
            f"*{len(alerts)} active alert(s). Check the Risk and Decisions tabs for details.*"
        )

    _save_report(content)
    return content


def _save_report(content: str) -> None:
    try:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.date.today().isoformat()
        path  = REPORTS_DIR / f"{today}.md"
        path.write_text(content, encoding="utf-8")
        # Prune reports older than 30 days
        cutoff = datetime.date.today() - datetime.timedelta(days=30)
        for f in REPORTS_DIR.glob("*.md"):
            try:
                file_date = datetime.date.fromisoformat(f.stem)
                if file_date < cutoff:
                    f.unlink()
            except ValueError:
                pass
    except Exception:
        pass


def get_today_report() -> str | None:
    """Return today's saved report text, or None if not yet generated."""
    path = REPORTS_DIR / f"{datetime.date.today().isoformat()}.md"
    return path.read_text(encoding="utf-8") if path.exists() else None


def build_chat_context(
    health: health_mod.HealthReport,
    positions: pd.DataFrame,
    alerts: list[dict],
    recommendations: list[dict],
) -> str:
    """Build the system prompt for the chat assistant."""
    context = _briefing_context(health, positions, alerts, recommendations, {})
    template = _load_template("chat_system.j2")
    return _render_template(template, context)
