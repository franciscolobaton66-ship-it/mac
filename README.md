# portfolio-copilot

A **portfolio monitoring copilot** for near real-time risk and performance insights.

> This project is **read-only/analytical** and intentionally includes **no brokerage execution or auto-trading code**.

## Project structure

```
portfolio-copilot/
├── config.yaml
├── requirements.txt
├── README.md
├── data/
│   └── portfolio.csv
├── logs/
│   └── alerts.jsonl (created at runtime)
├── src/
│   ├── __init__.py
│   ├── alerts.py
│   ├── analytics.py
│   ├── io_utils.py
│   ├── main.py
│   ├── models.py
│   ├── providers.py
│   └── rules.py
└── tests/
    └── test_analytics.py
```

## Features

- Loads holdings from `data/portfolio.csv` with schema:
  - `ticker, quantity, avg_cost, currency, asset_class`
- Pluggable market data providers:
  - `MockProvider` (offline synthetic data)
  - `RealProvider` skeleton (API key from env var)
- Analytics per position:
  - position value, PnL, total portfolio value
  - rolling volatility (20d, 60d)
  - drawdown
  - beta vs benchmark (`SPY` default)
  - historical VaR (default)
- Rule engine from `config.yaml`:
  - `max_weight_per_asset`
  - `stop_loss_pct_from_cost`
  - `max_portfolio_drawdown`
- Alerting:
  - prints to console
  - appends JSONL events to `logs/alerts.jsonl`

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run with MockProvider

The default `config.yaml` already uses `mock` provider.

Run one cycle (helpful for quick checks):

```bash
python -c "from src.main import run_once; run_once()"
```

Run continuous loop:

```bash
python -m src.main
```

Loop interval is controlled by `loop_interval_seconds` in `config.yaml`.

## RealProvider skeleton

`RealProvider` requires an API key environment variable (default: `MARKET_DATA_API_KEY`).
It currently raises `NotImplementedError` for live/history fetch methods and is designed as an integration point for your chosen market data API.

## Tests

Run unit tests for analytics:

```bash
pytest -q
```
