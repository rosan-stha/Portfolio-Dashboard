"""Ticker mapping store — company name → Yahoo Finance symbol.

Primary store is `st.session_state["ticker_map"]` (survives reruns, dies with
the session). Best-effort disk persistence at `Files/tickers.json` so local
users keep their mappings between sessions — silently fails on read-only
filesystems like Streamlit Cloud.
"""
from __future__ import annotations

import json
from typing import Dict

import streamlit as st

from app.config import FILES_DIR, TICKERS_JSON
from app.data.excel_loader import DEMO_COMPANIES_TICKERS

_SESSION_KEY = "ticker_map"


def _load_from_disk() -> Dict[str, str]:
    if not TICKERS_JSON.exists():
        return {}
    try:
        with open(TICKERS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {str(k): str(v) for k, v in data.items() if v}
    except Exception:
        return {}


def _save_to_disk(mapping: Dict[str, str]) -> bool:
    try:
        FILES_DIR.mkdir(parents=True, exist_ok=True)
        with open(TICKERS_JSON, "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2, sort_keys=True)
        return True
    except Exception:
        return False


def init() -> Dict[str, str]:
    """Ensure session_state has a ticker map; load from disk if first call."""
    if _SESSION_KEY not in st.session_state:
        st.session_state[_SESSION_KEY] = _load_from_disk()
    return st.session_state[_SESSION_KEY]


def all_mappings() -> Dict[str, str]:
    """Current full mapping (session_state)."""
    return init()


def get(company: str) -> str:
    """Return ticker for a company, '' if unmapped."""
    return init().get(company, "")


def set_many(mapping: Dict[str, str]) -> None:
    """Overwrite the mapping with a fresh dict and persist to disk."""
    cleaned = {str(k).strip(): str(v).strip() for k, v in mapping.items() if v and str(v).strip()}
    st.session_state[_SESSION_KEY] = cleaned
    _save_to_disk(cleaned)


def update(company: str, ticker: str) -> None:
    """Set/unset a single company's ticker."""
    m = init()
    company = str(company).strip()
    ticker = str(ticker).strip()
    if ticker:
        m[company] = ticker
    else:
        m.pop(company, None)
    st.session_state[_SESSION_KEY] = m
    _save_to_disk(m)


def seed_demo(companies: list[str]) -> None:
    """Pre-fill the mapping with demo tickers — only for companies present in the
    provided list AND missing from the current mapping. Never overwrites."""
    m = init()
    added = False
    for c in companies:
        if c not in m and c in DEMO_COMPANIES_TICKERS:
            m[c] = DEMO_COMPANIES_TICKERS[c]
            added = True
    if added:
        st.session_state[_SESSION_KEY] = m
        _save_to_disk(m)


def export_json() -> str:
    """Serialize the current mapping for download."""
    return json.dumps(all_mappings(), ensure_ascii=False, indent=2, sort_keys=True)


def import_json(text: str) -> int:
    """Replace mapping from a JSON blob. Returns number of entries loaded."""
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("JSON must be an object of {company: ticker}")
    set_many({str(k): str(v) for k, v in data.items()})
    return len(all_mappings())
