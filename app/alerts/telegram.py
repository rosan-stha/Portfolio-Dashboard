"""Telegram alert sender.

Bot token and chat ID are read from environment variables:
  TELEGRAM_BOT_TOKEN — from BotFather
  TELEGRAM_CHAT_ID   — your personal or group chat ID

All functions return bool indicating success. Failures are logged silently
so a missing Telegram config never crashes the app.
"""
from __future__ import annotations

import os


def _bot_token() -> str:
    return os.environ.get("TELEGRAM_BOT_TOKEN", "")


def _chat_id() -> str:
    return os.environ.get("TELEGRAM_CHAT_ID", "")


def _severity_emoji(severity: str) -> str:
    return {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🔵"}.get(severity.upper(), "⚪")


def _format_alert(alert: dict) -> str:
    emoji = _severity_emoji(alert.get("severity", "LOW"))
    severity = alert.get("severity", "").upper()
    alert_type = alert.get("type", "")
    company = alert.get("company", "")
    message = alert.get("message", "")
    action = alert.get("suggested_action", "")
    ts = alert.get("timestamp", "")
    return (
        f"{emoji} {severity} ALERT — {alert_type}\n"
        f"{company}\n"
        f"{message}\n"
        f"Suggested: {action}\n"
        f"[{ts}]"
    )


def send_alert(alert: dict) -> bool:
    """Send a single formatted alert to Telegram. Returns True if sent."""
    token = _bot_token()
    chat = _chat_id()
    if not token or not chat:
        return False
    try:
        import urllib.request, urllib.parse, json as _json
        text = _format_alert(alert)
        payload = _json.dumps({"chat_id": chat, "text": text}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False


def send_daily_summary(alerts: list[dict], health_score: float) -> bool:
    """Send end-of-day summary with all active alerts and health score."""
    token = _bot_token()
    chat = _chat_id()
    if not token or not chat:
        return False
    try:
        import urllib.request, json as _json
        high = [a for a in alerts if a.get("severity") == "HIGH"]
        mid  = [a for a in alerts if a.get("severity") == "MEDIUM"]
        low  = [a for a in alerts if a.get("severity") == "LOW"]
        lines = [
            f"📊 Daily Portfolio Summary",
            f"Health Score: {health_score:.0f}/100",
            f"",
            f"Alerts: 🔴 {len(high)} HIGH  🟡 {len(mid)} MEDIUM  🔵 {len(low)} LOW",
        ]
        for a in alerts[:5]:
            lines.append(f"\n{_format_alert(a)}")
        if len(alerts) > 5:
            lines.append(f"\n… and {len(alerts) - 5} more alerts.")
        text = "\n".join(lines)
        payload = _json.dumps({"chat_id": chat, "text": text}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False


def test_connection() -> bool:
    """Send a test message to verify the bot config is working."""
    token = _bot_token()
    chat = _chat_id()
    if not token or not chat:
        return False
    try:
        import urllib.request, json as _json
        payload = _json.dumps({"chat_id": chat, "text": "✅ Atlas Terminal — Telegram alerts connected."}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False
