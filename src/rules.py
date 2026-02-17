"""Rule engine for portfolio risk thresholds."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from .models import AlertEvent


def evaluate_rules(
    metrics_df: pd.DataFrame,
    portfolio_drawdown: float,
    rule_config: dict[str, float],
) -> list[AlertEvent]:
    """Evaluate configured rules and emit alerts."""
    alerts: list[AlertEvent] = []
    now = datetime.now(timezone.utc)

    max_weight = float(rule_config.get("max_weight_per_asset", 1.0))
    overweight = metrics_df[metrics_df["weight"] > max_weight]
    for _, row in overweight.iterrows():
        alerts.append(
            AlertEvent(
                message=f"{row['ticker']} exceeds max weight: {row['weight']:.2%} > {max_weight:.2%}",
                timestamp=now,
                severity="warning",
                rule_id="max_weight_per_asset",
            )
        )

    stop_loss = float(rule_config.get("stop_loss_pct_from_cost", 1.0))
    loss_pct = (metrics_df["latest_price"] - metrics_df["avg_cost"]) / metrics_df["avg_cost"]
    hit_stop = metrics_df[loss_pct <= -stop_loss]
    for _, row in hit_stop.iterrows():
        loss = (row["latest_price"] - row["avg_cost"]) / row["avg_cost"]
        alerts.append(
            AlertEvent(
                message=f"{row['ticker']} breached stop-loss: {loss:.2%} <= -{stop_loss:.2%}",
                timestamp=now,
                severity="critical",
                rule_id="stop_loss_pct_from_cost",
            )
        )

    max_dd = float(rule_config.get("max_portfolio_drawdown", 1.0))
    if portfolio_drawdown <= -max_dd:
        alerts.append(
            AlertEvent(
                message=(
                    f"Portfolio drawdown breached: {portfolio_drawdown:.2%} <= -{max_dd:.2%}"
                ),
                timestamp=now,
                severity="critical",
                rule_id="max_portfolio_drawdown",
            )
        )

    return alerts
