# 📋 BUILD PROMPT — Stock Analysis Module (Qualtrim-style)
## For: Portfolio Intelligence Platform v3.1 (Streamlit)

---

## CONTEXT

You are adding a new **"🔍 Stock Analysis"** tab to an existing Streamlit portfolio dashboard.

**Existing project structure:**
```
portfolio-dashboard/
├── portfolio.py              ← main entrypoint
├── app/
│   ├── config.py             ← colors, cache, paths
│   ├── ui/
│   │   ├── theme.py          ← TradingView dark CSS
│   │   ├── components.py     ← shared helpers
│   │   └── tab_*.py          ← existing tabs
│   ├── data/
│   │   ├── market.py         ← yfinance wrapper (cached)
│   │   ├── fx.py             ← FX rates
│   │   └── tickers.py        ← ticker store
│   └── analytics/
│       └── metrics.py        ← Sharpe, Sortino, Beta, etc.
```

**Existing color theme (from config.py):**
```python
BG    = "#131722"
CARD  = "#1e2130"
GREEN = "#089981"
RED   = "#f23645"
GOLD  = "#ffc94d"
BLUE  = "#2962ff"
```

---

## TASK

Create **`app/ui/tab_analysis.py`** — a full stock research page, and integrate it into `portfolio.py`.

Also update **`app/data/market.py`** with new data-fetching functions needed by this tab.

---

## FEATURES TO BUILD (all 7 sections)

### 1. STOCK SEARCH HEADER
- Text input: user types a ticker (e.g. `AAPL`, `7203.T`, `NVDA`)
- On submit: load all data for that ticker using `yfinance`
- Show a compact header bar with:
  - Company name + ticker + exchange badge
  - Current price (large, colored green/red vs prev close)
  - Price change $ and % today
  - Market cap, P/E ratio, P/FCF ratio, EV/EBITDA
  - 52-week high / low with a mini progress bar showing current price position
  - Sector + Industry tags

---

### 2. TRADINGVIEW PRICE CHART (embedded widget)
- Embed TradingView chart using `st.components.v1.html()`
- Use the TradingView **Advanced Chart Widget** (free, no API key)
- Widget config:
  - Dark theme (`#131722` background, matching app)
  - Show volume bars
  - Default interval: `1D`
  - Interval buttons: 1D, 1W, 1M, 3M, 1Y, 5Y
  - Width: 100%, Height: 500px
  - Hide top toolbar ads
- The widget auto-resolves the ticker symbol (AAPL works, for Japanese stocks pass `TSE:7203`)
- Add a helper function `to_tradingview_symbol(ticker: str) -> str`:
  - `7203.T` → `TSE:7203`
  - `AAPL` → `NASDAQ:AAPL` (use yfinance `.info["exchange"]` to get exchange)
  - fallback: return ticker as-is

---

### 3. FINANCIALS TAB GROUP
Use `st.tabs(["Revenue", "Earnings", "Cash Flow", "Margins", "Balance Sheet"])` inside the analysis page.

Pull data using `yfinance` `Ticker.financials`, `Ticker.quarterly_financials`, `Ticker.balance_sheet`, `Ticker.cashflow`.

For each chart use **Plotly bar charts** styled with the existing dark theme.
Add annual/quarterly toggle (`st.radio`) above the charts.

#### 3a. Revenue Tab
- **Total Revenue** — annual bar chart, 10 years, bars colored BLUE
- **Revenue YoY Growth %** — line overlay on secondary axis, colored GREEN/RED
- Label each bar with the value (in B/M with suffix)

#### 3b. Earnings Tab
- **EPS (diluted)** — annual bar chart, 10 years
- **Net Income** — bar chart
- **EPS YoY Growth %** — line overlay
- Color bars: GREEN if positive EPS, RED if negative

#### 3c. Cash Flow Tab — THIS IS THE MOST IMPORTANT CHART
- **Free Cash Flow** bar chart (Operating CF minus CapEx), colored GREEN/RED
- **Stock-Based Compensation** overlaid as an orange line (SBC is a real cost, show it clearly)
- **FCF after SBC** = FCF - SBC, shown as a separate bar series (dimmer color)
- **CapEx** shown separately below
- This is Qualtrim's signature feature — make it visually clear

#### 3d. Margins Tab
- Gross Margin % — line chart
- Operating Margin % — line chart  
- Net Margin % — line chart
- FCF Margin % — line chart
- All on same chart, different colors, with legend

#### 3e. Balance Sheet Tab
- Total Assets vs Total Liabilities — grouped bar
- Total Debt — bar chart
- Cash & Equivalents — bar chart
- Debt/Equity ratio — line chart

---

### 4. VALUATION CHARTS TAB GROUP
Use `st.tabs(["P/E History", "P/FCF History", "EV/EBITDA", "DCF Calculator"])`

For historical ratio charts:
- Pull 5 years of monthly price history using `yfinance`
- Pull annual EPS, FCF/share, EBITDA from financials
- Calculate rolling P/E = Price / TTM EPS (interpolate annual to monthly)
- Plot as area chart with colored zones:
  - Red zone: top 20% (expensive)
  - Green zone: bottom 20% (cheap)
  - Gray zone: middle (fair)
- Add a horizontal line for current ratio

---

### 5. DCF CALCULATOR (Advanced)
This is a key feature. Build a fully interactive DCF model.

**Inputs (use `st.columns` + `st.number_input` / `st.slider`):**

| Input | Default | Source |
|-------|---------|--------|
| Current FCF/Share | auto-pulled from yfinance | editable |
| Revenue Growth Rate Yr 1-5 | 15% | slider 0-50% |
| Revenue Growth Rate Yr 6-10 | 8% | slider 0-30% |
| FCF Margin % | auto from last year | slider 0-50% |
| Terminal Growth Rate | 3% | slider 0-5% |
| Discount Rate (WACC) | 10% | slider 5-20% |
| Shares Outstanding | auto | editable |
| Net Cash / (Debt) | auto | editable |

**Model logic:**
```python
def calculate_dcf(fcf_per_share, growth_1_5, growth_6_10, terminal_growth, 
                   discount_rate, years=10):
    projections = []
    fcf = fcf_per_share
    for yr in range(1, 11):
        growth = growth_1_5 if yr <= 5 else growth_6_10
        fcf = fcf * (1 + growth)
        pv = fcf / ((1 + discount_rate) ** yr)
        projections.append({"year": f"Year {yr}", "fcf": fcf, "pv": pv})
    
    terminal_value = (projections[-1]["fcf"] * (1 + terminal_growth)) / (discount_rate - terminal_growth)
    terminal_pv = terminal_value / ((1 + discount_rate) ** 10)
    
    intrinsic_value = sum(p["pv"] for p in projections) + terminal_pv
    intrinsic_value_per_share = intrinsic_value + net_cash_per_share
    
    margin_of_safety = (intrinsic_value_per_share - current_price) / current_price * 100
    return projections, intrinsic_value_per_share, terminal_pv, margin_of_safety
```

**Output display:**
- Large metric: **Intrinsic Value per Share** vs **Current Price**
- Color-coded: GREEN if undervalued, RED if overvalued
- **Margin of Safety %** shown as big badge
- Bar chart: Year 1-10 projected FCF (blue bars) + PV of each year (orange line)
- Terminal value as % of total value (pie or stat)
- Table: Year | Projected FCF | Present Value | Cumulative PV

**Sensitivity table** (like a Bloomberg grid):
- Rows: Discount Rate (8%, 9%, 10%, 11%, 12%)
- Columns: Terminal Growth (2%, 2.5%, 3%, 3.5%, 4%)
- Cells: Intrinsic Value
- Highlight the cell matching current inputs in GOLD

---

### 6. DIVIDEND TRACKER
Only show this section if the stock pays dividends (`yfinance` `.dividends` is not empty).

- **Dividend history** — bar chart of annual dividend per share (10 years), colored GOLD
- **Dividend Yield history** — line chart (annual yield %)
- **Payout Ratio** — line chart (dividends / EPS)
- Key metrics strip: Current Yield | 5Y Avg Yield | Consecutive Years of Growth | Annual DPS
- **Projected future dividends** — extend the trend for 5 years using simple linear regression on DPS growth rate (clearly label as "projection, not guaranteed")

---

### 7. WATCHLIST
- Persistent watchlist stored in `Files/watchlist.json`
- "➕ Add to Watchlist" button on the stock page
- Watchlist tab shows a comparison table:

| Ticker | Price | Change% | P/E | P/FCF | Rev Growth | FCF Growth | Div Yield |
|--------|-------|---------|-----|-------|------------|------------|-----------|

- Each row: green/red color for change%, clickable ticker loads that stock
- "🗑️ Remove" button per row
- Sort by any column

---

## DATA LAYER — new functions for `app/data/market.py`

Add these cached functions:

```python
@st.cache_data(ttl=86400)  # 24hr cache for financials
def get_financials(ticker: str) -> dict:
    """Returns annual + quarterly financials, cashflow, balance sheet"""
    t = yf.Ticker(ticker)
    return {
        "info": t.info,
        "financials_annual": t.financials,
        "financials_quarterly": t.quarterly_financials,
        "cashflow_annual": t.cashflow,
        "cashflow_quarterly": t.quarterly_cashflow,
        "balance_sheet": t.balance_sheet,
        "dividends": t.dividends,
        "history_5y": t.history(period="5y", interval="1mo"),
    }

@st.cache_data(ttl=900)  # 15min cache for price
def get_quote(ticker: str) -> dict:
    """Returns current price + key stats"""
    t = yf.Ticker(ticker)
    info = t.info
    hist = t.history(period="2d")
    return {
        "price": hist["Close"].iloc[-1],
        "prev_close": hist["Close"].iloc[-2],
        "change": hist["Close"].iloc[-1] - hist["Close"].iloc[-2],
        "change_pct": (hist["Close"].iloc[-1] / hist["Close"].iloc[-2] - 1) * 100,
        "market_cap": info.get("marketCap"),
        "pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "ev_ebitda": info.get("enterpriseToEbitda"),
        "week52_high": info.get("fiftyTwoWeekHigh"),
        "week52_low": info.get("fiftyTwoWeekLow"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "exchange": info.get("exchange"),
        "short_name": info.get("shortName"),
        "shares_outstanding": info.get("sharesOutstanding"),
        "total_cash": info.get("totalCash"),
        "total_debt": info.get("totalDebt"),
    }
```

---

## INTEGRATION — `portfolio.py`

Add to the tabs list:
```python
from app.ui.tab_analysis import render_analysis_tab

# In the st.tabs([...]) list, add:
"🔍 Analysis"

# In the tab rendering section, add:
with tab_analysis:
    render_analysis_tab()
```

---

## STYLING RULES

- All charts must use the existing dark theme: `BG = "#131722"`, `CARD = "#1e2130"`
- Use `chart_base()` from `components.py` as the base for all Plotly figures
- Font: match existing app (no new fonts)
- Bar chart bar width: 0.6
- Add `hovertemplate` to all charts — show formatted values (e.g., `$1.23B`)
- Charts height: 350px for standard, 450px for the DCF model chart
- All number formatting:
  - Billions: `$1.23B`
  - Millions: `$234M`
  - Percentages: `12.3%`
  - Per share: `$3.45`
- Use `st.metric()` for key stats with delta colors
- Empty state: if data unavailable, show `st.info("Data not available for this ticker")` — never crash

---

## ERROR HANDLING

- Wrap all `yfinance` calls in try/except
- If a financial statement row is missing (e.g., no SBC data), skip that series gracefully
- Japanese stocks (`.T` suffix): some yfinance fields return None — handle all None cases
- If `cashflow["Stock Based Compensation"]` doesn't exist, set SBC = 0
- Show `st.warning()` if ticker not found

---

## FILE OUTPUTS

Create these files:
1. `app/ui/tab_analysis.py` — main tab (all 7 sections)
2. Update `app/data/market.py` — add the 2 new cached functions
3. Update `portfolio.py` — add the new tab
4. `Files/watchlist.json` — empty init file `[]`

---

## QUALITY BAR

The finished tab should feel like a **professional research terminal**, not a student project. Every chart needs:
- Proper axis labels
- Value labels on bars
- Hover tooltips
- Clean legend
- Consistent color language (GREEN = good/positive, RED = bad/negative, GOLD = dividends, BLUE = revenue/neutral)

The DCF calculator in particular must be **interactive in real-time** — every slider change immediately recalculates and re-renders all outputs without a page reload (use `st.session_state` if needed).

---

*End of build prompt. Copy everything above this line into a new Claude conversation with your codebase attached.*
