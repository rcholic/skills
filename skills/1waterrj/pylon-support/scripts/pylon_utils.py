#!/usr/bin/env python3
"""Shared helpers for Pylon CLI utilities (config, IDs, formatting)."""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from pylon_client import api_request

CONFIG_PATH = Path(os.environ.get("PYLON_CONFIG_FILE", Path.home() / ".pylonrc"))
DEFAULT_WINDOW_DAYS = 30


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_config(updated: Dict[str, Any]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(updated, indent=2, sort_keys=True))


def get_user_id(force_refresh: bool = False) -> str:
    cfg = load_config()
    cached = cfg.get("user_id")
    if cached and not force_refresh:
        return cached
    resp = api_request("/me")
    user_id = (resp.get("data") or {}).get("id")
    if not user_id:
        raise RuntimeError("Unable to determine user id from /me response")
    cfg["user_id"] = user_id
    save_config(cfg)
    return user_id


def set_user_id(user_id: str) -> None:
    cfg = load_config()
    cfg["user_id"] = user_id
    save_config(cfg)


def get_window_days(override: Optional[int] = None) -> int:
    if override is not None:
        return override
    cfg = load_config()
    return int(cfg.get("window_days", DEFAULT_WINDOW_DAYS))


def set_window_days(days: int) -> None:
    cfg = load_config()
    cfg["window_days"] = int(days)
    save_config(cfg)


def compute_time_window(window_days: int) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=window_days)
    return (
        start.isoformat(timespec="seconds"),
        now.isoformat(timespec="seconds"),
    )


def parse_timestamp(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def humanize_timesince(ts: Optional[str]) -> str:
    dt = parse_timestamp(ts)
    if not dt:
        return "unknown"
    delta = datetime.now(timezone.utc) - dt
    days = delta.days
    hours = delta.seconds // 3600
    mins = (delta.seconds % 3600) // 60
    if days > 0:
        return f"{days}d {hours}h ago"
    if hours > 0:
        return f"{hours}h {mins}m ago"
    return f"{mins}m ago"
