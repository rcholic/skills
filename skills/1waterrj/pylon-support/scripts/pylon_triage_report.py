#!/usr/bin/env python3
"""Generate a triage summary for one or more assignees."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Sequence

from pylon_client import api_request
from pylon_utils import (
    compute_time_window,
    get_user_id,
    get_window_days,
    humanize_timesince,
)


def fetch_issues(
    assignee_ids: Sequence[str],
    start: str,
    end: str,
    limit: int,
) -> List[dict]:
    params = {
        "start_time": start,
        "end_time": end,
        "limit": str(limit),
    }
    resp = api_request("/issues", params=params)
    raw = resp.get("data", [])
    targets = set(assignee_ids)
    if not targets:
        return raw
    filtered = []
    for issue in raw:
        assignee = ((issue.get("assignee") or {}).get("id"))
        if assignee and assignee in targets:
            filtered.append(issue)
    return filtered


def buckets_by_state(issues: Iterable[dict]) -> Dict[str, List[dict]]:
    bucket: Dict[str, List[dict]] = defaultdict(list)
    for issue in issues:
        state = (issue.get("state") or "unknown").lower()
        bucket[state].append(issue)
    return bucket


def format_issue(issue: dict) -> str:
    number = issue.get("number")
    title = issue.get("title", "(no title)")
    latest = issue.get("latest_message_time") or issue.get("updated_at")
    ago = humanize_timesince(latest)
    link = issue.get("link") or f"https://app.usepylon.com/issues?issueNumber={number}"
    return f"[# {number}] {title}\n    last update {ago} · {link}"


def print_summary(issues: List[dict], top_n: int) -> None:
    if not issues:
        print("No matching issues in window.")
        return

    counts = Counter((issue.get("state") or "unknown").lower() for issue in issues)
    print("Counts by state:")
    for state, count in counts.most_common():
        print(f"  {state:<18} {count}")
    print("")

    bucket = buckets_by_state(issues)
    for state, bucket_issues in bucket.items():
        print(f"=== {state.upper()} ({len(bucket_issues)}) ===")
        for issue in bucket_issues[:top_n]:
            print(format_issue(issue))
            print("")


def main() -> int:
    parser = argparse.ArgumentParser(description="Triage summary for Pylon issues")
    parser.add_argument(
        "--assignee-id",
        action="append",
        help="Filter to one or more assignee IDs (default: current user)",
    )
    parser.add_argument(
        "--window-days",
        type=int,
        help="Lookback window in days (default: config or 30)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Max issues to fetch from the API (default 500)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of issues to show per bucket (default 20)",
    )
    args = parser.parse_args()

    assignees = args.assignee_id or [get_user_id()]
    window_days = get_window_days(args.window_days)
    start, end = compute_time_window(window_days)

    issues = fetch_issues(assignees, start, end, args.limit)
    print(f"Assignees: {', '.join(assignees)}")
    print(f"Window: last {window_days} days ({start} → {end})")
    print(f"Issues returned: {len(issues)}\n")

    print_summary(issues, args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
