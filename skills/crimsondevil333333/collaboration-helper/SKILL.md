---
name: collaboration-helper
description: Track action items and coordination signals for the community, including quick task creation, status checks, and handoff notes. Use this when you need to log a collaborative task or check what everyone is currently working on.
---

# Collaboration Helper

## Overview

`t` scripts/collaboration_helper.py` acts as a lightweight team tracker:

- `list` shows all open/in-progress tasks with owners, priorities, and creation timestamps.
- `add` lets you capture a new action item with an owner, priority, and optional context.
- `complete` marks a task as finished.

The data is stored in `data/tasks.json`, so your collaboration state survives multiple skill runs.

## Resources

- **GitHub:** https://github.com/CrimsonDevil333333/collaboration-helper
- **ClawHub:** https://www.clawhub.ai/skills/collaboration-helper
