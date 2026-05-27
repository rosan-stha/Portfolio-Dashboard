// Main shell — Atlas Terminal

function App() {
  const [active, setActive]     = React.useState("dashboard");
  const [period, setPeriod]     = React.useState("YTD");
  const [ccy, setCcy]           = React.useState("JPY");
  const [data, setData]         = React.useState(window.TERMINAL_DATA);
  const [uploading, setUploading] = React.useState(false);

  // Expose setter so Sidebar can trigger re-render after Excel parse
  React.useEffect(() => {
    window.__setTerminalData = (newData) => { window.TERMINAL_DATA = newData; setData(newData); };
    window.__setUploading    = setUploading;
    return () => { delete window.__setTerminalData; delete window.__setUploading; };
  }, []);

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar active={active} setActive={setActive} />
      <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column" }}>
        <Header period={period} setPeriod={setPeriod} ccy={ccy} setCcy={setCcy} asOf={data.asOf} />
        <main style={{ padding: "20px 24px 32px", display: "flex", flexDirection: "column", gap: 16 }}>
          <NewsTicker data={data} />

          {active === "dashboard"  && <Dashboard  data={data} ccy={ccy} period={period} />}
          {active === "portfolio"  && <Portfolio  data={data} ccy={ccy} period={period} />}
          {active === "analytics"  && <Analytics  data={data} ccy={ccy} period={period} />}
          {active === "risk"       && <RiskView   data={data} ccy={ccy} />}
          {active === "watchlist"  && <WatchView  data={data} ccy={ccy} />}
          {active === "ai"         && <AIView     data={data} ccy={ccy} />}
          {active === "backtest"   && <Backtest   data={data} ccy={ccy} />}
          {active === "settings"   && <SettingsView data={data} />}
        </main>
        <Footer asOf={data.asOf} />
      </div>
    </div>
  );
}

// ─── DASHBOARD ────────────────────────────────────────────────────────────
function Dashboard({ data, ccy, period }) {
  return (
    <>
      <KpiGrid data={data} ccy={ccy} />

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 14 }}>
        <EquityCurve data={data} ccy={ccy} period={period} />
        <AIInsights data={data} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
        <AllocationDonut data={data} ccy={ccy} />
        <RiskDecomp data={data} ccy={ccy} />
        <MarketOverview data={data} />
      </div>

      <HoldingsTerm data={data} ccy={ccy} />

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 14 }}>
        <CorrelationHeatmap data={data} />
        <Watchlist data={data} ccy={ccy} />
      </div>
    </>
  );
}

// ─── Other views (lighter) ────────────────────────────────────────────────
function Portfolio({ data, ccy, period }) {
  return (
    <>
      <KpiGrid data={data} ccy={ccy} />
      <HoldingsTerm data={data} ccy={ccy} />
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        <AllocationDonut data={data} ccy={ccy} />
        <RiskDecomp data={data} ccy={ccy} />
      </div>
    </>
  );
}
function Analytics({ data, ccy, period }) {
  return (
    <>
      <KpiGrid data={data} ccy={ccy} />
      <EquityCurve data={data} ccy={ccy} period={period} />
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        <CorrelationHeatmap data={data} />
        <RiskDecomp data={data} ccy={ccy} />
      </div>
    </>
  );
}
function RiskView({ data, ccy }) {
  return (
    <>
      <KpiGrid data={data} ccy={ccy} />
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        <RiskDecomp data={data} ccy={ccy} />
        <CorrelationHeatmap data={data} />
      </div>
    </>
  );
}
function WatchView({ data, ccy }) {
  return (
    <>
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 14 }}>
        <Watchlist data={data} ccy={ccy} />
        <MarketOverview data={data} />
      </div>
    </>
  );
}
function AIView({ data, ccy }) {
  return (
    <>
      <AIInsights data={data} />
      <KpiGrid data={data} ccy={ccy} />
    </>
  );
}
function Backtest({ data, ccy }) {
  return (
    <div className="card" style={{ padding: 32, textAlign: "center" }}>
      <div style={{
        width: 48, height: 48, borderRadius: 12,
        background: "linear-gradient(135deg, #3B82F6, #06B6D4)",
        display: "grid", placeItems: "center", margin: "0 auto 16px",
        boxShadow: "0 0 24px -4px rgba(6,182,212,0.5)",
      }}>{I.backtest}</div>
      <div className="font-display" style={{ fontSize: 18, fontWeight: 600, marginBottom: 6 }}>Backtesting Engine</div>
      <div style={{ fontSize: 13, color: "var(--muted)", maxWidth: 480, margin: "0 auto" }}>
        Replay strategies against your historical Excel data with realistic transaction costs and tax modeling.
      </div>
      <button className="btn btn--primary" style={{ marginTop: 18, padding: "10px 18px" }}>Start a backtest</button>
    </div>
  );
}
function SettingsView({ data }) {
  const settings = [
    { l: "Default currency",      v: "JPY (¥)" },
    { l: "JPY → USD rate",        v: "156.42 · live · refresh every 60s" },
    { l: "Excel schema",          v: "PayPay Securities v3.1" },
    { l: "Price source",          v: "Yahoo Finance + 15-min delayed fallback" },
    { l: "Tax rate (特定口座)",    v: "20.315% (income + reconstruction surtax)" },
    { l: "Cache refresh",         v: "Every 5 minutes during market hours" },
    { l: "Risk-free rate",        v: "JGB 10Y · 1.428%" },
    { l: "Benchmark",             v: "TOPIX (primary), Nikkei 225 (secondary)" },
  ];
  return (
    <div className="card" style={{ padding: 24, maxWidth: 760 }}>
      <div className="eyebrow" style={{ marginBottom: 8 }}>System</div>
      <div className="font-display" style={{ fontSize: 22, fontWeight: 600, marginBottom: 16 }}>Preferences</div>
      <div>
        {settings.map((s, i) => (
          <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", borderBottom: i < settings.length - 1 ? "1px solid var(--border)" : "none" }}>
            <span style={{ color: "var(--text-2)" }}>{s.l}</span>
            <span className="mono" style={{ color: "var(--text)" }}>{s.v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function Footer({ asOf }) {
  return (
    <footer style={{
      padding: "18px 24px",
      borderTop: "1px solid var(--border)",
      display: "flex", justifyContent: "space-between", alignItems: "center",
      fontSize: 11, color: "var(--muted)",
      background: "rgba(5,8,22,0.4)",
      backdropFilter: "blur(20px)",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
          <span className="live-dot" />
          <span style={{ color: "var(--text-2)" }}>All systems operational</span>
        </span>
        <span style={{ color: "var(--muted-2)" }}>·</span>
        <span>Data: Yahoo Finance + Excel</span>
        <span style={{ color: "var(--muted-2)" }}>·</span>
        <span style={{ color: "var(--warn)", fontWeight: 500 }}>Not financial advice</span>
      </div>
      <div className="mono" style={{ fontSize: 10.5 }}>
        Atlas Terminal v4.0 · As of {asOf.toLocaleString("en-GB")} JST
      </div>
    </footer>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
