---
name: noya-agent
description: Interact with the Noya AI agent for crypto trading, prediction markets, token analysis, and DCA strategies. Use when the user wants to send messages to Noya, manage conversation threads, or query agent capabilities via the Noya API.
---

# Noya Agent

Noya is a multi-agent AI system for crypto trading, prediction markets (Polymarket, Rain), token analysis, and DCA strategies. This skill enables programmatic interaction with Noya through its REST API.

## Prerequisites

1. Create an account at [agent.noya.ai](https://agent.noya.ai)
2. Generate an API key from the API Keys page (Settings > API Keys)
3. Store the key securely — it is only shown once at creation time

## Authentication

All requests require the `x-api-key` header:

```
x-api-key: noya_<your-key>
```

Base URL: `https://safenet.one`

## Quick Start

### Send a message to Noya

```bash
curl -N https://safenet.one/api/messages/stream \
  -H "Content-Type: application/json" \
  -H "x-api-key: noya_YOUR_KEY" \
  -d '{"message": "What is the current price of ETH?", "threadId": "my-thread-1"}'
```

The response is a chunked text stream. Each chunk is a JSON object separated by `--breakpoint--`.

### List conversation threads

```bash
curl https://safenet.one/api/threads \
  -H "x-api-key: noya_YOUR_KEY"
```

### Get agent capabilities

```bash
curl https://safenet.one/api/agents/summarize \
  -H "x-api-key: noya_YOUR_KEY"
```

## Endpoints

### POST /api/messages/stream

Send a message and receive a streamed response from the Noya agent graph.

**Request body:**

| Field    | Type   | Required | Description               |
|----------|--------|----------|---------------------------|
| message  | string | Yes      | The user message           |
| threadId | string | Yes      | Conversation thread ID     |

**Response:** Chunked text stream. Each chunk is JSON delimited by `--breakpoint--\n`.

**Chunk types:**

| Type                 | Description                                  |
|----------------------|----------------------------------------------|
| `message`            | Agent text response fragment                 |
| `tool`               | Tool call result with artifacts              |
| `progress`           | Progress update (current/total/message)      |
| `interrupt`          | Agent asking for user confirmation            |
| `reasonForExecution` | Agent explaining why it is taking an action  |
| `executionSteps`     | Step-by-step execution plan                  |
| `error`              | Error message                                |

**Parsing example (JavaScript):**

```javascript
const response = await fetch("https://safenet.one/api/messages/stream", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "x-api-key": "noya_YOUR_KEY",
  },
  body: JSON.stringify({ message: "Analyze SOL", threadId: "t1" }),
});

const reader = response.body.getReader();
const decoder = new TextDecoder();
let buffer = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  buffer += decoder.decode(value, { stream: true });
  const parts = buffer.split("--breakpoint--\n");
  buffer = parts.pop();
  for (const part of parts) {
    const trimmed = part.trim();
    if (!trimmed || trimmed === "keep-alive") continue;
    const chunk = JSON.parse(trimmed);
    if (chunk.type === "message") {
      process.stdout.write(chunk.message);
    }
  }
}
```

### GET /api/threads

List all conversation threads for the authenticated user.

**Response:**

```json
{
  "success": true,
  "data": { "threads": [{ "id": "...", "name": "...", "created_at": "..." }] }
}
```

### GET /api/threads/:threadId/messages

Get all messages from a specific thread.

**Response:**

```json
{
  "success": true,
  "data": { "messages": [...] }
}
```

### DELETE /api/threads/:threadId

Delete a conversation thread.

### POST /api/chat/completions

OpenAI-compatible chat completion endpoint. Maintains session history in Redis.

**Request body:**

| Field       | Type   | Required | Description                          |
|-------------|--------|----------|--------------------------------------|
| sessionId   | string | Yes      | Session identifier                   |
| message     | string | Yes      | User message                         |
| config      | object | No       | Model configuration                  |
| tools       | array  | No       | Tool definitions                     |
| toolResults | array  | No       | Results from previous tool calls     |

### GET /api/agents/summarize

Returns all available agent types with their specialties and tools.

## Additional Resources

- For the complete API specification with request/response schemas, see [reference.md](reference.md)
- MCP server available: `npx noya-agent-mcp` (configure with `NOYA_API_KEY` env var)
