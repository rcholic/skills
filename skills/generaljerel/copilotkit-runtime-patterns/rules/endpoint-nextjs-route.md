---
title: Set Up Next.js API Route Handler
impact: CRITICAL
impactDescription: incorrect route handler config breaks streaming in Next.js
tags: endpoint, nextjs, api-route, streaming
---

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
