// Holdings table + sector allocation donut + concentration risk card

function HoldingsTable({ data, ccy, limit }) {
  const [sortBy, setSortBy] = React.useState("mv");
  const [sortDir, setSortDir] = React.useState("desc");
  const [accountFilter, setAccountFilter] = React.useState("all");

  function toggleSort(col) {
    if (sortBy === col) setSortDir(d => d === "asc" ? "desc" : "asc");
    else { setSortBy(col); setSortDir("desc"); }
  }

  let rows = [...data.holdings];
  if (accountFilter !== "all") rows = rows.filter(h => h.account === accountFilter);
  rows.sort((a, b) => {
    const va = a[sortBy], vb = b[sortBy];
    const cmp = typeof va === "string" ? va.localeCompare(vb) : (va - vb);
    return sortDir === "asc" ? cmp : -cmp;
  });
  if (limit) rows = rows.slice(0, limit);

  const accountTag = {
    tsumitate: { label: "つみたて", cls: "tag--nisa-t" },
    growth:    { label: "成長",     cls: "tag--nisa-g" },
    tokutei:   { label: "特定",     cls: "tag--tokutei" },
    ippan:     { label: "一般",     cls: "tag--tokutei" },
  };

  const SortHeader = ({ id, children, align = "right" }) => (
    <th onClick={() => toggleSort(id)} style={{
      textAlign: align,
      cursor: "pointer",
      userSelect: "none",
      padding: "8px 10px",
      fontSize: 10.5,
      fontWeight: 600,
      letterSpacing: "0.08em",
      textTransform: "uppercase",
      color: sortBy === id ? "var(--text)" : "var(--muted)",
      borderBottom: "1px solid var(--border)",
      whiteSpace: "nowrap",
    }}>
      {children}
      {sortBy === id && <span style={{ marginLeft: 4, fontSize: 9 }}>{sortDir === "asc" ? "▲" : "▼"}</span>}
    </th>
  );

  return (
    <div className="card" style={{ overflow: "hidden" }}>
      <CardHeader
        eyebrow="Holdings"
        title={`${data.holdings.length} positions`}
        sub="Live prices · sortable"
        right={
          <div style={{ display: "flex", gap: 4 }}>
            {[
              { id: "all",       label: "All" },
              { id: "tsumitate", label: "つみたて" },
              { id: "growth",    label: "成長" },
              { id: "tokutei",   label: "特定" },
            ].map(f => (
              <button key={f.id} onClick={() => setAccountFilter(f.id)} style={{
                border: 0, background: accountFilter === f.id ? "var(--bg-2)" : "transparent",
                color: accountFilter === f.id ? "var(--text)" : "var(--muted)",
                padding: "4px 8px", fontSize: 11, borderRadius: 2,
                cursor: "pointer", fontFamily: "inherit",
                fontWeight: accountFilter === f.id ? 600 : 500,
              }}>{f.label}</button>
            ))}
          </div>
        }
      />

      <div style={{ overflow: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12.5 }}>
          <thead>
            <tr>
              <SortHeader id="code"   align="left">Ticker</SortHeader>
              <th style={hCellStyle}>Account</th>
              <SortHeader id="shares">Shares</SortHeader>
              <SortHeader id="avg">Avg Cost</SortHeader>
              <SortHeader id="last">Last</SortHeader>
              <SortHeader id="day">Day</SortHeader>
              <SortHeader id="mv">Market Value</SortHeader>
              <SortHeader id="pnl">Unrealized P&L</SortHeader>
              <SortHeader id="pnlPct">Return %</SortHeader>
              <SortHeader id="weight">Weight</SortHeader>
              <SortHeader id="yield">Yield</SortHeader>
            </tr>
          </thead>
          <tbody>
            {rows.map((h, i) => {
              const at = accountTag[h.account];
              return (
                <tr key={h.code} style={{
                  borderBottom: "1px solid var(--border)",
                }}
                onMouseEnter={e => e.currentTarget.style.background = "var(--surface-2)"}
                onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
                  <td style={{ ...bCellStyle, textAlign: "left" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <div style={{
                        width: 32, height: 32, borderRadius: 3,
                        background: "var(--bg-2)", border: "1px solid var(--border)",
                        display: "grid", placeItems: "center",
                        fontSize: 10, fontFamily: "IBM Plex Mono", fontWeight: 600,
                        color: "var(--text-2)",
                      }}>{h.code}</div>
                      <div style={{ minWidth: 0 }}>
                        <div className="jp" style={{ fontSize: 12.5, fontWeight: 500, lineHeight: 1.2 }}>{h.name}</div>
                        <div style={{ fontSize: 10.5, color: "var(--muted)" }}>{h.en} · {h.sector}</div>
                      </div>
                    </div>
                  </td>
                  <td style={bCellStyle}>
                    <span className={"tag " + at.cls} style={{ fontSize: 9.5 }}>{at.label}</span>
                  </td>
                  <td style={{ ...bCellStyle, fontFamily: "IBM Plex Mono", textAlign: "right" }}>{h.shares.toLocaleString()}</td>
                  <td style={{ ...bCellStyle, fontFamily: "IBM Plex Mono", textAlign: "right", color: "var(--text-2)" }}>{fmtMoney(h.avg, ccy)}</td>
                  <td style={{ ...bCellStyle, fontFamily: "IBM Plex Mono", textAlign: "right", fontWeight: 500 }}>{fmtMoney(h.last, ccy)}</td>
                  <td style={{ ...bCellStyle, textAlign: "right" }}>
                    <PctDelta value={h.day} size="sm" />
                  </td>
                  <td style={{ ...bCellStyle, fontFamily: "IBM Plex Mono", textAlign: "right", fontWeight: 500 }}>{fmtMoney(h.mv, ccy)}</td>
                  <td style={{ ...bCellStyle, textAlign: "right" }}>
                    <span className={"mono " + (h.pnl >= 0 ? "gain" : "loss")}>
                      {(h.pnl >= 0 ? "+" : "−")}{fmtMoney(Math.abs(h.pnl), ccy)}
                    </span>
                  </td>
                  <td style={{ ...bCellStyle, textAlign: "right" }}>
                    <PctDelta value={h.pnlPct} size="sm" />
                  </td>
                  <td style={{ ...bCellStyle, textAlign: "right" }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 8 }}>
                      <div style={{ width: 48 }}>
                        <MiniBar value={h.weight} max={0.2} color="var(--text-2)" height={3} />
                      </div>
                      <span className="mono" style={{ fontSize: 11.5, color: "var(--text-2)", width: 38, textAlign: "right" }}>{(h.weight * 100).toFixed(1)}%</span>
                    </div>
                  </td>
                  <td style={{ ...bCellStyle, fontFamily: "IBM Plex Mono", textAlign: "right", color: "var(--text-2)" }}>{(h.yield * 100).toFixed(2)}%</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const hCellStyle = {
  textAlign: "left",
  padding: "8px 10px",
  fontSize: 10.5,
  fontWeight: 600,
  letterSpacing: "0.08em",
  textTransform: "uppercase",
  color: "var(--muted)",
  borderBottom: "1px solid var(--border)",
};
const bCellStyle = { padding: "10px", textAlign: "right" };


// ─── Sector Allocation Donut ───────────────────────────────────────────────
function SectorAllocation({ data, ccy }) {
  const { sectors, total_mv } = data;
  const sectorColors = {
    "Tech":        "var(--accent)",
    "Financial":   "#3a6ea5",
    "Industrial":  "#7a5fb8",
    "Auto":        "#c87f10",
    "Trading":     "#2e8b6c",
    "Telecom":     "#a04f7a",
    "Materials":   "#5b6470",
    "Healthcare":  "#88a04f",
    "Services":    "#b8a05f",
  };

  const R_OUT = 78, R_IN = 50, CX = 90, CY = 90;
  let acc = 0;
  const segs = sectors.map(s => {
    const start = acc;
    acc += s.pct;
    return { ...s, start, end: acc, color: sectorColors[s.name] || "var(--muted)" };
  });

  function arcPath(start, end) {
    const a0 = start * 2 * Math.PI - Math.PI / 2;
    const a1 = end   * 2 * Math.PI - Math.PI / 2;
    const x0 = CX + R_OUT * Math.cos(a0);
    const y0 = CY + R_OUT * Math.sin(a0);
    const x1 = CX + R_OUT * Math.cos(a1);
    const y1 = CY + R_OUT * Math.sin(a1);
    const x2 = CX + R_IN  * Math.cos(a1);
    const y2 = CY + R_IN  * Math.sin(a1);
    const x3 = CX + R_IN  * Math.cos(a0);
    const y3 = CY + R_IN  * Math.sin(a0);
    const large = (end - start) > 0.5 ? 1 : 0;
    return `M ${x0} ${y0} A ${R_OUT} ${R_OUT} 0 ${large} 1 ${x1} ${y1} L ${x2} ${y2} A ${R_IN} ${R_IN} 0 ${large} 0 ${x3} ${y3} Z`;
  }

  return (
    <div className="card" style={{ overflow: "hidden" }}>
      <CardHeader eyebrow="Allocation" title="Sector mix" sub="By market value" />
      <div style={{ padding: 16, display: "flex", alignItems: "center", gap: 18 }}>
        <svg width="180" height="180" viewBox="0 0 180 180" style={{ flexShrink: 0 }}>
          {segs.map((s, i) => (
            <path key={i} d={arcPath(s.start, s.end)} fill={s.color} stroke="var(--surface)" strokeWidth="1.5" />
          ))}
          <text x={CX} y={CY - 4} textAnchor="middle" fontSize="10" fill="var(--muted)" fontFamily="IBM Plex Mono" letterSpacing="0.04em">SECTORS</text>
          <text x={CX} y={CY + 14} textAnchor="middle" fontSize="20" fontWeight="500" fill="var(--text)" fontFamily="IBM Plex Mono">{sectors.length}</text>
        </svg>
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 5 }}>
          {segs.map((s, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12 }}>
              <span style={{ width: 8, height: 8, borderRadius: 1, background: s.color, flexShrink: 0 }} />
              <span style={{ flex: 1, color: "var(--text-2)" }}>{s.name}</span>
              <span className="mono" style={{ color: "var(--muted)", fontSize: 11 }}>{fmtMoney(s.mv, ccy, { compact: true })}</span>
              <span className="mono" style={{ width: 44, textAlign: "right", fontSize: 11.5, color: "var(--text)" }}>{(s.pct * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}


// ─── Concentration / Risk Card ────────────────────────────────────────────
function RiskCard({ data, ccy }) {
  const { holdings, total_mv } = data;
  const sorted = [...holdings].sort((a, b) => b.mv - a.mv);
  const top5 = sorted.slice(0, 5);
  const top5Pct = top5.reduce((s, h) => s + h.weight, 0);
  // HHI (Herfindahl-Hirschman Index), 0..1
  const hhi = holdings.reduce((s, h) => s + h.weight * h.weight, 0);
  const effectiveN = 1 / hhi;

  const flags = [];
  if (top5Pct > 0.5) flags.push({ level: "warn",  text: "Top 5 holdings exceed 50% of portfolio" });
  if (sorted[0].weight > 0.15) flags.push({ level: "warn", text: `${sorted[0].name} is ${(sorted[0].weight * 100).toFixed(1)}% of portfolio` });
  const techWeight = holdings.filter(h => h.sector === "Tech").reduce((s, h) => s + h.weight, 0);
  if (techWeight > 0.35) flags.push({ level: "info", text: `Tech sector concentration ${(techWeight * 100).toFixed(1)}%` });

  return (
    <div className="card" style={{ overflow: "hidden" }}>
      <CardHeader eyebrow="Risk" title="Concentration" sub="Diversification check" />
      <div style={{ padding: 16 }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 14 }}>
          <RiskStat label="Top 5"      value={(top5Pct * 100).toFixed(1) + "%"} tone={top5Pct > 0.5 ? "warn" : "ok"} />
          <RiskStat label="HHI"        value={hhi.toFixed(3)}                   tone={hhi > 0.18 ? "warn" : "ok"} sub={hhi > 0.18 ? "concentrated" : "diversified"} />
          <RiskStat label="Effective N" value={effectiveN.toFixed(1)}            tone="neutral" sub={`of ${holdings.length}`} />
        </div>

        <div className="eyebrow" style={{ marginBottom: 6 }}>Top holdings</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          {top5.map((h, i) => (
            <div key={h.code} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12 }}>
              <span className="mono" style={{ width: 36, color: "var(--muted)", fontSize: 10.5 }}>{h.code}</span>
              <span className="jp" style={{ flex: 1, color: "var(--text-2)" }}>{h.name}</span>
              <div style={{ width: 80 }}>
                <MiniBar value={h.weight} max={top5[0].weight} color="var(--accent)" height={3} />
              </div>
              <span className="mono" style={{ width: 44, textAlign: "right", color: "var(--text)" }}>{(h.weight * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>

        {flags.length > 0 && (
          <div style={{ marginTop: 14, paddingTop: 12, borderTop: "1px dashed var(--border)" }}>
            <div className="eyebrow" style={{ marginBottom: 6 }}>Flags</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
              {flags.map((f, i) => (
                <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 8, fontSize: 11.5 }}>
                  <span style={{
                    width: 14, height: 14, borderRadius: 7, flexShrink: 0,
                    background: f.level === "warn" ? "color-mix(in oklab, var(--warn) 18%, transparent)" : "var(--bg-2)",
                    color: f.level === "warn" ? "var(--warn)" : "var(--text-2)",
                    display: "grid", placeItems: "center",
                    fontSize: 9, fontWeight: 700, marginTop: 1,
                  }}>!</span>
                  <span style={{ color: "var(--text-2)" }}>{f.text}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function RiskStat({ label, value, sub, tone }) {
  const color = tone === "warn" ? "var(--warn)" : (tone === "ok" ? "var(--gain)" : "var(--text)");
  return (
    <div style={{ padding: 10, background: "var(--surface-2)", borderRadius: 3, border: "1px solid var(--border)" }}>
      <div className="eyebrow" style={{ fontSize: 9.5, marginBottom: 4 }}>{label}</div>
      <div className="mono" style={{ fontSize: 19, fontWeight: 500, color, letterSpacing: "-0.01em" }}>{value}</div>
      {sub && <div style={{ fontSize: 10.5, color: "var(--muted)", marginTop: 2 }}>{sub}</div>}
    </div>
  );
}

Object.assign(window, { HoldingsTable, SectorAllocation, RiskCard });
