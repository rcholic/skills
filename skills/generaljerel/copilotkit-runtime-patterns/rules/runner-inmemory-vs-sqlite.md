---
title: InMemory for Dev, SQLite for Production
impact: HIGH
impactDescription: InMemory loses all state on restart; SQLite persists across deploys
tags: runner, InMemory, SQLite, persistence
---

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
