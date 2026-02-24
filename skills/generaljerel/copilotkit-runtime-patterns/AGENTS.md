# CopilotKit Runtime Patterns

**Version 1.0.0**  
CopilotKit  
February 2026

> **Note:**  
> This document is mainly for agents and LLMs to follow when maintaining,  
> generating, or refactoring CopilotKit codebases. Humans  
> may also find it useful, but guidance here is optimized for automation  
> and consistency by AI-assisted workflows.

---

## Abstract

Server-side runtime configuration patterns for CopilotKit. Contains 15 rules covering Express/Hono endpoint setup, agent runner selection (InMemory vs SQLite), middleware hooks, security configuration, and performance optimization.

---

## Table of Contents

1. [Endpoint Setup](#1-endpoint-setup) — **CRITICAL**
   - 1.1 [Configure Express Endpoint with CORS](#1.1-configure-express-endpoint-with-cors)
   - 1.2 [Configure Hono Endpoint for Edge](#1.2-configure-hono-endpoint-for-edge)
   - 1.3 [Set Up Next.js API Route Handler](#1.3-set-up-next-js-api-route-handler)
2. [Agent Runners](#2-agent-runners) — **HIGH**
   - 2.1 [Configure Multi-Agent Routing](#2.1-configure-multi-agent-routing)
   - 2.2 [InMemory for Dev, SQLite for Production](#2.2-inmemory-for-dev-sqlite-for-production)
   - 2.3 [Register Agents with Descriptive Metadata](#2.3-register-agents-with-descriptive-metadata)
3. [Middleware](#3-middleware) — **MEDIUM**
   - 3.1 [Handle Middleware Errors Gracefully](#3.1-handle-middleware-errors-gracefully)
   - 3.2 [Use afterRequest for Response Modification](#3.2-use-afterrequest-for-response-modification)
   - 3.3 [Use beforeRequest for Auth and Logging](#3.3-use-beforerequest-for-auth-and-logging)
4. [Security](#4-security) — **HIGH**
   - 4.1 [Authenticate Before Agent Execution](#4.1-authenticate-before-agent-execution)
   - 4.2 [Configure CORS for Specific Origins](#4.2-configure-cors-for-specific-origins)
   - 4.3 [Rate Limit by User or API Key](#4.3-rate-limit-by-user-or-api-key)
5. [Performance](#5-performance) — **MEDIUM**
   - 5.1 [Prevent Proxy Buffering of Streams](#5.1-prevent-proxy-buffering-of-streams)

---

## 1. Endpoint Setup

**Impact: CRITICAL**

Correct endpoint configuration is required for CopilotKit to function. Misconfigured endpoints cause connection failures or broken streaming.

### 1.1 Configure Express Endpoint with CORS

**Impact: CRITICAL (missing CORS or wrong path blocks all frontend connections)**

## Configure Express Endpoint with CORS

When using Express, mount the CopilotKit runtime at a specific path and configure CORS to allow your frontend origin. Missing CORS headers cause the browser to block all requests from your React app.

**Incorrect (no CORS, wrong path mounting):**

```typescript
import express from "express"
import { CopilotKitRuntime } from "@copilotkit/runtime"

const app = express()
const runtime = new CopilotKitRuntime({ agents: [myAgent] })

app.use(runtime.handler())
app.listen(3001)
```

**Correct (CORS configured, specific path):**

```typescript
import express from "express"
import cors from "cors"
import { CopilotKitRuntime } from "@copilotkit/runtime"

const app = express()
app.use(cors({ origin: process.env.FRONTEND_URL || "http://localhost:3000" }))

const runtime = new CopilotKitRuntime({ agents: [myAgent] })
app.use("/api/copilotkit", runtime.expressHandler())

app.listen(3001)
```

Reference: [Express Setup](https://docs.copilotkit.ai/guides/self-hosting/express)

### 1.2 Configure Hono Endpoint for Edge

**Impact: HIGH (Hono enables edge runtime deployment for lower latency)**

## Configure Hono Endpoint for Edge

Use Hono for edge runtime deployments (Cloudflare Workers, Vercel Edge). Hono's lightweight design and Web Standard APIs make it ideal for edge CopilotKit runtimes.

**Incorrect (Express patterns in edge runtime):**

```typescript
import { Hono } from "hono"
import { CopilotKitRuntime } from "@copilotkit/runtime"

const app = new Hono()
const runtime = new CopilotKitRuntime({ agents: [myAgent] })

app.all("/api/copilotkit", (c) => {
  return runtime.handler()(c.req.raw)
})
```

**Correct (Hono-native handler with CORS):**

```typescript
import { Hono } from "hono"
import { cors } from "hono/cors"
import { CopilotKitRuntime } from "@copilotkit/runtime"

const app = new Hono()
app.use("/api/copilotkit/*", cors({ origin: process.env.FRONTEND_URL }))

const runtime = new CopilotKitRuntime({ agents: [myAgent] })
app.all("/api/copilotkit", runtime.honoHandler())

export default app
```

Reference: [Hono Setup](https://docs.copilotkit.ai/guides/self-hosting/hono)

### 1.3 Set Up Next.js API Route Handler

**Impact: CRITICAL (incorrect route handler config breaks streaming in Next.js)**

## Set Up Next.js API Route Handler

For Next.js, create a catch-all API route at `app/api/copilotkit/[...copilotkit]/route.ts`. Export both GET and POST handlers. Ensure the route segment config allows streaming responses.

**Incorrect (single method, no streaming config):**

```typescript
// app/api/copilotkit/route.ts
import { CopilotKitRuntime } from "@copilotkit/runtime"

const runtime = new CopilotKitRuntime({ agents: [myAgent] })

export async function POST(req: Request) {
  return runtime.handler(req)
}
```

**Correct (catch-all route with streaming):**

```typescript
// app/api/copilotkit/[...copilotkit]/route.ts
import { CopilotKitRuntime } from "@copilotkit/runtime"

export const runtime = "edge" // or "nodejs"
export const maxDuration = 60

const copilotkit = new CopilotKitRuntime({ agents: [myAgent] })

export const GET = copilotkit.nextJsHandler()
export const POST = copilotkit.nextJsHandler()
```

Reference: [Next.js Setup](https://docs.copilotkit.ai/guides/self-hosting/nextjs)

## 2. Agent Runners

**Impact: HIGH**

Agent runners manage agent lifecycle and state persistence. Choosing the wrong runner causes data loss or memory leaks.

### 2.1 Configure Multi-Agent Routing

**Impact: HIGH (ambiguous routing sends requests to wrong agents)**

## Configure Multi-Agent Routing

When registering multiple agents, ensure each has a unique `name` that matches the `agentId` used in the frontend. The runtime routes requests based on this name. Duplicate names cause unpredictable routing.

**Incorrect (duplicate names, ambiguous routing):**

```typescript
const runtime = new CopilotKitRuntime({
  agents: [
    new BuiltInAgent({ name: "agent", tools: [searchTool] }),
    new BuiltInAgent({ name: "agent", tools: [writeTool] }),
  ],
})
```

**Correct (unique names matching frontend agentId):**

```typescript
const runtime = new CopilotKitRuntime({
  agents: [
    new BuiltInAgent({ name: "researcher", tools: [searchTool] }),
    new BuiltInAgent({ name: "writer", tools: [writeTool] }),
  ],
})

// Frontend:
// useAgent({ agentId: "researcher" })
// useAgent({ agentId: "writer" })
```

Reference: [Multi-Agent Setup](https://docs.copilotkit.ai/guides/multi-agent)

### 2.2 InMemory for Dev, SQLite for Production

**Impact: HIGH (InMemory loses all state on restart; SQLite persists across deploys)**

## InMemory for Dev, SQLite for Production

Use `InMemoryRunner` for development (fast, no setup) and `SQLiteRunner` for production (persistent state across restarts). InMemory loses all conversation state when the server restarts, which is unacceptable in production.

**Incorrect (InMemory in production, state lost on deploy):**

```typescript
import { CopilotKitRuntime, InMemoryRunner } from "@copilotkit/runtime"

const runtime = new CopilotKitRuntime({
  agents: [myAgent],
  runner: new InMemoryRunner(),
})
// Every deployment wipes all conversation history
```

**Correct (environment-based runner selection):**

```typescript
import { CopilotKitRuntime, InMemoryRunner, SQLiteRunner } from "@copilotkit/runtime"

const runner = process.env.NODE_ENV === "production"
  ? new SQLiteRunner({ dbPath: process.env.DB_PATH || "./copilotkit.db" })
  : new InMemoryRunner()

const runtime = new CopilotKitRuntime({
  agents: [myAgent],
  runner,
})
```

Reference: [Runtime Configuration](https://docs.copilotkit.ai/reference/runtime/runners)

### 2.3 Register Agents with Descriptive Metadata

**Impact: MEDIUM (missing metadata prevents proper agent routing and debugging)**

## Register Agents with Descriptive Metadata

When registering agents with the runtime, provide descriptive `name` and `description` fields. The name is used for routing (matching `agentId` from the frontend), and the description helps with debugging and multi-agent orchestration.

**Incorrect (no name or description):**

```typescript
const runtime = new CopilotKitRuntime({
  agents: [new BuiltInAgent({ tools: [searchTool] })],
})
```

**Correct (descriptive metadata for routing and debugging):**

```typescript
const runtime = new CopilotKitRuntime({
  agents: [
    new BuiltInAgent({
      name: "researcher",
      description: "Searches and synthesizes information from multiple sources",
      tools: [searchTool, summarizeTool],
    }),
  ],
})
```

Reference: [Agent Registration](https://docs.copilotkit.ai/reference/runtime/agents)

## 3. Middleware

**Impact: MEDIUM**

Middleware hooks for request/response processing. Used for auth, logging, context injection, and response modification.

### 3.1 Handle Middleware Errors Gracefully

**Impact: MEDIUM (unhandled middleware errors crash the runtime for all users)**

## Handle Middleware Errors Gracefully

Wrap middleware logic in try/catch to prevent individual request failures from crashing the entire runtime. Return appropriate HTTP error responses instead of letting exceptions propagate.

**Incorrect (unhandled error crashes runtime):**

```typescript
const runtime = new CopilotKitRuntime({
  middleware: {
    beforeRequest: async (req) => {
      const user = await fetchUser(req.headers.get("x-user-id"))
      req.context = { user: user.data }
      return req
    },
  },
})
```

**Correct (graceful error handling):**

```typescript
const runtime = new CopilotKitRuntime({
  middleware: {
    beforeRequest: async (req) => {
      try {
        const user = await fetchUser(req.headers.get("x-user-id"))
        req.context = { user: user.data }
      } catch (error) {
        console.error("Middleware error:", error)
        throw new Response("Internal Server Error", { status: 500 })
      }
      return req
    },
  },
})
```

Reference: [Middleware](https://docs.copilotkit.ai/reference/runtime/middleware)

### 3.2 Use afterRequest for Response Modification

**Impact: LOW (enables response logging and cleanup without modifying agents)**

## Use afterRequest for Response Modification

Use the `afterRequest` middleware hook for logging completed requests, tracking usage metrics, or cleaning up resources. This runs after the agent response stream has completed.

**Incorrect (logging inside agent, couples concerns):**

```typescript
class ResearchAgent {
  async run(input: RunInput) {
    const start = Date.now()
    // ... agent logic
    console.log(`Agent took ${Date.now() - start}ms`)
    await cleanupTempFiles()
  }
}
```

**Correct (afterRequest for logging and cleanup):**

```typescript
const runtime = new CopilotKitRuntime({
  agents: [researchAgent],
  middleware: {
    afterRequest: async (req, res) => {
      await logUsage({
        agentId: req.agentId,
        userId: req.context?.userId,
        duration: res.duration,
        tokenCount: res.tokenCount,
      })
      await cleanupTempFiles(req.threadId)
    },
  },
})
```

Reference: [Middleware](https://docs.copilotkit.ai/reference/runtime/middleware)

### 3.3 Use beforeRequest for Auth and Logging

**Impact: MEDIUM (centralizes cross-cutting concerns before agent execution)**

## Use beforeRequest for Auth and Logging

Use the `beforeRequest` middleware hook to handle authentication, logging, and context injection before the agent processes a request. This centralizes cross-cutting concerns and keeps agent code focused on business logic.

**Incorrect (auth logic inside each agent):**

```typescript
class ResearchAgent {
  async run(input: RunInput) {
    const token = input.headers?.authorization
    if (!verifyToken(token)) throw new Error("Unauthorized")
    // ... agent logic
  }
}
```

**Correct (auth in beforeRequest middleware):**

```typescript
const runtime = new CopilotKitRuntime({
  agents: [researchAgent, writerAgent],
  middleware: {
    beforeRequest: async (req) => {
      const token = req.headers.get("authorization")?.replace("Bearer ", "")
      if (!token || !await verifyToken(token)) {
        throw new Response("Unauthorized", { status: 401 })
      }
      req.context = { userId: decodeToken(token).sub }
      return req
    },
  },
})
```

Reference: [Middleware](https://docs.copilotkit.ai/reference/runtime/middleware)

## 4. Security

**Impact: HIGH**

Security patterns for production CopilotKit deployments. Unprotected endpoints expose your LLM and agent capabilities to abuse.

### 4.1 Authenticate Before Agent Execution

**Impact: CRITICAL (unauthenticated endpoints expose LLM capabilities to anyone)**

## Authenticate Before Agent Execution

Always authenticate requests before they reach the agent. An unauthenticated CopilotKit endpoint lets anyone invoke your agents and consume your LLM tokens. Use the `beforeRequest` middleware to validate tokens.

**Incorrect (no auth, open to public):**

```typescript
const runtime = new CopilotKitRuntime({
  agents: [myAgent],
})

app.use("/api/copilotkit", runtime.expressHandler())
```

**Correct (JWT auth before agent execution):**

```typescript
const runtime = new CopilotKitRuntime({
  agents: [myAgent],
  middleware: {
    beforeRequest: async (req) => {
      const token = req.headers.get("authorization")?.replace("Bearer ", "")
      if (!token) throw new Response("Missing token", { status: 401 })

      const payload = await verifyJwt(token)
      if (!payload) throw new Response("Invalid token", { status: 403 })

      req.context = { userId: payload.sub, role: payload.role }
      return req
    },
  },
})
```

Reference: [Security](https://docs.copilotkit.ai/guides/security)

### 4.2 Configure CORS for Specific Origins

**Impact: HIGH (wildcard CORS exposes your LLM endpoint to any website)**

## Configure CORS for Specific Origins

Never use wildcard (`*`) CORS in production. Specify the exact frontend origin(s) that should be allowed to access your CopilotKit runtime. Wildcard CORS lets any website send requests to your endpoint, potentially abusing your LLM quota.

**Incorrect (wildcard CORS, open to abuse):**

```typescript
app.use(cors({ origin: "*" }))
```

**Correct (specific origin in production):**

```typescript
const allowedOrigins = process.env.NODE_ENV === "production"
  ? [process.env.FRONTEND_URL!]
  : ["http://localhost:3000", "http://localhost:5173"]

app.use(cors({ origin: allowedOrigins }))
```

Reference: [Security](https://docs.copilotkit.ai/guides/security)

### 4.3 Rate Limit by User or API Key

**Impact: HIGH (unbounded access lets single users exhaust LLM budget)**

## Rate Limit by User or API Key

Add rate limiting to your CopilotKit runtime endpoint to prevent individual users from exhausting your LLM budget. Rate limit by authenticated user ID or API key, not just IP address (which doesn't work behind proxies/VPNs).

**Incorrect (no rate limiting):**

```typescript
app.use("/api/copilotkit", runtime.expressHandler())
```

**Correct (rate limiting by user ID):**

```typescript
import { RateLimiter } from "rate-limiter-flexible"

const limiter = new RateLimiter({
  points: 50,
  duration: 60,
  keyPrefix: "copilotkit",
})

const runtime = new CopilotKitRuntime({
  agents: [myAgent],
  middleware: {
    beforeRequest: async (req) => {
      const userId = req.context?.userId
      if (!userId) throw new Response("Unauthorized", { status: 401 })

      try {
        await limiter.consume(userId)
      } catch {
        throw new Response("Rate limit exceeded", { status: 429 })
      }
      return req
    },
  },
})
```

Reference: [Security](https://docs.copilotkit.ai/guides/security)

## 5. Performance

**Impact: MEDIUM**

Optimization patterns for runtime performance, streaming, and resource management.

### 5.1 Prevent Proxy Buffering of Streams

**Impact: MEDIUM (buffered streams cause long delays before first token appears)**

## Prevent Proxy Buffering of Streams

CopilotKit uses Server-Sent Events (SSE) for streaming. Reverse proxies (Nginx, Cloudflare) may buffer the response, causing long delays before the first token reaches the client. Set headers to disable buffering.

**Incorrect (no streaming headers, proxy buffers response):**

```typescript
app.use("/api/copilotkit", runtime.expressHandler())
```

**Correct (disable proxy buffering for streaming):**

```typescript
app.use("/api/copilotkit", (req, res, next) => {
  res.setHeader("X-Accel-Buffering", "no")
  res.setHeader("Cache-Control", "no-cache, no-transform")
  res.setHeader("Content-Type", "text/event-stream")
  next()
}, runtime.expressHandler())
```

For Nginx, also add to your server config:
```
proxy_buffering off;
```

Reference: [Deployment](https://docs.copilotkit.ai/guides/self-hosting)

---

## References

- https://docs.copilotkit.ai
- https://github.com/CopilotKit/CopilotKit
- https://docs.copilotkit.ai/reference/runtime
