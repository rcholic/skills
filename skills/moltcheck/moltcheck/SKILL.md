# MoltCheck Skill

Security scanner for Moltbot skills. Scans GitHub repositories for security risks before installation.

## Capabilities

- **Network Access** - Calls MoltCheck API

## Commands

### `scan <github_url>`
Scan a GitHub repository for security issues.

**Example:**
```
scan https://github.com/owner/repo
```

**Returns:** Trust score (0-100), grade (A-F), risks found, permission analysis.

### `credits`
Check your remaining scan credits.

### `setup`
Generate an API key and get payment instructions for credits.

## Configuration

Set your API key in the skill config:
```json
{
  "apiKey": "mc_your_api_key_here"
}
```

Or use the free tier (3 scans/day) without an API key.

## Pricing

- **Free tier:** 3 scans/day
- **Paid:** $0.20 per scan (pay in SOL)

Get credits at https://moltcheck.com/buy

## Links

- Website: https://moltcheck.com
- API Docs: https://moltcheck.com/api-docs.md
- OpenAPI: https://moltcheck.com/openapi.json
