---
name: black-box
description: Indestructible audit logs for agent actions, stored in TiDB Zero.
metadata:
  openclaw:
    emoji: 📦
    requires:
      bins: ["mysql", "python3"]
      env: ["TIDB_HOST", "TIDB_PORT", "TIDB_USER", "TIDB_PASSWORD"]
---

# Black Box (Powered by TiDB Zero)

## Goal
A "Flight Data Recorder" for Agents. Streams logs to a persistent cloud database, ensuring audit trails survive local crashes.

## Usage
*   **Log:** `python {baseDir}/run.py --action log --level ERROR --message "System crash imminent"`
*   **Read:** `python {baseDir}/run.py --action read --limit 5`
