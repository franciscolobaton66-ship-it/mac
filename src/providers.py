"""Market data provider interface and implementations."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd


class BaseProvider(ABC):
    """Abstract market data provider."""

    @abstractmethod
    def get_latest_prices(self, tickers: list[str]) -> dict[str, float]:
        """Return the latest available prices keyed by ticker."""

    @abstractmethod
    def get_history(self, ticker: str, days: int = 120) -> pd.Series:
        """Return historical close prices for a ticker."""


class MockProvider(BaseProvider):
    """Offline provider that synthesizes deterministic-ish price data."""

    def __init__(self, seed: int = 42) -> None:
        self.rng = np.random.default_rng(seed)

    def get_latest_prices(self, tickers: list[str]) -> dict[str, float]:
        prices: dict[str, float] = {}
        for t in tickers:
            base = 100 + (sum(map(ord, t)) % 200)
            prices[t] = round(float(base * (1 + self.rng.normal(0, 0.01))), 2)
        return prices

    def get_history(self, ticker: str, days: int = 120) -> pd.Series:
        base = 100 + (sum(map(ord, ticker)) % 200)
        daily_returns = self.rng.normal(0.0005, 0.02, days)
        prices = [base]
        for r in daily_returns:
            prices.append(prices[-1] * (1 + r))
        idx = pd.date_range(end=pd.Timestamp.today(), periods=days + 1, freq="B")
        return pd.Series(prices[1:], index=idx[1:], name=ticker)


class RealProvider(BaseProvider):
    """Skeleton for a live provider. Wire API calls as needed."""

    def __init__(self, api_key_env_var: str = "MARKET_DATA_API_KEY") -> None:
        self.api_key = os.getenv(api_key_env_var)
        if not self.api_key:
            raise ValueError(
                f"Missing API key in env var '{api_key_env_var}'. Set it before using RealProvider."
            )

    def get_latest_prices(self, tickers: list[str]) -> dict[str, float]:
        raise NotImplementedError("Implement provider-specific intraday price fetch logic.")

    def get_history(self, ticker: str, days: int = 120) -> pd.Series:
        raise NotImplementedError("Implement provider-specific historical close fetch logic.")
