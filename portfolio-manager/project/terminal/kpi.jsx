// Hero KPI cards — premium glow style

function KpiGrid({ data, ccy }) {
  if (data.mode === "paypay") return <KpiGridPayPay data={data} ccy={ccy} />;

  const { total_mv, total_cost, total_day, risk, portSeries, realizedYtd, divYtd } = data;
  const totalPnl = total_mv - total_cost;
  const totalReturnPct = totalPnl / total_cost;
  const dayPct = total_day / (total_mv - total_day);
  const totalReturnAll = totalPnl + realizedYtd + divYtd;

  const cards = [
    {
      eyebrow: "Total Portfolio Value",
      jp: "総資産",
      value: fmtJPY(total_mv, ccy),
      delta: { v: totalPnl, pct: totalReturnPct, label: "vs cost basis" },
      spark: portSeries.slice(-60),
      featured: true,
    },
    {
      eyebrow: "Daily P/L",
      jp: "本日損益",
      value: fmtSign(total_day, ccy),
      valueColor: total_day >= 0 ? "var(--pos)" : "var(--neg)",
      delta: { pct: dayPct, label: "9 of 14 gainers" },
      spark: portSeries.slice(-12),
      sparkColor: total_day >= 0 ? "var(--pos)" : "var(--neg)",
    },
    {
      eyebrow: "Total Return",
      jp: "総合リターン",
      value: fmtSign(totalReturnAll, ccy),
      valueColor: "var(--pos)",
      delta: { pct: totalReturnAll / total_cost, label: "all-time" },
      breakdown: [
        ["Unrealized", fmtSign(totalPnl, ccy, true)],
        ["Realized YTD", fmtSign(realizedYtd, ccy, true)],
        ["Dividends YTD", fmtSign(divYtd, ccy, true)],
      ],
    },
    {
      eyebrow: "Sharpe Ratio",
      jp: "シャープ比",
      value: risk.sharpe.toFixed(2),
      valueColor: "var(--cyan)",
      delta: { custom: "Top quartile" },
      breakdown: [
        ["Sortino", risk.sortino.toFixed(2)],
        ["Alpha", "+" + (risk.alpha * 100).toFixed(1) + "%"],
        ["Beta", risk.beta.toFixed(2)],
      ],
    },
    {
      eyebrow: "Win Rate",
      jp: "勝率",
      value: (risk.winRate * 100).toFixed(1) + "%",
      valueColor: "var(--pos)",
      delta: { custom: `${Math.round(risk.winRate * 24)} of 24 trades` },
      breakdown: [
        ["Avg win", "+" + (risk.avgWin * 100).toFixed(1) + "%"],
        ["Avg loss", (risk.avgLoss * 100).toFixed(1) + "%"],
        ["Profit factor", risk.profitFactor.toFixed(2)],
      ],
    },
    {
      eyebrow: "Risk Score",
      jp: "リスクスコア",
      value: risk.riskScore,
      valueSuffix: "/100",
      valueColor: "var(--warn)",
      delta: { custom: risk.riskLabel },
      gauge: { value: risk.riskScore, max: 100 },
      breakdown: [
        ["Volatility", (risk.volAnn * 100).toFixed(1) + "%"],
        ["Max DD", (risk.maxDD * 100).toFixed(1) + "%"],
        ["VaR (95%)", (risk.var95 * 100).toFixed(1) + "%"],
      ],
    },
  ];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr 1.1fr 1fr 1fr 1.1fr", gap: 14 }}>
      {cards.map((c, i) => <KpiCard key={i} card={c} ccy={ccy} delay={i * 60} />)}
    </div>
  );
}

function KpiCard({ card, delay }) {
  return (
    <div className={"card " + (card.featured ? "card--gradient-edge" : "")} style={{
      padding: 16,
      display: "flex", flexDirection: "column",
      minHeight: 168,
      animationDelay: delay + "ms",
    }}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 12 }}>
        <div>
          <div className="eyebrow" style={{ fontSize: 9.5 }}>{card.eyebrow}</div>
          <div style={{ fontSize: 10.5, color: "var(--muted-2)", marginTop: 3, letterSpacing: "0.02em" }}>{card.jp}</div>
        </div>
        {card.delta?.pct != null && (
          <span className={"pill " + (card.delta.pct >= 0 ? "pill--pos" : "pill--neg")}>
            <span style={{ color: "inherit" }}><Triangle2 up={card.delta.pct >= 0} /></span>
            {Math.abs(card.delta.pct * 100).toFixed(2)}%
          </span>
        )}
        {card.delta?.custom && (
          <span className="pill pill--cyan" style={{ fontSize: 10 }}>{card.delta.custom}</span>
        )}
      </div>

      <div className="font-display mono" style={{
        fontSize: card.featured ? 32 : 26,
        fontWeight: 600,
        letterSpacing: "-0.02em",
        lineHeight: 1.05,
        color: card.valueColor || "var(--text)",
        textShadow: card.valueColor ? `0 0 24px ${card.valueColor === "var(--cyan)" ? "rgba(6,182,212,0.4)" : (card.valueColor === "var(--pos)" ? "rgba(34,197,94,0.4)" : (card.valueColor === "var(--neg)" ? "rgba(239,68,68,0.4)" : (card.valueColor === "var(--warn)" ? "rgba(245,158,11,0.4)" : "transparent")))}` : "none",
      }}>
        {card.value}
        {card.valueSuffix && <span style={{ fontSize: 14, color: "var(--muted)", marginLeft: 4, fontWeight: 400 }}>{card.valueSuffix}</span>}
      </div>

      {card.delta?.v != null && (
        <div style={{ marginTop: 6, fontSize: 12 }}>
          <span className={card.delta.v >= 0 ? "pos" : "neg"} style={{ fontWeight: 500 }}>
            {card.delta.v >= 0 ? "+" : "−"}{fmtJPY(Math.abs(card.delta.v))} 
          </span>
          <span style={{ color: "var(--muted)", marginLeft: 8 }}>{card.delta.label}</span>
        </div>
      )}
      {!card.delta?.v && card.delta?.label && (
        <div style={{ marginTop: 6, fontSize: 11.5, color: "var(--muted)" }}>
          {card.delta.label}
        </div>
      )}

      <div style={{ flex: 1 }} />

      {/* Foot */}
      {card.spark && (
        <div style={{ marginTop: 12, paddingTop: 12, borderTop: "1px solid var(--border)" }}>
          <Spark values={card.spark} width={card.featured ? 230 : 140} height={card.featured ? 36 : 26}
                 color={card.sparkColor || "var(--cyan)"} />
        </div>
      )}
      {card.gauge && <RiskGauge value={card.gauge.value} />}
      {card.breakdown && (
        <div style={{ marginTop: 12, paddingTop: 12, borderTop: "1px solid var(--border)", display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
          {card.breakdown.map(([l, v], i) => (
            <div key={i}>
              <div style={{ fontSize: 9.5, color: "var(--muted)", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 3 }}>{l}</div>
              <div className="mono" style={{ fontSize: 12, color: "var(--text-2)", fontWeight: 500 }}>{v}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function RiskGauge({ value }) {
  const W = 200, H = 36;
  const segs = 24;
  // 0-33: green, 33-66: amber, 66-100: red
  const colorFor = (i) => {
    const p = i / segs;
    if (p < 0.33) return "var(--pos)";
    if (p < 0.66) return "var(--warn)";
    return "var(--neg)";
  };
  const activeMax = Math.round((value / 100) * segs);
  return (
    <div style={{ marginTop: 12, paddingTop: 12, borderTop: "1px solid var(--border)" }}>
      <div style={{ display: "flex", gap: 2, alignItems: "flex-end" }}>
        {Array.from({ length: segs }).map((_, i) => {
          const active = i < activeMax;
          const h = 8 + (i / segs) * 16;
          return (
            <span key={i} style={{
              flex: 1,
              height: h,
              background: active ? colorFor(i) : "rgba(148,163,184,0.10)",
              boxShadow: active ? `0 0 6px ${colorFor(i)}` : "none",
              borderRadius: 1,
              transition: "all 200ms",
            }} />
          );
        })}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4, fontSize: 9.5, color: "var(--muted)", fontFamily: "JetBrains Mono", letterSpacing: "0.06em" }}>
        <span>LOW</span><span>MOD</span><span>HIGH</span>
      </div>
    </div>
  );
}

// ─── PayPay mode KPI grid ─────────────────────────────────────────────────
function KpiGridPayPay({ data, ccy }) {
  const { total_cost, total_sold, total_net, total_div_annual, holdings, total_trades, dt, divYtd } = data;
  const divs      = total_div_annual || divYtd || 0;
  const divYield  = total_cost > 0 ? divs / total_cost : 0;

  const cards = [
    {
      eyebrow: "Total Invested", jp: "買付合計",
      value: fmtJPY(total_cost, ccy),
      valueColor: "var(--cyan)",
      delta: { custom: `${holdings.length} positions` },
      spark: data.portSeries.slice(-60),
      featured: true,
    },
    {
      eyebrow: "Net Invested", jp: "純投資額",
      value: fmtJPY(total_net, ccy),
      valueColor: total_net >= 0 ? "var(--pos)" : "var(--neg)",
      delta: {
        pct: total_cost > 0 ? (total_cost - total_net) / total_cost : 0,
        label: "recovered via sales",
      },
    },
    {
      eyebrow: "Dividend Income", jp: "配当合計",
      value: fmtJPY(divs, ccy),
      valueColor: "var(--pos)",
      delta: { pct: divYield, label: "yield on cost" },
      breakdown: dt && dt.length > 0
        ? dt.slice(0, 3).map(r => [r.company.slice(0, 12), fmtJPY(r.received, ccy, true)])
        : undefined,
    },
    {
      eyebrow: "Total Sold", jp: "売却合計",
      value: fmtJPY(total_sold || 0, ccy),
      valueColor: "var(--warn)",
      delta: { custom: "realized exits" },
    },
    {
      eyebrow: "Positions", jp: "保有銘柄数",
      value: String(holdings.length),
      delta: { custom: "active holdings" },
    },
    {
      eyebrow: "Buy Trades", jp: "買付回数",
      value: (total_trades || 0).toLocaleString(),
      valueColor: "var(--cyan)",
      delta: { custom: "total transactions" },
    },
  ];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr 1.1fr 1fr 1fr 1.1fr", gap: 14 }}>
      {cards.map((c, i) => <KpiCard key={i} card={c} ccy={ccy} delay={i * 60} />)}
    </div>
  );
}

window.KpiGrid = KpiGrid;
