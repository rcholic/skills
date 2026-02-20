#!/usr/bin/env python3
"""Inspect and manage local Pylon CLI configuration."""
from __future__ import annotations

import argparse
from pathlib import Path

from pylon_utils import (
    CONFIG_PATH,
    get_user_id,
    get_window_days,
    load_config,
    save_config,
    set_user_id,
    set_window_days,
)


def show_summary() -> None:
    cfg = load_config()
    user_id = cfg.get("user_id")
    window_days = cfg.get("window_days", None)
    print(f"Config file: {CONFIG_PATH}")
    print(f"User ID: {user_id or 'not cached'}")
    if window_days:
        print(f"Default window (days): {window_days}")
    else:
        print("Default window (days): using builtin default")


def main() -> int:
    parser = argparse.ArgumentParser(description="Pylon config helper")
    parser.add_argument(
        "--refresh-user-id",
        action="store_true",
        help="Call /me and cache the current user id",
    )
    parser.add_argument("--set-user-id", help="Explicitly set a user id in the config")
    parser.add_argument(
        "--set-window-days",
        type=int,
        help="Persist a default lookback window (days) for other scripts",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Print the current configuration summary (default)",
    )
    args = parser.parse_args()

    if args.set_user_id:
        set_user_id(args.set_user_id)
        print(f"Saved user id {args.set_user_id} -> {CONFIG_PATH}")

    if args.set_window_days is not None:
        set_window_days(args.set_window_days)
        print(f"Saved default window_days={args.set_window_days} -> {CONFIG_PATH}")

    if args.refresh_user_id:
        user_id = get_user_id(force_refresh=True)
        print(f"Discovered user id via /me: {user_id}")

    if args.set_user_id or args.set_window_days is not None or args.refresh_user_id:
        print("")

    if args.show or not any(
        [args.set_user_id, args.set_window_days is not None, args.refresh_user_id]
    ):
        show_summary()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
