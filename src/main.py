"""Main runner for the portfolio copilot loop."""

from __future__ import annotations

import time

import pandas as pd

from .alerts import emit_alerts
from .analytics import (
    beta,
    compute_position_metrics,
    drawdown,
    historical_var,
    portfolio_total_value,
    rolling_volatility,
)
from .io_utils import load_config, load_portfolio
from .providers import BaseProvider, MockProvider, RealProvider
from .rules import evaluate_rules


def _provider_factory(provider_type: str, api_env_var: str) -> BaseProvider:
    if provider_type.lower() == "mock":
        return MockProvider()
    if provider_type.lower() == "real":
        return RealProvider(api_key_env_var=api_env_var)
    raise ValueError(f"Unknown provider type: {provider_type}")


def _build_summary_row(row: pd.Series, provider: BaseProvider, benchmark_close: pd.Series) -> dict[str, float | str]:
    close = provider.get_history(str(row["ticker"]), days=120)
    returns = close.pct_change().dropna()
    return {
        "ticker": str(row["ticker"]),
        "value": float(row["position_value"]),
        "pnl": float(row["pnl"]),
        "weight": float(row["weight"]),
        "vol_20d": rolling_volatility(close, 20),
        "vol_60d": rolling_volatility(close, 60),
        "drawdown": drawdown(close),
        "beta_spy": beta(close, benchmark_close),
        "var_hist": historical_var(returns),
    }


def _portfolio_history(portfolio: pd.DataFrame, provider: BaseProvider, days: int = 120) -> pd.Series:
    weighted_total: pd.Series | None = None
    for _, row in portfolio.iterrows():
        hist = provider.get_history(str(row["ticker"]), days=days) * float(row["quantity"])
        weighted_total = hist if weighted_total is None else weighted_total.add(hist, fill_value=0.0)
    if weighted_total is None:
        return pd.Series(dtype=float)
    return weighted_total.sort_index()


def run_once(config_path: str = "config.yaml", portfolio_path: str = "data/portfolio.csv") -> None:
    """Execute one monitoring cycle and print a summary table."""
    config = load_config(config_path)
    portfolio = load_portfolio(portfolio_path)

    provider_cfg = config.get("provider", {})
    provider = _provider_factory(
        provider_type=str(provider_cfg.get("type", "mock")),
        api_env_var=str(provider_cfg.get("real_api_key_env_var", "MARKET_DATA_API_KEY")),
    )

    tickers = portfolio["ticker"].tolist()
    latest = provider.get_latest_prices(tickers)
    metrics_df = compute_position_metrics(portfolio, latest)

    benchmark_ticker = str(config.get("benchmark_ticker", "SPY"))
    benchmark_close = provider.get_history(benchmark_ticker, days=120)

    summary_rows = [_build_summary_row(row, provider, benchmark_close) for _, row in metrics_df.iterrows()]
    summary_df = pd.DataFrame(summary_rows)
    total_value = portfolio_total_value(metrics_df)

    port_hist = _portfolio_history(portfolio, provider)
    portfolio_drawdown = drawdown(port_hist) if not port_hist.empty else 0.0

    alerts = evaluate_rules(
        metrics_df=metrics_df,
        portfolio_drawdown=portfolio_drawdown,
        rule_config=dict(config.get("rules", {})),
    )
    emit_alerts(alerts)

    print("\n=== Portfolio Copilot Summary ===")
    print(summary_df.to_string(index=False, float_format=lambda x: f"{x:,.4f}"))
    print(f"\nTotal Portfolio Value: {total_value:,.2f}")


def run_loop(config_path: str = "config.yaml", portfolio_path: str = "data/portfolio.csv") -> None:
    """Run monitoring loop every N seconds from config."""
    config = load_config(config_path)
    interval = int(config.get("loop_interval_seconds", 10))

    while True:
        try:
            run_once(config_path=config_path, portfolio_path=portfolio_path)
        except Exception as exc:  # basic top-level guard
            print(f"Error in loop iteration: {exc}")
        time.sleep(interval)


if __name__ == "__main__":
    run_loop()
