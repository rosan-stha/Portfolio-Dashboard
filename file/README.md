# Agent System — Portfolio Intelligence Platform

## How This Works

This project uses a multi-agent system. Each agent owns a specific part of the codebase
and has strict boundaries on what it can touch.

**The user only talks to the Orchestrator.**
The Orchestrator reads this folder and spawns the correct sub-agent for every task.

---

## Entry Point

When the user gives you a task, you are acting as the **Orchestrator**.
Read `agents/orchestrator.md` first. It tells you how to route every request.

---

## Agent Map

| Agent file | Owns | Never touches |
|---|---|---|
| `orchestrator.md` | Routing, delegation, synthesis | Never edits code directly |
| `market-data.md` | `app/data/market.py`, `fx.py`, `tickers.py` | UI, analytics |
| `health-analyst.md` | `app/analytics/health.py`, `tab_health.py` | Other tabs, data layer |
| `decision-engine.md` | `app/analytics/decisions.py`, `tab_decisions.py` | Existing analytics files |
| `risk-monitor.md` | `app/analytics/correlation.py`, `tab_risk.py`, `app/alerts/` | Health, positions tabs |
| `report-writer.md` | `app/ui/tab_chat.py`, `app/reports/`, `app/agents/report_writer.py` | All analytics and data |
| `ui-stylist.md` | `app/ui/theme.py`, `app/ui/components.py` | Business logic in tabs |
| `data-loader.md` | `app/data/excel_loader.py`, `tab_tickers.py`, `Files/tickers.json` | Market data, analytics |

---

## Dependency Order

When building Phase 3 features, always follow this order:

```
1. data-loader      (foundation — Excel + tickers)
2. market-data      (foundation — live prices)
3. health-analyst   (depends on: positions, metrics, correlation)
4. risk-monitor     (depends on: positions, metrics, correlation)
5. decision-engine  (depends on: health, market, positions)
6. report-writer    (depends on: all of the above)
7. ui-stylist       (called anytime layout/style breaks)
```

---

## Shared Output Contracts

These data structures are passed between agents. Never change the keys without
updating all consumers.

### Health score dict (health-analyst → decision-engine, report-writer)
```python
{
    "total_score": float,
    "grade": str,
    "subscores": dict,
    "weakest_subscore": str,
    "alerts": list[str],
    "recommendation": str,
    "narrative": str,
}
```

### Decision recommendation dict (decision-engine → report-writer)
```python
{
    "action": str,
    "ticker": str,
    "company": str,
    "reason": str,
    "signals": list[str],
    "confidence": float,
    "priority": int,
    "simulated_impact": dict,
    "suggested_amount_jpy": int,
}
```

### Alert dict (risk-monitor → report-writer)
```python
{
    "severity": str,
    "type": str,
    "ticker": str,
    "company": str,
    "message": str,
    "current_value": float,
    "threshold": float,
    "suggested_action": str,
    "timestamp": str,
}
```

---

## After Every Change

Run this verification sequence before reporting back to the user:

```bash
python -c "import app; print('imports OK')"
streamlit run portfolio.py --server.headless true &
sleep 3 && curl -s http://localhost:8501 | grep -q "streamlit" && echo "app starts OK"
```

---

## Project File Tree (reference)

```
portfolio-dashboard/
├── portfolio.py
├── requirements.txt
├── agents/                     ← YOU ARE HERE
│   ├── README.md
│   ├── orchestrator.md
│   ├── market-data.md
│   ├── health-analyst.md
│   ├── decision-engine.md
│   ├── risk-monitor.md
│   ├── report-writer.md
│   ├── ui-stylist.md
│   └── data-loader.md
├── app/
│   ├── config.py
│   ├── ui/
│   ├── data/
│   └── analytics/
└── Files/
    └── tickers.json
```
