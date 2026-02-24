---
title: Register Agents with Descriptive Metadata
impact: MEDIUM
impactDescription: missing metadata prevents proper agent routing and debugging
tags: runner, agents, registration, metadata
---

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
