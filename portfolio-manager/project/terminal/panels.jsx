// AI Insights, Watchlist, Market Overview, News ticker, Holdings table

// ─── AI Insights ───────────────────────────────────────────────────────────
function AIInsights({ data }) {
  const { insights } = data;
  const sevMeta = {
    warn: { color: "var(--warn)", bg: "rgba(245,158,11,0.06)", border: "rgba(245,158,11,0.3)", glow: "rgba(245,158,11,0.25)", label: "RISK" },
    ok:   { color: "var(--cyan)", bg: "rgba(6,182,212,0.06)", border: "rgba(6,182,212,0.3)", glow: "rgba(6,182,212,0.25)", label: "OPPORTUNITY" },
    info: { color: "var(--blue)", bg: "rgba(59,130,246,0.06)", border: "rgba(59,130,246,0.3)", glow: "rgba(59,130,246,0.25)", label: "ALERT" },
  };
  const kindLabel = { risk: "RISK", opportunity: "OPPORTUNITY", alert: "ALERT", performance: "PERFORMANCE" };

  return (
    <div className="card card--glow" style={{ overflow: "hidden", height: "100%", position: "relative" }}>
      {/* Animated header */}
      <div style={{
        padding: "14px 16px 12px",
        borderBottom: "1px solid var(--border)",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: "linear-gradient(90deg, rgba(6,182,212,0.06), transparent 60%)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: "linear-gradient(135deg, #3B82F6, #06B6D4)",
            display: "grid", placeItems: "center",
            boxShadow: "0 0 16px -2px rgba(6,182,212,0.5), inset 0 1px 0 rgba(255,255,255,0.15)",
          }}>
            <svg viewBox="0 0 20 20" width="16" height="16" fill="none">
              <path d="M10 2L11.5 7L16 8L11.5 9L10 14L8.5 9L4 8L8.5 7Z" fill="white" />
              <circle cx="16" cy="3" r="1" fill="white" />
              <circle cx="4" cy="16" r="1" fill="white" opacity="0.6" />
            </svg>
          </div>
          <div>
            <div className="font-display" style={{ fontSize: 15, fontWeight: 600, letterSpacing: "-0.01em", display: "flex", alignItems: "center", gap: 8 }}>
              AI Insights
              <span className="pill pill--cyan" style={{ fontSize: 9, padding: "2px 6px" }}>BETA</span>
            </div>
            <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 1 }}>4 active signals · updated 2m ago</div>
          </div>
        </div>
        <button className="btn btn--ghost" style={{ fontSize: 11.5 }}>Ask AI →</button>
      </div>

      <div style={{ padding: 12, display: "flex", flexDirection: "column", gap: 10 }}>
        {insights.map((ins, i) => {
          const sm = sevMeta[ins.severity];
          return (
            <div key={i} style={{
              padding: 12,
              background: sm.bg,
              border: `1px solid ${sm.border}`,
              borderRadius: 10,
              position: "relative",
              animation: `fadeup 400ms ease-out ${i * 80}ms backwards`,
            }}>
              <div style={{
                position: "absolute", inset: 0, borderRadius: 10,
                boxShadow: `inset 0 0 30px -10px ${sm.glow}`,
                pointerEvents: "none",
              }} />
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6, gap: 8, position: "relative" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{
                    fontSize: 9, fontWeight: 700, letterSpacing: "0.12em",
                    color: sm.color,
                    padding: "2px 7px",
                    background: "rgba(0,0,0,0.25)",
                    border: `1px solid ${sm.border}`,
                    borderRadius: 3,
                  }}>{kindLabel[ins.kind] || sm.label}</span>
                  <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text)" }}>{ins.title}</span>
                </div>
                <button style={{
                  background: "transparent", border: 0,
                  color: "var(--muted)", cursor: "pointer",
                  fontSize: 16, lineHeight: 1, padding: 0,
                }}>›</button>
              </div>
              <div style={{ fontSize: 11.5, color: "var(--text-2)", lineHeight: 1.5, marginBottom: 8 }}>
                {ins.body}
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 10.5, color: "var(--muted)" }}>Action · <span style={{ color: sm.color, fontWeight: 500 }}>{ins.action}</span></span>
                <button style={{
                  fontSize: 10.5,
                  color: sm.color,
                  background: "transparent",
                  border: `1px solid ${sm.border}`,
                  borderRadius: 4,
                  padding: "3px 8px",
                  cursor: "pointer",
                  fontFamily: "inherit",
                }}>Apply →</button>
              </div>
            </div>
          );
        })}
      </div>

      <style>{`@keyframes fadeup { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }`}</style>
    </div>
  );
}


// ─── Watchlist ────────────────────────────────────────────────────────────
function Watchlist({ data, ccy }) {
  const { watchlist } = data;
  return (
    <div className="card" style={{ overflow: "hidden", height: "100%" }}>
      <CardHd
        eyebrow="Watchlist"
        title="Tracking"
        sub={watchlist.length + " symbols"}
        right={<button className="btn btn--ghost" style={{ fontSize: 11.5 }}>+ Add</button>}
      />
      <div>
        {watchlist.map((w, i) => (
          <div key={i} style={{
            display: "flex", alignItems: "center", gap: 12,
            padding: "12px 16px",
            borderBottom: i < watchlist.length - 1 ? "1px solid var(--border)" : "none",
            transition: "background 160ms",
            cursor: "pointer",
          }}
          onMouseEnter={e => e.currentTarget.style.background = "rgba(59,130,246,0.04)"}
          onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <span className="mono" style={{ fontSize: 11, color: "var(--muted)" }}>{w.code}</span>
                <span style={{ fontSize: 13, fontWeight: 500 }}>{w.en}</span>
              </div>
              {w.alert && (
                <div style={{ fontSize: 10.5, color: "var(--warn)", marginTop: 2, display: "flex", alignItems: "center", gap: 5 }}>
                  <span style={{ width: 5, height: 5, borderRadius: "50%", background: "var(--warn)", boxShadow: "0 0 6px var(--warn)" }} />
                  {w.alert}
                </div>
              )}
            </div>
            <div style={{ color: w.day >= 0 ? "var(--pos)" : "var(--neg)" }}>
              <Spark values={w.spark} width={56} height={22} color="currentColor" glow={false} strokeWidth={1.3} />
            </div>
            <div style={{ textAlign: "right", minWidth: 84 }}>
              <div className="mono" style={{ fontSize: 12.5, fontWeight: 500 }}>{fmtJPY(w.last, ccy)}</div>
              <div style={{ marginTop: 2 }}>
                <span className={"mono " + (w.day >= 0 ? "pos" : "neg")} style={{ fontSize: 11 }}>
                  {w.day >= 0 ? "+" : ""}{(w.day * 100).toFixed(2)}%
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


// ─── Market Overview ──────────────────────────────────────────────────────
function MarketOverview({ data }) {
  const { market } = data;
  const regionColor = { JP: "var(--cyan)", US: "var(--blue)", FX: "var(--warn)", Rate: "#A78BFA", Comm: "#F97316" };

  return (
    <div className="card" style={{ overflow: "hidden", height: "100%" }}>
      <CardHd eyebrow="Markets" title="Market Overview" sub="Indices · FX · Rates" />
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 0 }}>
        {market.map((m, i) => (
          <div key={i} style={{
            padding: "12px 14px",
            borderRight: i % 2 === 0 ? "1px solid var(--border)" : "none",
            borderBottom: i < market.length - 2 ? "1px solid var(--border)" : "none",
            position: "relative",
            overflow: "hidden",
          }}>
            <div style={{
              position: "absolute", inset: 0, opacity: 0.5,
              background: m.day >= 0
                ? "linear-gradient(135deg, transparent 60%, rgba(34,197,94,0.06))"
                : "linear-gradient(135deg, transparent 60%, rgba(239,68,68,0.06))",
              pointerEvents: "none",
            }} />
            <div style={{ position: "relative" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                <span style={{
                  fontSize: 9, fontWeight: 600,
                  color: regionColor[m.region], 
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                }}>{m.region}</span>
                <span style={{ fontSize: 12, fontWeight: 500, color: "var(--text)" }}>{m.name}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
                <div className="mono" style={{ fontSize: 16, fontWeight: 500, letterSpacing: "-0.01em" }}>
                  {m.last.toLocaleString(undefined, { maximumFractionDigits: m.last < 100 ? 2 : 0 })}
                  {m.unit && <span style={{ fontSize: 11, color: "var(--muted)", marginLeft: 2 }}>{m.unit}</span>}
                </div>
                <div style={{ textAlign: "right", color: m.day >= 0 ? "var(--pos)" : "var(--neg)", display: "flex", alignItems: "center", gap: 6 }}>
                  <Spark values={m.spark} width={36} height={18} color="currentColor" glow={false} strokeWidth={1.2} filled={false} />
                  <span className="mono" style={{ fontSize: 11.5 }}>
                    {m.day >= 0 ? "+" : ""}{(m.day * 100).toFixed(2)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


// ─── News Ticker ──────────────────────────────────────────────────────────
function NewsTicker({ data }) {
  const { news } = data;
  return (
    <div className="card" style={{
      padding: "10px 16px",
      display: "flex", alignItems: "center", gap: 16,
      overflow: "hidden",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, flexShrink: 0 }}>
        <span style={{
          width: 6, height: 6, borderRadius: "50%",
          background: "var(--neg)",
          boxShadow: "0 0 8px var(--neg)",
          animation: "pulse-dot 1.6s ease-in-out infinite",
        }} />
        <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.12em", color: "var(--neg)" }}>LIVE</span>
      </div>
      <div style={{ flex: 1, overflow: "hidden", position: "relative", maskImage: "linear-gradient(90deg, transparent, #000 5%, #000 95%, transparent)" }}>
        <div style={{
          display: "inline-flex", gap: 40,
          whiteSpace: "nowrap",
          animation: "scroll 60s linear infinite",
        }}>
          {[...news, ...news].map((n, i) => (
            <span key={i} style={{ display: "inline-flex", alignItems: "center", gap: 8, fontSize: 12 }}>
              <span className="mono" style={{ color: "var(--muted)" }}>{n.time}</span>
              <span style={{ color: "var(--cyan)", fontWeight: 600, fontSize: 10, letterSpacing: "0.08em" }}>{n.src.toUpperCase()}</span>
              <span style={{ color: "var(--text-2)" }}>{n.text}</span>
            </span>
          ))}
        </div>
      </div>
      <style>{`@keyframes scroll { from { transform: translateX(0); } to { transform: translateX(-50%); } }`}</style>
    </div>
  );
}


// ─── Holdings Table (terminal-styled) ────────────────────────────────────
function HoldingsTerm({ data, ccy, limit }) {
  const isPayPay = data.mode === "paypay";
  const defaultSort = isPayPay ? "total_bought" : "mv";
  const [sortBy, setSortBy] = React.useState(defaultSort);
  const [dir, setDir]       = React.useState("desc");

  function toggle(col) {
    if (sortBy === col) setDir(d => d === "asc" ? "desc" : "asc");
    else { setSortBy(col); setDir("desc"); }
  }

  let rows = [...data.holdings].sort((a, b) => {
    const va = a[sortBy], vb = b[sortBy];
    const c  = typeof va === "string" ? va.localeCompare(vb) : (va - vb);
    return dir === "asc" ? c : -c;
  });
  if (limit) rows = rows.slice(0, limit);

  const HCol = ({ id, children, align = "right" }) => (
    <th onClick={() => toggle(id)} style={{ textAlign: align, cursor: "pointer", userSelect: "none", color: sortBy === id ? "var(--text)" : "var(--muted)" }}>
      {children}{sortBy === id && <span style={{ fontSize: 9, marginLeft: 3 }}>{dir === "asc" ? "▲" : "▼"}</span>}
    </th>
  );

  if (isPayPay) {
    // ── PayPay mode: show Excel-sourced columns ──────────────────────────────
    return (
      <div className="card" style={{ overflow: "hidden" }}>
        <CardHd
          eyebrow="Portfolio"
          title="Holdings"
          sub={`${data.holdings.length} positions · PayPay Securities`}
          right={<span style={{ fontSize: 10.5, color: "var(--cyan)", background: "rgba(6,182,212,0.10)", border: "1px solid rgba(6,182,212,0.25)", padding: "3px 8px", borderRadius: 4, fontWeight: 600 }}>LIVE DATA</span>}
        />
        <div style={{ overflow: "auto", maxHeight: limit ? "none" : 560 }}>
          <table className="term">
            <thead>
              <tr>
                <HCol id="name" align="left">Company</HCol>
                <HCol id="total_bought">Total Bought</HCol>
                <HCol id="total_sold">Total Sold</HCol>
                <HCol id="net_invested">Net Invested</HCol>
                <HCol id="dividends">Dividends</HCol>
                <HCol id="buy_trades">Trades</HCol>
                <HCol id="weight">Weight</HCol>
                <th style={{ textAlign: "right" }}>Trend</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((h, idx) => (
                <tr key={idx}>
                  <td style={{ textAlign: "left" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <div style={{
                        width: 30, height: 30, borderRadius: 6,
                        background: "rgba(59,130,246,0.10)",
                        border: "1px solid rgba(59,130,246,0.20)",
                        display: "grid", placeItems: "center",
                        fontFamily: "JetBrains Mono", fontSize: 9, fontWeight: 600,
                        color: "var(--cyan)", flexShrink: 0,
                      }}>{idx + 1}</div>
                      <span style={{ fontSize: 12.5, fontWeight: 500, color: "var(--text)" }}>{h.name}</span>
                    </div>
                  </td>
                  <td className="mono" style={{ textAlign: "right", fontWeight: 500, color: "var(--text-2)" }}>{fmtJPY(h.total_bought, ccy)}</td>
                  <td className="mono" style={{ textAlign: "right", fontWeight: 500, color: h.total_sold > 0 ? "var(--warn)" : "var(--muted)" }}>{h.total_sold > 0 ? fmtJPY(h.total_sold, ccy) : "—"}</td>
                  <td className="mono" style={{ textAlign: "right", fontWeight: 600, color: "var(--pos)" }}>{fmtJPY(h.net_invested, ccy)}</td>
                  <td className="mono" style={{ textAlign: "right", fontWeight: 600, color: h.dividends > 0 ? "var(--warn)" : "var(--muted)" }}>{h.dividends > 0 ? fmtJPY(h.dividends, ccy) : "—"}</td>
                  <td className="mono" style={{ textAlign: "right", color: "var(--text-2)" }}>{h.buy_trades}</td>
                  <td style={{ textAlign: "right" }}>
                    <div style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                      <div style={{ width: 44 }}>
                        <MiniMeter value={h.weight} max={0.25} color="var(--cyan)" height={3} />
                      </div>
                      <span className="mono" style={{ fontSize: 11, color: "var(--text-2)", width: 34, textAlign: "right" }}>{(h.weight * 100).toFixed(1)}%</span>
                    </div>
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <div style={{ display: "flex", justifyContent: "flex-end", color: "var(--cyan)" }}>
                      <Spark values={h.spark || []} width={52} height={20} color="currentColor" glow={false} strokeWidth={1.2} filled={false} />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  // ── Demo / live mode: original columns ───────────────────────────────────
  const accountTag = {
    tsumitate: { label: "NISA·T", color: "var(--pos)" },
    growth:    { label: "NISA·G", color: "var(--cyan)" },
    tokutei:   { label: "Tokutei",color: "var(--muted)" },
    ippan:     { label: "General",color: "var(--muted)" },
  };

  return (
    <div className="card" style={{ overflow: "hidden" }}>
      <CardHd
        eyebrow="Portfolio"
        title="Holdings"
        sub={`${data.holdings.length} positions · live`}
        right={<button className="btn btn--ghost" style={{ fontSize: 11.5 }}>View all →</button>}
      />
      <div style={{ overflow: "auto", maxHeight: limit ? "none" : 540 }}>
        <table className="term">
          <thead>
            <tr>
              <HCol id="code" align="left">Symbol</HCol>
              <th style={{ textAlign: "left" }}>Account</th>
              <HCol id="last">Last</HCol>
              <HCol id="day">Day</HCol>
              <HCol id="mv">Market Value</HCol>
              <HCol id="pnl">P/L</HCol>
              <HCol id="pnlPct">Return</HCol>
              <HCol id="weight">Weight</HCol>
              <th style={{ textAlign: "right" }}>30d</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(h => {
              const at    = accountTag[h.account];
              const spark = data.portSeries.slice(-30);
              return (
                <tr key={h.code}>
                  <td style={{ textAlign: "left" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <div style={{
                        width: 32, height: 32, borderRadius: 6,
                        background: "rgba(59,130,246,0.10)",
                        border: "1px solid rgba(59,130,246,0.25)",
                        display: "grid", placeItems: "center",
                        fontFamily: "JetBrains Mono", fontSize: 9.5, fontWeight: 600,
                        color: "var(--cyan)",
                        boxShadow: "inset 0 0 8px rgba(59,130,246,0.10)",
                      }}>{h.code}</div>
                      <div style={{ minWidth: 0 }}>
                        <div style={{ fontSize: 12.5, fontWeight: 500, color: "var(--text)" }}>{h.en}</div>
                        <div style={{ fontSize: 10.5, color: "var(--muted)" }}>{h.sector}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span style={{ fontSize: 9.5, fontWeight: 600, letterSpacing: "0.06em", color: at.color, padding: "2px 6px", border: "1px solid currentColor", borderRadius: 3, opacity: 0.9 }}>{at.label}</span>
                  </td>
                  <td className="mono" style={{ textAlign: "right", fontWeight: 500 }}>{fmtJPY(h.last, ccy)}</td>
                  <td style={{ textAlign: "right" }}>
                    <span className={"mono " + (h.day >= 0 ? "pos" : "neg")} style={{ fontWeight: 500 }}>
                      {h.day >= 0 ? "+" : ""}{(h.day * 100).toFixed(2)}%
                    </span>
                  </td>
                  <td className="mono" style={{ textAlign: "right", fontWeight: 500 }}>{fmtJPY(h.mv, ccy)}</td>
                  <td style={{ textAlign: "right" }}>
                    <span className={"mono " + (h.pnl >= 0 ? "pos" : "neg")} style={{ fontWeight: 500 }}>
                      {h.pnl >= 0 ? "+" : "−"}{fmtJPY(Math.abs(h.pnl), ccy, true)}
                    </span>
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <span className={"mono " + (h.pnlPct >= 0 ? "pos" : "neg")} style={{ fontWeight: 500 }}>
                      {h.pnlPct >= 0 ? "+" : ""}{(h.pnlPct * 100).toFixed(2)}%
                    </span>
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <div style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
                      <div style={{ width: 50 }}><MiniMeter value={h.weight} max={0.2} color="var(--cyan)" height={3} /></div>
                      <span className="mono" style={{ fontSize: 11.5, color: "var(--text-2)", width: 38, textAlign: "right" }}>{(h.weight * 100).toFixed(1)}%</span>
                    </div>
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <div style={{ display: "flex", justifyContent: "flex-end", color: h.pnl >= 0 ? "var(--pos)" : "var(--neg)" }}>
                      <Spark values={spark} width={56} height={20} color="currentColor" glow={false} strokeWidth={1.2} filled={false} />
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

Object.assign(window, { AIInsights, Watchlist, MarketOverview, NewsTicker, HoldingsTerm });
