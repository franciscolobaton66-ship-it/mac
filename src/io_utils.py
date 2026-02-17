"""I/O helpers for configuration and portfolio data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

REQUIRED_COLUMNS = {"ticker", "quantity", "avg_cost", "currency", "asset_class"}


def load_config(path: str | Path) -> dict[str, Any]:
    """Load YAML config from disk."""
    with Path(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_portfolio(path: str | Path) -> pd.DataFrame:
    """Load holdings CSV and validate required columns."""
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Portfolio file missing required columns: {sorted(missing)}")
    return df
