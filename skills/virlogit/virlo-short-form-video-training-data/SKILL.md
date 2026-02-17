---
name: virlo
description: Virlo social media intelligence — viral video analytics, hashtag rankings, trend digests, and social listening across YouTube, TikTok, and Instagram. Use for content strategy, trend discovery, competitive analysis, and niche monitoring.
license: MIT
metadata:
  {
    "openclaw":
      {
        "emoji": "☄️",
        "requires": { "bins": ["curl"], "env": ["VIRLO_API_KEY"] },
        "primaryEnv": "VIRLO_API_KEY",
      },
  }
---

# Virlo

Social media intelligence for short-form video — Bloomberg for viral content.

## Config

Set `VIRLO_API_KEY` environment variable. Your API key has the format `virlo_tkn_<your_key>` and can be obtained from the [Virlo dashboard](https://dev.virlo.ai/dashboard).

## Context

The Virlo API provides cross-platform analytics across YouTube, TikTok, and Instagram. Key capabilities:

- **Hashtags** — 500K+ hashtags ranked by usage count and total views
- **Trends** — Daily curated trending topics updated at 1am UTC
- **Videos** — 2M+ viral video performance data (views, likes, shares, comments)
- **Orbit** — Keyword-based social listening with async analysis jobs
- **Comet** — Automated niche monitoring with scheduled scraping

All endpoints use the `/v1` prefix, `snake_case` naming, and return data in a `{ "data": ... }` envelope.

## API Access

```bash
# GET request
{baseDir}/scripts/virlo-api.sh GET <endpoint>

# POST request with JSON body
{baseDir}/scripts/virlo-api.sh POST <endpoint> '<json-body>'
```

Examples:
- `{baseDir}/scripts/virlo-api.sh GET /v1/hashtags` — list top hashtags
- `{baseDir}/scripts/virlo-api.sh GET "/v1/videos?limit=10"` — top viral videos
- `{baseDir}/scripts/virlo-api.sh GET /v1/trends` — daily trend digest
- `{baseDir}/scripts/virlo-api.sh POST /v1/orbit '{"name":"AI research","keywords":["artificial intelligence","AI tools"]}'`

## Local API Reference

Start with `{baseDir}/references/api-overview.md` for auth, pagination, and common patterns. Then load the domain file you need:

| Domain          | File                            | Covers                                                                       |
| --------------- | ------------------------------- | ---------------------------------------------------------------------------- |
| API Overview    | `references/api-overview.md`    | Authentication, pagination, base URL, response envelope                      |
| Hashtags        | `references/hashtags.md`        | Hashtag rankings by count and views, filtering                               |
| Trends          | `references/trends.md`          | Daily trend digest, trend groups, rankings                                   |
| Videos          | `references/videos.md`          | Top videos cross-platform, platform-specific endpoints, filtering & sorting  |
| Orbit           | `references/orbits.md`          | Keyword search jobs, async polling, videos, ads, creator outliers, analysis  |
| Comet           | `references/comets.md`          | Automated niche configs, scheduling, CRUD, videos, ads, creator outliers     |
| Rate Limits     | `references/rate-limits.md`     | Rate limiting policies and headers                                           |
| Error Handling  | `references/error-handling.md`  | HTTP status codes, error response format                                     |

Only load the reference file relevant to the current task — don't load them all.

## Remote Documentation

Full API documentation is available at https://dev.virlo.ai/docs with an interactive playground at https://dev.virlo.ai/docs/playground.
