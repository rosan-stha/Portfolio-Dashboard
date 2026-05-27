// Shared primitives for the Terminal

const FX_T = { JPY: 1, USD: 1 / 156.4 };
const SYM_T = { JPY: "¥", USD: "$" };

function fmtJPY(jpy, ccy = "JPY", compact = false) {
  const v = jpy * FX_T[ccy];
  if (compact) {
    if (ccy === "JPY") {
      if (Math.abs(v) >= 1e8) return SYM_T[ccy] + (v / 1e8).toFixed(2) + "B";
      if (Math.abs(v) >= 1e6) return SYM_T[ccy] + (v / 1e6).toFixed(2) + "M";
      if (Math.abs(v) >= 1e3) return SYM_T[ccy] + (v / 1e3).toFixed(1) + "K";
      return SYM_T[ccy] + Math.round(v).toLocaleString();
    } else {
      if (Math.abs(v) >= 1e6) return SYM_T[ccy] + (v / 1e6).toFixed(2) + "M";
      if (Math.abs(v) >= 1e3) return SYM_T[ccy] + (v / 1e3).toFixed(1) + "K";
      return SYM_T[ccy] + v.toFixed(0);
    }
  }
  return SYM_T[ccy] + v.toLocaleString(undefined, { maximumFractionDigits: 0 });
}

function fmtSign(jpy, ccy = "JPY", compact = false) {
  const sign = jpy >= 0 ? "+" : "−";
  return sign + fmtJPY(Math.abs(jpy), ccy, compact);
}

function PctT({ value, withSign = true, size = "md", colorize = true }) {
  const sizes = { sm: 11, md: 13, lg: 17 };
  const sign = value >= 0 ? "+" : "−";
  const cls = colorize ? (value >= 0 ? "pos" : "neg") : "";
  return (
    <span className={"mono " + cls} style={{ fontSize: sizes[size], fontWeight: 500 }}>
      {withSign ? sign : ""}{Math.abs(value * 100).toFixed(2)}%
    </span>
  );
}

function Spark({ values, width = 80, height = 24, color = "var(--cyan)", glow = true, strokeWidth = 1.5, filled = true }) {
  if (!values || values.length < 2) return null;
  const min = Math.min(...values), max = Math.max(...values);
  const range = max - min || 1;
  const stepX = width / (values.length - 1);
  const pts = values.map((v, i) => [i * stepX, height - ((v - min) / range) * (height - 4) - 2]);
  const d = pts.map((p, i) => (i === 0 ? "M" : "L") + p[0].toFixed(2) + " " + p[1].toFixed(2)).join(" ");
  const dF = d + ` L ${width} ${height} L 0 ${height} Z`;
  const id = "sg-" + Math.random().toString(36).slice(2, 8);
  return (
    <svg width={width} height={height} style={{ display: "block", overflow: "visible" }}>
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.35" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      {filled && <path d={dF} fill={`url(#${id})`} />}
      <path d={d} fill="none" stroke={color} strokeWidth={strokeWidth} strokeLinejoin="round" strokeLinecap="round"
            style={{ filter: glow ? `drop-shadow(0 0 4px ${color})` : "none" }} />
    </svg>
  );
}

function Triangle2({ up }) {
  return (
    <svg width="9" height="9" viewBox="0 0 10 10" style={{ display: "inline-block", verticalAlign: "middle" }}>
      {up ? <path d="M5 1.5 L9 8 L1 8 Z" fill="currentColor" />
          : <path d="M5 8.5 L9 2 L1 2 Z" fill="currentColor" />}
    </svg>
  );
}

// Icon set (single-stroke, currentColor)
const I = {
  dashboard: <svg viewBox="0 0 20 20" width="16" height="16" fill="none"><path d="M3 3h6v8H3zm8 0h6v5h-6zM3 13h6v4H3zm8-2h6v6h-6z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/></svg>,
  portfolio: <svg viewBox="0 0 20 20" width="16" height="16" fill="none"><path d="M3 7h14v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V7Zm4-2V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/></svg>,
  analytics: <svg viewBox="0 0 20 20" width="16" height="16" fill="none"><path d="M3 17V8m4 9v-6m4 6V5m4 12v-9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>,
  risk:      <svg viewBox="0 0 20 20" width="16" height="16" fill="none"><path d="M10 2 2 17h16L10 2Zm0 6v4m0 2v.5" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" strokeLinecap="round"/></svg>,
  watchlist: <svg viewBox="0 0 20 20" width="16" height="16" fill="none"><path d="M2 10s3-6 8-6 8 6 8 6-3 6-8 6-8-6-8-6Zm8 2a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z" stroke="currentColor" strokeWidth="1.4"/></svg>,
  ai:        <svg viewBox="0 0 20 20" width="16" height="16" fill="none"><path d="M10 2v3m0 10v3M3 10H1m18 0h-2M4.2 4.2 5.6 5.6m8.8 8.8 1.4 1.4M4.2 15.8l1.4-1.4m8.8-8.8 1.4-1.4M10 6a4 4 0 1 1 0 8 4 4 0 0 1 0-8Z" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/></svg>,
  backtest:  <svg viewBox="0 0 20 20" width="16" height="16" fill="none"><path d="M3 4h14v12H3zM3 8h14M7 4v12M11 11l2 2 4-4" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round"/></svg>,
  settings:  <svg viewBox="0 0 20 20" width="16" height="16" fill="none"><circle cx="10" cy="10" r="2.5" stroke="currentColor" strokeWidth="1.4"/><path d="M10 1v2m0 14v2M1 10h2m14 0h2M3.5 3.5l1.4 1.4m10.2 10.2 1.4 1.4M3.5 16.5l1.4-1.4m10.2-10.2 1.4-1.4" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/></svg>,
  search:    <svg viewBox="0 0 20 20" width="14" height="14" fill="none"><circle cx="9" cy="9" r="6" stroke="currentColor" strokeWidth="1.5"/><path d="m14 14 4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>,
  bell:      <svg viewBox="0 0 20 20" width="15" height="15" fill="none"><path d="M5 8a5 5 0 1 1 10 0v3l2 3H3l2-3V8Zm3 8a2 2 0 0 0 4 0" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/></svg>,
  download:  <svg viewBox="0 0 20 20" width="14" height="14" fill="none"><path d="M10 3v10m0 0 4-4m-4 4-4-4M3 16h14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  collapse:  <svg viewBox="0 0 20 20" width="14" height="14" fill="none"><path d="M8 5 13 10l-5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>,
};

function CardHd({ eyebrow, title, sub, right }) {
  return (
    <div style={{ padding: "14px 16px 12px", display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12, borderBottom: "1px solid var(--border)" }}>
      <div>
        {eyebrow && <div className="eyebrow" style={{ marginBottom: 4 }}>{eyebrow}</div>}
        <div className="font-display" style={{ fontSize: 15.5, fontWeight: 600 }}>{title}</div>
        {sub && <div style={{ fontSize: 11.5, color: "var(--muted)", marginTop: 3 }}>{sub}</div>}
      </div>
      {right && <div style={{ flexShrink: 0 }}>{right}</div>}
    </div>
  );
}

function MiniMeter({ value, max, color = "var(--cyan)", height = 3 }) {
  const pct = Math.min(1, Math.max(0, value / max));
  return (
    <div style={{ width: "100%", height, background: "rgba(148,163,184,0.10)", borderRadius: height / 2, overflow: "hidden" }}>
      <div style={{ width: (pct * 100) + "%", height: "100%", background: color, boxShadow: `0 0 8px ${color}` }} />
    </div>
  );
}

Object.assign(window, { fmtJPY, fmtSign, PctT, Spark, Triangle2, I, CardHd, MiniMeter, FX_T, SYM_T });
