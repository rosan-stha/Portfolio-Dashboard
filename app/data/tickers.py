"""Ticker mapping store — company name → Yahoo Finance symbol + category/exchange.

Primary store is `st.session_state` (survives reruns, dies with the session).
Best-effort disk persistence at `Files/tickers.json`.

Disk format (v2):
    {company: {ticker, category, exchange}}

Backward-compat: old flat {company: ticker_string} format is migrated on read
and written in v2 format on the next save.
"""
from __future__ import annotations

import json
import logging
from typing import Dict, Tuple

import streamlit as st

from app.config import FILES_DIR, TICKERS_JSON
from app.data.excel_loader import DEMO_COMPANIES_TICKERS

_SESSION_TICKERS = "ticker_map"
_SESSION_META    = "ticker_meta"

logger = logging.getLogger(__name__)

VALID_CATEGORIES = ["American Stock", "Japanese Stock", "ETF", "Mutual Fund", "Other"]


# ── Disk I/O ─────────────────────────────────────────────────────────────────

def _load_from_disk() -> Tuple[Dict[str, str], Dict[str, dict]]:
    if not TICKERS_JSON.exists():
        return {}, {}
    try:
        with open(TICKERS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}, {}

    ticker_map: Dict[str, str] = {}
    meta_map:   Dict[str, dict] = {}

    for k, v in data.items():
        k = str(k)
        if isinstance(v, str):
            if v.strip():
                ticker_map[k] = v.strip()
        elif isinstance(v, dict):
            t = str(v.get("ticker", "")).strip()
            if t:
                ticker_map[k] = t
            meta_map[k] = {
                "category": str(v.get("category", "Other")),
                "exchange":  str(v.get("exchange", "")),
            }

    return ticker_map, meta_map


def _save_to_disk(ticker_map: Dict[str, str], meta_map: Dict[str, dict]) -> None:
    try:
        FILES_DIR.mkdir(parents=True, exist_ok=True)
        data: Dict[str, dict] = {}
        for k in sorted(set(ticker_map) | set(meta_map)):
            data[k] = {
                "ticker":   ticker_map.get(k, ""),
                "category": meta_map.get(k, {}).get("category", "Other"),
                "exchange":  meta_map.get(k, {}).get("exchange", ""),
            }
        with open(TICKERS_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    except Exception as exc:
        logger.warning("Failed to save tickers.json: %s", exc)


# ── Session init ─────────────────────────────────────────────────────────────

def _init() -> Tuple[Dict[str, str], Dict[str, dict]]:
    if _SESSION_TICKERS not in st.session_state:
        tm, mm = _load_from_disk()
        st.session_state[_SESSION_TICKERS] = tm
        st.session_state[_SESSION_META]    = mm
    return st.session_state[_SESSION_TICKERS], st.session_state[_SESSION_META]


# ── Public API — ticker map ───────────────────────────────────────────────────

def init() -> Dict[str, str]:
    """Ensure session_state has a ticker map; return it."""
    tm, _ = _init()
    return tm


def all_mappings() -> Dict[str, str]:
    return init()


def get(company: str) -> str:
    return init().get(company, "")


# ── Public API — meta (category / exchange) ───────────────────────────────────

def all_meta() -> Dict[str, dict]:
    """Return full meta map: {company: {category, exchange}}."""
    _, mm = _init()
    return mm


def get_meta(company: str) -> dict:
    _, mm = _init()
    return mm.get(company, {"category": "Other", "exchange": ""})


# ── Write operations ──────────────────────────────────────────────────────────

def set_many(mapping: Dict[str, str], meta: Dict[str, dict] | None = None) -> None:
    """Replace the ticker map. Optionally replace meta too."""
    cleaned = {str(k).strip(): str(v).strip() for k, v in mapping.items() if v and str(v).strip()}
    _init()  # ensure both session keys exist before writing
    st.session_state[_SESSION_TICKERS] = cleaned
    if meta is not None:
        st.session_state[_SESSION_META] = {str(k).strip(): v for k, v in meta.items()}
    _save_to_disk(st.session_state[_SESSION_TICKERS], st.session_state[_SESSION_META])


def update(company: str, ticker: str, category: str = "", exchange: str = "") -> None:
    """Set or clear a single company's ticker and/or meta."""
    tm, mm = _init()
    company = str(company).strip()
    ticker  = str(ticker).strip()

    if ticker:
        tm[company] = ticker
    else:
        tm.pop(company, None)

    if category or exchange:
        existing = mm.get(company, {"category": "Other", "exchange": ""})
        mm[company] = {
            "category": category or existing["category"],
            "exchange":  exchange  or existing["exchange"],
        }

    st.session_state[_SESSION_TICKERS] = tm
    st.session_state[_SESSION_META]    = mm
    _save_to_disk(tm, mm)


def seed_demo(companies: list[str]) -> None:
    """Pre-fill ticker map with known demo tickers; never overwrites."""
    tm, mm = _init()
    added = False
    for c in companies:
        if c not in tm and c in DEMO_COMPANIES_TICKERS:
            tm[c] = DEMO_COMPANIES_TICKERS[c]
            added = True
    if added:
        st.session_state[_SESSION_TICKERS] = tm
        _save_to_disk(tm, mm)


# ── Import / export ───────────────────────────────────────────────────────────

def export_json() -> str:
    tm, mm = _init()
    data: Dict[str, dict] = {}
    for k in sorted(set(tm) | set(mm)):
        data[k] = {
            "ticker":   tm.get(k, ""),
            "category": mm.get(k, {}).get("category", "Other"),
            "exchange":  mm.get(k, {}).get("exchange", ""),
        }
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)


def import_json(text: str) -> int:
    """Replace mapping from a JSON blob. Returns number of entries loaded."""
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("JSON must be an object of {company: ...}")
    tm: Dict[str, str] = {}
    mm: Dict[str, dict] = {}
    for k, v in data.items():
        k = str(k).strip()
        if isinstance(v, str):
            if v.strip():
                tm[k] = v.strip()
        elif isinstance(v, dict):
            t = str(v.get("ticker", "")).strip()
            if t:
                tm[k] = t
            mm[k] = {
                "category": str(v.get("category", "Other")),
                "exchange":  str(v.get("exchange", "")),
            }
    set_many(tm, mm)
    return len(tm)
