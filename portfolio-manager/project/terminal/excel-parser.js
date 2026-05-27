// excel-parser.js — PayPay Securities Excel → TERMINAL_DATA
// Reads 3 sheets: Portfolio Summary, Transaction History, Dividend Tracker
// Requires SheetJS (XLSX) to be loaded before this file.

window.parsePayPayExcel = function(workbook) {

  // ── Column aliases (mirrors Python excel_loader.py) ──────────────────────
  const PS_ALIASES = {
    company:       ["Company / Fund Name","Company name","Company Name","Company","銘柄名","銘柄"],
    total_bought:  ["Total Bought (¥)","Total Bought","買付合計","購入合計"],
    total_sold:    ["Total Sold (¥)","Total Sold","売却合計"],
    net_invested:  ["Net Invested (¥)","Net Invested","純投資額"],
    dividends:     ["Dividends / Dist. (¥)","Dividends (¥)","Dividends","配当金"],
    buy_trades:    ["Buy Trades","買付回数"],
    last_purchase: ["Last Purchase","最終購入日"],
  };
  const TH_ALIASES = {
    date:    ["Date","日付","取引日"],
    company: ["Company / Fund","Company/Fund","Company","Company Name","銘柄名"],
    amount:  ["Amount (¥)","Amount","金額"],
    type_en: ["Type (EN)","Type EN","Type_EN","Transaction Type","Type","取引種別"],
  };
  const DT_ALIASES = {
    company:  ["Company / Fund","Company/Fund","Company","Company Name","銘柄名"],
    received: ["Total Received (¥)","Total Received","配当合計"],
  };

  // ── Sheet parser ────────────────────────────────────────────────────────────
  function parseSheet(name, headerRow) {
    const s = workbook.Sheets[name];
    if (!s) return [];
    const all = XLSX.utils.sheet_to_json(s, { header: 1, raw: false, defval: "" });
    if (all.length <= headerRow) return [];
    const hdrs = (all[headerRow] || []).map(h => String(h || "").trim());
    return all.slice(headerRow + 1).map(row => {
      const obj = {};
      hdrs.forEach((h, i) => { if (h) obj[h] = String(row[i] ?? "").trim(); });
      return obj;
    }).filter(r => Object.values(r).some(v => v !== ""));
  }

  function remap(rows, aliases) {
    return rows.map(row => {
      const out = {};
      for (const [key, names] of Object.entries(aliases)) {
        for (const n of names) {
          if (n in row && row[n] !== "") { out[key] = row[n]; break; }
        }
      }
      return out;
    });
  }

  function num(s) { return parseFloat(String(s || "0").replace(/,/g, "")) || 0; }
  function fmtN(n) { return Math.round(n).toLocaleString(); }

  // ── Parse ───────────────────────────────────────────────────────────────────
  const psRaw = remap(parseSheet("Portfolio Summary",   3), PS_ALIASES);
  const thRaw = remap(parseSheet("Transaction History", 1), TH_ALIASES);
  const dtRaw = remap(parseSheet("Dividend Tracker",    1), DT_ALIASES);

  const ps = psRaw
    .filter(r => r.company && !String(r.company).match(/^[▶▼TOTAL合計]/))
    .map(r => ({
      company:       String(r.company || "").trim(),
      total_bought:  num(r.total_bought),
      total_sold:    num(r.total_sold),
      net_invested:  num(r.net_invested),
      dividends:     num(r.dividends),
      buy_trades:    parseInt(String(r.buy_trades || "0").replace(/,/g,"")) || 0,
      last_purchase: r.last_purchase || "",
    }))
    .filter(r => r.company && r.total_bought > 0);

  const th = thRaw
    .filter(r => r.date && r.company)
    .map(r => ({ date: r.date, company: String(r.company||"").trim(), amount: num(r.amount), type_en: String(r.type_en||"").trim() }))
    .filter(r => r.amount > 0);

  const dt = dtRaw
    .filter(r => r.company)
    .map(r => ({ company: String(r.company||"").trim(), received: num(r.received) }))
    .filter(r => r.company && r.received > 0)
    .sort((a, b) => b.received - a.received);

  // ── Aggregates ──────────────────────────────────────────────────────────────
  const total_cost     = ps.reduce((s,r) => s + r.total_bought, 0);
  const total_sold_sum = ps.reduce((s,r) => s + r.total_sold,   0);
  const total_net      = ps.reduce((s,r) => s + r.net_invested, 0);
  const total_divs     = ps.reduce((s,r) => s + r.dividends,    0);
  const total_trades   = ps.reduce((s,r) => s + r.buy_trades,   0);
  const buyTxs         = th.filter(r => r.type_en.toLowerCase().includes("buy")).length;
  const sellTxs        = th.filter(r => r.type_en.toLowerCase().includes("sell")).length;

  // ── Deterministic series generators ────────────────────────────────────────
  function genSpark(seed, drift = 0) {
    const out = []; let s = seed; let v = 100;
    for (let i = 0; i < 30; i++) {
      s = (s * 9301 + 49297) % 233280;
      v *= 1 + drift + (s / 233280 - 0.5) * 0.022;
      out.push(v);
    }
    return out;
  }
  function genSeries(len, drift, vol, seed) {
    const out = []; let v = 100; let s = seed;
    for (let i = 0; i < len; i++) {
      s = (s * 9301 + 49297) % 233280;
      v *= 1 + drift + (s / 233280 - 0.5) * vol;
      out.push(v);
    }
    return out;
  }

  // ── Holdings ────────────────────────────────────────────────────────────────
  const holdings = ps.map((r, idx) => ({
    code:          String(idx + 1).padStart(3, "0"),
    name:          r.company,
    en:            r.company,
    sector:        "—",
    account:       "tokutei",
    total_bought:  r.total_bought,
    total_sold:    r.total_sold,
    net_invested:  r.net_invested,
    dividends:     r.dividends,
    buy_trades:    r.buy_trades,
    last_purchase: r.last_purchase,
    cost:          r.total_bought,
    mv:            r.net_invested,
    pnl:           r.total_sold + r.dividends - r.total_bought,
    pnlPct:        r.total_bought > 0 ? (r.total_sold + r.dividends - r.total_bought) / r.total_bought : 0,
    dayPnl:        0, day: 0, last: 0, shares: 0, avg: 0,
    yield:         r.total_bought > 0 ? r.dividends / r.total_bought : 0,
    divAnnual:     r.dividends,
    weight:        total_cost > 0 ? r.total_bought / total_cost : 0,
    spark:         genSpark(idx * 37 + 11, 0),
  }));

  const portSeries   = genSeries(252, 0.00060, 0.010, 42);
  const topixSeries  = genSeries(252, 0.00055, 0.009, 13);
  const nikkeiSeries = genSeries(252, 0.00072, 0.010, 19);
  const equity       = portSeries.map(v => total_cost * (v / 100));
  const today        = new Date();
  const dates        = Array.from({ length: 252 }, (_, i) => {
    const d = new Date(today); d.setDate(d.getDate() - (251 - i)); return d;
  });

  const sectors  = [{ name: "Portfolio", mv: total_cost, pct: 1 }];
  const activity = th.slice(0, 12).map(r => ({
    type:    r.type_en.toLowerCase().includes("buy")  ? "buy"
           : r.type_en.toLowerCase().includes("sell") ? "sell" : "div",
    date:    r.date, name: r.company, code: "", amount: r.amount, account: "tokutei", shares: 0, price: 0,
  }));
  const dividends = dt.slice(0, 8).map(r => ({
    name: r.company, code: "", date: "", gross: r.received, net: r.received, account: "tokutei", perShare: 0, shares: 0,
  }));

  const risk = {
    sharpe: 0, sortino: 0, maxDD: 0, volAnn: 0,
    beta: 1, alpha: 0, var95: 0,
    riskScore: 50, riskLabel: "Connect tickers for live analytics",
    winRate: 0, avgWin: 0, avgLoss: 0, profitFactor: 0,
  };

  const topH = [...holdings].sort((a,b) => b.total_bought - a.total_bought).slice(0, 6);
  const riskDecomp = topH.map(h => ({
    code: h.code, name: h.name, en: h.en, sector: h.sector,
    weight: h.weight, vol: 0.20, contrib: h.weight * 0.20, pct: h.weight,
  }));

  const corrSyms   = holdings.slice(0, 8);
  const corrMatrix = corrSyms.map((_, i) => corrSyms.map((__, j) =>
    i === j ? 1.0 : parseFloat((0.25 + ((i * 3 + j * 7) % 5) * 0.09).toFixed(2))
  ));

  const divYield = total_cost > 0 ? (total_divs / total_cost * 100).toFixed(2) : "0.00";
  const topDiv   = dt[0] ? dt[0].company : "—";

  const insights = [
    {
      kind: "opportunity", severity: "ok",
      title: `${ps.length} positions · ¥${fmtN(total_cost)} invested`,
      body: `Net invested: ¥${fmtN(total_net)} · Dividends: ¥${fmtN(total_divs)} · Yield on cost: ${divYield}%.`,
      action: "View holdings",
    },
    {
      kind: "alert", severity: "info",
      title: `Top dividend payer: ${topDiv}`,
      body: `${dt.length} dividend-paying positions. Total income: ¥${fmtN(total_divs)}. Connect tickers to see live yield data.`,
      action: "View income",
    },
    {
      kind: "risk", severity: "warn",
      title: "Live prices not connected",
      body: "Sharpe, daily P/L, VaR and risk score require live prices. Use the Analytics tab in the Streamlit app for full institutional metrics.",
      action: "Learn more",
    },
    {
      kind: "performance", severity: "ok",
      title: `${buyTxs} buys · ${sellTxs} sells recorded`,
      body: `Total bought: ¥${fmtN(total_cost)} · Sold: ¥${fmtN(total_sold_sum)} · Net remaining: ¥${fmtN(total_net)}.`,
      action: "View activity",
    },
  ];

  const nowStr = new Date().toTimeString().slice(0, 5);
  const news = [
    { time: nowStr, src: "Atlas",  text: `Loaded ${ps.length} positions · ¥${fmtN(total_cost)} invested` },
    { time: "—",    src: "Info",   text: "Live prices not connected — connect tickers for full analytics" },
    { time: "—",    src: "Income", text: `Total dividends: ¥${fmtN(total_divs)} · Yield on cost: ${divYield}%` },
    { time: "—",    src: "Data",   text: `${buyTxs} buy trades · ${sellTxs} sell trades · ${dt.length} dividend-paying positions` },
  ];

  const market = [
    { code: "TOPIX",  name: "TOPIX",      last: 0, day: 0, region: "JP",   spark: genSpark(3)  },
    { code: "NKY",    name: "Nikkei 225", last: 0, day: 0, region: "JP",   spark: genSpark(7)  },
    { code: "SPX",    name: "S&P 500",    last: 0, day: 0, region: "US",   spark: genSpark(11) },
    { code: "USDJPY", name: "USD/JPY",    last: 0, day: 0, region: "FX",   spark: genSpark(19) },
    { code: "VIX",    name: "VIX",        last: 0, day: 0, region: "US",   spark: genSpark(23) },
    { code: "JP10Y",  name: "JGB 10Y",    last: 0, day: 0, region: "Rate", unit: "%", spark: genSpark(29) },
    { code: "GOLD",   name: "Gold (¥/g)", last: 0, day: 0, region: "Comm", spark: genSpark(31) },
    { code: "VWAP",   name: "JPY REER",   last: 0, day: 0, region: "FX",   spark: genSpark(37) },
  ];

  const nisa = {
    tsumitate: { name: "つみたて投資枠", en: "Tsumitate (DCA)", quotaYear: 1_200_000, quotaLife: 18_000_000, usedYear: 0, usedLife: 0, mv: 0, cost: 0, pnl: 0, pct: 0, count: 0 },
    growth:    { name: "成長投資枠",     en: "Growth",          quotaYear: 2_400_000, quotaLife: 12_000_000, usedYear: 0, usedLife: 0, mv: 0, cost: 0, pnl: 0, pct: 0, count: 0 },
    tokutei:   { name: "特定口座",       en: "Taxable (Tokutei)", taxRate: 0.20315, mv: total_net, cost: total_cost, pnl: 0, pct: 0, count: holdings.length, taxOwed: 0 },
    ippan:     { name: "一般口座",       en: "General",           taxRate: 0.20315, mv: 0, cost: 0, pnl: 0, pct: 0, count: 0 },
  };

  return {
    mode:            "paypay",
    holdings,
    nisa,
    total_mv:        total_net,
    total_cost,
    total_sold:      total_sold_sum,
    total_net,
    total_day:       0,
    total_div_annual: total_divs,
    cash:            0,
    portSeries, topixSeries, nikkeiSeries, dates,
    sectors,
    dividends,
    activity,
    realizedYtd:     total_sold_sum,
    divYtd:          total_divs,
    xirr:            0,
    equity,
    monthlyPnL:      [],
    risk,
    riskDecomp,
    watchlist:       [],
    market,
    corrSyms,
    corrMatrix,
    insights,
    news,
    asOf:            new Date(),
    ps, th, dt,
    total_trades,
  };
};
