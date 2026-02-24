---
title: Configure Hono Endpoint for Edge
impact: HIGH
impactDescription: Hono enables edge runtime deployment for lower latency
tags: endpoint, hono, edge, setup
---

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
