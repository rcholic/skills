#!/usr/bin/env python3
"""
MoltFlow Outreach - Bulk Send, Scheduled Messages, Custom Groups
"""
import os
import json
import requests

API_KEY = os.environ.get("MOLTFLOW_API_KEY")
BASE_URL = os.environ.get("MOLTFLOW_API_URL", "https://apiv2.waiflow.app")

if not API_KEY:
    print("Error: MOLTFLOW_API_KEY environment variable not set")
    exit(1)

headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


# ============================================================================
# Custom Groups
# ============================================================================

def list_custom_groups(limit: int = 50, offset: int = 0):
    """List all custom contact groups."""
    r = requests.get(
        f"{BASE_URL}/api/v2/custom-groups",
        headers=headers,
        params={"limit": limit, "offset": offset},
    )
    r.raise_for_status()
    return r.json()


def create_custom_group(name: str, members: list = None):
    """Create a new custom group. members = list of {"phone": str, "name": str?} dicts."""
    data = {"name": name}
    if members:
        data["members"] = members
    r = requests.post(f"{BASE_URL}/api/v2/custom-groups", headers=headers, json=data)
    r.raise_for_status()
    return r.json()


def add_members(group_id: str, contacts: list):
    """Add members to a custom group. contacts = list of {"phone": str} dicts."""
    r = requests.post(
        f"{BASE_URL}/api/v2/custom-groups/{group_id}/members/add",
        headers=headers,
        json={"contacts": contacts},
    )
    r.raise_for_status()
    return r.json()


def export_group_csv(group_id: str):
    """Export group members as CSV."""
    r = requests.get(
        f"{BASE_URL}/api/v2/custom-groups/{group_id}/export/csv",
        headers=headers,
    )
    r.raise_for_status()
    return r.text


def export_group_json(group_id: str):
    """Export group members as JSON."""
    r = requests.get(
        f"{BASE_URL}/api/v2/custom-groups/{group_id}/export/json",
        headers=headers,
    )
    r.raise_for_status()
    return r.json()


# ============================================================================
# Bulk Send
# ============================================================================

def create_bulk_job(session_id: str, custom_group_id: str, message_content: str):
    """Create a bulk send job targeting a custom group."""
    r = requests.post(
        f"{BASE_URL}/api/v2/bulk-send",
        headers=headers,
        json={
            "session_id": session_id,
            "custom_group_id": custom_group_id,
            "message_content": message_content,
        },
    )
    r.raise_for_status()
    return r.json()


def list_bulk_jobs(limit: int = 50):
    """List all bulk send jobs."""
    r = requests.get(
        f"{BASE_URL}/api/v2/bulk-send",
        headers=headers,
        params={"limit": limit},
    )
    r.raise_for_status()
    return r.json()


def get_bulk_job(job_id: str):
    """Get bulk job details and progress."""
    r = requests.get(f"{BASE_URL}/api/v2/bulk-send/{job_id}", headers=headers)
    r.raise_for_status()
    return r.json()


def pause_bulk_job(job_id: str):
    """Pause a running bulk send job."""
    r = requests.post(f"{BASE_URL}/api/v2/bulk-send/{job_id}/pause", headers=headers)
    r.raise_for_status()
    return r.json()


def resume_bulk_job(job_id: str):
    """Resume a paused bulk send job."""
    r = requests.post(f"{BASE_URL}/api/v2/bulk-send/{job_id}/resume", headers=headers)
    r.raise_for_status()
    return r.json()


def cancel_bulk_job(job_id: str):
    """Cancel a bulk send job."""
    r = requests.post(f"{BASE_URL}/api/v2/bulk-send/{job_id}/cancel", headers=headers)
    r.raise_for_status()
    return r.json()


# ============================================================================
# Scheduled Messages
# ============================================================================

def create_scheduled_message(
    session_id: str,
    custom_group_id: str,
    message_content: str,
    name: str = "Scheduled Message",
    schedule_type: str = "one_time",
    cron_expression: str = None,
    timezone: str = "UTC",
    scheduled_time: str = None,
):
    """Create a scheduled message.

    schedule_type: one_time, daily, weekly, monthly, cron
    scheduled_time: ISO 8601 datetime (required for 'one_time')
    cron_expression: cron string (required for recurring types)
    """
    data = {
        "session_id": session_id,
        "custom_group_id": custom_group_id,
        "message_content": message_content,
        "name": name,
        "schedule_type": schedule_type,
        "timezone": timezone,
    }
    if scheduled_time:
        data["scheduled_time"] = scheduled_time
    if cron_expression:
        data["cron_expression"] = cron_expression
    r = requests.post(f"{BASE_URL}/api/v2/scheduled-messages", headers=headers, json=data)
    r.raise_for_status()
    return r.json()


def list_scheduled_messages(limit: int = 50):
    """List all scheduled messages."""
    r = requests.get(
        f"{BASE_URL}/api/v2/scheduled-messages",
        headers=headers,
        params={"limit": limit},
    )
    r.raise_for_status()
    return r.json()


def pause_scheduled(message_id: str):
    """Pause a scheduled message."""
    r = requests.post(
        f"{BASE_URL}/api/v2/scheduled-messages/{message_id}/pause",
        headers=headers,
    )
    r.raise_for_status()
    return r.json()


def resume_scheduled(message_id: str):
    """Resume a paused scheduled message."""
    r = requests.post(
        f"{BASE_URL}/api/v2/scheduled-messages/{message_id}/resume",
        headers=headers,
    )
    r.raise_for_status()
    return r.json()


def cancel_scheduled(message_id: str):
    """Cancel a scheduled message."""
    r = requests.post(
        f"{BASE_URL}/api/v2/scheduled-messages/{message_id}/cancel",
        headers=headers,
    )
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    print("MoltFlow Outreach")
    print("=" * 40)

    # Custom groups
    groups = list_custom_groups()
    group_list = groups.get("groups", groups) if isinstance(groups, dict) else groups
    print(f"\nCustom Groups: {len(group_list) if isinstance(group_list, list) else 0}")

    # Bulk jobs
    jobs = list_bulk_jobs()
    job_list = jobs.get("jobs", jobs) if isinstance(jobs, dict) else jobs
    print(f"Bulk Jobs: {len(job_list) if isinstance(job_list, list) else 0}")

    # Scheduled messages
    scheduled = list_scheduled_messages()
    sched_list = scheduled.get("messages", scheduled) if isinstance(scheduled, dict) else scheduled
    print(f"Scheduled Messages: {len(sched_list) if isinstance(sched_list, list) else 0}")
