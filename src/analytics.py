"""Portfolio analytics functions."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_position_metrics(portfolio: pd.DataFrame, latest_prices: dict[str, float]) -> pd.DataFrame:
    """Compute per-position value and PnL metrics."""
    df = portfolio.copy()
    df["latest_price"] = df["ticker"].map(latest_prices)
    if df["latest_price"].isna().any():
        missing = df.loc[df["latest_price"].isna(), "ticker"].tolist()
        raise ValueError(f"Missing prices for tickers: {missing}")
    df["position_value"] = df["quantity"] * df["latest_price"]
    df["cost_basis"] = df["quantity"] * df["avg_cost"]
    df["pnl"] = df["position_value"] - df["cost_basis"]
    df["weight"] = df["position_value"] / df["position_value"].sum()
    return df


def rolling_volatility(close: pd.Series, window: int) -> float:
    """Annualized rolling volatility from close prices."""
    returns = close.pct_change().dropna()
    if len(returns) < window:
        return float("nan")
    return float(returns.rolling(window).std().iloc[-1] * np.sqrt(252))


def drawdown(close: pd.Series) -> float:
    """Maximum drawdown (negative number)."""
    running_peak = close.cummax()
    dd = (close - running_peak) / running_peak
    return float(dd.min())


def beta(asset_close: pd.Series, benchmark_close: pd.Series) -> float:
    """Beta versus benchmark computed from aligned returns."""
    asset_ret = asset_close.pct_change().dropna()
    bench_ret = benchmark_close.pct_change().dropna()
    aligned = pd.concat([asset_ret, bench_ret], axis=1).dropna()
    if aligned.empty:
        return float("nan")
    cov = np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1], ddof=1)
    if cov[1, 1] == 0:
        return float("nan")
    return float(cov[0, 1] / cov[1, 1])


def historical_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Historical VaR as a positive loss percentage."""
    if returns.empty:
        return float("nan")
    q = np.quantile(returns, 1 - confidence)
    return float(max(0.0, -q))


def portfolio_total_value(metrics_df: pd.DataFrame) -> float:
    """Compute total portfolio value."""
    return float(metrics_df["position_value"].sum())
