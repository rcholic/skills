# Error Codes

All errors return a JSON body with `success: false` and a human-readable `error` message.

## Error Reference

| Code | HTTP | Meaning | What to do |
|------|------|---------|------------|
| `VALIDATION_ERROR` | 400 | Missing or invalid fields | Check the `details` array for specifics |
| `INVALID_SLUG` | 400 | Slug not in curated list | Use `GET /api/public/slugs` to see valid slugs |
| `INVALID_TEMPLATE` | 400 | Template ID not recognized | Use a valid built-in template ID or a valid `agent-*` custom template |
| `SLUG_UNAVAILABLE` | 409 | Slug + name combo already taken | Try a different slug |
| `RATE_LIMITED` | 429 | Daily limit reached | Wait until midnight UTC, or register for an Access-ID (50/day) |
| `INVALID_ACCESS_ID` | 401 | Access-ID not found or revoked | Check format: `talent_agent_[a-z0-9]{4}` (lowercase only) |

## Rate Limit Response

When rate-limited, the response includes:

```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "code": "RATE_LIMITED",
  "limit": 3,
  "used": 3,
  "resets_at": "2025-01-16T00:00:00Z"
}
```

## Using cv-simple

The `/api/agent/cv-simple` endpoint returns human-readable error messages and auto-fixes problems when possible. For example, if a slug is taken, it automatically picks the next available one instead of returning an error.
