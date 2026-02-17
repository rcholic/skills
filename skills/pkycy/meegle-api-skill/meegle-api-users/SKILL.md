---
name: meegle-api-users
description: |
  Meegle API prerequisite: domain, access token (plugin/user), context (project_key, user_key),
  request headers, and global constraints. User-related OpenAPIs. Read this first before other Meegle API skills.
metadata:
  openclaw: {}
  required_credentials:
    plugin_id:
      description: "Plugin ID from Meegle Developer Platform → Plugin → Basic Information"
      source: secret
    plugin_secret:
      description: "Plugin secret from Meegle Developer Platform → Plugin → Basic Information"
      source: secret
    domain:
      description: "API host: project.larksuite.com (international) or project.feishu.cn (China)"
      default: project.larksuite.com
  optional_credentials:
    authorization_code:
      description: "OAuth code from getAuthCode(); required for user_access_token"
    refresh_token:
      description: "From user_plugin_token response; for refreshing user_access_token"
  context:
    project_key: "Space identifier; in Meegle Developer Platform double-click the project icon to get it"
    user_key: "User identifier; in Meegle Developer Platform double-click the avatar to get it (or from user_access_token response)"
---

# Meegle API — Users (and shared prerequisites)

Shared prerequisites for all Meegle OpenAPI calls. Other Meegle API skills (Space, Work Items, Setting, Comments, Views & Measurement) assume you have followed this skill for token and headers.

## Domain (API base host)

Replace `{domain}` in requests with the actual Meegle API host for your region:

| Region | domain |
|--------|--------|
| **International** | `project.larksuite.com` — base URL: `https://project.larksuite.com` |
| **China (Feishu Project)** | `project.feishu.cn` — base URL: `https://project.feishu.cn` |

Example: plugin token URL is `https://{domain}/open_api/authen/plugin_token` — use `https://project.larksuite.com/open_api/authen/plugin_token` (international) or `https://project.feishu.cn/open_api/authen/plugin_token` (China).

---

## Obtain Access Token

Generate Meegle access credentials for OpenClaw to call OpenAPI.

### When to Use

- Before calling any Meegle OpenAPI
- When plugin_access_token has expired (valid for 2 hours)
- When an operation must be performed on behalf of a specific user

### Capabilities

- `generate_plugin_token` — obtain plugin_access_token or virtual_plugin_token
- `exchange_user_access_token` — exchange authorization code for user_access_token
- `refresh_user_access_token` — refresh an expired user_access_token

### API Spec: obtain_access_token

```yaml
name: meegle.obtain_access_token
description: >
  Generate Meegle access credentials for OpenClaw to call OpenAPI.
  Supports plugin_access_token, virtual_plugin_token (dev),
  and user_access_token (on behalf of a user).

when_to_use:
  - Before calling any Meegle OpenAPI
  - When plugin_access_token expires (2 hours)
  - When an operation must be performed on behalf of a specific user

capabilities:
  - generate_plugin_token
  - generate_virtual_plugin_token
  - exchange_user_access_token
  - refresh_user_access_token

flows:

  generate_plugin_token:
    description: Obtain plugin_access_token or virtual_plugin_token
    http:
      method: POST
      path: /open_api/authen/plugin_token
    headers:
      Content-Type: application/json
    body:
      plugin_id:
        type: string
        required: true
      plugin_secret:
        type: string
        required: true
      type:
        type: integer
        required: false
        default: 0
        enum:
          - 0  # plugin_access_token
          - 1  # virtual_plugin_token
    response:
      token:
        type: string
      expire_time:
        type: integer
        unit: seconds
    notes:
      - Token valid for 7200 seconds
      - Token must be cached and reused until expiration

  exchange_user_access_token:
    description: >
      Exchange authorization code for user_access_token.
      Must be called server-side.
    prerequisites:
      - plugin_access_token
      - authorization_code (from client getAuthCode)
    http:
      method: POST
      path: /open_api/authen/user_plugin_token
    headers:
      Content-Type: application/json
      X-Plugin-Token: "{{plugin_access_token}}"
    body:
      code:
        type: string
        required: true
      grant_type:
        type: string
        required: true
        fixed: authorization_code
    response:
      token:
        type: string
        description: user_access_token
      refresh_token:
        type: string
      expire_time:
        type: integer
      refresh_token_expire_time:
        type: integer
      user_key:
        type: string
      saas_tenant_key:
        type: string

  refresh_user_access_token:
    description: Refresh an expired user_access_token
    prerequisites:
      - plugin_access_token
      - refresh_token
    http:
      method: POST
      path: /open_api/authen/refresh_token
    headers:
      Content-Type: application/json
      X-Plugin-Token: "{{plugin_access_token}}"
    body:
      refresh_token:
        type: string
        required: true
      type:
        type: integer
        required: true
        fixed: 1
    response:
      token:
        type: string
      expire_time:
        type: integer
      refresh_token:
        type: string
      refresh_token_expire_time:
        type: integer

usage_in_other_skills:
  plugin_access_token:
    headers:
      X-Plugin-Token: "{{plugin_access_token}}"
      X-User-Key: "{{user_key}}"
  user_access_token:
    headers:
      X-Plugin-Token: "{{user_access_token}}"

constraints:
  - user_access_token must be generated server-side
  - front-end plugins cannot call OpenAPI directly
  - permissions depend on plugin scope, space installation, and user role

recommended_openclaw_strategy:
  - Cache plugin_access_token globally
  - Bind user_access_token to conversation/session
  - Auto-refresh user_access_token when expired
  - Choose token type per API based on permission requirements
```

### How to use tokens (when calling other OpenAPIs)

- **plugin_access_token**: Add header `X-Plugin-Token: {{plugin_access_token}}`; optionally `X-User-Key: {{user_key}}`.
- **user_access_token**: Add header `X-Plugin-Token: {{user_access_token}}` (use the user token here, not the plugin token).

### Constraints and recommendations

- user_access_token must be obtained server-side via authorization code; front-end plugins cannot call OpenAPI directly.
- Permissions depend on plugin scope, space installation, and user role.
- Recommended: cache plugin_access_token globally; bind user_access_token to conversation/session; refresh user_access_token when expired; choose token type per API based on permission requirements.

---

## Skill Pack (implementation details)

Auth, context, request headers, and global constraints for OpenClaw implementation and integration.

### Auth Layer

```yaml
name: meegle.auth.get_plugin_token
type: internal
description: Get or refresh Meegle plugin_access_token (cache and reuse)
inputs:
  plugin_id:
    type: string
    required: true
    source: secret
    description: |
      Plugin ID.
      Location: Meegle Developer Platform → Plugin → Basic Information → Plugin ID
  plugin_secret:
    type: string
    required: true
    source: secret
    description: |
      Plugin secret.
      Location: Meegle Developer Platform → Plugin → Basic Information → Plugin Secret
  type:
    type: integer
    required: false
    default: 0
    description: |
      0 = plugin_access_token
      1 = virtual_plugin_token (dev only)
http:
  method: POST
  url: https://{domain}/open_api/authen/plugin_token
  notes: domain = project.larksuite.com (international) or project.feishu.cn (China Feishu Project)
headers:
  Content-Type: application/json
outputs:
  token:
    type: string
    description: plugin_access_token
  expire_time:
    type: number
    description: Token validity in seconds

---

name: meegle.auth.get_user_token
type: flow
description: Exchange OAuth authorization code for user_access_token (act on behalf of user)
inputs:
  auth_code:
    type: string
    required: true
    description: |
      OAuth authorization code.
      Obtain via front-end: window.JSSDK.utils.getAuthCode()
  plugin_access_token:
    type: string
    required: true
http:
  method: POST
  url: https://{domain}/open_api/authen/user_plugin_token
headers:
  Content-Type: application/json
  X-Plugin-Token: "{{plugin_access_token}}"
body:
  code: "{{auth_code}}"
  grant_type: authorization_code
outputs:
  user_access_token:
    type: string
  refresh_token:
    type: string
  expire_time:
    type: number
  refresh_token_expire_time:
    type: number
  user_key:
    type: string
    description: |
      Current user unique identifier.
      Source: user_key field in this response

---

name: meegle.auth.refresh_user_token
type: internal
description: Refresh user_access_token
inputs:
  refresh_token:
    type: string
    required: true
  plugin_access_token:
    type: string
    required: true
http:
  method: POST
  url: https://{domain}/open_api/authen/refresh_token
headers:
  Content-Type: application/json
  X-Plugin-Token: "{{plugin_access_token}}"
body:
  type: 1
outputs:
  user_access_token:
    type: string
  expire_time:
    type: number
  refresh_token:
    type: string
  refresh_token_expire_time:
    type: number
```

### Context Layer

```yaml
name: meegle.context.resolve_project
type: utility
description: Resolve project_key
inputs:
  project_key:
    type: string
    required: false
    description: |
      Space unique identifier.
      How to get: In Meegle Developer Platform, double-click the project icon; or use project_key from project URL.
behavior:
  - If default project_key is configured, use it
  - Otherwise ask user to provide
outputs:
  project_key:
    type: string

---

name: meegle.context.resolve_user_key
type: utility
description: Resolve user_key
inputs:
  user_key:
    type: string
    required: false
    description: |
      User unique identifier.
      How to get: In Meegle Developer Platform, double-click the avatar; or use user_key from user_access_token response.
  user_access_token:
    type: string
    required: false
behavior:
  - If user_access_token exists, use its user_key first
  - Otherwise ask user to provide explicitly
outputs:
  user_key:
    type: string
```

### Header Decision Rule

```yaml
name: meegle.http.prepare_headers
type: internal
description: Build OpenAPI request headers by operation type
inputs:
  operation_type:
    type: string
    required: true
    description: read | write
  plugin_access_token:
    type: string
    required: true
  user_access_token:
    type: string
    required: false
  user_key:
    type: string
    required: false
rules:
  - if: operation_type == "write" and user_access_token exists
    headers:
      X-Plugin-Token: "{{user_access_token}}"
  - if: operation_type == "read"
    headers:
      X-Plugin-Token: "{{plugin_access_token}}"
      X-User-Key: "{{user_key}}"
```

### Global Constraints

- plugin_access_token is valid for 7200 seconds; cache and reuse.
- user_access_token must be used server-side only.
- Prefer user_access_token for write operations.
- All OpenAPI calls must respect 15 QPS per token.

---

## Users (OpenAPIs)

User-related Meegle OpenAPIs (e.g. user info, list members). Prerequisites: domain and token from sections above.

---

## Get User Group Members

Query the members of user groups in a specified space. Supports space administrator, space member, and custom user groups.

### Points to Note

**This API only supports user access credentials (user_access_token).** Plugin access token is not supported. See Obtain Access Credentials for how to get user_access_token.

### When to Use

- When listing members of space admin, space member, or custom user groups
- When resolving user_group_ids to user_keys in a space
- When building permission or membership checks

### API Spec: get_user_group_members

```yaml
name: get_user_group_members
type: api
description: >
  Query the members of user groups in a specified space.
  Supports PROJECT_ADMIN, PROJECT_MEMBER, and CUSTOMIZE user group types.

auth:
  type: user_access_token
  note: Only user_access_token is supported; plugin_access_token is NOT supported.

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/user_groups/members/page
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{user_access_token}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
      project_key: Double-click space name in Meegle.
      simple_name: From space URL, e.g. https://meegle.com/doc/overview → doc.

inputs:
  user_group_type:
    type: string
    required: true
    enum: [PROJECT_ADMIN, PROJECT_MEMBER, CUSTOMIZE]
    description: |
      PROJECT_ADMIN: Space administrator
      PROJECT_MEMBER: Space member
      CUSTOMIZE: Custom user group
  user_group_ids:
    type: array
    items: string
    required: false
    constraints:
      max_items: 50
    description: >
      List of user group IDs. From user group page URL, e.g.
      .../userGroup/756472096042365xxxx → 756472096042365xxxx.
      When user_group_type=CUSTOMIZE, if empty, returns all members of all custom user groups in the space.
      Max 50 user groups per request.
  page_num:
    type: integer
    required: false
    default: 1
    description: Page number. Default first page.
  page_size:
    type: integer
    required: false
    default: 50
    constraints:
      max: 100
    description: Items per page. Default 50, max 100.

outputs:
  data:
    type: object
    properties:
      list:
        type: array
        items:
          user_count: integer
          user_members: array
          id: string
          name: string
        description: |
          user_members: user_key list of members
          id: user group ID
          name: user group name
      pagination:
        page_num: integer
        page_size: integer
        has_more: boolean

constraints:
  - Permission: Permission Management – Users
  - user_group_ids max 50 when user_group_type=CUSTOMIZE
  - page_size max 100

error_mapping:
  20002: Page size limit (more than 100 per page)
  1000053008: User group type not supported
  1000053010: User group not found (no matching user group in the space)
  1000053011: User group limit (more than 50 user groups in one request)
```

### Usage notes

- **user_access_token only**: Use `X-Plugin-Token: {{user_access_token}}`; plugin token will not work.
- **user_group_type**: PROJECT_ADMIN / PROJECT_MEMBER / CUSTOMIZE.
- **user_group_ids**: For CUSTOMIZE, optional; omit to get all custom user groups’ members. From URL `.../userGroup/{id}`.
- **page_size**: Max 100; default 50.

---

## Get Tenant User List

Perform a fuzzy search for users within the tenant and return their detailed information. Searches by user name or other keywords; e.g. query "user1" returns users like "user1" and "user1.1".

### When to Use

- When searching for users in the tenant by name or keyword
- When resolving user_key from partial names
- When building user pickers or member selection UIs

### API Spec: get_tenant_user_list

```yaml
name: get_tenant_user_list
type: api
description: >
  Fuzzy search for users within the tenant and return detailed information.
  Supports query by user name. E.g. "user1" returns "user1", "user1.1", etc.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/user/search
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  query:
    type: string
    required: false
    description: Search keywords, e.g. user names.
  project_key:
    type: string
    required: false
    description: |
      Space ID (project_key). Determines which tenant to search.
      Required if:
      - Enterprise plugin: user's primary tenant != plugin tenant
      - Marketplace plugin: always required
      Obtain: Double-click space name in Meegle project space.

outputs:
  data:
    type: array
    items:
      avatar_url: string
      name_cn: string
      name_en: string
      user_id: integer
      user_key: string
      email: string
      name:
        en_us: string
        default: string
        zh_cn: string
      username: string
      out_id: string
      status: string
    description: List of matching user objects (avatar_url, name_cn/en, user_key, email, etc.).

constraints:
  - Permission: Permission Management – Users
  - project_key required for marketplace plugin; for enterprise plugin when user tenant != plugin tenant

error_mapping:
  30006: User not found (user_key in Header not found)
  1000052063: Project not exist (incorrect project_key)
```

### Usage notes

- **query**: Fuzzy search by user name; omit to list users in the tenant.
- **project_key**: Required for marketplace plugins; for enterprise plugins, required when the user's primary tenant differs from the plugin tenant.

---

## Get User Details

Obtain detailed information of one or more specified users by user_key, out_id (UnionId), or email.

### Points to Note

When using a **virtual token**, only collaborators of the plugin can be retrieved. To query other users, use the official (non-virtual) token.

When using **plugin_access_token** for this interface, **X-User-Key is not required**.

### When to Use

- When resolving user_key / out_id / email to full user profile
- When fetching avatar, name, email, status for display
- When batching user lookups (up to 100 per request)

### API Spec: get_user_details

```yaml
name: get_user_details
type: api
description: >
  Obtain detailed information of one or more specified users.
  Supports lookup by user_keys, out_ids (UnionId), or emails.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  note: X-User-Key is not required when using plugin_access_token.

http:
  method: POST
  url: https://{domain}/open_api/user/query
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"

inputs:
  user_keys:
    type: array
    items: string
    required: false
    constraints:
      max_items: 100
    description: |
      Array of Meegle user_keys.
      Obtain: Double-click personal avatar in Meegle space; or use Get Tenant User List.
      At least one of user_keys, out_ids, emails must be provided. Max 100 per request.
  out_ids:
    type: array
    items: string
    required: false
    constraints:
      max_items: 100
    description: |
      Array of UnionIds from Feishu Open Platform (unified identity across apps).
      At least one of user_keys, out_ids, emails must be provided. Max 100.
  emails:
    type: array
    items: string
    required: false
    constraints:
      max_items: 100
    description: |
      Array of emails. Emails must be bound on Feishu.
      At least one of user_keys, out_ids, emails must be provided. Max 100.
  tenant_key:
    type: string
    required: false
    description: |
      saas_tenant_key of the tenant where the user to be queried is located.
      For emails query when querying users from a tenant other than the plugin's
      (e.g. tenant Y installs plugin from tenant X — pass tenant Y's tenant_key).
      If empty, query is under the plugin's tenant.

outputs:
  data:
    type: array
    items:
      user_id: integer
      name_cn: string
      name_en: string
      out_id: string
      name:
        default: string
        en_us: string
        zh_cn: string
      user_key: string
      username: string
      email: string
      avatar_url: string
      status: string
    description: List of user detail objects.

constraints:
  - Permission: Permission Management – Users
  - At least one of user_keys, out_ids, emails must be provided
  - Max 100 users per request (across all three arrays)

error_mapping:
  30006: User not found (query result empty; check user_key / out_ids / emails)
  20004: Search user limit (exceeds 100 records)
```

### Usage notes

- **user_keys / out_ids / emails**: At least one must be provided; max 100 identifiers in total per request.
- **tenant_key**: When querying by email for users in a tenant other than the plugin's, pass that tenant's saas_tenant_key.
- **X-User-Key**: Not required when using plugin_access_token for this API.

---

## Get Team Member in Space

Return a list of teams whose visibility scope is searchable within the specified space and whose visible project space is the requested space. Each team includes members (user_keys) and administrators.

### When to Use

- When listing teams visible within a space
- When fetching team members and administrators
- When building team pickers or membership UIs

### API Spec: get_team_member_in_space

```yaml
name: get_team_member_in_space
type: api
description: >
  Return a list of teams whose visibility scope is searchable within the specified
  space and whose visible project space is the requested space.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: GET
  url: https://{domain}/open_api/{project_key}/teams/all
  headers:
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
      project_key: Double-click space name in Meegle.
      simple_name: From space URL, e.g. https://meegle.com/doc/overview → doc.

inputs:
  offset:
    type: integer
    required: false
    description: Page offset (0-based).
  limit:
    type: integer
    required: false
    default: 300
    constraints:
      max: 300
    description: Items per page. Max 300. Default 300 if not provided.

outputs:
  data:
    type: array
    items:
      team_name: string
      user_keys: array
      administrators: array
      team_id: integer
    description: |
      user_keys: Member list of the team
      administrators: Admin list of the team
      team_id: Team ID
  has_more:
    type: boolean
    description: Whether more teams exist.

constraints:
  - Permission: Permission Management – Users
  - limit max 300; default 300

error_mapping:
  30006: User not found (user_key in Header not found)
```

### Usage notes

- **project_key**: Path parameter identifying the space.
- **offset / limit**: Pagination; offset 0-based; limit max 300, default 300.

---

## Create Customized User Group

Create a custom user group in a specified space. Only user members (user_key) are supported; department members cannot be added.

### Points to Note

**This API only supports user access credentials (user_access_token).** See Get Access Credentials for how to obtain user_access_token.

### When to Use

- When creating a new custom user group in a space
- When defining a group of users by user_key list
- When setting up permission or notification groups

### API Spec: create_customized_user_group

```yaml
name: create_customized_user_group
type: api
description: >
  Create a custom user group in a specified space.
  Only user members (user_key) are supported; department members cannot be added.

auth:
  type: user_access_token
  note: Only user_access_token is supported; plugin_access_token is NOT supported.

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/user_group
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{user_access_token}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
      project_key: Double-click space name in Meegle.
      simple_name: From space URL, e.g. https://meegle.com/doc/overview → doc.

inputs:
  name:
    type: string
    required: true
    constraints:
      max_length: 250
    description: |
      User group name. Cannot duplicate existing or system user group names
      (e.g. Space administrators, Space members). No special characters such as "/".
      Max 250 characters.
  users:
    type: array
    items: string
    required: true
    constraints:
      max_items: 100
    description: >
      List of user_keys for members. Max 100 per request.
      Only user members supported; department members cannot be added.

outputs:
  data:
    type: object
    properties:
      id: string
    description: ID of the newly created user group.

constraints:
  - Permission: Permission Management – Users
  - name: unique, no special chars (e.g. /), max 250 chars
  - users: max 100; only user members

error_mapping:
  1000053001: User group name exists (duplicate with existing or system name)
  1000053002: Name contains unsupported character (e.g. "/")
  1000053003: Name length not supported (exceeds 250)
  1000053004: User invalid (left company or does not exist)
  1000053005: Users limit 100 (more than 100 employees at a time)
  1000053006: Need user (no employees added)
  1000053007: Need name (name is empty)
```

### Usage notes

- **user_access_token only**: Use `X-Plugin-Token: {{user_access_token}}`; plugin token will not work.
- **name**: Must be unique; no "/" or other unsupported characters; max 250 characters.
- **users**: List of user_key; max 100; cannot add users who have left or do not exist.

---

## Update User Group Member

Update the members of a user group. Supports add, delete, or replace members. Works with space members (PROJECT_MEMBER) or custom user groups (CUSTOMIZE).

### Points to Note

**This API only supports user access credentials (user_access_token).** See Obtain Access Credentials for how to obtain user_access_token.

- When adding a user from non-space members, the user is automatically added to space members.
- When deleting a user from space members, the user is automatically removed from other user groups.

### When to Use

- When adding or removing members from a custom user group
- When replacing the full member list of a user group
- When updating space members (PROJECT_MEMBER) or custom groups (CUSTOMIZE)

### API Spec: update_user_group_member

```yaml
name: update_user_group_member
type: api
description: >
  Update the members of a user group. Supports add, delete, or replace members.
  Works with PROJECT_MEMBER or CUSTOMIZE user groups.

auth:
  type: user_access_token
  note: Only user_access_token is supported; plugin_access_token is NOT supported.

http:
  method: PATCH
  url: https://{domain}/open_api/{project_key}/user_group/members
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{user_access_token}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
      project_key: Double-click space name in Meegle.
      simple_name: From space URL, e.g. https://meegle.com/doc/overview → doc.

inputs:
  user_group_type:
    type: string
    required: true
    enum: [PROJECT_MEMBER, CUSTOMIZE]
    description: |
      PROJECT_MEMBER: Space members
      CUSTOMIZE: Custom user groups
  user_group_id:
    type: string
    required: false
    description: >
      User group ID. Required when user_group_type=CUSTOMIZE.
      Obtain from user group page URL, e.g. .../userGroup/756472096042365xxxx → 756472096042365xxxx.
  add_users:
    type: array
    items: string
    required: false
    constraints:
      max_items: 100
    description: >
      List of user_keys to add. Max 100. Cannot add left/non-existent employees.
      At least one of add_users, delete_users, replace_users must be non-empty.
  delete_users:
    type: array
    items: string
    required: false
    constraints:
      max_items: 100
    description: >
      List of user_keys to delete. Max 100.
      If same user_key exists in add_users and delete_users, it is ignored.
      At least one of add_users, delete_users, replace_users must be non-empty.
  replace_users:
    type: array
    items: string
    required: false
    constraints:
      max_items: 100
    description: >
      Completely overwrite existing members. Max 100.
      If non-empty, add_users and delete_users are ignored.
      At least one of add_users, delete_users, replace_users must be non-empty.

outputs:
  data:
    type: object
    description: Empty object on success.

constraints:
  - Permission: Permission Management – Users
  - At least one of add_users, delete_users, replace_users must be non-empty
  - user_group_id required when user_group_type=CUSTOMIZE
  - Max 100 users per field (add_users, delete_users, replace_users)

error_mapping:
  1000053004: User invalid (employee left or does not exist)
  1000053005: Users limit 100 (more than 100 employees at a time)
  1000053008: User group type not supported (check user_group_type)
  1000053009: Need user group ID (user_group_id required when CUSTOMIZE)
  1000053006: Need user (add_users, delete_users, replace_users all empty)
  1000053010: User group not found (no matching user group in the space)
```

### Usage notes

- **user_access_token only**: Use `X-Plugin-Token: {{user_access_token}}`; plugin token will not work.
- **user_group_id**: Required when `user_group_type=CUSTOMIZE`; from user group page URL.
- **replace_users** takes precedence: when non-empty, `add_users` and `delete_users` are ignored.
- If the same `user_key` appears in both `add_users` and `delete_users`, it is ignored.
