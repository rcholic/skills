---
name: compaction-ui
description: Manual memory compaction button with context gauge for OpenClaw Control UI. Adds a circular progress ring showing context window utilization (tokens used vs available), a click-to-compact action that triggers LLM-based summarization, a modal with animated progress phases, token before/after reporting, compaction divider lines in chat history, and NO_REPLY/HEARTBEAT_OK message filtering. Use when adding or upgrading manual compaction controls in the OpenClaw web dashboard.
---

# Compaction UI

Adds a manual compaction button with context utilization gauge to the OpenClaw Control UI chat toolbar.

## Components

### 1. Context Gauge Button (`app-render.helpers.ts`)

A circular SVG progress ring that doubles as the compact trigger.

- **Placement:** After session selector dropdown in `renderChatControls()`
- **Data source:** `sessionsResult.sessions[].totalTokens` and `contextTokens` from session rows
- **Colors:** Green (<60%), Yellow (60-85%), Red (≥85%)
- **Disabled:** When utilization <20% or during active compaction
- **Tooltip:** Shows "Context: XK / YK tokens (Z%)"

On click, calls `sessions.compact` RPC and shows a modal overlay with animated progress phases:
1. "Preparing compaction…"
2. "Reading session history…"
3. "Summarizing conversation…"
4. "Compacting context window…"
5. "✅ Compaction Complete — XK → YK tokens" (holds 2s, then auto-closes and refreshes chat)

See `references/context-gauge-ui.diff.md` for the full `renderContextGauge()` implementation.

### 2. LLM-Based `sessions.compact` RPC (`sessions.ts`)

Replaces the original line-trimming RPC with real LLM summarization via `compactEmbeddedPiSession()`.

**Flow:**
1. Resolve session entry, agent ID, model/provider from config
2. Abort any active agent run on the session
3. Call `compactEmbeddedPiSession()` with `trigger: "manual"`
4. Update session store with new token counts and increment `compactionCount`
5. Return `{ ok, compacted, tokensBefore, tokensAfter, reason }`

See `references/sessions-compact-rpc.diff.md` for the full diff.

### 3. Chat History Filters (`chat.ts`)

- **NO_REPLY/HEARTBEAT_OK filtering:** Skip assistant messages where full text content is exactly `NO_REPLY` or `HEARTBEAT_OK` in `buildChatItems()`
- **Compaction divider:** Detects `raw.__openclaw.kind === "compaction"` on message objects and renders a labeled divider line

See `references/chat-filters.diff.md` for the diff.

### 4. Compaction Marker in JSONL

The pi-agent compaction engine writes `type: "compaction"` entries to session JSONL files. The `readSessionMessages()` function in `session-utils.fs.ts` converts these to synthetic messages with `__openclaw: { kind: "compaction" }` for the UI to detect.

## Installation

Apply the three patches in `references/` against the OpenClaw source tree:

```bash
cd /path/to/openclaw
git apply skills/compaction-ui/references/sessions-compact-rpc.diff.md
git apply skills/compaction-ui/references/context-gauge-ui.diff.md
git apply skills/compaction-ui/references/chat-filters.diff.md
npm run build
```

Then restart the gateway.

## Key Architecture Notes

- The gauge reads token data from `GatewaySessionRow.totalTokens` and `contextTokens` fields, populated by the session store after each agent turn
- `compactEmbeddedPiSession` requires live LLM access (resolves model/provider/apiKey from config) — compaction takes 10-30s
- The modal uses `position:fixed` overlay with `backdrop-filter:blur(3px)` and a CSS keyframe animation for the progress bar
- After compaction, chat refresh is deferred until after the 2s "complete" display to prevent the modal from being wiped by re-render
