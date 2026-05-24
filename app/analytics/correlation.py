"""Correlation matrix + cluster detection.

Computes pairwise Pearson correlation of position daily returns and surfaces
hidden concentration risk: pairs with corr > threshold are flagged.
"""
from __future__ import annotations

from typing import List, Tuple

import numpy as np
import pandas as pd

from app.analytics.returns import position_price_matrix


CONCENTRATION_THRESHOLD = 0.85


def correlation_matrix(
    positions: pd.DataFrame,
    period: str = "1Y",
) -> pd.DataFrame:
    """Symmetric correlation matrix of position daily returns.

    Index/columns are tickers. Empty DataFrame if fewer than 2 positions or
    insufficient overlapping history.
    """
    prices = position_price_matrix(positions, period)
    if prices.empty or prices.shape[1] < 2:
        return pd.DataFrame()
    returns = prices.pct_change().dropna(how="all")
    if returns.empty:
        return pd.DataFrame()
    return returns.corr()


def average_pairwise_correlation(corr: pd.DataFrame) -> float:
    """Average of off-diagonal correlations. 0 if matrix is empty or 1×1."""
    if corr.empty or len(corr) < 2:
        return 0.0
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    values = corr.values[mask]
    if len(values) == 0 or np.all(np.isnan(values)):
        return 0.0
    return float(np.nanmean(values))


def high_correlation_pairs(
    corr: pd.DataFrame,
    threshold: float = CONCENTRATION_THRESHOLD,
) -> List[Tuple[str, str, float]]:
    """Pairs (a, b, corr) where corr > threshold, sorted by correlation desc."""
    if corr.empty or len(corr) < 2:
        return []
    pairs: List[Tuple[str, str, float]] = []
    tickers = corr.index.tolist()
    for i, a in enumerate(tickers):
        for b in tickers[i + 1:]:
            c = corr.loc[a, b]
            if pd.notna(c) and c >= threshold:
                pairs.append((a, b, float(c)))
    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs
