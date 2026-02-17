# Meegle API Skill

> Cursor AI skills for Meegle (Feishu Project / Lark Project) Open API

This repository provides a collection of Cursor Agent Skills that help AI assistants understand and correctly call Meegle Open API for space, work items, comments, views, and related operations.

## Overview

Meegle API Skill splits Meegle OpenAPI into multiple sub-skills by functional area. Before calling any Meegle API, read **meegle-api-users** first to obtain domain, access token, request headers, and other prerequisites.

## Required Credentials

All skills declare required credentials in their metadata. For the initial setup (meegle-api-users), you need:

| Credential | Description | Where to obtain |
|------------|-------------|-----------------|
| `plugin_id` | Plugin ID | Meegle Developer Platform → Plugin → Basic Information |
| `plugin_secret` | Plugin secret | Meegle Developer Platform → Plugin → Basic Information |
| `domain` | API host | `project.larksuite.com` (international) or `project.feishu.cn` (China) |

Optional context: `project_key` (space identifier), `user_key` (user identifier). In **Meegle Developer Platform**, double-click the **avatar** to get `user_key`, and double-click the **project icon** to get `project_key`. For user operations, `authorization_code` and `refresh_token` are used to obtain `user_access_token`. See [meegle-api-users](./meegle-api-users/SKILL.md) for details.

## Skill List

| Order | Sub-skill | When to read |
|-------|-----------|--------------|
| 1 | [meegle-api-users](./meegle-api-users/SKILL.md) | Domain, access token, context (project_key, user_key), request headers, global constraints. **Read this before any Meegle API call.** |
| 2 | [meegle-api-space](./meegle-api-space/SKILL.md) | Space (project) operations |
| 3 | [meegle-api-work-items](./meegle-api-work-items/SKILL.md) | Create, get, update work items (tasks, stories, bugs, etc.) |
| 4 | [meegle-api-setting](./meegle-api-setting/SKILL.md) | Settings, work item types, fields, process configuration |
| 5 | [meegle-api-comments](./meegle-api-comments/SKILL.md) | Comments on work items or other entities |
| 6 | [meegle-api-views-measurement](./meegle-api-views-measurement/SKILL.md) | Views, kanban, Gantt, charts, measurement |

## Work Item Sub-skills

`meegle-api-work-items` includes:

| Sub-skill | Directory | Description |
|-----------|-----------|-------------|
| Create / Read / Update work items | `work-item-read-and-write/` | Create work items, get details, update work items |
| List & search work items | `work-item-lists/` | Filter, search, full-text search, associated items, universal search |
| Workflows & nodes | `workflows-and-nodes/` | Workflow and node related APIs |
| Tasks | `tasks/` | Task related APIs |
| Attachment | `attachment/` | Work item attachment related APIs |
| Space association | `space-association/` | Space association related APIs |
| Group | `group/` | Work item group related APIs |

## Usage

1. Reference this repository as a Cursor skill, or copy the relevant `SKILL.md` files into your Cursor skills directory.
2. When working on Meegle-related tasks in Cursor, have the AI use the `Read` tool to load the corresponding `SKILL.md` for the needed API area.
3. Before any Meegle API call, have the AI read **meegle-api-users** to obtain domain, token, and request headers.

## API Regions

- **International**: `https://project.larksuite.com`
- **China (Feishu Project)**: `https://project.feishu.cn`

See [meegle-api-users](./meegle-api-users/SKILL.md) for domain and authentication details.

## Repository Structure

```
meegle-api-skill/
├── SKILL.md                 # Skill index (entry point)
├── README.md                # This file
├── meegle-api-users/        # Users and shared prerequisites
├── meegle-api-space/        # Space
├── meegle-api-work-items/   # Work items (includes sub-skills)
├── meegle-api-setting/      # Settings
├── meegle-api-comments/     # Comments
└── meegle-api-views-measurement/  # Views and measurement
```

## License

See the LICENSE file in the repository root, if present.
