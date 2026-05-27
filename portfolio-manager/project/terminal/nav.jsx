// Sidebar + Header

function Sidebar({ active, setActive }) {
  const [fileName, setFileName] = React.useState(null);
  const [uploading, setUploading] = React.useState(false);

  async function handleFile(e) {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    try {
      const buf = await file.arrayBuffer();
      const wb  = XLSX.read(buf, { type: "array" });
      const parsed = window.parsePayPayExcel(wb);
      if (window.__setTerminalData) window.__setTerminalData(parsed);
      setFileName(file.name);
    } catch(err) {
      alert("Could not read Excel:\n" + err.message);
    }
    setUploading(false);
    e.target.value = "";
  }
  const items = [
    { id: "dashboard", label: "Dashboard",   icon: I.dashboard },
    { id: "portfolio", label: "Portfolio",   icon: I.portfolio },
    { id: "analytics", label: "Analytics",   icon: I.analytics },
    { id: "risk",      label: "Risk",        icon: I.risk },
    { id: "watchlist", label: "Watchlist",   icon: I.watchlist },
    { id: "ai",        label: "AI Insights", icon: I.ai },
    { id: "backtest",  label: "Backtesting", icon: I.backtest },
    { id: "settings",  label: "Settings",    icon: I.settings },
  ];

  return (
    <aside style={{
      width: 220, flexShrink: 0,
      borderRight: "1px solid var(--border)",
      background: "linear-gradient(180deg, #0A1228 0%, #060A1C 100%)",
      display: "flex", flexDirection: "column",
      minHeight: "100vh", padding: "18px 14px",
      position: "sticky", top: 0, alignSelf: "flex-start",
    }}>
      {/* Brand */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "0 6px 18px", borderBottom: "1px solid var(--border)" }}>
        <div style={{
          width: 32, height: 32, borderRadius: 8,
          background: "linear-gradient(135deg, #3B82F6, #06B6D4)",
          display: "grid", placeItems: "center",
          boxShadow: "0 4px 16px -4px rgba(59,130,246,0.6), inset 0 1px 0 rgba(255,255,255,0.2)",
        }}>
          <svg viewBox="0 0 20 20" width="18" height="18" fill="none">
            <path d="M3 14L7 9L11 12L17 5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <circle cx="17" cy="5" r="1.5" fill="white" />
          </svg>
        </div>
        <div>
          <div className="font-display" style={{ fontSize: 14, fontWeight: 700, letterSpacing: "-0.01em", lineHeight: 1.1 }}>Atlas</div>
          <div style={{ fontSize: 10, color: "var(--muted)", letterSpacing: "0.08em", textTransform: "uppercase" }}>Terminal · v4.0</div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ display: "flex", flexDirection: "column", gap: 2, paddingTop: 16 }}>
        <div className="eyebrow" style={{ padding: "0 8px 6px", fontSize: 9.5 }}>Navigation</div>
        {items.map(it => {
          const isActive = active === it.id;
          return (
            <button key={it.id} onClick={() => setActive(it.id)} style={{
              display: "flex", alignItems: "center", gap: 10,
              padding: "8px 10px",
              background: isActive
                ? "linear-gradient(90deg, rgba(59,130,246,0.18), rgba(6,182,212,0.06))"
                : "transparent",
              border: 0,
              borderRadius: 8,
              color: isActive ? "var(--text)" : "var(--text-2)",
              cursor: "pointer",
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: isActive ? 600 : 500,
              textAlign: "left",
              transition: "all 160ms",
              position: "relative",
              boxShadow: isActive ? "inset 0 0 0 1px rgba(59,130,246,0.25), 0 0 18px -6px rgba(59,130,246,0.4)" : "none",
            }}>
              {isActive && (
                <span style={{
                  position: "absolute", left: 0, top: 8, bottom: 8, width: 2,
                  background: "var(--cyan)",
                  boxShadow: "0 0 8px var(--cyan)",
                  borderRadius: 2,
                }} />
              )}
              <span style={{ color: isActive ? "var(--cyan)" : "var(--muted)", display: "inline-flex" }}>{it.icon}</span>
              <span>{it.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* Excel upload */}
      <div style={{ paddingTop: 14, borderTop: "1px solid var(--border)", marginBottom: 12 }}>
        <div className="eyebrow" style={{ padding: "0 8px 8px", fontSize: 9.5 }}>Data Source</div>
        <label style={{
          display: "flex", alignItems: "center", gap: 9,
          padding: "9px 10px", borderRadius: 8, cursor: "pointer",
          background: fileName ? "rgba(34,197,94,0.07)" : "rgba(6,182,212,0.07)",
          border: `1px dashed ${fileName ? "rgba(34,197,94,0.35)" : "rgba(6,182,212,0.35)"}`,
          fontSize: 12, color: "var(--text-2)",
          transition: "all 160ms",
        }}>
          {uploading ? (
            <span style={{ color: "var(--cyan)", fontSize: 11 }}>Reading…</span>
          ) : fileName ? (
            <>
              <svg viewBox="0 0 16 16" width="13" height="13" fill="none">
                <path d="M2 8l4 4 8-8" stroke="var(--pos)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span style={{ color: "var(--pos)", fontSize: 11, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 130 }}>{fileName}</span>
            </>
          ) : (
            <>
              <svg viewBox="0 0 16 16" width="13" height="13" fill="none">
                <path d="M8 2v8M5 5l3-3 3 3" stroke="var(--cyan)" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M2 12v2h12v-2" stroke="var(--cyan)" strokeWidth="1.4" strokeLinecap="round"/>
              </svg>
              <span>Upload PayPay Excel</span>
            </>
          )}
          <input type="file" accept=".xlsx,.xls" style={{ display: "none" }} onChange={handleFile} />
        </label>
        {fileName && (
          <button onClick={() => {
            if (window.__setTerminalData) window.__setTerminalData(window.__DEMO_DATA || window.TERMINAL_DATA);
            setFileName(null);
          }} style={{
            width: "100%", marginTop: 5,
            background: "transparent", border: "1px solid var(--border)",
            color: "var(--muted)", fontSize: 10.5, padding: "5px 0",
            borderRadius: 6, cursor: "pointer", fontFamily: "inherit",
          }}>← Back to demo</button>
        )}
      </div>

      {/* Account block */}
      <div className="card" style={{ padding: 12, marginTop: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 34, height: 34, borderRadius: 8,
            background: "linear-gradient(135deg, #1E40AF, #06B6D4)",
            display: "grid", placeItems: "center",
            fontWeight: 700, fontSize: 13,
            boxShadow: "0 4px 14px -4px rgba(6,182,212,0.5)",
          }}>HK</div>
          <div style={{ minWidth: 0 }}>
            <div style={{ fontSize: 12.5, fontWeight: 600, lineHeight: 1.2 }}>H. Kobayashi</div>
            <div style={{ fontSize: 10.5, color: "var(--muted)" }}>PayPay Securities</div>
          </div>
        </div>
        <div style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid var(--border)", display: "flex", justifyContent: "space-between", fontSize: 10.5 }}>
          <span style={{ color: "var(--muted)" }}>Live sync</span>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 5 }}>
            <span className="live-dot" /> <span style={{ color: "var(--pos)" }}>Active</span>
          </span>
        </div>
      </div>
    </aside>
  );
}


function Header({ period, setPeriod, ccy, setCcy, asOf }) {
  const periods = ["1D", "1W", "1M", "3M", "YTD", "1Y", "ALL"];
  const [now, setNow] = React.useState(asOf);
  React.useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  const t = now.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" });

  return (
    <header style={{
      display: "flex", alignItems: "center", justifyContent: "space-between",
      padding: "16px 24px",
      borderBottom: "1px solid var(--border)",
      background: "rgba(8, 12, 28, 0.92)",
      position: "sticky", top: 0, zIndex: 40,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
        <div>
          <div className="eyebrow" style={{ fontSize: 9.5, marginBottom: 2 }}>Dashboard</div>
          <div className="font-display" style={{ fontSize: 20, fontWeight: 600, letterSpacing: "-0.02em" }}>
            Portfolio Overview
          </div>
        </div>
        <div style={{ height: 32, width: 1, background: "var(--border)" }} />
        <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 11.5, color: "var(--muted)" }}>
          <span className="live-dot" />
          <span className="mono" style={{ color: "var(--text-2)", letterSpacing: "0.05em" }}>
            LIVE · {t} JST
          </span>
          <span style={{ color: "var(--muted-2)" }}>·</span>
          <span>Tokyo open</span>
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        {/* Search */}
        <div style={{ position: "relative" }}>
          <span style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: "var(--muted)" }}>{I.search}</span>
          <input className="input" placeholder="Search tickers, sectors, accounts…"
                 style={{ width: 280, paddingLeft: 30 }} />
          <span style={{
            position: "absolute", right: 8, top: "50%", transform: "translateY(-50%)",
            fontSize: 10, fontFamily: "JetBrains Mono",
            color: "var(--muted)",
            border: "1px solid var(--border)",
            padding: "1px 5px",
            borderRadius: 3,
          }}>⌘K</span>
        </div>

        <div className="chips">
          {periods.map(p => (
            <button key={p} className={"chip " + (period === p ? "active" : "")} onClick={() => setPeriod(p)}>{p}</button>
          ))}
        </div>

        <div className="chips">
          {["JPY", "USD"].map(c => (
            <button key={c} className={"chip " + (ccy === c ? "active" : "")} onClick={() => setCcy(c)}>
              {c === "JPY" ? "¥" : "$"} {c}
            </button>
          ))}
        </div>

        <button className="btn btn--ghost" style={{ position: "relative", padding: "8px 10px" }}>
          {I.bell}
          <span style={{ position: "absolute", top: 5, right: 6, width: 7, height: 7, borderRadius: "50%", background: "var(--cyan)", boxShadow: "0 0 8px var(--cyan)" }} />
        </button>
        <button className="btn btn--primary">
          {I.download} Export
        </button>
      </div>
    </header>
  );
}

Object.assign(window, { Sidebar, Header });
