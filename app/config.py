"""Global constants — colour palette, paths, cache TTLs."""
from pathlib import Path

# ── Paths ───────────────────────────────────────────────────────────────────
ROOT_DIR    = Path(__file__).resolve().parent.parent
FILES_DIR   = ROOT_DIR / "Files"
TICKERS_JSON = FILES_DIR / "tickers.json"

# ── TradingView dark theme palette ──────────────────────────────────────────
BG     = "#131722"   # page background
CARD   = "#1e2130"   # metric cards / table-row hover
BORDER = "#2a2e39"   # subtle borders
TEXT   = "#d1d4dc"   # primary text
MUTED  = "#787b86"   # secondary / labels
GREEN  = "#089981"   # profit / buy
RED    = "#f23645"   # loss / sell
GOLD   = "#ffc94d"   # dividends / special
BLUE   = "#2962ff"   # links / accent
NOGRID = "rgba(0,0,0,0)"

# ── Market-data cache TTLs (seconds) ────────────────────────────────────────
QUOTE_TTL   = 15 * 60         # live quote — 15 minutes
HISTORY_TTL = 6 * 60 * 60     # historical bars — 6 hours
INFO_TTL    = 24 * 60 * 60    # company info / sector — 24 hours

# ── Default FX ──────────────────────────────────────────────────────────────
DEFAULT_USD_JPY = 150.0
