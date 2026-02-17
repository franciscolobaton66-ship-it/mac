"""Alert sinks for console and JSONL logs."""

from __future__ import annotations

import json
from pathlib import Path

from .models import AlertEvent


def emit_alerts(alerts: list[AlertEvent], log_path: str | Path = "logs/alerts.jsonl") -> None:
    """Print alerts and append them to a JSONL file."""
    if not alerts:
        return

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as f:
        for alert in alerts:
            payload = {
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "severity": alert.severity,
                "rule_id": alert.rule_id,
            }
            print(f"[ALERT][{payload['severity'].upper()}] {payload['timestamp']} {payload['rule_id']}: {payload['message']}")
            f.write(json.dumps(payload) + "\n")
