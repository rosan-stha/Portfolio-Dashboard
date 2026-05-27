// Top bar — brand, tabs, period selector, currency, live indicator, user

function TopBar({ tab, setTab, period, setPeriod, ccy, setCcy, asOf, ia, ds }) {
  const tabsConsolidated = [
    { id: "overview",    label: "Overview",     jp: "概要" },
    { id: "holdings",    label: "Holdings",     jp: "保有銘柄" },
    { id: "performance", label: "Performance",  jp: "パフォーマンス" },
    { id: "income",      label: "Income",       jp: "配当・収益" },
    { id: "activity",    label: "Activity",     jp: "取引履歴" },
    { id: "settings",    label: "Settings",     jp: "設定" },
  ];
  const tabsFull = [
    { id: "overview",    label: "Overview" },
    { id: "health",      label: "Health" },
    { id: "positions",   label: "Positions" },
    { id: "risk",        label: "Risk" },
    { id: "performance", label: "Performance" },
    { id: "holdings",    label: "Holdings" },
    { id: "activity",    label: "Activity" },
    { id: "income",      label: "Dividends" },
    { id: "tickers",     label: "Tickers" },
  ];
  const tabs = ia === "consolidated" ? tabsConsolidated : tabsFull;
  const periods = ["1D", "1W", "1M", "3M", "YTD", "1Y", "ALL"];

  return (
    <div style={{
      position: "sticky", top: 0, zIndex: 50,
      background: "var(--bg)",
      borderBottom: "1px solid var(--border)",
    }}>
      {/* Row 1: brand · live · currency · user */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "10px 24px",
        gap: 16,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
            {/* Logo mark */}
            <div style={{
              width: 26, height: 26, borderRadius: 4,
              background: "var(--text)", color: "var(--surface)",
              display: "grid", placeItems: "center",
              fontWeight: 700, fontSize: 13, fontFamily: "IBM Plex Serif",
            }}>P</div>
            <div>
              <div style={{ fontSize: 13.5, fontWeight: 600, letterSpacing: "-0.01em", lineHeight: 1.1 }}>
                Portfolio Intelligence
              </div>
              <div style={{ fontSize: 10.5, color: "var(--muted)", letterSpacing: "0.04em" }}>
                PayPay Securities · 日本株
              </div>
            </div>
          </div>
          <div className="vdivider" style={{ height: 22 }} />
          <LivePill asOf={asOf} />
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{
            display: "inline-flex",
            border: "1px solid var(--border)",
            borderRadius: 3,
            overflow: "hidden",
          }}>
            {["JPY", "USD"].map(c => (
              <button key={c}
                onClick={() => setCcy(c)}
                style={{
                  border: 0, padding: "5px 10px",
                  background: ccy === c ? "var(--text)" : "transparent",
                  color: ccy === c ? "var(--surface)" : "var(--text-2)",
                  fontSize: 11.5, fontFamily: "IBM Plex Mono",
                  cursor: "pointer",
                }}>
                {c === "JPY" ? "¥ JPY" : "$ USD"}
              </button>
            ))}
          </div>
          <button className="btn" title="Export report" style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
            <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M3 10v2.5a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5V10M8 2v8m0 0 3-3m-3 3L5 7" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/></svg>
            Export
          </button>
          <button className="btn" title="Settings" style={{ width: 28, padding: 0, display: "grid", placeItems: "center" }}>
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="2" stroke="currentColor" strokeWidth="1.3"/><path d="M8 1v2m0 10v2M1 8h2m10 0h2M3.5 3.5l1.4 1.4m6.2 6.2 1.4 1.4M3.5 12.5l1.4-1.4m6.2-6.2 1.4-1.4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/></svg>
          </button>
          <div style={{
            width: 28, height: 28, borderRadius: "50%",
            background: "var(--bg-2)", border: "1px solid var(--border)",
            display: "grid", placeItems: "center",
            fontSize: 11, fontWeight: 600,
          }}>HK</div>
        </div>
      </div>

      <hr className="divider" />

      {/* Row 2: tabs + period selector */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 16px",
        gap: 16,
      }}>
        <div style={{ display: "flex", gap: 0, overflowX: "auto" }}>
          {tabs.map(t => (
            <button key={t.id}
              onClick={() => setTab(t.id)}
              style={{
                border: 0,
                background: "transparent",
                padding: "11px 14px 10px",
                fontSize: 13,
                fontWeight: tab === t.id ? 600 : 500,
                color: tab === t.id ? "var(--text)" : "var(--muted)",
                borderBottom: "2px solid " + (tab === t.id ? "var(--accent)" : "transparent"),
                cursor: "pointer",
                whiteSpace: "nowrap",
                fontFamily: "inherit",
                letterSpacing: "-0.005em",
                marginBottom: -1,
              }}>
              {t.label}
            </button>
          ))}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 2, padding: "6px 0" }}>
          <span className="eyebrow" style={{ marginRight: 8 }}>Period</span>
          {periods.map(p => (
            <button key={p}
              onClick={() => setPeriod(p)}
              style={{
                border: 0, background: "transparent",
                padding: "4px 8px",
                fontSize: 11.5,
                fontFamily: "IBM Plex Mono",
                color: period === p ? "var(--text)" : "var(--muted)",
                fontWeight: period === p ? 600 : 500,
                cursor: "pointer",
                borderRadius: 2,
                ...(period === p ? { background: "var(--bg-2)" } : {}),
              }}>
              {p}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

window.TopBar = TopBar;
