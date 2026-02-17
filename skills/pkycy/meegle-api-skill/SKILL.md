---
name: meegle-api
description: |
  Meegle Open API skills (index). Read the specific skill for your need. Order: Users, Space, Work Items, Setting, Comments, Views & Measurement.
metadata:
  openclaw: {}
  required_credentials:
    plugin_id: "Plugin ID from Meegle Developer Platform → Plugin → Basic Information"
    plugin_secret: "Plugin secret from Meegle Developer Platform → Plugin → Basic Information"
    domain: "API host: project.larksuite.com (international) or project.feishu.cn (China)"
  optional_context:
    project_key: "Space identifier; in Meegle Developer Platform double-click the project icon to get it"
    user_key: "User identifier; in Meegle Developer Platform double-click the avatar to get it"
    user_access_token: "Required for write operations on behalf of user; obtain via OAuth (see meegle-api-users)"
---

# Meegle API (index)

Meegle OpenAPI is split into the following skills. Read **meegle-api-users** first for domain and token; then read the skill that matches your task.

| Order | Sub-skill (path) | When to read |
|-------|------------------|--------------|
| 1 | **meegle-api-users/SKILL.md** | Domain, access token, context (project_key, user_key), request headers, global constraints. Read this before any other Meegle API call. |
| 2 | **meegle-api-space/SKILL.md** | Space (project) operations. |
| 3 | **meegle-api-work-items/SKILL.md** | Create, get, update work items (tasks, stories, bugs). |
| 4 | **meegle-api-setting/SKILL.md** | Settings, work item types, fields, process configuration. |
| 5 | **meegle-api-comments/SKILL.md** | Comments on work items or other entities. |
| 6 | **meegle-api-views-measurement/SKILL.md** | Views, kanban, Gantt, charts, measurement. |

Each sub-skill lives under `meegle-api-skill/` (e.g. `meegle-api-users/SKILL.md`). Use the `Read` tool on the relevant path when you need that API area.
