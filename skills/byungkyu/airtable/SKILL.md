---
name: airtable
description: |
  Airtable API integration with managed OAuth. Manage bases, tables, and records. Use this skill when users want to read, create, update, or delete Airtable records, or query data with filter formulas.
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
---

# Airtable

Access the Airtable API with managed OAuth authentication. Manage bases, tables, and records with full CRUD operations.

## Quick Start

```bash
# List records from a table
curl -s -X GET 'https://gateway.maton.ai/airtable/v0/{baseId}/{tableIdOrName}?maxRecords=100' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

## Base URL

```
https://gateway.maton.ai/airtable/{native-api-path}
```

Replace `{native-api-path}` with the actual Airtable API endpoint path. The gateway proxies requests to `api.airtable.com` and automatically injects your OAuth token.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your Airtable OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
curl -s -X GET 'https://ctrl.maton.ai/connections?app=airtable&status=ACTIVE' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

### Create Connection

```bash
curl -s -X POST 'https://ctrl.maton.ai/connections' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -d '{"app": "airtable"}'
```

### Get Connection

```bash
curl -s -X GET 'https://ctrl.maton.ai/connections/{connection_id}' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

**Response:**
```json
{
  "connection": {
    "connection_id": "21fd90f9-5935-43cd-b6c8-bde9d915ca80",
    "status": "ACTIVE",
    "creation_time": "2025-12-08T07:20:53.488460Z",
    "last_updated_time": "2026-01-31T20:03:32.593153Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "airtable",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
curl -s -X DELETE 'https://ctrl.maton.ai/connections/{connection_id}' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

### Specifying Connection

If you have multiple Airtable connections, specify which one to use with the `Maton-Connection` header:

```bash
curl -s -X GET 'https://gateway.maton.ai/airtable/v0/appXXXXX/TableName' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Maton-Connection: 21fd90f9-5935-43cd-b6c8-bde9d915ca80'
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### List Bases

```bash
GET /airtable/v0/meta/bases
```

### Get Base Schema

```bash
GET /airtable/v0/meta/bases/{baseId}/tables
```

### List Records

```bash
GET /airtable/v0/{baseId}/{tableIdOrName}?maxRecords=100
```

With view:

```bash
GET /airtable/v0/{baseId}/{tableIdOrName}?view=Grid%20view&maxRecords=100
```

With filter formula:

```bash
GET /airtable/v0/{baseId}/{tableIdOrName}?filterByFormula={Status}='Active'
```

With field selection:

```bash
GET /airtable/v0/{baseId}/{tableIdOrName}?fields[]=Name&fields[]=Status&fields[]=Email
```

With sorting:

```bash
GET /airtable/v0/{baseId}/{tableIdOrName}?sort[0][field]=Created&sort[0][direction]=desc
```

### Get Record

```bash
GET /airtable/v0/{baseId}/{tableIdOrName}/{recordId}
```

### Create Records

```bash
POST /airtable/v0/{baseId}/{tableIdOrName}
Content-Type: application/json

{
  "records": [
    {
      "fields": {
        "Name": "New Record",
        "Status": "Active",
        "Email": "test@example.com"
      }
    }
  ]
}
```

### Update Records (PATCH - partial update)

```bash
PATCH /airtable/v0/{baseId}/{tableIdOrName}
Content-Type: application/json

{
  "records": [
    {
      "id": "recXXXXXXXXXXXXXX",
      "fields": {
        "Status": "Completed"
      }
    }
  ]
}
```

### Update Records (PUT - full replace)

```bash
PUT /airtable/v0/{baseId}/{tableIdOrName}
Content-Type: application/json

{
  "records": [
    {
      "id": "recXXXXXXXXXXXXXX",
      "fields": {
        "Name": "Updated Name",
        "Status": "Active"
      }
    }
  ]
}
```

### Delete Records

```bash
DELETE /airtable/v0/{baseId}/{tableIdOrName}?records[]=recXXXXX&records[]=recYYYYY
```

## Pagination

Use `pageSize` and `offset` for pagination:

```bash
GET /airtable/v0/{baseId}/{tableIdOrName}?pageSize=50&offset=itrXXXXXXXXXXX
```

Response includes `offset` when more records exist:

```json
{
  "records": [...],
  "offset": "itrXXXXXXXXXXX"
}
```

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/airtable/v0/appXXXXX/TableName?maxRecords=10',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/airtable/v0/appXXXXX/TableName',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'maxRecords': 10}
)
```

## Notes

- Base IDs start with `app`
- Table IDs start with `tbl` (can also use table name)
- Record IDs start with `rec`
- Maximum 100 records per request for create/update
- Maximum 10 records per delete request
- Filter formulas use Airtable formula syntax

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Airtable connection |
| 401 | Invalid or missing Maton API key |
| 429 | Rate limited (10 req/sec per account) |
| 4xx/5xx | Passthrough error from Airtable API |

## Resources

- [Airtable API Overview](https://airtable.com/developers/web/api/introduction)
- [List Records](https://airtable.com/developers/web/api/list-records)
- [Create Records](https://airtable.com/developers/web/api/create-records)
- [Update Records](https://airtable.com/developers/web/api/update-record)
- [Delete Records](https://airtable.com/developers/web/api/delete-record)
- [Formula Reference](https://support.airtable.com/docs/formula-field-reference)
