// Dividends calendar + activity feed

function DividendsCalendar({ data, ccy }) {
  const { dividends } = data;
  const total = dividends.reduce((s, d) => s + d.net, 0);

  const accountTag = {
    tsumitate: { label: "つみたて", cls: "tag--nisa-t" },
    growth:    { label: "成長",     cls: "tag--nisa-g" },
    tokutei:   { label: "特定",     cls: "tag--tokutei" },
    ippan:     { label: "一般",     cls: "tag--tokutei" },
  };

  // Group by month
  const months = {};
  for (const d of dividends) {
    const dt = new Date(d.date);
    const key = dt.toLocaleDateString("en-GB", { month: "short", year: "numeric" });
    (months[key] ||= []).push({ ...d, dt });
  }

  return (
    <div className="card" style={{ overflow: "hidden" }}>
      <CardHeader
        eyebrow="Income"
        title="Upcoming dividends"
        sub="Next 60 days · net of withholding"
        right={<span className="mono" style={{ fontSize: 13, color: "var(--gain)", fontWeight: 500 }}>+{fmtMoney(total, ccy, { compact: true })}</span>}
      />
      <div style={{ padding: "4px 0" }}>
        {Object.entries(months).map(([m, items]) => (
          <div key={m}>
            <div style={{
              padding: "8px 16px 4px",
              fontSize: 10.5, color: "var(--muted)",
              fontFamily: "IBM Plex Mono",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              background: "var(--surface-2)",
              borderTop: "1px solid var(--border)",
              borderBottom: "1px solid var(--border)",
            }}>{m}</div>
            {items.map((d, i) => {
              const at = accountTag[d.account];
              const day = d.dt.getDate();
              return (
                <div key={i} style={{
                  display: "flex", alignItems: "center", gap: 12,
                  padding: "10px 16px",
                  borderBottom: "1px solid var(--border)",
                }}>
                  <div style={{
                    width: 34, height: 34, borderRadius: 3,
                    background: "var(--bg-2)", border: "1px solid var(--border)",
                    display: "grid", placeItems: "center",
                    flexShrink: 0,
                  }}>
                    <div className="mono" style={{ fontSize: 14, fontWeight: 600, lineHeight: 1, color: "var(--text)" }}>{day}</div>
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <span className="mono" style={{ fontSize: 10.5, color: "var(--muted)" }}>{d.code}</span>
                      <span className="jp" style={{ fontSize: 12.5, fontWeight: 500 }}>{d.name}</span>
                      <span className={"tag " + at.cls} style={{ fontSize: 9 }}>{at.label}</span>
                    </div>
                    <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 1 }}>
                      <span className="mono">¥{d.perShare}</span>/sh × <span className="mono">{d.shares}</span> sh
                    </div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div className="mono gain" style={{ fontSize: 13, fontWeight: 500 }}>
                      +{fmtMoney(d.net, ccy, { compact: true })}
                    </div>
                    {d.gross !== d.net && (
                      <div style={{ fontSize: 10, color: "var(--muted)" }}>
                        gross <span className="mono">{fmtMoney(d.gross, ccy, { compact: true })}</span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}


// ─── Activity feed ─────────────────────────────────────────────────────────
function ActivityFeed({ data, ccy }) {
  const { activity } = data;

  const accountTag = {
    tsumitate: { label: "つみたて", cls: "tag--nisa-t" },
    growth:    { label: "成長",     cls: "tag--nisa-g" },
    tokutei:   { label: "特定",     cls: "tag--tokutei" },
    ippan:     { label: "一般",     cls: "tag--tokutei" },
  };
  const typeMeta = {
    buy:  { label: "BUY",  color: "var(--accent)", bg: "color-mix(in oklab, var(--accent) 12%, var(--surface))" },
    sell: { label: "SELL", color: "var(--loss)",   bg: "color-mix(in oklab, var(--loss) 12%, var(--surface))" },
    div:  { label: "DIV",  color: "var(--text-2)", bg: "var(--bg-2)" },
  };

  return (
    <div className="card" style={{ overflow: "hidden" }}>
      <CardHeader
        eyebrow="Activity"
        title="Recent transactions"
        sub="Last 30 days"
        right={<button className="btn" style={{ fontSize: 11.5 }}>View all →</button>}
      />
      <div style={{ padding: 0 }}>
        {activity.map((a, i) => {
          const tm = typeMeta[a.type];
          const at = accountTag[a.account];
          const amount = a.type === "div" ? a.amount : a.shares * a.price;
          return (
            <div key={i} style={{
              display: "flex", alignItems: "center", gap: 12,
              padding: "10px 16px",
              borderBottom: i < activity.length - 1 ? "1px solid var(--border)" : "none",
            }}>
              <div style={{
                padding: "2px 7px",
                background: tm.bg, color: tm.color,
                fontSize: 10, fontWeight: 600,
                fontFamily: "IBM Plex Mono",
                letterSpacing: "0.06em",
                borderRadius: 2,
                minWidth: 42, textAlign: "center",
                flexShrink: 0,
              }}>{tm.label}</div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span className="mono" style={{ fontSize: 10.5, color: "var(--muted)" }}>{a.code}</span>
                  <span className="jp" style={{ fontSize: 12.5, fontWeight: 500 }}>{a.name}</span>
                  <span className={"tag " + at.cls} style={{ fontSize: 9 }}>{at.label}</span>
                </div>
                <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 1 }}>
                  {a.type !== "div"
                    ? <><span className="mono">{a.shares}</span> sh @ <span className="mono">{fmtMoney(a.price, ccy)}</span> · {a.date}</>
                    : <>Dividend received · {a.date}</>
                  }
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div className={"mono " + (a.type === "div" ? "gain" : "")} style={{ fontSize: 13, fontWeight: 500 }}>
                  {a.type === "div" ? "+" : (a.type === "sell" ? "+" : "−")}{fmtMoney(amount, ccy, { compact: true })}
                </div>
                {a.realized != null && (
                  <div style={{ fontSize: 10, color: "var(--gain)" }}>
                    realized <span className="mono">+{fmtMoney(a.realized, ccy, { compact: true })}</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

Object.assign(window, { DividendsCalendar, ActivityFeed });
