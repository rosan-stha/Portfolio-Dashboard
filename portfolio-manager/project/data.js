// Mock portfolio data — realistic Japanese equities portfolio
// Values in JPY

window.PORTFOLIO_DATA = (() => {
  const holdings = [
    { code: "7203", name: "トヨタ自動車",       en: "Toyota Motor",         sector: "Auto",        shares: 320, avg: 2415, last: 3128, day: 0.018,  account: "growth",   yield: 0.029 },
    { code: "6758", name: "ソニーグループ",     en: "Sony Group",           sector: "Tech",        shares: 110, avg: 11420, last: 14650, day: -0.006, account: "growth",   yield: 0.006 },
    { code: "6861", name: "キーエンス",         en: "Keyence",              sector: "Industrial",  shares: 12,  avg: 58200, last: 64800, day: 0.024,  account: "growth",   yield: 0.005 },
    { code: "9984", name: "ソフトバンクG",      en: "SoftBank Group",       sector: "Tech",        shares: 95,  avg: 6240, last: 9418,  day: 0.041,  account: "tokutei",  yield: 0.005 },
    { code: "8058", name: "三菱商事",           en: "Mitsubishi Corp",      sector: "Trading",     shares: 240, avg: 2380, last: 3192,  day: -0.012, account: "tokutei",  yield: 0.034 },
    { code: "9433", name: "KDDI",               en: "KDDI",                 sector: "Telecom",     shares: 180, avg: 4180, last: 4985,  day: 0.003,  account: "tsumitate",yield: 0.030 },
    { code: "8306", name: "三菱UFJ FG",         en: "Mitsubishi UFJ",       sector: "Financial",   shares: 520, avg: 1190, last: 1862,  day: 0.022,  account: "growth",   yield: 0.027 },
    { code: "4063", name: "信越化学工業",       en: "Shin-Etsu Chemical",   sector: "Materials",   shares: 80,  avg: 5210, last: 6498,  day: -0.009, account: "growth",   yield: 0.018 },
    { code: "7974", name: "任天堂",             en: "Nintendo",             sector: "Tech",        shares: 38,  avg: 7180, last: 8245,  day: 0.011,  account: "tokutei",  yield: 0.022 },
    { code: "8035", name: "東京エレクトロン",   en: "Tokyo Electron",       sector: "Tech",        shares: 28,  avg: 24800, last: 31650, day: 0.032,  account: "growth",   yield: 0.018 },
    { code: "6098", name: "リクルートHD",       en: "Recruit Holdings",     sector: "Services",    shares: 95,  avg: 6420, last: 9890,  day: 0.014,  account: "tsumitate",yield: 0.005 },
    { code: "4502", name: "武田薬品工業",       en: "Takeda Pharmaceutical",sector: "Healthcare",  shares: 210, avg: 4180, last: 4426,  day: -0.004, account: "tokutei",  yield: 0.043 },
    { code: "8316", name: "三井住友FG",         en: "SMFG",                 sector: "Financial",   shares: 180, avg: 5840, last: 9285,  day: 0.018,  account: "growth",   yield: 0.029 },
    { code: "9434", name: "ソフトバンク",       en: "SoftBank Corp",        sector: "Telecom",     shares: 420, avg: 1620, last: 2018,  day: -0.002, account: "tsumitate",yield: 0.043 },
  ];

  // Derived fields
  for (const h of holdings) {
    h.cost      = h.shares * h.avg;
    h.mv        = h.shares * h.last;
    h.pnl       = h.mv - h.cost;
    h.pnlPct    = h.pnl / h.cost;
    h.dayPnl    = h.mv * h.day;
    h.divAnnual = h.mv * h.yield;
  }

  const total_mv   = holdings.reduce((s,h)=>s+h.mv, 0);
  const total_cost = holdings.reduce((s,h)=>s+h.cost, 0);
  const total_day  = holdings.reduce((s,h)=>s+h.dayPnl, 0);
  const total_div_annual = holdings.reduce((s,h)=>s+h.divAnnual, 0);
  const cash       = 384210;

  // Weights
  for (const h of holdings) h.weight = h.mv / total_mv;

  // NISA buckets — Japan 新NISA rules:
  //   つみたて投資枠 ¥1.2M/yr, lifetime ¥18M total (combined w/ growth, growth max ¥12M)
  //   成長投資枠 ¥2.4M/yr
  const nisa = {
    tsumitate: { name: "つみたて投資枠", en: "Tsumitate (DCA)", quotaYear: 1_200_000, quotaLife: 18_000_000, usedYear: 980_000, usedLife: 4_620_000 },
    growth:    { name: "成長投資枠",     en: "Growth",          quotaYear: 2_400_000, quotaLife: 12_000_000, usedYear: 2_180_000, usedLife: 8_240_000 },
    tokutei:   { name: "特定口座",       en: "Taxable (Tokutei)", taxRate: 0.20315 },
    ippan:     { name: "一般口座",       en: "General",         taxRate: 0.20315 },
  };
  for (const k of Object.keys(nisa)) {
    const accountHoldings = holdings.filter(h => h.account === k);
    nisa[k].mv   = accountHoldings.reduce((s,h)=>s+h.mv, 0);
    nisa[k].cost = accountHoldings.reduce((s,h)=>s+h.cost, 0);
    nisa[k].pnl  = nisa[k].mv - nisa[k].cost;
    nisa[k].pct  = nisa[k].cost > 0 ? nisa[k].pnl / nisa[k].cost : 0;
    nisa[k].count = accountHoldings.length;
  }
  // Estimated tax owed on unrealized gains in taxable accounts
  nisa.tokutei.taxOwed = Math.max(0, nisa.tokutei.pnl) * nisa.tokutei.taxRate;

  // Performance series — 252 daily points (1Y). Portfolio vs TOPIX vs Nikkei.
  // Normalize: all start at 100, portfolio outperforms.
  function genSeries(startVal, drift, vol, seed) {
    const out = [];
    let v = startVal;
    let s = seed;
    for (let i = 0; i < 252; i++) {
      // deterministic pseudo-random
      s = (s * 9301 + 49297) % 233280;
      const r = (s / 233280 - 0.5);
      v = v * (1 + drift + r * vol);
      out.push(v);
    }
    return out;
  }
  const portSeries   = genSeries(100, 0.00115, 0.012, 7);   // ~33% YTD
  const topixSeries  = genSeries(100, 0.00055, 0.009, 13);  // ~14% YTD
  const nikkeiSeries = genSeries(100, 0.00072, 0.010, 19);  // ~19% YTD

  // Dates for x-axis (last 252 trading days)
  const dates = [];
  const today = new Date(2026, 4, 25);
  for (let i = 251; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    dates.push(d);
  }

  // Sector aggregation
  const sectorMap = {};
  for (const h of holdings) {
    sectorMap[h.sector] = (sectorMap[h.sector] || 0) + h.mv;
  }
  const sectors = Object.entries(sectorMap)
    .map(([name, mv]) => ({ name, mv, pct: mv / total_mv }))
    .sort((a,b)=>b.mv - a.mv);

  // Upcoming dividends (next 60 days)
  const dividends = [
    { code: "8058", name: "三菱商事",       date: "2026-06-08", perShare: 95,  shares: 240, account: "tokutei" },
    { code: "8306", name: "三菱UFJ FG",     date: "2026-06-15", perShare: 25,  shares: 520, account: "growth" },
    { code: "9433", name: "KDDI",           date: "2026-06-22", perShare: 75,  shares: 180, account: "tsumitate" },
    { code: "4502", name: "武田薬品",       date: "2026-06-30", perShare: 95,  shares: 210, account: "tokutei" },
    { code: "7203", name: "トヨタ自動車",   date: "2026-07-04", perShare: 45,  shares: 320, account: "growth" },
    { code: "8316", name: "三井住友FG",     date: "2026-07-12", perShare: 135, shares: 180, account: "growth" },
  ];
  for (const d of dividends) {
    d.gross = d.perShare * d.shares;
    d.net = d.account === "tsumitate" || d.account === "growth" ? d.gross : d.gross * (1 - 0.20315);
  }

  // Recent activity
  const activity = [
    { type: "buy",  date: "2026-05-23", code: "7203", name: "トヨタ自動車",   shares: 20,  price: 3105, account: "growth" },
    { type: "div",  date: "2026-05-20", code: "9433", name: "KDDI",           amount: 13500, account: "tsumitate" },
    { type: "buy",  date: "2026-05-18", code: "8035", name: "東京エレクトロン", shares: 4,  price: 31250, account: "growth" },
    { type: "sell", date: "2026-05-14", code: "9984", name: "ソフトバンクG",  shares: 15, price: 9320, account: "tokutei", realized: 46200 },
    { type: "div",  date: "2026-05-10", code: "8058", name: "三菱商事",       amount: 18240, account: "tokutei" },
    { type: "buy",  date: "2026-05-06", code: "6098", name: "リクルートHD",   shares: 10, price: 9712, account: "tsumitate" },
  ];

  // Realized P&L YTD + dividend income YTD
  const realizedYtd = 184_320;
  const divYtd      = 142_650;
  const xirr        = 0.286;  // 28.6% money-weighted annualized

  return {
    holdings,
    nisa,
    total_mv, total_cost, total_day, total_div_annual,
    cash,
    portSeries, topixSeries, nikkeiSeries, dates,
    sectors,
    dividends,
    activity,
    realizedYtd, divYtd, xirr,
    asOf: new Date(2026, 4, 25, 14, 32),
  };
})();
