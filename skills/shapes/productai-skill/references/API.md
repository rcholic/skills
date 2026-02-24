# ProductAI API Documentation

Complete reference for the ProductAI.photo API endpoints.

## Base URL

```
https://api.productai.photo/v1
```

All API requests should be made to this base URL with the appropriate endpoint path.

## Authentication

Include your API key in the `x-api-key` header for all requests:

```bash
curl -X POST https://api.productai.photo/v1/api/generate \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "kontext-pro", "image_url": "https://example.com/product.jpg", "prompt": "Add sunglasses"}'
```

**Getting Your API Key:**

1. Go to [ProductAI Studio](https://www.productai.photo)
2. Navigate to **API Access** section
3. Click **Generate API Key** or copy existing key
4. Store securely in your configuration

## Rate Limits

- **Rate Limit:** 15 requests per minute
- **Daily Limit:** Based on your subscription plan
- **Credit System:** Each operation deducts tokens from your account balance

## Endpoints

### POST `/api/generate`

Generate AI-powered product images using the ProductAI engine.

**Request Body:**

```json
{
  "model": "kontext-pro",
  "image_url": "https://example.com/product.jpg",
  "prompt": "Add sunglasses"
}
```

**Parameters:**

- **`model`** (required) — Model to use for generation:
  - `gpt-low` — GPT Low Quality Generation (2 tokens)
  - `gpt-medium` — GPT Medium Quality Generation (3 tokens)
  - `gpt-high` — GPT High Quality Generation (8 tokens)
  - `kontext-pro` — Kontext Pro (3 tokens)
  - `nanobanana` — Nano Banana (3 tokens)
  - `nanobananapro` — Nano Banana Pro (8 tokens)
  - `seedream` — Seedream (3 tokens)

- **`image_url`** (required) — URL of the source image to process
  - Can be a single URL string OR array of URLs
  - **`seedream`, `nanobananapro`, and `nanobanana` models support up to 2 reference images (use array format!)**
  - Each image must be below 10MB in PNG, JPG, or WebP format

- **`prompt`** (required) — Text description of desired output

**Success Response:**

```json
{
  "status": "OK",
  "data": {
    "id": 22292,
    "status": "RUNNING",
    "prompt": "lipstick should be on fire"
  }
}
```

**Running Job Response:**

```json
{
  "status": "OK",
  "data": {
    "id": 22292,
    "status": "RUNNING",
    "prompt": "lipstick should be on fire"
  }
}
```

**Completed Job Response:**

```json
{
  "status": "OK",
  "data": {
    "id": 22292,
    "status": "COMPLETED",
    "prompt": "lipstick should be on fire",
    "image_url": "https://generated-image-url.jpg"
  }
}
```

**Status Values:**
- `"RUNNING"` — Job is currently being processed
- `"COMPLETED"` — Job completed successfully, image_url available
- `"ERROR"` — Job failed to complete

**Error Response (Out of Credits):**

```json
{
  "name": "ApiError",
  "message": "OUT_OF_TOKENS",
  "details": "Not enough credits"
}
```

---

### POST `/api/upscale`

Upscale an image using professional AI upscaling technology without changing image details.

**Request Body:**

```json
{
  "image_url": "https://example.com/image.jpg"
}
```

**Parameters:**

- **`image_url`** (required) — URL of the image to upscale
  - Image must be below 10MB in PNG, JPG, or WebP format

**Token Cost:** 20 tokens (Magnific Precision Upscale)

**Success Response:**

```json
{
  "status": "OK",
  "data": {
    "id": 22293,
    "status": "RUNNING"
  }
}
```

**Completed Response:**

```json
{
  "status": "OK",
  "data": {
    "id": 22293,
    "status": "COMPLETED",
    "image_url": "https://upscaled-image-url.jpg"
  }
}
```

**Error Response:**

```json
{
  "name": "ApiError",
  "message": "OUT_OF_TOKENS",
  "details": "Not enough credits"
}
```

---

### GET `/api/job/:job_id`

Check the status of a specific generation job using the job ID returned from `/api/generate` or `/api/upscale`.

**URL Parameters:**

- **`job_id`** (required) — The job ID returned from generate/upscale request

**Example Request:**

```bash
curl -X GET https://api.productai.photo/v1/api/job/22292 \
  -H "x-api-key: YOUR_API_KEY"
```

**Success Response (Completed):**

```json
{
  "status": "OK",
  "data": {
    "id": 22292,
    "status": "COMPLETED",
    "prompt": "lipstick should be on fire",
    "image_url": "https://generated-image-url.jpg"
  }
}
```

**Running Job Response:**

```json
{
  "status": "OK",
  "data": {
    "id": 22292,
    "status": "RUNNING",
    "prompt": "lipstick should be on fire"
  }
}
```

**Error Response:**

```json
{
  "status": "OK",
  "data": {
    "id": 22292,
    "status": "ERROR"
  }
}
```

---

## Webhooks

For each image generation request, a result will be sent to your configured webhook URL.

**Configure Webhook:**

Set your webhook URL in the **API Access** page in the ProductAI Studio.

**Webhook Payload (Success):**

```json
{
  "status": "success",
  "image_url": "https://generated-image-url.jpg",
  "job_id": "12312"
}
```

**Webhook Payload (Error):**

```json
{
  "status": "error"
}
```

**Webhook Requirements:**

- Your endpoint must respond with HTTP 200 status
- Configure your webhook URL in the API Access page
- Webhook calls are sent when jobs complete (success or error)

---

## Token Pricing

| Operation | Token Cost |
|-----------|------------|
| GPT Low Quality Generation | 2 tokens |
| GPT Medium Quality Generation | 3 tokens |
| GPT High Quality Generation | 8 tokens |
| Kontext Pro | 3 tokens |
| Nano Banana Pro | 8 tokens |
| Nano Banana | 3 tokens |
| Seedream | 3 tokens |
| Magnific Precision Upscale | 20 tokens |

**Note:** Tokens are deducted from your account balance when each operation starts.

---

## Common Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Invalid API key |
| 500 | Internal Server Error | Server-side error |
| — | OUT_OF_TOKENS | Not enough credits |

---

## Usage Examples

### Generate Product Photo with Multiple Reference Images

```bash
curl -X POST https://api.productai.photo/v1/api/generate \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nanobanana",
    "image_url": [
      "https://example.com/product1.jpg",
      "https://example.com/product2.jpg"
    ],
    "prompt": "Put the first image on top of the second image."
  }'
```

### Poll Job Status Until Complete

```bash
#!/bin/bash
API_KEY="YOUR_API_KEY"
JOB_ID="22292"

while true; do
  RESPONSE=$(curl -s -X GET \
    "https://api.productai.photo/v1/api/job/$JOB_ID" \
    -H "x-api-key: $API_KEY")
  
  STATUS=$(echo "$RESPONSE" | jq -r '.data.status')
  
  if [ "$STATUS" == "COMPLETED" ]; then
    IMAGE_URL=$(echo "$RESPONSE" | jq -r '.data.image_url')
    echo "Done! Image URL: $IMAGE_URL"
    break
  elif [ "$STATUS" == "ERROR" ]; then
    echo "Job failed"
    break
  else
    echo "Still running... ($STATUS)"
    sleep 5
  fi
done
```

### Upscale an Image

```bash
curl -X POST https://api.productai.photo/v1/api/upscale \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg"
  }'
```

---

## Best Practices

1. **Poll Responsibly:** Wait at least 3-5 seconds between job status checks
2. **Handle Rate Limits:** Implement exponential backoff for 429 responses
3. **Use Webhooks:** For production, configure webhooks instead of polling
4. **Validate Images:** Ensure images are under 10MB and in supported formats
5. **Monitor Credits:** Check account balance regularly to avoid OUT_OF_TOKENS errors
6. **Secure API Keys:** Never commit API keys to version control

---

## Support

- **Website:** https://www.productai.photo
- **API Issues:** Contact support via the dashboard
- **Rate Limit Increases:** Available for Pro plan users
