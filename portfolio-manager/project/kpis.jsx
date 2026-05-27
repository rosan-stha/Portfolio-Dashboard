// Hero KPI row + NISA segmentation strip

function KpiRow({ data, ccy, period }) {
  const { total_mv, total_cost, total_day, total_div_annual, cash, realizedYtd, divYtd, xirr, portSeries } = data;
  const totalPnl = total_mv - total_cost;
  const totalPnlPct = totalPnl / total_cost;
  const dayPct = total_day / (total_mv - total_day);
  const incomeYtd = realizedYtd + divYtd;
  // 30-day sparkline subset
  const spark = portSeries.slice(-30);

  const kpis = [
    {
      label: "Portfolio Value",
      jp: "評価額",
      hero: true,
      content: (
        <>
          <div className="mono" style={{ fontSize: 32, fontWeight: 500, letterSpacing: "-0.02em", lineHeight: 1.05 }}>
            {fmtMoney(total_mv, ccy)}
          </div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 8 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ color: totalPnl >= 0 ? "var(--gain)" : "var(--loss)", display: "inline-flex", alignItems: "center" }}>
                <Triangle up={totalPnl >= 0} size={9} />
              </span>
              <Delta value={totalPnl} pct={totalPnlPct} ccy={ccy} showCcy={true} size="md" />
            </div>
            <div style={{ color: "var(--muted)", fontSize: 11 }}>vs cost</div>
          </div>
        </>
      ),
      foot: (
        <div style={{ marginTop: 10, paddingTop: 10, borderTop: "1px dashed var(--border)" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: 11, color: "var(--muted)" }}>30-day</span>
            <span style={{ color: spark[spark.length - 1] >= spark[0] ? "var(--gain)" : "var(--loss)" }}>
              <Sparkline values={spark} width={104} height={22} />
            </span>
          </div>
        </div>
      ),
    },
    {
      label: "Today",
      jp: "本日",
      content: (
        <>
          <div className="mono" style={{ fontSize: 22, fontWeight: 500, letterSpacing: "-0.01em", color: total_day >= 0 ? "var(--gain)" : "var(--loss)" }}>
            {total_day >= 0 ? "+" : "−"}{fmtMoney(Math.abs(total_day), ccy)}
          </div>
          <div style={{ marginTop: 4 }}>
            <PctDelta value={dayPct} size="md" />
          </div>
        </>
      ),
      foot: (
        <KpiBreakdown rows={[
          ["Gainers",  "9 / 14"],
          ["Top mover", "9984 +4.1%"],
        ]} />
      ),
    },
    {
      label: "Return",
      jp: "総合リターン",
      sub: "Unrealized + realized + div",
      content: (
        <>
          <div className="mono" style={{ fontSize: 22, fontWeight: 500, letterSpacing: "-0.01em", color: "var(--gain)" }}>
            +{fmtMoney(totalPnl + realizedYtd + divYtd, ccy)}
          </div>
          <div style={{ marginTop: 4 }}>
            <PctDelta value={(totalPnl + realizedYtd + divYtd) / total_cost} size="md" />
          </div>
        </>
      ),
      foot: (
        <KpiBreakdown rows={[
          ["Unrealized", fmtMoney(totalPnl, ccy, { compact: true })],
          ["Realized YTD", fmtMoney(realizedYtd, ccy, { compact: true })],
          ["Dividends YTD", fmtMoney(divYtd, ccy, { compact: true })],
        ]} />
      ),
    },
    {
      label: "XIRR",
      jp: "年率リターン",
      sub: "Money-weighted, annualized",
      content: (
        <>
          <div className="mono" style={{ fontSize: 22, fontWeight: 500, letterSpacing: "-0.01em", color: "var(--gain)" }}>
            +{(xirr * 100).toFixed(1)}%
          </div>
          <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 4 }}>since Jan 2023</div>
        </>
      ),
      foot: (
        <KpiBreakdown rows={[
          ["vs TOPIX",   "+14.2pp"],
          ["vs Nikkei",  "+9.4pp"],
        ]} />
      ),
    },
    {
      label: "Dividends",
      jp: "想定配当",
      sub: "Forward 12mo",
      content: (
        <>
          <div className="mono" style={{ fontSize: 22, fontWeight: 500, letterSpacing: "-0.01em" }}>
            {fmtMoney(total_div_annual, ccy)}
          </div>
          <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 4 }}>
            Yield on mkt <span className="mono" style={{ color: "var(--text-2)" }}>{((total_div_annual / total_mv) * 100).toFixed(2)}%</span>
          </div>
        </>
      ),
      foot: (
        <KpiBreakdown rows={[
          ["Yield on cost", ((total_div_annual / total_cost) * 100).toFixed(2) + "%"],
          ["Next 30d", fmtMoney(46_320, ccy, { compact: true })],
        ]} />
      ),
    },
    {
      label: "Cash",
      jp: "余力",
      content: (
        <>
          <div className="mono" style={{ fontSize: 22, fontWeight: 500, letterSpacing: "-0.01em" }}>
            {fmtMoney(cash, ccy)}
          </div>
          <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 4 }}>
            <span className="mono" style={{ color: "var(--text-2)" }}>{((cash / (cash + total_mv)) * 100).toFixed(1)}%</span> of total
          </div>
        </>
      ),
      foot: (
        <KpiBreakdown rows={[
          ["Settled",   fmtMoney(cash * 0.86, ccy, { compact: true })],
          ["T+2 pending", fmtMoney(cash * 0.14, ccy, { compact: true })],
        ]} />
      ),
    },
  ];

  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "1.4fr 1fr 1fr 1fr 1fr 1fr",
      gap: 12,
      padding: "16px 24px",
    }}>
      {kpis.map((k, i) => (
        <div key={i} className="card" style={{ padding: 14, display: "flex", flexDirection: "column", minHeight: 158 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
            <div>
              <div className="eyebrow">{k.label}</div>
              {k.sub && <div style={{ fontSize: 10.5, color: "var(--muted)", marginTop: 2 }}>{k.sub}</div>}
            </div>
            <div className="jp" style={{ fontSize: 10.5, color: "var(--muted)" }}>{k.jp}</div>
          </div>
          <div>{k.content}</div>
          <div style={{ marginTop: "auto" }}>{k.foot}</div>
        </div>
      ))}
    </div>
  );
}

function KpiBreakdown({ rows }) {
  return (
    <div style={{ marginTop: 10, paddingTop: 10, borderTop: "1px dashed var(--border)", display: "flex", flexDirection: "column", gap: 4 }}>
      {rows.map(([l, v], i) => (
        <div key={i} style={{ display: "flex", justifyContent: "space-between", fontSize: 11 }}>
          <span style={{ color: "var(--muted)" }}>{l}</span>
          <span className="mono" style={{ color: "var(--text-2)" }}>{v}</span>
        </div>
      ))}
    </div>
  );
}


// ─── NISA strip ────────────────────────────────────────────────────────────
function NisaStrip({ data, ccy, prominent }) {
  const { nisa } = data;
  const buckets = [
    { key: "tsumitate", k: nisa.tsumitate, accent: "var(--gain)",  tagCls: "tag--nisa-t" },
    { key: "growth",    k: nisa.growth,    accent: "var(--accent)",tagCls: "tag--nisa-g" },
    { key: "tokutei",   k: nisa.tokutei,   accent: "var(--text-2)",tagCls: "tag--tokutei" },
    { key: "ippan",     k: nisa.ippan,     accent: "var(--muted)", tagCls: "tag--tokutei" },
  ];

  // Non-prominent: compact row inline with KPIs
  if (!prominent) {
    return (
      <div style={{ padding: "0 24px 16px" }}>
        <div className="card" style={{ display: "flex", padding: 0 }}>
          {buckets.map((b, i) => (
            <div key={b.key} style={{
              flex: 1, padding: "10px 14px",
              borderRight: i < buckets.length - 1 ? "1px solid var(--border)" : "none",
              display: "flex", alignItems: "center", gap: 12,
            }}>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
                  <span className={"tag " + b.tagCls} style={{ fontSize: 10 }}>{b.k.en}</span>
                  <span className="jp" style={{ fontSize: 10.5, color: "var(--muted)" }}>{b.k.name}</span>
                </div>
                <div className="mono" style={{ fontSize: 15, fontWeight: 500 }}>{fmtMoney(b.k.mv, ccy, { compact: true })}</div>
              </div>
              <div style={{ textAlign: "right" }}>
                <PctDelta value={b.k.pct} size="sm" />
                <div style={{ fontSize: 10.5, color: "var(--muted)", marginTop: 2 }}>{b.k.count} pos</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Prominent: NISA centerpiece w/ quota meters
  return (
    <div style={{ padding: "0 24px 16px" }}>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: 8 }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
          <div className="eyebrow">Account Segmentation</div>
          <div className="jp" style={{ fontSize: 11, color: "var(--muted)" }}>新NISA · 特定口座</div>
        </div>
        <div style={{ fontSize: 11, color: "var(--muted)" }}>
          Tax owed on unrealized (特定): <span className="mono" style={{ color: "var(--warn)" }}>{fmtMoney(nisa.tokutei.taxOwed, ccy, { compact: true })}</span>
          <span style={{ marginLeft: 12, opacity: 0.6 }}>(20.315%)</span>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1.2fr 1fr 0.8fr", gap: 12 }}>
        {buckets.map((b) => {
          const hasQuota = b.k.quotaYear != null;
          return (
            <div key={b.key} className="card" style={{ padding: 14 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                    <span className={"tag " + b.tagCls}>{b.k.en}</span>
                  </div>
                  <div className="jp" style={{ fontSize: 11.5, color: "var(--muted)", marginBottom: 8 }}>{b.k.name}</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <PctDelta value={b.k.pct} size="sm" />
                  <div style={{ fontSize: 10.5, color: "var(--muted)", marginTop: 1 }}>{b.k.count} pos</div>
                </div>
              </div>

              <div className="mono" style={{ fontSize: 19, fontWeight: 500, letterSpacing: "-0.01em" }}>
                {fmtMoney(b.k.mv, ccy)}
              </div>
              <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 2 }}>
                cost <span className="mono" style={{ color: "var(--text-2)" }}>{fmtMoney(b.k.cost, ccy, { compact: true })}</span>
                <span style={{ margin: "0 6px", opacity: 0.4 }}>·</span>
                P&L <span className={"mono " + (b.k.pnl >= 0 ? "gain" : "loss")}>{(b.k.pnl >= 0 ? "+" : "−") + fmtMoney(Math.abs(b.k.pnl), ccy, { compact: true })}</span>
              </div>

              {hasQuota && (
                <div style={{ marginTop: 12 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10.5, color: "var(--muted)", marginBottom: 4 }}>
                    <span>2026 quota</span>
                    <span className="mono" style={{ color: "var(--text-2)" }}>
                      {fmtMoney(b.k.usedYear, ccy, { compact: true })} / {fmtMoney(b.k.quotaYear, ccy, { compact: true })}
                    </span>
                  </div>
                  <MiniBar value={b.k.usedYear} max={b.k.quotaYear} color={b.accent} />

                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10.5, color: "var(--muted)", marginTop: 8, marginBottom: 4 }}>
                    <span>Lifetime</span>
                    <span className="mono" style={{ color: "var(--text-2)" }}>
                      {fmtMoney(b.k.usedLife, ccy, { compact: true })} / {fmtMoney(b.k.quotaLife, ccy, { compact: true })}
                    </span>
                  </div>
                  <MiniBar value={b.k.usedLife} max={b.k.quotaLife} color={b.accent} height={3} />
                </div>
              )}

              {!hasQuota && (
                <div style={{ marginTop: 12, paddingTop: 10, borderTop: "1px dashed var(--border)", fontSize: 11, color: "var(--muted)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Tax rate</span>
                    <span className="mono" style={{ color: "var(--text-2)" }}>20.315%</span>
                  </div>
                  {b.key === "tokutei" && (
                    <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4 }}>
                      <span>If realized now</span>
                      <span className="mono" style={{ color: "var(--warn)" }}>−{fmtMoney(nisa.tokutei.taxOwed, ccy, { compact: true })}</span>
                    </div>
                  )}
                  {b.key === "ippan" && (
                    <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4, fontStyle: "italic" }}>
                      <span style={{ opacity: 0.7 }}>no holdings</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

Object.assign(window, { KpiRow, NisaStrip });
