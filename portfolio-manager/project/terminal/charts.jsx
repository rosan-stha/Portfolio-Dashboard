// Charts — Equity Curve, Allocation Donut, Risk Decomposition, Correlation Matrix

// ─── Equity Curve ──────────────────────────────────────────────────────────
function EquityCurve({ data, ccy, period }) {
  const periodMap = { "1D": 5, "1W": 5, "1M": 22, "3M": 66, "YTD": 110, "1Y": 252, "ALL": 252 };
  const n = periodMap[period] || 252;
  const equity = data.equity.slice(-n);
  const topix  = data.topixSeries.slice(-n).map(v => v / data.topixSeries.slice(-n)[0] * equity[0]);
  const nikkei = data.nikkeiSeries.slice(-n).map(v => v / data.nikkeiSeries.slice(-n)[0] * equity[0]);
  const dates  = data.dates.slice(-n);

  const W = 1000, H = 320;
  const PL = 60, PR = 18, PT = 20, PB = 32;
  const innerW = W - PL - PR, innerH = H - PT - PB;
  const all = [...equity, ...topix, ...nikkei];
  const minV = Math.min(...all), maxV = Math.max(...all);
  const pad = (maxV - minV) * 0.08;
  const yMin = minV - pad, yMax = maxV + pad;
  const x = (i) => PL + (i / (equity.length - 1)) * innerW;
  const y = (v) => PT + (1 - (v - yMin) / (yMax - yMin)) * innerH;
  const path = (arr) => arr.map((v, i) => (i === 0 ? "M" : "L") + x(i).toFixed(1) + " " + y(v).toFixed(1)).join(" ");
  const fillP = (arr) => path(arr) + ` L ${x(arr.length - 1).toFixed(1)} ${H - PB} L ${x(0).toFixed(1)} ${H - PB} Z`;

  const yTicks = []; for (let i = 0; i <= 4; i++) yTicks.push(yMin + ((yMax - yMin) / 4) * i);
  const xTickIdxs = [0, Math.floor(equity.length * 0.25), Math.floor(equity.length * 0.5), Math.floor(equity.length * 0.75), equity.length - 1];

  const [hover, setHover] = React.useState(null);
  const svgRef = React.useRef(null);
  function onMove(e) {
    const r = svgRef.current.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width * W;
    const i = Math.max(0, Math.min(equity.length - 1, Math.round((px - PL) / innerW * (equity.length - 1))));
    setHover(i);
  }

  const portReturn = (equity[equity.length - 1] - equity[0]) / equity[0];

  return (
    <div className="card card--glow" style={{ overflow: "hidden", height: "100%" }}>
      <CardHd
        eyebrow="Performance Analytics"
        title="Equity Curve"
        sub={`Portfolio value vs benchmarks · ${period}`}
        right={
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            {[
              { l: "Portfolio",  c: "var(--cyan)",  v: portReturn,     w: 2.5, dash: null },
              { l: "TOPIX",      c: "#94A3B8",      v: (topix[topix.length-1]-topix[0])/topix[0],     w: 1.2, dash: "5 3" },
              { l: "Nikkei 225", c: "#F59E0B",      v: (nikkei[nikkei.length-1]-nikkei[0])/nikkei[0], w: 1.2, dash: "2 3" },
            ].map((s, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 7, fontSize: 11.5 }}>
                <span style={{ width: 18, height: 0, borderTop: `${s.w}px ${s.dash ? "dashed" : "solid"} ${s.c}`, filter: s.dash ? "none" : "drop-shadow(0 0 4px " + s.c + ")" }} />
                <span style={{ color: "var(--text-2)" }}>{s.l}</span>
                <span className={"mono " + (s.v >= 0 ? "pos" : "neg")} style={{ fontWeight: 500 }}>
                  {s.v >= 0 ? "+" : ""}{(s.v * 100).toFixed(2)}%
                </span>
              </div>
            ))}
          </div>
        }
      />
      <div style={{ padding: "12px 16px 16px" }}>
        <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", height: H, display: "block", cursor: "crosshair" }} onMouseMove={onMove} onMouseLeave={() => setHover(null)}>
          <defs>
            <linearGradient id="ec-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#06B6D4" stopOpacity="0.35" />
              <stop offset="60%" stopColor="#06B6D4" stopOpacity="0.05" />
              <stop offset="100%" stopColor="#06B6D4" stopOpacity="0" />
            </linearGradient>
            <linearGradient id="ec-line" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#3B82F6" />
              <stop offset="100%" stopColor="#06B6D4" />
            </linearGradient>
          </defs>
          {/* Grid */}
          {yTicks.map((t, i) => (
            <g key={i}>
              <line x1={PL} x2={W - PR} y1={y(t)} y2={y(t)} stroke="var(--grid)" />
              <text x={PL - 10} y={y(t) + 3} fontSize="10" fontFamily="JetBrains Mono" textAnchor="end" fill="var(--muted)">
                {SYM_T[ccy]}{((t * FX_T[ccy]) / 1e6).toFixed(1)}M
              </text>
            </g>
          ))}
          {/* X labels */}
          {xTickIdxs.map((idx, i) => (
            <text key={i} x={x(idx)} y={H - 10} fontSize="10" fontFamily="JetBrains Mono" textAnchor="middle" fill="var(--muted)">
              {dates[idx].toLocaleDateString("en-GB", { day: "2-digit", month: "short" })}
            </text>
          ))}
          {/* Benchmarks first */}
          <path d={path(topix)}  fill="none" stroke="#94A3B8" strokeWidth="1.2" strokeDasharray="5 3" opacity="0.7" />
          <path d={path(nikkei)} fill="none" stroke="#F59E0B" strokeWidth="1.2" strokeDasharray="2 3" opacity="0.6" />
          {/* Portfolio fill */}
          <path d={fillP(equity)} fill="url(#ec-fill)" />
          <path d={path(equity)} fill="none" stroke="url(#ec-line)" strokeWidth="2.5" style={{ filter: "drop-shadow(0 0 6px rgba(6,182,212,0.6))" }} />
          {/* Endpoint */}
          <circle cx={x(equity.length - 1)} cy={y(equity[equity.length - 1])} r="4" fill="var(--cyan)" style={{ filter: "drop-shadow(0 0 6px var(--cyan))" }} />
          <circle cx={x(equity.length - 1)} cy={y(equity[equity.length - 1])} r="8" fill="none" stroke="var(--cyan)" strokeWidth="1" opacity="0.4">
            <animate attributeName="r" from="4" to="16" dur="1.6s" repeatCount="indefinite" />
            <animate attributeName="opacity" from="0.6" to="0" dur="1.6s" repeatCount="indefinite" />
          </circle>

          {/* Crosshair */}
          {hover != null && (
            <g>
              <line x1={x(hover)} x2={x(hover)} y1={PT} y2={H - PB} stroke="var(--cyan)" strokeWidth="1" strokeDasharray="3 3" opacity="0.6" />
              <line x1={PL} x2={W - PR} y1={y(equity[hover])} y2={y(equity[hover])} stroke="var(--cyan)" strokeWidth="1" strokeDasharray="3 3" opacity="0.3" />
              <circle cx={x(hover)} cy={y(equity[hover])} r="4.5" fill="var(--bg)" stroke="var(--cyan)" strokeWidth="2" />
            </g>
          )}
        </svg>
        {hover != null && (
          <div style={{
            marginTop: -38, marginLeft: PL,
            display: "inline-flex", gap: 14,
            padding: "6px 10px",
            background: "rgba(11,18,32,0.92)",
            border: "1px solid var(--border-glow)",
            borderRadius: 6, fontSize: 11,
            boxShadow: "0 8px 24px -8px rgba(6,182,212,0.4)",
          }}>
            <span className="mono" style={{ color: "var(--muted)" }}>
              {dates[hover].toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" })}
            </span>
            <span style={{ display: "inline-flex", alignItems: "center", gap: 5 }}>
              <span style={{ width: 8, height: 2, background: "var(--cyan)", display: "inline-block", boxShadow: "0 0 6px var(--cyan)" }} />
              <span className="mono pos" style={{ fontWeight: 500 }}>
                {fmtJPY(equity[hover], ccy)}
              </span>
            </span>
          </div>
        )}
      </div>
    </div>
  );
}


// ─── Allocation Donut ──────────────────────────────────────────────────────
function AllocationDonut({ data, ccy }) {
  const { sectors, total_mv } = data;
  const COLORS = {
    "Tech":        "#06B6D4",
    "Financial":   "#3B82F6",
    "Industrial":  "#8B5CF6",
    "Auto":        "#F59E0B",
    "Trading":     "#10B981",
    "Telecom":     "#EC4899",
    "Materials":   "#64748B",
    "Healthcare":  "#84CC16",
    "Services":    "#F97316",
  };
  const R_OUT = 92, R_IN = 60, CX = 110, CY = 110;
  let acc = 0;
  const segs = sectors.map(s => {
    const start = acc; acc += s.pct;
    return { ...s, start, end: acc, color: COLORS[s.name] || "#64748B" };
  });

  function arc(start, end, ri = R_IN, ro = R_OUT) {
    const a0 = start * 2 * Math.PI - Math.PI / 2;
    const a1 = end * 2 * Math.PI - Math.PI / 2;
    const x0 = CX + ro * Math.cos(a0), y0 = CY + ro * Math.sin(a0);
    const x1 = CX + ro * Math.cos(a1), y1 = CY + ro * Math.sin(a1);
    const x2 = CX + ri * Math.cos(a1), y2 = CY + ri * Math.sin(a1);
    const x3 = CX + ri * Math.cos(a0), y3 = CY + ri * Math.sin(a0);
    const large = (end - start) > 0.5 ? 1 : 0;
    return `M ${x0} ${y0} A ${ro} ${ro} 0 ${large} 1 ${x1} ${y1} L ${x2} ${y2} A ${ri} ${ri} 0 ${large} 0 ${x3} ${y3} Z`;
  }

  const [hover, setHover] = React.useState(null);

  return (
    <div className="card" style={{ overflow: "hidden", height: "100%" }}>
      <CardHd eyebrow="Asset Allocation" title="Sector Exposure" sub="By market value" />
      <div style={{ padding: 16, display: "flex", alignItems: "center", gap: 18 }}>
        <svg width="220" height="220" viewBox="0 0 220 220" style={{ flexShrink: 0 }}>
          <defs>
            {segs.map((s, i) => (
              <filter key={i} id={"glow-" + i}>
                <feGaussianBlur stdDeviation="4" />
              </filter>
            ))}
          </defs>
          {segs.map((s, i) => (
            <path key={i} d={arc(s.start, s.end)} fill={s.color}
                  opacity={hover != null && hover !== i ? 0.4 : 1}
                  onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(null)}
                  style={{
                    transition: "all 200ms",
                    filter: hover === i ? `drop-shadow(0 0 10px ${s.color})` : "none",
                    transform: hover === i ? "scale(1.02)" : "scale(1)",
                    transformOrigin: "center",
                    cursor: "pointer",
                  }} />
          ))}
          {/* Center */}
          <text x={CX} y={CY - 6} textAnchor="middle" fontSize="9.5" fill="var(--muted)" fontFamily="JetBrains Mono" letterSpacing="0.1em">
            {hover != null ? segs[hover].name.toUpperCase() : "TOTAL"}
          </text>
          <text x={CX} y={CY + 14} textAnchor="middle" fontSize="18" fontWeight="600" fill="var(--text)" fontFamily="JetBrains Mono">
            {hover != null ? (segs[hover].pct * 100).toFixed(1) + "%" : fmtJPY(total_mv, ccy, true)}
          </text>
          <text x={CX} y={CY + 30} textAnchor="middle" fontSize="10" fill="var(--muted)" fontFamily="Inter">
            {hover != null ? fmtJPY(segs[hover].mv, ccy, true) : sectors.length + " sectors"}
          </text>
        </svg>
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 6 }}>
          {segs.map((s, i) => (
            <div key={i}
                 onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(null)}
                 style={{
                   display: "flex", alignItems: "center", gap: 10,
                   fontSize: 12, padding: "3px 0",
                   opacity: hover != null && hover !== i ? 0.5 : 1,
                   transition: "opacity 160ms",
                   cursor: "pointer",
                 }}>
              <span style={{ width: 8, height: 8, borderRadius: 2, background: s.color, boxShadow: `0 0 6px ${s.color}`, flexShrink: 0 }} />
              <span style={{ flex: 1, color: "var(--text-2)" }}>{s.name}</span>
              <span className="mono" style={{ color: "var(--muted)", fontSize: 11 }}>{fmtJPY(s.mv, ccy, true)}</span>
              <span className="mono" style={{ width: 46, textAlign: "right", color: "var(--text)", fontWeight: 500 }}>{(s.pct * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}


// ─── Risk Decomposition ───────────────────────────────────────────────────
function RiskDecomp({ data, ccy }) {
  const { riskDecomp, risk } = data;
  return (
    <div className="card" style={{ overflow: "hidden", height: "100%" }}>
      <CardHd
        eyebrow="Risk Analysis"
        title="Risk Decomposition"
        sub="Variance contribution by position"
        right={
          <div style={{ display: "flex", gap: 12 }}>
            {[
              ["Vol", (risk.volAnn * 100).toFixed(1) + "%"],
              ["Beta", risk.beta.toFixed(2)],
              ["MaxDD", (risk.maxDD * 100).toFixed(1) + "%"],
            ].map(([l, v], i) => (
              <div key={i} style={{ textAlign: "right" }}>
                <div style={{ fontSize: 9.5, color: "var(--muted)", letterSpacing: "0.08em", textTransform: "uppercase" }}>{l}</div>
                <div className="mono" style={{ fontSize: 13, color: "var(--text)", fontWeight: 500 }}>{v}</div>
              </div>
            ))}
          </div>
        }
      />
      <div style={{ padding: 16, display: "flex", flexDirection: "column", gap: 11 }}>
        {riskDecomp.map((r, i) => (
          <div key={i}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4, fontSize: 12 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span className="mono" style={{ color: "var(--muted)", fontSize: 10.5 }}>{r.code}</span>
                <span style={{ color: "var(--text-2)" }}>{r.en}</span>
                <span className="pill" style={{ fontSize: 9.5 }}>{r.sector}</span>
              </div>
              <div className="mono" style={{ color: "var(--text)", fontWeight: 500 }}>{(r.pct * 100).toFixed(1)}%</div>
            </div>
            <div style={{ height: 6, background: "rgba(148,163,184,0.08)", borderRadius: 3, overflow: "hidden", position: "relative" }}>
              <div style={{
                position: "absolute", left: 0, top: 0, bottom: 0,
                width: (r.pct * 100) + "%",
                background: `linear-gradient(90deg, rgba(59,130,246,0.6), rgba(6,182,212,0.95))`,
                boxShadow: "0 0 8px rgba(6,182,212,0.5)",
                borderRadius: 3,
                animation: `slidein 600ms ease-out ${i * 80}ms backwards`,
              }} />
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 3, fontSize: 10, color: "var(--muted)" }}>
              <span>Weight <span className="mono" style={{ color: "var(--text-2)" }}>{(r.weight * 100).toFixed(1)}%</span></span>
              <span>σ <span className="mono" style={{ color: "var(--text-2)" }}>{(r.vol * 100).toFixed(1)}%</span></span>
            </div>
          </div>
        ))}
      </div>
      <style>{`@keyframes slidein { from { width: 0 !important; } }`}</style>
    </div>
  );
}


// ─── Correlation Heatmap ──────────────────────────────────────────────────
function CorrelationHeatmap({ data }) {
  const { corrSyms, corrMatrix } = data;
  const N = corrSyms.length;
  const cell = 38;
  const labelW = 88;
  const W = labelW + N * cell + 8;
  const H = 24 + N * cell + 8;

  function colorFor(v) {
    // -1..1 → blue ↔ neutral ↔ cyan/red intensity
    if (v >= 0) {
      const t = v; // 0..1
      const o = 0.08 + t * 0.7;
      return `rgba(6, 182, 212, ${o})`;
    } else {
      const t = -v;
      return `rgba(239, 68, 68, ${0.08 + t * 0.5})`;
    }
  }

  return (
    <div className="card" style={{ overflow: "hidden", height: "100%" }}>
      <CardHd eyebrow="Correlation" title="Position Correlation Matrix" sub="90-day rolling · top 8 holdings"
        right={
          <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11 }}>
            <span style={{ color: "var(--muted)" }}>−1</span>
            <span style={{ width: 100, height: 8, borderRadius: 4, background: "linear-gradient(90deg, #EF4444, rgba(148,163,184,0.15), #06B6D4)" }} />
            <span style={{ color: "var(--muted)" }}>+1</span>
          </div>
        }
      />
      <div style={{ padding: 16, overflowX: "auto" }}>
        <svg width={W} height={H} style={{ display: "block" }}>
          {/* Column labels */}
          {corrSyms.map((s, j) => (
            <text key={j} x={labelW + j * cell + cell / 2} y={16} fontSize="10" fontFamily="JetBrains Mono" textAnchor="middle" fill="var(--muted)">{s.code}</text>
          ))}
          {/* Rows */}
          {corrSyms.map((s, i) => (
            <g key={i}>
              <text x={labelW - 10} y={24 + i * cell + cell / 2 + 4} fontSize="10" fontFamily="JetBrains Mono" textAnchor="end" fill="var(--muted)">{s.code}</text>
              {corrMatrix[i].map((v, j) => (
                <g key={j}>
                  <rect x={labelW + j * cell} y={24 + i * cell} width={cell - 2} height={cell - 2}
                        rx={3} fill={colorFor(v)}
                        stroke={i === j ? "var(--cyan)" : "transparent"}
                        strokeWidth={i === j ? 1 : 0} />
                  <text x={labelW + j * cell + (cell - 2) / 2} y={24 + i * cell + (cell - 2) / 2 + 3}
                        fontSize="9.5" fontFamily="JetBrains Mono" textAnchor="middle"
                        fill={Math.abs(v) > 0.5 ? "#fff" : "var(--text-2)"}>
                    {v.toFixed(2)}
                  </text>
                </g>
              ))}
            </g>
          ))}
        </svg>
      </div>
    </div>
  );
}

Object.assign(window, { EquityCurve, AllocationDonut, RiskDecomp, CorrelationHeatmap });
