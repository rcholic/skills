---
name: meegle-api-setting
description: |
  Meegle OpenAPI for space/work item settings and configuration. Prerequisites: token and domain — see skill meegle-api-users.
metadata:
  openclaw: {}
  required_credentials:
    domain: "From meegle-api-users"
    plugin_access_token_or_user_access_token: "From meegle-api-users (obtain token first)"
---

# Meegle API — Setting

Setting and configuration related OpenAPIs (e.g. work item types, fields, process templates). Use when you need to read or change space or work item settings.

**Prerequisites:** Obtain domain and access token first; see skill **meegle-api-users** for domain, `plugin_access_token` / `user_access_token`, and request headers.

---

## Where to Find Setting Skills

| Skill | Directory | Description |
|-------|-----------|-------------|
| Space setting | `space-setting/` | Get work item types in space, Get business line details in space |
| Work item settings | `work-item-settings/` | Get basic work item settings, Update work item basic information settings |
| Field settings | `field-settings/` | Get field information, Create custom field, Update custom field |
| Relationship settings | `relationship-settings/` | List, create, update, delete work item relationships |
| Roles | `roles/` | Create workflow role, Get detailed role settings, Update/Delete workflow role |
| Workflow settings | `workflow-settings/` | Get workflow templates, Get detailed settings, Create/Update/Delete workflow templates |
