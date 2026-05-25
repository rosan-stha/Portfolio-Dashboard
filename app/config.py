"""Global constants — colour palette, paths, cache TTLs."""
from pathlib import Path

# ── Paths ───────────────────────────────────────────────────────────────────
ROOT_DIR    = Path(__file__).resolve().parent.parent
FILES_DIR   = ROOT_DIR / "Files"
TICKERS_JSON = FILES_DIR / "tickers.json"

# ── Portfolio Intelligence — warm cream / financial-pro palette ──────────────
BG      = "#f5f3ec"   # warm cream page background
BG2     = "#ebe7da"   # slightly darker bg / hover
CARD    = "#ffffff"   # white surface / card background
TEXT    = "#0c0c0c"   # primary text
TEXT2   = "#3d3d36"   # secondary text
MUTED   = "#767168"   # muted / labels
BORDER  = "#e2ddcd"   # warm border
ACCENT  = "#c8102e"   # Japanese flag red — primary accent
GREEN   = "#c8102e"   # gain / buy  (Japan convention: red = up)
RED     = "#1f6e3a"   # loss / sell (Japan convention: green = down)
GOLD    = "#c87f10"   # dividends / warning / amber
BLUE    = "#5b6470"   # neutral chart / benchmark color
NOGRID  = "rgba(0,0,0,0)"

# ── Market-data cache TTLs (seconds) ────────────────────────────────────────
QUOTE_TTL   = 15 * 60         # live quote — 15 minutes
HISTORY_TTL = 6 * 60 * 60     # historical bars — 6 hours
INFO_TTL    = 24 * 60 * 60    # company info / sector — 24 hours

# ── Default FX ──────────────────────────────────────────────────────────────
DEFAULT_USD_JPY = 150.0
