---
name: meegle-api-work-items
description: |
  Meegle OpenAPI for work items: create, get, update, list, search, and related operations.
  Prerequisites: token and domain — see skill meegle-api-users.
metadata:
  openclaw: {}
  required_credentials:
    domain: "From meegle-api-users"
    plugin_access_token_or_user_access_token: "From meegle-api-users (obtain token first)"
---

# Meegle API — Work Items

Create and manage work items (tasks, stories, bugs, etc.) in a Meegle space.

**Prerequisites:** Obtain domain and access token first; see skill **meegle-api-users**.

---

## Where to Find Work Item Skills

| Skill | Directory | Description |
|-------|-----------|-------------|
| Create / Read / Update work items | `work-item-read-and-write/` | Create work items, get work item details, update work items |
| List & search work items | `work-item-lists/` | Filter, search, full-text search, associated items, universal search |
| Workflows & nodes | `workflows-and-nodes/` | Workflow and node related APIs |
| Tasks | `tasks/` | Task related APIs |
| Attachment | `attachment/` | Work item attachment related APIs |
| Space association | `space-association/` | Space association related APIs |
| Group | `group/` | Work item group related APIs |
