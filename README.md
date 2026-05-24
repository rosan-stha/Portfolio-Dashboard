# 📊 Portfolio Intelligence Platform
### Personal AI-Powered Investment Management System
**Built for:** Foreign investors in Japan · PayPay Securities · Multi-currency  
**Version:** 3.1 · Built with Python + Streamlit + Yahoo Finance

---

## 🎯 What This Is

A personal, institutional-grade portfolio intelligence system that transforms your PayPay Securities transaction history into a full investment analytics platform — with live prices, AI health scoring, risk analysis, and performance tracking.

**Live App:** https://zii-portfolio-dashboard.streamlit.app

---

## ⚡ Quick Start

### 1. Clone or Download the Project
```bash
git clone https://github.com/YOURUSERNAME/portfolio-dashboard.git
cd portfolio-dashboard
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Locally
```bash
streamlit run portfolio.py
```

### 4. Open in Browser
```
http://localhost:8501
```

---

## 📁 Project Structure

```
portfolio-dashboard/
│
├── portfolio.py              # Main entrypoint — run this
├── requirements.txt          # Python dependencies
│
├── app/
│   ├── config.py             # Colors, paths, cache settings
│   │
│   ├── ui/                   # All dashboard tabs
│   │   ├── theme.py          # TradingView dark theme CSS
│   │   ├── components.py     # Shared helpers (labels, charts, formatters)
│   │   ├── tab_overview.py   # Overview tab
│   │   ├── tab_health.py     # Health Score tab
│   │   ├── tab_positions.py  # Live Positions tab
│   │   ├── tab_risk.py       # Risk Exposure tab
│   │   ├── tab_performance.py# Performance tab
│   │   ├── tab_holdings.py   # Holdings table tab
│   │   ├── tab_activity.py   # Transaction History tab
│   │   ├── tab_dividends.py  # Dividend Tracker tab
│   │   └── tab_tickers.py    # Ticker Mapping tab
│   │
│   ├── data/                 # Data fetching layer
│   │   ├── excel_loader.py   # Reads your PayPay Excel file
│   │   ├── market.py         # Yahoo Finance wrapper (cached)
│   │   ├── fx.py             # Live FX rates (USD/EUR/GBP → JPY)
│   │   └── tickers.py        # Company name → ticker symbol store
│   │
│   └── analytics/            # Calculation engine
│       ├── positions.py      # Derives shares + P&L from transactions
│       ├── returns.py        # Portfolio time series reconstruction
│       ├── metrics.py        # Sharpe, Sortino, Beta, VaR, CAGR
│       ├── correlation.py    # Correlation matrix + risk detection
│       ├── relative_strength.py # Multi-period trailing returns
│       └── health.py         # Portfolio Health Score engine
│
└── Files/
    └── tickers.json          # Your saved ticker mappings (auto-created)
```

---

## 📂 How to Upload Your Data

### Step 1 — Export from PayPay Securities
- Open PayPay Securities app
- Go to **残高履歴** (Balance History)
- Save the page as HTML
- Or manually create an Excel file (see format below)

### Step 2 — Prepare Your Excel File
Your Excel must have **exactly 3 sheets** with these names:

**Sheet 1: `Portfolio Summary`**
| Company name | Total Bought (¥) | Total Sold (¥) | Net Invested (¥) | Dividends (¥) | Buy Trades | Last Purchase |
|---|---|---|---|---|---|---|
| Toyota Motor | 120000 | 0 | 120000 | 3600 | 4 | 2025.12.30 |

**Sheet 2: `Transaction History`**
| Date | Transaction Type | Company/Fund | Amount (¥) | Type (EN) |
|---|---|---|---|---|
| 2025.12.30 | 買付 | Toyota Motor | 30000 | Buy |
| 2026.01.15 | 売却 | Sony Group | 15000 | Sell |
| 2026.03.01 | 配当金入金 | Toyota Motor | 900 | Dividend |

**Sheet 3: `Dividend Tracker`**
| Company/Fund | Total Received (¥) |
|---|---|
| Toyota Motor | 3600 |

### Step 3 — Upload in the App
- Open the app
- Find the **Upload Excel File** section in the left sidebar
- Click **Browse files** and select your Excel file
- Dashboard updates automatically

---

## 🏷️ Setting Up Ticker Mapping

This is the most important step for live data features.

### What It Does
Maps your company names (e.g. `Toyota Motor`) to Yahoo Finance ticker symbols (e.g. `7203.T`) so the app can fetch live prices, calculate real P&L, and run analytics.

### How To Do It
1. Go to the **🏷️ Tickers** tab
2. Click **✨ Auto-seed** if using demo data (fills 15 known tickers automatically)
3. For your real holdings — type the ticker symbol next to each company name
4. Click **🔎 Validate All** to confirm each ticker works
5. Mappings are saved automatically to `Files/tickers.json`

### Finding Ticker Symbols
| Market | Format | Example |
|---|---|---|
| Tokyo Stock Exchange | NUMBER.T | 7203.T (Toyota) |
| US Stocks | Plain symbol | AAPL, MSFT, NVDA |
| US ETFs | Plain symbol | SPY, QQQ, VTI |
| Crypto | SYMBOL-USD | BTC-USD, ETH-USD |

**Quick lookup:** Go to https://finance.yahoo.com and search the company name.

---

## 📊 Dashboard Tabs Explained

### 📊 Overview
Your portfolio at a glance.
- Donut chart — allocation by net invested
- Top 20 horizontal bar chart
- Holdings treemap — all positions sized by value
- Monthly buy vs sell volume chart

### 🎯 Health Score
Portfolio health rated 0–100 with letter grade (A/B/C/D/F).

**8 subscores:**
| Subscore | Weight | What It Measures |
|---|---|---|
| Diversification | 15% | How spread across positions |
| Sector Balance | 15% | Spread across industries |
| Concentration | 15% | Size of your biggest position |
| Drawdown | 13% | Worst historical loss |
| Volatility | 12% | Daily price swings |
| Sharpe Ratio | 12% | Return per unit of risk |
| Correlation | 10% | How positions move together |
| Momentum | 8% | % of positions trending up |

**Requires:** Ticker mappings to be set up.

### 💹 Positions
Live portfolio with real-time prices.
- Current price, market value, unrealized P&L per stock
- Today's price change %
- Sector exposure donut
- Top 20 positions by market value
- Full CSV export

**Requires:** Ticker mappings to be set up.

### ⚠️ Risk
Where your hidden risks live.
- Sector / Country / Currency / Market-cap exposure
- Interactive correlation heatmap
- Highly correlated pairs detection
- Diversification warnings

**Requires:** Ticker mappings to be set up.

### 📈 Performance
How your portfolio performed over time.
- Equity curve vs benchmarks (SPY, QQQ, EWJ, BTC, Gold)
- Drawdown chart
- 10 institutional metrics (Sharpe, Sortino, Beta, Alpha, VaR, CAGR, and more)
- Per-position multi-period returns heatmap
- Benchmark comparison table

**Requires:** Ticker mappings to be set up.

### 📋 Holdings
Full table of all positions from your Excel.
- Search by company name
- Filter: All / Top 10 / Top 20 / Dividends Only
- Sort by any column
- TradingView links per company
- Export to CSV

### 📜 Activity
Complete transaction history.
- Filter by type: Buy / Sell / Dividend / All
- Search by company name
- Sort newest or oldest first
- Color coded: Green=Buy, Red=Sell, Gold=Dividend
- Export to CSV

### 💰 Dividends
Income tracking.
- Total dividend income metric
- All payers ranked by highest received
- Share % of total dividend income
- Top 20 bar chart
- Export to CSV

### 🏷️ Tickers
Ticker management system.
- Map company names to Yahoo Finance symbols
- Validate each ticker is working
- Export/Import your mappings as JSON
- Auto-seed for demo companies

---

## 🔧 Configuration

### Cache Settings
Edit `app/config.py`:
```python
CACHE_QUOTE_TTL  = 900    # Live prices refresh every 15 minutes
CACHE_HIST_TTL   = 21600  # History refreshes every 6 hours
CACHE_INFO_TTL   = 86400  # Company info refreshes every 24 hours
```

### Default Currency Rate
```python
DEFAULT_USD_JPY = 150.0   # Change to current rate
```

### Color Theme
All colors defined in `app/config.py`:
```python
BG     = "#131722"   # Page background
CARD   = "#1e2130"   # Cards and tables
GREEN  = "#089981"   # Profit / Buy
RED    = "#f23645"   # Loss / Sell
GOLD   = "#ffc94d"   # Dividends
BLUE   = "#2962ff"   # Links / accent
```

---

## 🚀 Deploying to the Web (Free)

### Step 1 — Push to GitHub
```bash
git add .
git commit -m "your update description"
git push
```

### Step 2 — Streamlit Cloud (already set up)
Your live URL updates automatically within 1-2 minutes after every push.

**Live URL:** https://zii-portfolio-dashboard.streamlit.app

### Ticker Mappings on Cloud
Streamlit Cloud does not save files between sessions. To keep your ticker mappings:
1. Set them up locally
2. Go to 🏷️ Tickers tab → **Export JSON**
3. Save the file as `Files/tickers.json` in your project folder
4. Push to GitHub — mappings will load automatically on the cloud

---

## 📦 Dependencies

```
streamlit>=1.32       # Dashboard framework
pandas>=2.0           # Data manipulation
numpy>=1.24           # Numerical computing
plotly>=5.18          # Interactive charts
openpyxl>=3.1         # Excel file reading
yfinance>=0.2.40      # Live market data
```

Install all:
```bash
pip install -r requirements.txt
```

---

## 🗺️ Roadmap

### ✅ Phase 1 — Foundation (Complete)
- Modular architecture
- Excel data loader
- Live prices via Yahoo Finance
- FX currency conversion
- Positions tab with real P&L
- Ticker mapping system

### ✅ Phase 2 — Intelligence Core (Complete)
- Portfolio Health Score (0-100)
- Correlation heatmap
- Risk exposure dashboard
- Performance vs benchmarks
- Institutional metrics (Sharpe, Sortino, Beta, VaR)

### 🔄 Phase 3 — Decision Tools (Next)
- What-If Simulator
- Rebalancing Engine
- Watchlist Intelligence
- AI Buy Recommendation Engine

### 📅 Phase 4 — AI Layer (Planned)
- LLM Chat Assistant ("Is my portfolio too risky?")
- AI-generated daily insights
- Market regime detection
- Trade journal with pattern analysis
- Strategy backtesting engine

### 📅 Phase 5 — Automation (Future)
- Auto-trading bot integration
- Broker API connections (IBKR, kabu.com)
- Telegram/email alerts
- Scheduled rebalancing

---

## ⚠️ Important Notes

- **Not financial advice.** This tool is for personal tracking and analysis only.
- **Data privacy.** Your portfolio data stays on your machine and your GitHub account. Nothing is sent to any third-party server except Yahoo Finance for market prices.
- **Accuracy.** Share counts are derived by dividing ¥ amounts by historical closing prices. This gives ±1-2% accuracy. For exact share counts, add them manually to your Excel.
- **PayPay Securities limitation.** PayPay does not have a public API or CSV export. Data must be manually exported or entered.

---

## 🛠️ Troubleshooting

### App won't start
```bash
pip install -r requirements.txt
streamlit run portfolio.py
```

### `showlegend` error
Open `app/ui/components.py` — change `chart_base()` to use `base.update(extra)` instead of `**extra` in the return dict.

### Ticker not found
- Check the ticker symbol on https://finance.yahoo.com
- Japanese stocks need `.T` suffix (e.g. `7203.T`)
- Try the full symbol including exchange

### No live data showing
- Make sure you have set up ticker mappings in the 🏷️ Tickers tab
- Click **🔎 Validate All** to confirm connections

### Data looks wrong
- Check your Excel has exactly 3 sheets named correctly
- Column names must match exactly (see Upload section above)
- Amounts must be numbers, not text with ¥ symbols

---

## 📬 Contact & Updates

Built by: You  
Stack: Python · Streamlit · Yahoo Finance · Plotly  
Deployed: Streamlit Cloud (free)

---

*Portfolio Intelligence Platform v3.1 · Not financial advice*
