# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the app
streamlit run portfolio.py

# Install dependencies
pip install -r requirements.txt
```

No test suite or linter is configured.

## Architecture

**Entry point:** `portfolio.py` — sets up the Streamlit page, sidebar (file upload, currency toggle), loads data, and routes to tab renderers based on `active_page`.

**Data flow:**
1. `app/data/excel_loader.py` — parses a 3-sheet PayPay Securities Excel file (Portfolio Summary, Transaction History, Dividend Tracker) into DataFrames `ps`, `th`, `dt`. Falls back to `make_demo()` when no file is uploaded.
2. `app/data/market.py` — Yahoo Finance wrapper with `@st.cache_data` (TTLs in `app/config.py`).
3. `app/data/tickers.py` — loads/saves company-name → Yahoo Finance ticker mappings from `Files/tickers.json`.
4. `app/data/fx.py` — live FX rates.

**Analytics layer** (`app/analytics/`): stateless functions that receive the DataFrames and return computed results — positions P&L, time-series returns, Sharpe/Sortino/Beta/VaR, correlation matrix, health score.

**UI layer** (`app/ui/`):
- `theme.py` — injects global CSS (dark navy palette) via `st.markdown`.
- `components.py` — shared HTML primitives: `kpi_card`, `ai_insight_card`, `label`, `money_formatter`, `news_ticker`, `chart_base` (Plotly dark theme defaults).
- `tab_*.py` — each exports a single `render(...)` function called from `portfolio.py`.

**Design system** (`app/config.py`): all colors, cache TTLs, and paths are defined here. The palette is dark navy: `BG=#050816`, `ACCENT=#06B6D4` (cyan), `POS=#22C55E`, `NEG=#EF4444`. Always use these constants — never inline raw hex in new code.

**Excel column mapping:** `excel_loader.py` uses `PS_MAP / TH_MAP / DT_MAP` dicts to resolve Japanese and English column name variants to internal keys. Add new aliases here when the Excel schema changes.

**Ticker mappings** persist to `Files/tickers.json` locally; on Streamlit Cloud this file must be committed to the repo (Cloud has no persistent filesystem between sessions).

## Deployment

Live at: https://zii-portfolio-dashboard.streamlit.app  
Streamlit Cloud auto-deploys on push to `main`.
