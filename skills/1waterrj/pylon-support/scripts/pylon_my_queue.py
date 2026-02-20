#!/usr/bin/env python3
"""Summarize the current user's Pylon queue."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from typing import Iterable, List

from pylon_client import api_request
from pylon_utils import (
    compute_time_window,
    get_user_id,
    get_window_days,
    humanize_timesince,
)


def fetch_issues(assignee_id: str, start: str, end: str, limit: int) -> List[dict]:
    params = {
        "start_time": start,
        "end_time": end,
        "limit": str(limit),
    }
    resp = api_request("/issues", params=params)
    raw = resp.get("data", [])
    filtered = []
    for issue in raw:
        assignee = (issue.get("assignee") or {}).get("id")
        if assignee == assignee_id:
            filtered.append(issue)
    return filtered


def format_issue(issue: dict) -> str:
    number = issue.get("number")
    title = issue.get("title", "(no title)")
    state = (issue.get("state") or "").lower()
    latest = issue.get("latest_message_time") or issue.get("updated_at")
    ago = humanize_timesince(latest)
    link = issue.get("link") or f"https://app.usepylon.com/issues?issueNumber={number}"
    priority = ((issue.get("custom_fields") or {}).get("priority") or {}).get("value")
    priority_str = f" · priority: {priority}" if priority else ""
    return f"[# {number}] {state}{priority_str}\n    {title}\n    latest update {ago} · {link}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize your Pylon queue")
    parser.add_argument(
        "--assignee-id",
        help="Override the assignee id (defaults to cached / current user)",
    )
    parser.add_argument(
        "--window-days",
        type=int,
        help="Lookback window in days (defaults to config or 30)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=200,
        help="Max issues to fetch from the API (default 200)",
    )
    args = parser.parse_args()

    assignee_id = args.assignee_id or get_user_id()
    window_days = get_window_days(args.window_days)
    start, end = compute_time_window(window_days)

    issues = fetch_issues(assignee_id, start, end, args.limit)
    counts = Counter((issue.get("state") or "unknown").lower() for issue in issues)

    print(f"Assignee: {assignee_id}")
    print(f"Window: last {window_days} days ({start} → {end})")
    print(f"Issues returned: {len(issues)}\n")

    if counts:
        print("By state:")
        for state, count in counts.most_common():
            print(f"  {state:<18} {count}")
        print("")

    if not issues:
        print("No matching issues in this window.")
        return 0

    print("Details:")
    for issue in sorted(
        issues,
        key=lambda x: (x.get("state") or "", x.get("latest_message_time") or ""),
        reverse=True,
    ):
        print(format_issue(issue))
        print("")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
