---
title: Configure Multi-Agent Routing
impact: HIGH
impactDescription: ambiguous routing sends requests to wrong agents
tags: runner, multi-agent, routing, agentId
---

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
