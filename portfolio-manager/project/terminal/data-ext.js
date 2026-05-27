// Extended data for the Terminal — Sharpe, win rate, risk score, watchlist,
// market indices, correlations, AI insights, equity curve in JPY.

window.TERMINAL_DATA = (() => {
  const base = window.PORTFOLIO_DATA;

  // Equity curve in JPY (vs cost baseline). Total cost ≈ 9.87M, current MV ≈ 13.0M.
  const totalCost = base.total_cost;
  // Reuse portSeries (rebased) but in JPY
  const equity = base.portSeries.map(v => totalCost * (v / 100));

  // Realized vs unrealized split by month (6 months)
  const months = ["Dec", "Jan", "Feb", "Mar", "Apr", "May"];
  const monthlyPnL = [
    { m: "Dec '25", realized:  42_500, unrealized: 184_200, dividends: 28_400 },
    { m: "Jan '26", realized:  28_300, unrealized: 268_400, dividends: 14_800 },
    { m: "Feb '26", realized: -12_400, unrealized: -98_200, dividends: 31_200 },
    { m: "Mar '26", realized:  86_400, unrealized: 412_800, dividends: 22_600 },
    { m: "Apr '26", realized:  18_200, unrealized: 326_500, dividends: 18_900 },
    { m: "May '26", realized:  21_320, unrealized: 248_300, dividends: 26_750 },
  ];

  // Risk metrics
  const risk = {
    sharpe:   1.84,
    sortino:  2.31,
    maxDD:   -0.082,   // -8.2%
    volAnn:   0.142,   // 14.2% annualized
    beta:     0.86,    // vs TOPIX
    alpha:    0.092,   // 9.2% annualized
    var95:   -0.027,   // 1-day 95% VaR
    riskScore: 42,     // 0..100
    riskLabel: "Moderate",
    winRate:  0.682,
    avgWin:   0.038,
    avgLoss: -0.021,
    profitFactor: 2.42,
  };

  // Risk decomposition (variance contribution by holding) — top 6
  const riskDecomp = [...base.holdings]
    .sort((a, b) => b.mv - a.mv)
    .slice(0, 6)
    .map(h => {
      // synthetic vol: tech > others
      const sectorVol = { "Tech": 0.32, "Financial": 0.18, "Auto": 0.22, "Industrial": 0.20, "Trading": 0.22, "Telecom": 0.15, "Materials": 0.24, "Healthcare": 0.19, "Services": 0.20 }[h.sector] || 0.20;
      return { code: h.code, name: h.name, en: h.en, sector: h.sector, weight: h.weight, vol: sectorVol, contrib: h.weight * sectorVol };
    });
  const totalContrib = riskDecomp.reduce((s, r) => s + r.contrib, 0);
  for (const r of riskDecomp) r.pct = r.contrib / totalContrib;

  // Watchlist — not held, tracking
  const watchlist = [
    { code: "6920", name: "レーザーテック",        en: "Lasertec",            last: 24_350, day:  0.028, vol: 1_842_300, alert: "above 200MA" },
    { code: "9988", name: "アリババ ADR",          en: "Alibaba ADR",          last: 12_840, day: -0.012, vol:   428_900, alert: null },
    { code: "4661", name: "オリエンタルランド",     en: "Oriental Land",        last: 4_186,  day:  0.041, vol: 2_148_700, alert: "RSI overbought" },
    { code: "9101", name: "日本郵船",              en: "NYK Line",             last: 5_028,  day:  0.018, vol:   892_400, alert: null },
    { code: "8001", name: "伊藤忠商事",            en: "Itochu",               last: 7_492,  day:  0.006, vol:   612_300, alert: null },
    { code: "7741", name: "HOYA",                  en: "Hoya",                 last: 18_420, day: -0.022, vol:   315_800, alert: "−5% from peak" },
  ];

  // Market overview — indices/FX
  const market = [
    { code: "TOPIX",       name: "TOPIX",          last: 2_842.18, day:  0.0042, region: "JP" },
    { code: "NKY",         name: "Nikkei 225",     last: 39_218.4, day:  0.0061, region: "JP" },
    { code: "MOTHERS",     name: "Mothers",        last:   742.31, day: -0.0083, region: "JP" },
    { code: "SPX",         name: "S&P 500",        last: 5_842.12, day:  0.0029, region: "US" },
    { code: "USDJPY",      name: "USD/JPY",        last:   156.42, day: -0.0018, region: "FX" },
    { code: "VIX",         name: "VIX",            last:    14.82, day:  0.0210, region: "US" },
    { code: "JP10Y",       name: "JGB 10Y",        last:     1.428, day:  0.0140, region: "Rate", unit: "%" },
    { code: "GOLD",        name: "Gold (¥/g)",     last: 14_852,    day:  0.0034, region: "Comm" },
  ];

  // Tiny sparklines for market items (deterministic)
  function genSpark(seed, drift = 0) {
    const out = []; let s = seed; let v = 100;
    for (let i = 0; i < 24; i++) {
      s = (s * 9301 + 49297) % 233280;
      const r = (s / 233280 - 0.5);
      v *= 1 + drift + r * 0.012;
      out.push(v);
    }
    return out;
  }
  for (let i = 0; i < market.length; i++) market[i].spark = genSpark(i * 17 + 3, market[i].day * 0.05);
  for (let i = 0; i < watchlist.length; i++) watchlist[i].spark = genSpark(i * 23 + 11, watchlist[i].day * 0.04);

  // Correlation matrix — top 8 holdings
  const corrSyms = [...base.holdings].sort((a,b)=>b.mv-a.mv).slice(0, 8);
  // Deterministic synthetic correlations based on sector similarity
  function corr(a, b) {
    if (a.code === b.code) return 1.0;
    const sameSector = a.sector === b.sector;
    const sameTheme = (a.sector === "Tech" && b.sector === "Tech") || (a.sector === "Financial" && b.sector === "Financial");
    // hash-based jitter
    const h = ((a.code.charCodeAt(0) + b.code.charCodeAt(1)) * 9973) % 1000 / 1000;
    const base = sameSector ? 0.55 : 0.15;
    const themeBoost = sameTheme ? 0.15 : 0;
    return Math.max(-0.4, Math.min(0.95, base + themeBoost + (h - 0.5) * 0.5));
  }
  const corrMatrix = corrSyms.map(a => corrSyms.map(b => corr(a, b)));

  // AI Insights — generated alerts
  const insights = [
    {
      kind: "risk", severity: "warn",
      title: "Tech concentration above target",
      body: "Technology sector now 36.4% of portfolio (target: 30%). Concentration in 4 names — SoftBank G, Sony, Tokyo Electron, Nintendo — drives 78% of YTD return but raises drawdown risk.",
      action: "Trim or hedge",
    },
    {
      kind: "opportunity", severity: "ok",
      title: "NISA growth quota: ¥220K remaining this year",
      body: "Highest-yield holding (Takeda, 4.3%) is in 特定口座 incurring 20.315% tax. Migrating to NISA growth slot would save ¥1,840/yr in withholding.",
      action: "Plan transfer",
    },
    {
      kind: "alert", severity: "info",
      title: "Ex-dividend events within 30 days",
      body: "4 positions go ex-dividend between Jun 8–22, totaling ¥56,940 net. KDDI (Jun 22) is in tsumitate — tax-free.",
      action: "Review calendar",
    },
    {
      kind: "performance", severity: "ok",
      title: "Outperforming TOPIX by 14.2pp YTD",
      body: "Portfolio beta of 0.86 vs TOPIX with alpha of +9.2% annualized. Sharpe 1.84 — top quartile vs Japan-equity mutual funds.",
      action: "View attribution",
    },
  ];

  // News ticker headlines
  const news = [
    { time: "14:28", src: "Nikkei",   text: "BOJ holds rate, signals October normalization path" },
    { time: "13:55", src: "Reuters",  text: "Toyota raises FY guidance on stronger Q4 US sales" },
    { time: "13:12", src: "Bloomberg", text: "Tokyo Electron up 3.2% as ASML deliveries beat" },
    { time: "12:48", src: "Nikkei",   text: "Yen weakens past 156 as US yields climb" },
    { time: "11:30", src: "Reuters",  text: "SoftBank Group to spin out Arm China unit" },
  ];

  return {
    ...base,
    equity,
    monthlyPnL,
    risk,
    riskDecomp,
    watchlist,
    market,
    corrSyms,
    corrMatrix,
    insights,
    news,
  };
})();
