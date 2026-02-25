---
name: talent-de-platform
description: >-
  Create CVs, search jobs, match skills, and negotiate via Work Deal Language.
  Several templates, PDF export, human-in-the-loop review. Free API for AI agents —
  basic use without API key, full features with Access-ID. Router skill — see
  domain-specific skills below for detailed instructions.
homepage: https://www.talent.de
license: Free-to-use
compatibility: Requires HTTP client and network access.
env_vars:
  TALENT_ACCESS_ID:
    required: false
    sensitive: true
    description: >-
      Access-ID for higher rate limits and advanced features (Template Create,
      Job Negotiate, Template Contest). Also used as HMAC secret for callback
      signature verification. Optional for CV Builder and Job Search.
metadata:
  openclaw:
    emoji: "\U0001F3AF"
  talent:
    category: career
    version: "5.2.2"
    api_base: https://www.talent.de/api
    credentials:
      access_id:
        required: per-skill
        format: "talent_agent_[a-z0-9]{4}"
        obtain: "POST /api/agent/register"
        env_var: "TALENT_ACCESS_ID"
        sensitive: true
        note: >-
          Free skills (CV Builder, Job Search) work without Access-ID at lower rate limits.
          Template Create, Job Negotiate, and Template Contest require an Access-ID.
          Also used as HMAC secret for callback signature verification.
          Store in environment variable TALENT_ACCESS_ID — do not hardcode.
  hitl:
    supported: true
    spec_version: "0.6"
    types: [confirmation, input, selection, approval, escalation]
    notifications: [polling, sse, callback]
    review_base_url: "https://www.talent.de/en/hitl/review"
    timeout_default: "24h"
    grace_period: "5min"
    discovery: "https://www.talent.de/.well-known/hitl.json"
    info: "May ask user to confirm context, enter data, select template, approve CV draft, or handle escalations."
---

# talent.de Platform

Create CVs, search jobs, match skills, and negotiate work conditions — all via API. Templates from classic PDFs to 3D worlds. Free for basic use.

## Agent Guidelines

> **HITL (Human In The Loop) is required.** You MUST choose: `"prefer_hitl": true` (human review — recommended) or `"skip_hitl": true` (direct creation — automated pipelines only). Omitting both returns a 400 error. If a human is present, ALWAYS use `"prefer_hitl": true`.

> **Data principle:** Only use data the requestor has explicitly provided or approved in this conversation.

> **Before sending:** Present a brief summary — name, title, email — and ask "Send it? Or should I change anything?"

> **Claim token:** Treat like a password. Share only with the requestor.

> **Keep it friendly.** See [User Communication](skills/cv-builder/SKILL.md#user-communication) for suggested messages at each step.

## Credentials

An **Access-ID** (`talent_agent_[a-z0-9]{4}`) unlocks higher rate limits and advanced skills. It is **optional** for CV Builder and Job Search, **required** for Template Create, Job Negotiate, and Template Contest.

Register (free, no user data transmitted):
```http
POST https://www.talent.de/api/agent/register
Content-Type: application/json

{ "agent_name": "my-agent" }
```

The Access-ID is also used as the HMAC secret for verifying `X-HITL-Signature` on callback webhooks. Store it securely — do not embed in client-side code or share across agents. See [Access System](skills/shared/access.md) for full details.

## Quick Start

```http
POST https://www.talent.de/api/agent/cv-simple
Content-Type: application/json

{
  "prefer_hitl": true,
  "cv_data": {
    "firstName": "Alex",
    "lastName": "Johnson",
    "title": "Software Engineer",
    "email": "alex@example.com"
  }
}
```

Response (202 — human review required):
```json
{
  "status": "human_input_required",
  "message": "Please confirm: is this CV for you?",
  "hitl": {
    "case_id": "review_a7f3b2c8d9e1f0g4",
    "review_url": "https://www.talent.de/en/hitl/review/review_a7f3b2c8d9e1f0g4?token=abc123...",
    "poll_url": "https://www.talent.de/api/hitl/cases/review_a7f3b2c8d9e1f0g4/status",
    "type": "confirmation"
  }
}
```

Present the `review_url` to the user. They choose slug, template, and approve. Poll `poll_url` for completion, continue through steps. See [CV Builder skill](skills/cv-builder/SKILL.md) for full flow.

## Skills

| Skill | Use when | Key endpoint |
|-------|----------|--------------|
| [CV Builder](skills/cv-builder/SKILL.md) | User wants to create, build, or export a CV | `POST /api/agent/cv-simple` |
| [Job Search](skills/job-search/SKILL.md) | User wants to find jobs or match their CV | `GET /api/agent/jobs` |
| [Job Negotiate](skills/job-negotiate/SKILL.md) | User wants to negotiate conditions or apply conditionally (coming soon) | `POST /api/agent/wdl/request` |
| [Template Create](skills/template-create/SKILL.md) | User wants to build a custom HTML template (coming soon) | `POST /api/agent/template` |
| [Template Contest](skills/template-contest/SKILL.md) | User wants to join template battles or showcases (coming soon) | — |

## Cross-Cutting References

- [Access System](skills/shared/access.md): Rate limits and Access-ID registration
- [Error Codes](skills/shared/errors.md): Error reference and troubleshooting
- [Privacy](skills/shared/privacy.md): Data handling and GDPR compliance

## Specs

- [agent.json](https://www.talent.de/.well-known/agent.json)
- [hitl.json](https://www.talent.de/.well-known/hitl.json)
- [llms.txt](https://www.talent.de/llms.txt)
