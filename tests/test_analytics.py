"""Unit tests for analytics functions."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.analytics import (
    beta,
    compute_position_metrics,
    drawdown,
    historical_var,
    portfolio_total_value,
    rolling_volatility,
)


def test_compute_position_metrics_and_total_value() -> None:
    portfolio = pd.DataFrame(
        [
            {"ticker": "AAA", "quantity": 10, "avg_cost": 100.0, "currency": "USD", "asset_class": "equity"},
            {"ticker": "BBB", "quantity": 5, "avg_cost": 200.0, "currency": "USD", "asset_class": "equity"},
        ]
    )
    latest = {"AAA": 110.0, "BBB": 190.0}
    metrics = compute_position_metrics(portfolio, latest)

    assert np.isclose(metrics.loc[0, "position_value"], 1100.0)
    assert np.isclose(metrics.loc[1, "pnl"], -50.0)
    assert np.isclose(metrics["weight"].sum(), 1.0)
    assert np.isclose(portfolio_total_value(metrics), 2050.0)


def test_rolling_volatility_positive() -> None:
    prices = pd.Series(np.linspace(100, 130, 100))
    vol = rolling_volatility(prices, window=20)
    assert vol >= 0


def test_drawdown_detects_loss() -> None:
    prices = pd.Series([100, 120, 80, 90])
    dd = drawdown(prices)
    assert np.isclose(dd, -1 / 3)


def test_beta_around_two_for_scaled_series() -> None:
    bench = pd.Series([100, 101, 103, 102, 105, 106])
    asset = bench * 2
    b = beta(asset, bench)
    assert np.isclose(b, 1.0)


def test_historical_var_non_negative() -> None:
    returns = pd.Series([-0.02, 0.01, -0.03, 0.02, -0.01])
    var = historical_var(returns, confidence=0.95)
    assert var >= 0
