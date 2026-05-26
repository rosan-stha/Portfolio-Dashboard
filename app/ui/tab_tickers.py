"""Tickers tab — editable company → Yahoo Finance symbol mapping.

Lets the user map each company in their uploaded portfolio to a Yahoo Finance
ticker (e.g. `Toyota Motor` → `7203.T`). The mapping is what enables every
live-data feature: positions, P&L, sectors, correlations.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from app.config import GOLD, GREEN, MUTED, RED
from app.data import market, tickers
from app.data.excel_loader import DEMO_COMPANIES_TICKERS
from app.ui.components import label, section_hd


def render(ps: pd.DataFrame) -> None:
    ticker_map = tickers.all_mappings()

    # ── Status banner ────────────────────────────────────────────────────────
    total = len(ps)
    mapped = sum(1 for c in ps["company"] if ticker_map.get(c, "").strip())
    unmapped = total - mapped

    st.markdown(section_hd("Ticker Coverage", "Yahoo Finance symbol mapping", "Tickers"), unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Companies", f"{total:,}")
    c2.metric("Mapped",          f"{mapped:,}", delta=f"{mapped / total * 100:.0f}%" if total else None)
    c3.metric("Unmapped",        f"{unmapped:,}")

    if unmapped > 0:
        st.info(
            f"📌 **{unmapped}** companies have no ticker. Live prices, P&L, and "
            f"sector analytics require a Yahoo Finance symbol per company. "
            f"Japan stocks use the `.T` suffix (e.g. Toyota → `7203.T`)."
        )

    # ── Quick actions ────────────────────────────────────────────────────────
    qa1, qa2, qa3 = st.columns([2, 2, 3])

    with qa1:
        demo_hits = sum(1 for c in ps["company"] if c in DEMO_COMPANIES_TICKERS and not ticker_map.get(c))
        if st.button(
            f"✨ Auto-seed {demo_hits} known tickers" if demo_hits else "✨ No known tickers to seed",
            disabled=(demo_hits == 0),
            use_container_width=True,
        ):
            tickers.seed_demo(ps["company"].tolist())
            st.rerun()

    with qa2:
        st.download_button(
            "⬇ Export mapping (JSON)",
            data=tickers.export_json(),
            file_name="tickers.json",
            mime="application/json",
            use_container_width=True,
        )

    with qa3:
        uploaded = st.file_uploader(
            "Import mapping (JSON)",
            type=["json"],
            label_visibility="collapsed",
            key="ticker_import",
        )
        if uploaded is not None:
            try:
                n = tickers.import_json(uploaded.read().decode("utf-8"))
                st.success(f"Imported {n} mappings.")
                st.rerun()
            except Exception as e:
                st.error(f"Import failed: {e}")

    st.markdown("---")

    # ── Editable table ───────────────────────────────────────────────────────
    st.markdown(section_hd("Edit Mappings", "Company → Yahoo Finance symbol", "Edit"), unsafe_allow_html=True)
    st.caption(
        "Edit the **Ticker** column inline. Leave blank to clear. "
        "Click **Save Changes** to persist. Use the **Validate** button to test "
        "tickers against Yahoo Finance."
    )

    edit_df = pd.DataFrame({
        "Company": ps["company"].tolist(),
        "Ticker":  [ticker_map.get(c, "") for c in ps["company"]],
    })

    edited = st.data_editor(
        edit_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Company": st.column_config.TextColumn("Company", disabled=True, width="large"),
            "Ticker":  st.column_config.TextColumn(
                "Ticker",
                help="Yahoo Finance symbol (e.g. 7203.T, AAPL, BTC-USD)",
                width="medium",
            ),
        },
        num_rows="fixed",
        key="ticker_editor",
    )

    bcol1, bcol2, _ = st.columns([1, 1, 4])
    with bcol1:
        save_clicked = st.button("💾 Save Changes", type="primary", use_container_width=True)
    with bcol2:
        validate_clicked = st.button("🔎 Validate", use_container_width=True)

    if save_clicked:
        new_map = {
            row["Company"]: str(row["Ticker"]).strip()
            for _, row in edited.iterrows()
            if str(row["Ticker"]).strip()
        }
        tickers.set_many(new_map)
        st.success(f"Saved {len(new_map)} ticker mappings.")
        st.rerun()

    if validate_clicked:
        _validate(edited)


def _validate(edited: pd.DataFrame) -> None:
    """Ping yfinance for each non-empty ticker; report results inline."""
    rows = [r for _, r in edited.iterrows() if str(r["Ticker"]).strip()]
    if not rows:
        st.warning("No tickers to validate.")
        return

    progress = st.progress(0.0, text="Validating…")
    results = []
    for i, r in enumerate(rows, 1):
        ticker = str(r["Ticker"]).strip()
        info = market.get_info(ticker)
        quote = market.get_quote(ticker)
        ok = bool(info.get("name")) and bool(quote.get("price"))
        results.append({
            "Company": r["Company"],
            "Ticker":  ticker,
            "Name":    info.get("name", "—") if ok else "—",
            "Sector":  info.get("sector", "—") if ok else "—",
            "Price":   f"{quote.get('price', 0):,.2f} {quote.get('currency', '')}" if ok else "—",
            "OK":      "✅" if ok else "❌",
        })
        progress.progress(i / len(rows), text=f"Validating {ticker} ({i}/{len(rows)})")
    progress.empty()

    res_df = pd.DataFrame(results)
    ok_count = (res_df["OK"] == "✅").sum()
    bad_count = len(res_df) - ok_count

    if bad_count == 0:
        st.success(f"All {ok_count} tickers validated successfully.")
    else:
        st.warning(f"{ok_count} valid, **{bad_count} invalid** — review below.")

    tbl = '<table class="ptable"><thead><tr>'
    for h in ["Company", "Ticker", "Name", "Sector", "Price", "Status"]:
        tbl += f"<th>{h}</th>"
    tbl += "</tr></thead><tbody>"
    for _, r in res_df.iterrows():
        ok_color = GREEN if r["OK"] == "✅" else RED
        tbl += (
            f"<tr>"
            f'<td style="font-weight:600">{r["Company"]}</td>'
            f'<td style="color:{GOLD};font-weight:600">{r["Ticker"]}</td>'
            f'<td>{r["Name"]}</td>'
            f'<td style="color:{MUTED}">{r["Sector"]}</td>'
            f'<td>{r["Price"]}</td>'
            f'<td style="text-align:center;color:{ok_color};font-weight:700">{r["OK"]}</td>'
            f"</tr>"
        )
    tbl += "</tbody></table>"
    st.markdown(
        f'<div class="card" style="padding:0;overflow:hidden">'
        f'<div class="card-hd-inner">'
        f'<div class="eyebrow">Validation Results</div>'
        f'<div class="card-title font-display">{ok_count} valid · {bad_count} invalid</div>'
        f'</div>'
        f'<div style="overflow-x:auto">{tbl}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
