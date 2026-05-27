// Shared primitives — formatters, deltas, sparklines, etc.
// Globals: Money, Pct, Delta, Sparkline, MiniBar, Section, Stat, Pill

const FX = { JPY: 1, USD: 1 / 156.4 };
const SYM = { JPY: "¥", USD: "$" };

function fmtMoney(jpy, ccy = "JPY", { compact = false, decimals = 0 } = {}) {
  const v = jpy * FX[ccy];
  if (compact) {
    if (ccy === "JPY") {
      if (Math.abs(v) >= 1e8) return SYM[ccy] + (v / 1e8).toFixed(2) + "億";
      if (Math.abs(v) >= 1e4) return SYM[ccy] + (v / 1e4).toFixed(1) + "万";
      return SYM[ccy] + Math.round(v).toLocaleString();
    } else {
      if (Math.abs(v) >= 1e6) return SYM[ccy] + (v / 1e6).toFixed(2) + "M";
      if (Math.abs(v) >= 1e3) return SYM[ccy] + (v / 1e3).toFixed(1) + "K";
      return SYM[ccy] + v.toFixed(0);
    }
  }
  return SYM[ccy] + v.toLocaleString(undefined, { maximumFractionDigits: decimals, minimumFractionDigits: decimals });
}

function fmtPct(x, digits = 2, withSign = false) {
  const n = (x * 100).toFixed(digits);
  const s = withSign && x > 0 ? "+" : "";
  return s + n + "%";
}

function Money({ jpy, ccy = "JPY", compact = false, decimals = 0, className = "" }) {
  return <span className={"mono " + className}>{fmtMoney(jpy, ccy, { compact, decimals })}</span>;
}

function Delta({ value, pct, ccy = "JPY", showCcy = true, size = "md" }) {
  const sign = value >= 0 ? "+" : "−";
  const cls = value >= 0 ? "gain" : "loss";
  const sizes = { sm: "11px", md: "13px", lg: "15px", xl: "18px" };
  return (
    <span className={"mono " + cls} style={{ fontSize: sizes[size], fontWeight: 500, letterSpacing: "-0.01em" }}>
      {sign}{showCcy ? SYM[ccy] : ""}{Math.abs(value * (ccy === "JPY" ? 1 : FX.USD)).toLocaleString(undefined, { maximumFractionDigits: 0 })}
      {pct != null && (
        <span style={{ marginLeft: 6, opacity: 0.85 }}>
          ({sign}{Math.abs(pct * 100).toFixed(2)}%)
        </span>
      )}
    </span>
  );
}

function PctDelta({ value, size = "md", showSign = true }) {
  const cls = value >= 0 ? "gain" : "loss";
  const sizes = { sm: "11px", md: "13px", lg: "15px", xl: "18px" };
  const sign = value >= 0 ? "+" : "−";
  return (
    <span className={"mono " + cls} style={{ fontSize: sizes[size], fontWeight: 500 }}>
      {showSign ? sign : ""}{Math.abs(value * 100).toFixed(2)}%
    </span>
  );
}

function Triangle({ up, size = 8 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 10 10" style={{ display: "inline-block", verticalAlign: "middle", marginRight: 3 }}>
      {up
        ? <path d="M5 1 L9 8 L1 8 Z" fill="currentColor" />
        : <path d="M5 9 L9 2 L1 2 Z" fill="currentColor" />}
    </svg>
  );
}

// Tiny inline sparkline
function Sparkline({ values, width = 90, height = 26, color = "currentColor", filled = true, strokeWidth = 1.25 }) {
  if (!values || values.length < 2) return null;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const stepX = width / (values.length - 1);
  const pts = values.map((v, i) => [i * stepX, height - ((v - min) / range) * (height - 2) - 1]);
  const d = pts.map((p, i) => (i === 0 ? "M" : "L") + p[0].toFixed(2) + " " + p[1].toFixed(2)).join(" ");
  const dFill = d + ` L ${width} ${height} L 0 ${height} Z`;
  return (
    <svg width={width} height={height} style={{ display: "block", color }}>
      {filled && <path d={dFill} fill="currentColor" opacity="0.10" />}
      <path d={d} fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  );
}

// Horizontal mini progress bar (e.g. quota usage)
function MiniBar({ value, max, color, height = 4, showRemaining = false }) {
  const pct = Math.min(1, Math.max(0, value / max));
  return (
    <div style={{
      width: "100%",
      height,
      background: "var(--bg-2)",
      borderRadius: 2,
      overflow: "hidden",
      position: "relative",
    }}>
      <div style={{
        width: (pct * 100) + "%",
        height: "100%",
        background: color || "var(--accent)",
        transition: "width 300ms",
      }} />
    </div>
  );
}

// Sectioned card header (eyebrow + title + right slot)
function CardHeader({ eyebrow, title, right, sub }) {
  return (
    <div style={{
      display: "flex",
      alignItems: "flex-start",
      justifyContent: "space-between",
      padding: "14px 16px 10px",
      borderBottom: "1px solid var(--border)",
      gap: 12,
    }}>
      <div style={{ minWidth: 0 }}>
        {eyebrow && <div className="eyebrow" style={{ marginBottom: 4 }}>{eyebrow}</div>}
        <div style={{ fontSize: 15, fontWeight: 600, letterSpacing: "-0.005em" }}>{title}</div>
        {sub && <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 2 }}>{sub}</div>}
      </div>
      {right && <div>{right}</div>}
    </div>
  );
}

// Status pill (e.g. LIVE indicator)
function LivePill({ asOf }) {
  const [tick, setTick] = React.useState(0);
  React.useEffect(() => {
    const id = setInterval(() => setTick(t => t + 1), 1500);
    return () => clearInterval(id);
  }, []);
  const t = asOf.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
  return (
    <div style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 11.5, color: "var(--muted)" }}>
      <span style={{
        width: 6, height: 6, borderRadius: 3,
        background: "var(--gain)",
        opacity: tick % 2 ? 0.4 : 1,
        transition: "opacity 600ms",
      }} />
      <span className="mono" style={{ color: "var(--text-2)" }}>LIVE</span>
      <span className="mono">{t} JST</span>
    </div>
  );
}

Object.assign(window, { fmtMoney, fmtPct, FX, SYM, Money, Delta, PctDelta, Triangle, Sparkline, MiniBar, CardHeader, LivePill });
