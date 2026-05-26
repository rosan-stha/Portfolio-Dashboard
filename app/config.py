"""Global constants — dark terminal palette, paths, cache TTLs."""
from pathlib import Path

# ── Paths ───────────────────────────────────────────────────────────────────
ROOT_DIR     = Path(__file__).resolve().parent.parent
FILES_DIR    = ROOT_DIR / "Files"
TICKERS_JSON = FILES_DIR / "tickers.json"

# ── Portfolio Terminal — dark navy institutional palette ─────────────────────
BG      = "#050816"               # deep dark page background
BG2     = "#0B1220"               # card / surface
BG3     = "#111827"               # secondary surface
CARD    = "#0B1220"               # card background (same as BG2)
TEXT    = "#F8FAFC"               # primary text
TEXT2   = "#CBD5E1"               # secondary text
MUTED   = "#64748B"               # muted / labels
MUTED2  = "#475569"               # very muted
BORDER  = "rgba(148,163,184,0.10)"   # subtle border
BORDER2 = "rgba(148,163,184,0.18)"   # slightly more visible
ACCENT  = "#06B6D4"               # cyan — primary accent
NAVY    = "#1E3A8A"               # navy blue
NAVY2   = "#1E40AF"               # lighter navy
BLUE    = "#3B82F6"               # blue
CYAN    = "#06B6D4"               # cyan (same as ACCENT)
POS     = "#22C55E"               # positive / gain
NEG     = "#EF4444"               # negative / loss
WARN    = "#F59E0B"               # warning / amber
GREEN   = "#22C55E"               # alias for POS
RED     = "#EF4444"               # alias for NEG
GOLD    = "#F59E0B"               # alias for WARN
NOGRID  = "rgba(0,0,0,0)"

# ── Market-data cache TTLs (seconds) ────────────────────────────────────────
QUOTE_TTL   = 15 * 60         # live quote — 15 minutes
HISTORY_TTL = 6 * 60 * 60     # historical bars — 6 hours
INFO_TTL    = 24 * 60 * 60    # company info / sector — 24 hours

# ── Default FX ──────────────────────────────────────────────────────────────
DEFAULT_USD_JPY = 150.0

# ── Alert thresholds (read by risk-monitor and decision-engine) ──────────────
ALERT_THRESHOLDS = {
    "max_position_pct":  0.20,   # Single position > 20% → alert
    "daily_move_pct":    0.05,   # Any holding moves ±5% in a day
    "max_correlation":   0.85,   # Two holdings correlation > 0.85
    "min_health_score":  65,     # Health score drops below 65
    "health_score_drop": 10,     # Health score drops 10+ pts in one session
    "max_sector_pct":    0.35,   # Single sector > 35% of portfolio
    "max_currency_pct":  0.60,   # Single currency > 60% of portfolio
}
