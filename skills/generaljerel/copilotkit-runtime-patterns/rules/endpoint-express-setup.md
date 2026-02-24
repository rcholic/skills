---
title: Configure Express Endpoint with CORS
impact: CRITICAL
impactDescription: missing CORS or wrong path blocks all frontend connections
tags: endpoint, express, CORS, setup
---

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
