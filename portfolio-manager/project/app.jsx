// Main app shell

function App() {
  // Tweakable defaults
  const [t, setTweak] = useTweaks(/*EDITMODE-BEGIN*/{
    "theme": "light",
    "gainLoss": "japan",
    "nisa": "prominent",
    "ia": "consolidated",
    "accent": "#c8102e"
  }/*EDITMODE-END*/);

  // Apply theme + accent to root
  React.useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle("theme-dark",  t.theme === "dark");
    root.classList.toggle("theme-light", t.theme === "light");
    root.classList.toggle("gl-western",  t.gainLoss === "western");
    root.style.setProperty("--accent", t.accent);
    if (t.gainLoss === "japan") {
      root.style.setProperty("--gain", t.accent);
    } else {
      root.style.removeProperty("--gain");
    }
  }, [t.theme, t.gainLoss, t.accent]);

  const data = window.PORTFOLIO_DATA;
  const [tab, setTab] = React.useState("overview");
  const [period, setPeriod] = React.useState("YTD");
  const [ccy, setCcy] = React.useState("JPY");

  return (
    <div style={{ minHeight: "100vh" }}>
      <TopBar
        tab={tab} setTab={setTab}
        period={period} setPeriod={setPeriod}
        ccy={ccy} setCcy={setCcy}
        asOf={data.asOf}
        ia={t.ia}
      />

      {/* Demo data banner */}
      <div style={{
        padding: "8px 24px",
        background: "color-mix(in oklab, var(--warn) 8%, var(--bg))",
        borderBottom: "1px solid var(--border)",
        fontSize: 11.5, color: "var(--text-2)",
        display: "flex", alignItems: "center", gap: 8,
      }}>
        <span style={{
          padding: "1px 6px",
          background: "var(--warn)", color: "var(--surface)",
          fontSize: 9.5, fontWeight: 700,
          letterSpacing: "0.08em",
          borderRadius: 2,
        }}>DEMO</span>
        <span>Showing sample portfolio. Upload your PayPay Securities Excel to see real data.</span>
        <button className="btn" style={{ marginLeft: "auto", fontSize: 11 }}>Upload .xlsx</button>
      </div>

      {tab === "overview"    && <OverviewTab    data={data} ccy={ccy} period={period} nisaProminent={t.nisa === "prominent"} />}
      {tab === "holdings"    && <HoldingsTab    data={data} ccy={ccy} />}
      {tab === "performance" && <PerformanceTab data={data} ccy={ccy} period={period} />}
      {tab === "income"      && <IncomeTab      data={data} ccy={ccy} />}
      {tab === "activity"    && <ActivityTab    data={data} ccy={ccy} />}
      {tab === "settings"    && <SettingsTab    data={data} ccy={ccy} />}
      {/* Full IA extras — same content rerouted */}
      {tab === "health"     && <OverviewTab    data={data} ccy={ccy} period={period} nisaProminent={true} />}
      {tab === "positions"  && <HoldingsTab    data={data} ccy={ccy} />}
      {tab === "risk"       && <RiskTab        data={data} ccy={ccy} />}
      {tab === "tickers"    && <SettingsTab    data={data} ccy={ccy} />}

      <Footer asOf={data.asOf} />

      {/* Tweaks panel */}
      <TweaksPanel title="Tweaks">
        <TweakSection label="Theme">
          <TweakRadio label="Mode"        value={t.theme}    options={[{value:"light",label:"Light"},{value:"dark",label:"Dark"}]}      onChange={v => setTweak("theme", v)} />
          <TweakColor label="Accent"      value={t.accent}   options={["#c8102e","#0f4c81","#2d7d4f","#7e3d8f","#c87f10"]}                onChange={v => setTweak("accent", v)} />
          <TweakRadio label="Gain / Loss" value={t.gainLoss} options={[{value:"japan",label:"Red = up"},{value:"western",label:"Green = up"}]} onChange={v => setTweak("gainLoss", v)} />
        </TweakSection>
        <TweakSection label="Layout">
          <TweakRadio label="NISA strip"        value={t.nisa} options={[{value:"prominent",label:"Centerpiece"},{value:"compact",label:"Compact"}]} onChange={v => setTweak("nisa", v)} />
          <TweakRadio label="Info architecture" value={t.ia}   options={[{value:"consolidated",label:"6 tabs"},{value:"full",label:"9 tabs"}]}        onChange={v => setTweak("ia", v)} />
        </TweakSection>
      </TweaksPanel>
    </div>
  );
}


// ─── Tabs ───────────────────────────────────────────────────────────────────
function OverviewTab({ data, ccy, period, nisaProminent }) {
  return (
    <>
      <KpiRow data={data} ccy={ccy} period={period} />
      <NisaStrip data={data} ccy={ccy} prominent={nisaProminent} />
      <div style={{ padding: "0 24px 16px", display: "grid", gridTemplateColumns: "2fr 1fr", gap: 12 }}>
        <PerformanceChart data={data} period={period} ccy={ccy} />
        <RiskCard data={data} ccy={ccy} />
      </div>
      <div style={{ padding: "0 24px 16px" }}>
        <HoldingsTable data={data} ccy={ccy} limit={6} />
      </div>
      <div style={{ padding: "0 24px 24px", display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
        <DividendsCalendar data={data} ccy={ccy} />
        <ActivityFeed data={data} ccy={ccy} />
        <SectorAllocation data={data} ccy={ccy} />
      </div>
    </>
  );
}

function HoldingsTab({ data, ccy }) {
  return (
    <>
      <KpiRow data={data} ccy={ccy} period="YTD" />
      <div style={{ padding: "0 24px 16px" }}>
        <HoldingsTable data={data} ccy={ccy} />
      </div>
      <div style={{ padding: "0 24px 24px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <SectorAllocation data={data} ccy={ccy} />
        <RiskCard data={data} ccy={ccy} />
      </div>
    </>
  );
}

function PerformanceTab({ data, ccy, period }) {
  return (
    <>
      <KpiRow data={data} ccy={ccy} period={period} />
      <div style={{ padding: "0 24px 16px" }}>
        <PerformanceChart data={data} period={period} ccy={ccy} />
      </div>
      <div style={{ padding: "0 24px 24px", display: "grid", gridTemplateColumns: "2fr 1fr", gap: 12 }}>
        <HoldingsTable data={data} ccy={ccy} />
        <RiskCard data={data} ccy={ccy} />
      </div>
    </>
  );
}

function IncomeTab({ data, ccy }) {
  return (
    <>
      <KpiRow data={data} ccy={ccy} period="YTD" />
      <div style={{ padding: "0 24px 24px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <DividendsCalendar data={data} ccy={ccy} />
        <SectorAllocation data={data} ccy={ccy} />
      </div>
    </>
  );
}

function ActivityTab({ data, ccy }) {
  return (
    <>
      <KpiRow data={data} ccy={ccy} period="YTD" />
      <div style={{ padding: "0 24px 24px" }}>
        <ActivityFeed data={data} ccy={ccy} />
      </div>
    </>
  );
}

function RiskTab({ data, ccy }) {
  return (
    <>
      <KpiRow data={data} ccy={ccy} period="YTD" />
      <div style={{ padding: "0 24px 24px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <RiskCard data={data} ccy={ccy} />
        <SectorAllocation data={data} ccy={ccy} />
      </div>
    </>
  );
}

function SettingsTab({ data }) {
  return (
    <div style={{ padding: "16px 24px 32px" }}>
      <div className="card" style={{ padding: 24, maxWidth: 720 }}>
        <div className="eyebrow" style={{ marginBottom: 8 }}>Settings</div>
        <div style={{ fontSize: 20, fontWeight: 600, letterSpacing: "-0.01em", marginBottom: 16 }}>Preferences</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {[
            { l: "Default currency", v: "JPY (¥)" },
            { l: "JPY → USD rate",   v: "156.4 (live)" },
            { l: "Excel schema",     v: "PayPay Securities v3.1" },
            { l: "Price source",     v: "Yahoo Finance · 15min delayed fallback" },
            { l: "Tax rate (特定)",   v: "20.315%" },
            { l: "Refresh cache",    v: "Every 5 minutes" },
          ].map((r, i) => (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingBottom: 12, borderBottom: "1px solid var(--border)" }}>
              <span style={{ color: "var(--text-2)" }}>{r.l}</span>
              <span className="mono" style={{ color: "var(--text)" }}>{r.v}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Footer({ asOf }) {
  return (
    <div style={{
      padding: "16px 24px 24px",
      borderTop: "1px solid var(--border)",
      display: "flex", justifyContent: "space-between",
      fontSize: 11, color: "var(--muted)",
    }}>
      <div>
        Portfolio Intelligence v4.0 · Data: Excel + Yahoo Finance · <span style={{ fontWeight: 600 }}>Not financial advice.</span>
      </div>
      <div className="mono">As of {asOf.toLocaleString("en-GB")} JST</div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
