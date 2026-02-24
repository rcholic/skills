---
name: roundtable
description: "Adaptive multi-model AI roundtable. A meta-panel of 4 premium models (Claude Opus, GPT-5.2, Gemini 3.1 Pro, Grok 4) first designs the optimal workflow for your task — parallel debate, sequential pipeline, or hybrid — then spawns the right panel to execute it. Features: web-search grounding, self-authored digests (no orchestrator bias), formal consensus scoring, optional validation round, neutral synthesis model. Requires Blockrun for full panel. Use for complex analysis, coding reviews, adversarial stress-testing, and multi-perspective decisions."
metadata:
  openclaw:
    emoji: "🎯"
    requires:
      recommended: ["blockrun"]
    tags: ["multi-model", "debate", "orchestration", "reasoning", "blockrun"]
---

# Roundtable v2 — Adaptive Multi-Model Orchestrator

**Your main agent session = TRIGGER ONLY.** When roundtable is called, spawn ONE isolated orchestrator and reply "🎯 Roundtable started..." — then stop.

```
sessions_spawn(
  task = <full orchestrator instructions below>,
  model = "blockrun/sonnet",   ← ALWAYS blockrun/sonnet, never Anthropic OAuth
  mode = "run",
  label = "roundtable-orchestrator",
  runTimeoutSeconds = 600
)
```

**The orchestrator = COORDINATOR ONLY.** Never argues a position, never joins the panel.

Core principle: the Meta-Panel (4 premium models) designs the optimal WORKFLOW for the task — not just which models to use, but how they collaborate, in what order, and with what division of labor.

---

## Requirements

**Full panel (recommended):** Blockrun configured at `localhost:8402` — provides Claude Opus 4.6, GPT-5.2, Gemini 3.1 Pro, Grok 4 via a single proxy.
Without Blockrun, panels degrade automatically to available fallbacks (see `panels.json` → `fallbacks`).

**Minimum setup (degraded mode):** At least one of these providers configured in `openclaw.json`:
- `anthropic` (Claude Opus/Sonnet) — for Opus fallback
- `openai-codex` (GPT-5.3 Codex) — for GPT fallback

**Cost warning:** A full roundtable (meta-panel + 2 rounds + synthesis) spawns 9–12 premium model calls. Use `--quick` for a lightweight single-round run. Cost scale: ~$0.50–$3.00 per full run depending on topic length and providers.

---

## Trigger Patterns

- `roundtable [prompt]` — auto-detect mode, full flow
- `roundtable --debate [prompt]` — force parallel debate mode
- `roundtable --build [prompt]` — force build/coding mode
- `roundtable --redteam [prompt]` — force adversarial mode
- `roundtable --vote [prompt]` — force decision mode
- `roundtable --quick [prompt]` — skip meta-panel, use default panel for mode, 1 round only
- `roundtable --panel model1,model2,model3 [prompt]` — manual panel override, skip meta-panel
- `roundtable --validate [prompt]` — add Round 3 agent validation of synthesis
- `roundtable --context-from YYYY-MM-DD-slug [prompt]` — inject previous roundtable as context *(planned — not yet implemented in prompts; currently loads the JSON from memory and prepends to CURRENT_CONTEXT manually)*
- `roundtable --no-search [prompt]` — skip web search (use only for purely theoretical/abstract topics)

---

## Step -1: Create a Thread (FIRST ACTION)

Before anything else, create a thread in your configured channel and save the thread ID.

```
message(
  action = 'thread-create',
  channel = '[your configured channel]',
  channelId = '[CHANNEL_ID from user config]',
  threadName = '🎯 [topic — max 8 words] [[MODE]]',
  message = '**Panel:** [model list]\n**Mode:** [mode] | **Rounds:** [N]\n⏳ Analysis in progress...'
)
```

Save the returned thread ID as `THREAD_ID`.

**All subsequent message() calls use `target = THREAD_ID`, NOT the channel ID.**

If thread creation fails or channel is not configured: fall back to posting directly in the active channel.

---

## Step 0: Web Search Grounding (always first)

Run a web search on the topic **before anything else** — meta-panel and all agents will have current context.

```
web_search(query = prompt, count = 5)
```

**Timeout policy:** If web_search returns no result or errors within ~10s, do NOT block — continue immediately with `CURRENT_CONTEXT = "No real-time data available (search failed or timed out)."`. The roundtable proceeds on model knowledge only.

**Caching:** If re-running the same topic within the same session, reuse the prior `CURRENT_CONTEXT` block — do not re-search.

Summarize results into a `CURRENT_CONTEXT` block (max 250 words):
- Key facts, recent developments, relevant data points
- Date of search
- If no useful results found: note "No relevant real-time data found" and continue

This block is injected into:
1. The meta-panel prompt (so they design the workflow with current context)
2. Every Round 1 agent prompt (so all panelists argue from the same updated baseline)

---

## Step 0b: Meta-Panel — Workflow Design

**Skip if**: `--panel` flag used, OR `--quick` flag used.

### Spawn 4 premium meta-analysts in parallel

Read `panels.json` → `meta.models`. For each:
```
sessions_spawn(
  task = filled prompts/meta-panel.md,
  model = model_id,
  mode = "run",
  label = "rt-meta-[A/B/C/D]",
  runTimeoutSeconds = 90
)
```

### 0b. Synthesize workflow from 4 recommendations

After collecting all meta responses, the orchestrator synthesizes the final workflow:

1. **Workflow type**: majority vote among 4 recommendations
   - Tie → prefer `hybrid` (more flexible)

2. **Stage composition**: tally model recommendations per stage
   - For each stage position, pick the most-recommended model
   - If a model is not in `agents.defaults.models` allowlist → skip, use next
   - If a model is your orchestrator's model → skip (reserved for the orchestrator, never a panelist)

3. **Rounds**: median of recommendations (round up if tie) — **hard cap at 3 max, always**

4. **Synthesis model**: most-recommended premium model not on the main panel

5. **Log the decision** (include in output header):
   > "Meta-panel designed workflow: [type]. Stages: [N]. Panel: [models]. Synthesis: [model]."

### 0c. Workflow types explained

**parallel_debate** — classic roundtable
- All agents in Stage 1 work independently, same prompt
- Round 2: cross-critique
- Best for: debates, opinions, risk analysis, decision-making

**sequential** — output chains between stages
- Stage 1 agents produce outputs (drafts, code, research)
- Stage 2 agents receive Stage 1 outputs and review/validate/improve
- Best for: coding (write → review), research (collect → synthesize), creative (draft → refine)
- Round 2 within Stage 1 still possible; Stage 2 is a separate pass

**hybrid** — parallel within stages, sequential between
- Stage 1: N agents work in parallel on different aspects
- Stage 2: 1-2 premium agents receive ALL Stage 1 outputs and produce integrated output
- Best for: complex analysis (parallel research → premium synthesis)

### 0d. Panel degradation rule

If any agent fails and fallback is SAME MODEL FAMILY → log:
`⚠️ PANEL DEGRADED — [role] substituted [original] with [fallback] (same family: [family])`

Always surface this in META section of final output with **actionable guidance**:
- If degraded due to missing blockrun → "Action: Start Blockrun at localhost:8402 for full panel, or use `--panel budget` for stable 2-model run"
- If degraded due to model not in allowlist → "Action: Add [model] to `agents.defaults.models` in openclaw.json"
- If degraded due to API error → "Action: Check provider API key / quota, then retry"

---

## Step 1: Detect Mode (if no flag given)

| Mode | Keywords |
|------|----------|
| **debate** | pros/cons, tradeoff, should we, ethics, compare, opinion, better |
| **build** | implement, code, architecture, build, design, develop, create |
| **redteam** | attack, vulnerability, failure, risk, break, threat, exploit |
| **vote** | choose, decide, which one, best option, select, recommend between |
| **default** | anything else |

---

## Step 2: Execute Workflow

### parallel_debate (standard)

**Round 1**: Spawn all Stage 1 agents in parallel.
- Use `prompts/round1.md`
- Each agent writes their full response + SELF-DIGEST (last section)
- Collect all self-digests

**Round 2** (if rounds ≥ 2): Cross-critique in parallel.
- Use `prompts/round2-cross-critique.md`
- `[SELF_DIGEST]` = this agent's own digest from Round 1
- `[PEER_DIGESTS]` = other agents' digests (labeled with role)
- Extract AGREEMENT SCORES from each response

**Round 3** (if `--validate`): See Step 5.

### sequential

**Stage 1**: Spawn agents in parallel using standard `prompts/round1.md`.
- Round 2 cross-critique optional based on `rounds` setting.
- Collect full Round 1 outputs (not just digests) for Stage 2.

**Stage 2**: Spawn Stage 2 agents sequentially or in parallel.
- Build a custom prompt: `prompts/round1.md` base + prepend Stage 1 outputs
- Label: "STAGE 1 OUTPUT from [Role]: [full output]"
- Stage 2 agents review/validate/improve Stage 1 work
- Stage 2 agents also write SELF-DIGESTs

### hybrid

**Stage 1**: Parallel agents, different sub-tasks.
- Customize Round 1 prompt to specify each agent's specific sub-task:
  > "Your specific task for this stage: [task from workflow design]"
- Agents write SELF-DIGESTs

**Stage 2**: 1-2 premium agents receive ALL Stage 1 self-digests + full outputs.
- Build prompt: `prompts/round1.md` base + "You are integrating and synthesizing the work of multiple agents. Their outputs: [all Stage 1 outputs]"
- Stage 2 produces the integrated output

---

## Step 3: Consensus Scoring

After Round 2 (parallel_debate) or Stage 2 (sequential/hybrid):

Extract AGREEMENT SCORES from each agent's Round 2 response.
Build score matrix: `{ agent_role: { peer_role: score_1_to_5 } }`
Consensus % = (sum of all scores / (n_scores × 5)) × 100
If no Round 2 scores (quick mode / sequential): omit consensus %, mark as "N/A"

> **Note on Round 3:** Round 3 validation uses ACCURATE/PARTIALLY/INACCURATE — this is a **separate metric** from consensus %. Round 3 checks synthesis fidelity, not inter-agent agreement. Do NOT mix these two metrics. Consensus % comes only from Round 2 scores; Round 3 result appears separately in the META block as `Validated: yes/no/partial`.

---

## Step 4: Round 3 — Validation (`--validate` flag only)

**When to recommend `--validate` to the user:**
- Consensus % < 40% (high disagreement — synthesis risks distortion)
- Redteam mode (adversarial stakes — synthesis must be bulletproof)
- Build mode with 3+ Stage 2 models (complex integration, easy to misrepresent)
- User explicitly mentions "high-stakes", "final decision", or "publishing this"

**When NOT to use it:** Quick mode, debate on subjective topics, or when time matters more than precision.

Draft synthesis first (Step 5 below), but do NOT post.

Spawn validation agents:
```
sessions_spawn(
  task = filled prompts/round3-validation.md,
  model = original agent model,
  label = "rt-r3-validate-[role]",
  runTimeoutSeconds = 60
)
```

Tally:
- 2+ INACCURATE → rewrite synthesis incorporating corrections
- 1 INACCURATE → note in META: `⚠️ [Role] flagged misrepresentation: [correction summary]`
- All ACCURATE/PARTIAL → mark `Validated: yes` or `Validated: partial` in META

---

## Step 5: Synthesis — Spawned Neutral Model

**Never write synthesis yourself.**

```
sessions_spawn(
  task = filled prompts/final-synthesis.md,
  model = [synthesis model from meta-panel recommendation, or anthropic/claude-opus-4-6 as default],
  label = "rt-synthesis",
  runTimeoutSeconds = 120
)
```

Fill `prompts/final-synthesis.md` placeholders:
- `[ROUND1_SUMMARIES]` → all self-digests: "**[ROLE]** ([model]): [digest]"
- `[ROUND2_SUMMARIES]` → critiques: "**[ROLE]** criticized **[peer]**'s [claim] because [reason]"
- `[CONSENSUS_SCORES]` → full score matrix + calculated %
- `[DISCORD_THREAD_ID]` → the THREAD_ID from Step -1 (synthesis agent posts here)

**Post to Discord** using `THREAD_ID` from Step -1 (not the channel ID). All round outputs and the final synthesis go into the same thread.

---

## Step 6: Persist Results

Save to `~/clawd/memory/roundtables/YYYY-MM-DD-[topic-slug].json`:
```json
{
  "date": "YYYY-MM-DD",
  "topic": "[prompt]",
  "mode": "[mode]",
  "workflow_type": "parallel_debate|sequential|hybrid",
  "stages": [{ "model": "...", "role": "...", "task": "..." }],
  "meta_panel_recommendation": "[summary of meta votes]",
  "panel_degraded": false,
  "panel_degradation_notes": "",
  "consensus_pct": "XX% or N/A",
  "synthesis_model": "[model]",
  "validated": "yes|no|partial",
  "synthesis": "[final synthesis text]"
}
```

---

## Edge Cases

| Situation | Action |
|-----------|--------|
| Web search fails | Continue with note "No real-time context available" in all prompts |
| `--no-search` flag | Skip Step 0 web search entirely |
| Meta-panel all fail | Use default panel for detected mode, log warning |
| `--quick` | Skip meta-panel + round 2. Always uses `parallel_debate` workflow. Spawns default panel for detected mode (3 models). Synthesizes after round 1 only. |
| `--panel` override | Skip meta-panel, use specified models, default to parallel_debate |
| Fallback = same family | Continue + log PANEL DEGRADED warning in META |
| Both model and fallback fail | Skip agent, note in META — **do not wait, do not block** |
| No blockrun configured | Warn user: "Blockrun not available. Using budget panel. Full panel requires Blockrun at localhost:8402." Auto-switch to `budget` profile from panels.json. |
| Agent timeout (any round) | **FAIL-CONTINUE**: treat as absent, mark `[TIMEOUT]` in META, proceed with surviving agents |
| Agent fails mid-Round 2 | Use its Round 1 digest as final position, omit its scores from consensus calculation |
| Synthesis agent fails | Orchestrator writes synthesis, note: "Synthesis by orchestrator (bias risk — no neutral model available)" |
| Stage 2 agent fails | Note in META, synthesize with Stage 1 only |
| 0 agents respond | Report failure, suggest retry |
| 1 agent responds | Skip Round 2 (no peers), synthesize from Round 1 only, mark consensus "N/A" |
| `--context-from SLUG` | Load `~/clawd/memory/roundtables/[slug].json`, extract `synthesis` field, prepend to `CURRENT_CONTEXT` as "PRIOR ROUNDTABLE CONTEXT: [synthesis]". If file not found: warn and continue without prior context. |

### Placeholder Contract

When filling prompt templates, apply this rule for every `[PLACEHOLDER]`:

| Placeholder | If missing/failed | Action |
|-------------|------------------|--------|
| `[CURRENT_CONTEXT]` | Web search failed | Insert: "No real-time context available." |
| `[SELF_DIGEST]` | Agent timed out R1 | Skip agent entirely from R2 |
| `[PEER_DIGESTS]` | All peers failed | Skip R2, go to synthesis directly |
| `[ROUND1_SUMMARIES]` | No R1 outputs | Abort with error: "0 agents responded" |
| `[ROUND2_SUMMARIES]` | Quick mode / no R2 | Insert: "No cross-critique (quick mode or single round)" |
| `[CONSENSUS_SCORES]` | No scores extracted | Insert: "N/A — scores not available" |
| `[SYNTHESIS_DRAFT]` | Synthesis failed | Skip R3, note in META |

**Never leave a `[PLACEHOLDER]` unfilled in a prompt.** Unfilled placeholders confuse models and produce garbage output.

### Score Parsing (Round 2)
Agents write scores in free text. Extract scores with this heuristic:
1. Look for the `SCORES:` block
2. Match pattern: `- [Role]: X/5` — extract integer X (1–5)
3. If no clean integer found, scan for digit 1–5 nearest to the role name
4. If still ambiguous → assign 3 (neutral) and note `[SCORE INFERRED]` in META
Do NOT crash the workflow on a malformed score block.

---

## Quick Reference: Default Panels (fallback if meta-panel fails)

```json
debate:  [opus-4.6, gpt-5.2, gemini-3.1-pro] → Advocate / Skeptic / Devil's Advocate
build:   [gpt-5.2, grok-code-fast, opus-4.6] → Implementer / Optimizer / Architect-Reviewer
redteam: [grok-4, gpt-5.2, gemini-3.1-pro, opus-4.6] → Attacker / Defender / Auditor / Insider Threat
vote:    [opus-4.6, gpt-5.2, gemini-3.1-pro, grok-4]  → 4-way vote panel
(all via blockrun/ prefix — see panels.json for exact model IDs and fallbacks)
```
