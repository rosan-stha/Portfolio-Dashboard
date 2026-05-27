// Performance chart — portfolio vs TOPIX vs Nikkei, with crosshair

function PerformanceChart({ data, period, ccy }) {
  const periodToDays = { "1D": 1, "1W": 5, "1M": 22, "3M": 66, "YTD": 110, "1Y": 252, "ALL": 252 };
  const days = periodToDays[period] || 252;
  const slice = (arr) => arr.slice(-days);

  const port   = slice(data.portSeries);
  const topix  = slice(data.topixSeries);
  const nikkei = slice(data.nikkeiSeries);
  const dates  = slice(data.dates);

  // Rebase all to 0% at period start
  const rebase = (s) => s.map(v => (v / s[0] - 1) * 100);
  const portR   = rebase(port);
  const topixR  = rebase(topix);
  const nikkeiR = rebase(nikkei);

  const all = [...portR, ...topixR, ...nikkeiR];
  const minY = Math.min(...all, 0);
  const maxY = Math.max(...all, 0);
  const padY = (maxY - minY) * 0.12;
  const yMin = Math.floor((minY - padY) / 5) * 5;
  const yMax = Math.ceil((maxY + padY) / 5) * 5;

  const W = 900, H = 320;
  const PL = 50, PR = 16, PT = 18, PB = 26;
  const innerW = W - PL - PR;
  const innerH = H - PT - PB;

  const x = (i) => PL + (i / (portR.length - 1)) * innerW;
  const y = (v) => PT + (1 - (v - yMin) / (yMax - yMin)) * innerH;

  const linePath = (arr) => arr.map((v, i) => (i === 0 ? "M" : "L") + x(i).toFixed(1) + " " + y(v).toFixed(1)).join(" ");
  const fillPath = (arr) => linePath(arr) + ` L ${x(arr.length - 1).toFixed(1)} ${y(0).toFixed(1)} L ${x(0).toFixed(1)} ${y(0).toFixed(1)} Z`;

  // Y-axis ticks
  const yTicks = [];
  const step = (yMax - yMin) / 4;
  for (let i = 0; i <= 4; i++) yTicks.push(yMin + step * i);

  // X-axis ticks (4-5 labels)
  const xTickIdxs = [];
  const nTicks = 5;
  for (let i = 0; i < nTicks; i++) xTickIdxs.push(Math.round((portR.length - 1) * (i / (nTicks - 1))));

  // Crosshair
  const [hover, setHover] = React.useState(null);
  const svgRef = React.useRef(null);
  function onMove(e) {
    const rect = svgRef.current.getBoundingClientRect();
    const px = e.clientX - rect.left;
    const ratio = px / rect.width;
    const i = Math.max(0, Math.min(portR.length - 1, Math.round((ratio * W - PL) / innerW * (portR.length - 1))));
    setHover(i);
  }

  const endVals = {
    port: portR[portR.length - 1],
    topix: topixR[topixR.length - 1],
    nikkei: nikkeiR[nikkeiR.length - 1],
  };

  const seriesMeta = [
    { id: "port",   label: "Portfolio",     color: "var(--accent)",        width: 2,    val: endVals.port,   filled: true },
    { id: "topix",  label: "TOPIX",         color: "var(--chart-bench-1)", width: 1.25, val: endVals.topix,  dash: "4 3" },
    { id: "nikkei", label: "Nikkei 225",    color: "var(--chart-bench-2)", width: 1.25, val: endVals.nikkei, dash: "1 3" },
  ];

  return (
    <div className="card" style={{ overflow: "hidden" }}>
      <CardHeader
        eyebrow="Performance"
        title="Portfolio vs Benchmarks"
        sub={`Rebased to 0% at start of ${period}`}
        right={
          <div style={{ display: "flex", gap: 14, alignItems: "center" }}>
            {seriesMeta.map(s => (
              <div key={s.id} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11.5 }}>
                <span style={{ width: 16, height: 0, borderTop: `${s.width || 1.5}px ${s.dash ? "dashed" : "solid"} ${s.color}` }} />
                <span style={{ color: "var(--text-2)" }}>{s.label}</span>
                <span className={"mono " + (s.val >= 0 ? "gain" : "loss")} style={{ fontWeight: 500 }}>
                  {s.val >= 0 ? "+" : ""}{s.val.toFixed(2)}%
                </span>
              </div>
            ))}
          </div>
        }
      />

      <div style={{ padding: "12px 16px 16px" }}>
        <svg
          ref={svgRef}
          viewBox={`0 0 ${W} ${H}`}
          style={{ width: "100%", height: H, display: "block", cursor: "crosshair" }}
          onMouseMove={onMove}
          onMouseLeave={() => setHover(null)}
        >
          {/* Grid */}
          {yTicks.map((t, i) => (
            <g key={i}>
              <line x1={PL} x2={W - PR} y1={y(t)} y2={y(t)} stroke="var(--grid)" strokeWidth="1" />
              <text x={PL - 8} y={y(t) + 3} fontSize="10" fontFamily="IBM Plex Mono" textAnchor="end" fill="var(--muted)">
                {(t >= 0 ? "+" : "") + t.toFixed(0) + "%"}
              </text>
            </g>
          ))}
          {/* Zero line */}
          <line x1={PL} x2={W - PR} y1={y(0)} y2={y(0)} stroke="var(--border-2)" strokeWidth="1" strokeDasharray="2 2" />

          {/* X labels */}
          {xTickIdxs.map((idx, i) => (
            <text key={i} x={x(idx)} y={H - 8} fontSize="10" fontFamily="IBM Plex Mono" textAnchor="middle" fill="var(--muted)">
              {dates[idx].toLocaleDateString("en-GB", { day: "2-digit", month: "short" })}
            </text>
          ))}

          {/* Portfolio fill */}
          <defs>
            <linearGradient id="port-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.18" />
              <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
            </linearGradient>
          </defs>
          <path d={fillPath(portR)} fill="url(#port-fill)" />

          {/* Lines */}
          <path d={linePath(topixR)}  fill="none" stroke="var(--chart-bench-1)" strokeWidth="1.25" strokeDasharray="4 3" />
          <path d={linePath(nikkeiR)} fill="none" stroke="var(--chart-bench-2)" strokeWidth="1.25" strokeDasharray="1 3" />
          <path d={linePath(portR)}   fill="none" stroke="var(--accent)" strokeWidth="2" />

          {/* Endpoint dots */}
          {[
            { v: portR, c: "var(--accent)", r: 3.5 },
            { v: topixR, c: "var(--chart-bench-1)", r: 2.5 },
            { v: nikkeiR, c: "var(--chart-bench-2)", r: 2.5 },
          ].map((s, i) => (
            <circle key={i} cx={x(s.v.length - 1)} cy={y(s.v[s.v.length - 1])} r={s.r} fill={s.c} />
          ))}

          {/* Crosshair */}
          {hover != null && (
            <g>
              <line x1={x(hover)} x2={x(hover)} y1={PT} y2={H - PB} stroke="var(--text-2)" strokeWidth="1" strokeDasharray="2 2" opacity="0.5" />
              {[
                { v: portR[hover], c: "var(--accent)" },
                { v: topixR[hover], c: "var(--chart-bench-1)" },
                { v: nikkeiR[hover], c: "var(--chart-bench-2)" },
              ].map((s, i) => (
                <circle key={i} cx={x(hover)} cy={y(s.v)} r="3.5" fill="var(--surface)" stroke={s.c} strokeWidth="1.5" />
              ))}
            </g>
          )}
        </svg>

        {/* Crosshair tooltip */}
        {hover != null && (
          <div style={{
            marginTop: -28, marginLeft: PL,
            display: "inline-flex", gap: 14,
            padding: "4px 8px",
            background: "var(--surface-2)",
            border: "1px solid var(--border)",
            borderRadius: 3,
            fontSize: 11,
          }}>
            <span style={{ color: "var(--muted)" }} className="mono">
              {dates[hover].toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" })}
            </span>
            {[
              { id: "port",   v: portR[hover],   c: "var(--accent)",         l: "Port" },
              { id: "topix",  v: topixR[hover],  c: "var(--chart-bench-1)",  l: "TOPIX" },
              { id: "nikkei", v: nikkeiR[hover], c: "var(--chart-bench-2)",  l: "N225" },
            ].map(s => (
              <span key={s.id} style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
                <span style={{ width: 8, height: 2, background: s.c, display: "inline-block" }} />
                <span style={{ color: "var(--text-2)" }}>{s.l}</span>
                <span className={"mono " + (s.v >= 0 ? "gain" : "loss")}>
                  {s.v >= 0 ? "+" : ""}{s.v.toFixed(2)}%
                </span>
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

window.PerformanceChart = PerformanceChart;
