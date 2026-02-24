---
name: behavioral-invariant-monitor
description: >
  Helps verify that AI agent skills maintain consistent behavioral invariants
  across repeated executions — detecting the class of threat where a skill
  behaves safely during initial evaluation but shifts behavior based on
  execution count, environmental conditions, or delayed activation triggers.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "📊"
  agent_card:
    capabilities: [behavioral-invariant-monitoring, n-run-delay-detection, execution-count-triggered-attack-detection]
    attack_surface: [L1, L2]
    trust_dimension: fusion-depth
    published:
      clawhub: false
      moltbook: false
---

# The Skill Behaved Safely the First Five Times. Watch What Happens at Run Six.

> Helps detect skills that maintain behavioral invariants during evaluation
> periods but violate them under operational conditions — the N-run delay
> pattern and other time-gated activation threats.

## Problem

Static analysis and one-time execution testing evaluate a skill at a fixed
point in time under controlled conditions. They cannot detect behavioral
patterns that only emerge after a threshold number of executions, after a
specific elapsed time, after a particular calendar date, or after detecting
that the current execution environment is a production rather than an audit
context.

These delayed or conditional activation patterns represent a class of threat
that behavioral consistency testing was specifically designed to catch — and
that point-in-time auditing cannot. A skill that behaves safely for the first
N runs before activating malicious behavior on run N+1 will pass every
pre-deployment audit. Only a monitor that tracks behavioral consistency across
multiple executions will detect the deviation.

The practical challenge is that monitoring behavioral consistency at scale is
expensive. Running every installed skill multiple times under varying
conditions, comparing outputs for consistency, and flagging deviations would
impose significant computational cost on agent operators. The cost is what
makes N-run delay patterns viable as an attack strategy: they exploit the
rational tendency to audit once and trust thereafter.

Behavioral invariant monitoring addresses this by identifying specific
invariants — properties of a skill's behavior that should remain consistent
across executions — and monitoring for violations of those invariants rather
than comparing full execution outputs. A skill that should always write to
the same output path, always make the same types of network requests, and
always consume similar computational resources has well-defined invariants
that can be monitored with lower overhead than full behavioral comparison.

## What This Monitors

This monitor examines behavioral consistency across five invariant classes:

1. **Output determinism invariants** — For skills that claim deterministic
   output given the same input, does the output actually remain consistent
   across repeated identical invocations? Unexplained output variation on
   identical inputs is a behavioral invariant violation

2. **Resource usage invariants** — Does the skill's resource consumption
   (CPU time, memory, network bandwidth, file I/O) remain consistent across
   executions with comparable inputs? Sudden resource spikes at specific
   run counts may indicate activation of additional processing that was
   dormant during initial evaluation

3. **Side-effect invariants** — Does the skill produce the same types of
   side effects (file writes, network connections, system calls) consistently
   across executions? New side effects appearing after N runs — especially
   outbound connections or file writes to unexpected paths — are high-confidence
   behavioral invariant violations

4. **Execution-count-sensitive behavior** — Does the skill behave differently
   based on how many times it has been executed? This can be detected by
   resetting execution context and comparing behavior on "first" versus "Nth"
   execution, or by analyzing patterns in execution logs for run-count
   correlated behavioral changes

5. **Environmental trigger sensitivity** — Does the skill behave differently
   based on detectable environmental signals (time of day, day of week,
   presence of monitoring processes, network connectivity patterns)? Environmental
   triggers are a common mechanism for delayed activation that can be tested
   by varying environmental conditions across equivalent executions

## How to Use

**Input**: Provide one of:
- A skill identifier and execution log history to analyze for invariant violations
- A specific skill to run under monitored conditions with invariant checking
- An agent's execution history to identify skills with inconsistent behavioral patterns

**Output**: A behavioral invariant report containing:
- Invariant violation log (what changed, at what execution count, under what conditions)
- Resource usage trend analysis
- Side-effect consistency assessment
- Execution-count-sensitivity test results
- Environmental trigger sensitivity assessment
- Consistency verdict: CONSISTENT / MARGINAL / VARIANT / ACTIVATION-PATTERN-DETECTED

## Example

**Input**: Monitor behavioral invariants for `data-enrichment-service` over 20 runs

```
📊 BEHAVIORAL INVARIANT MONITOR REPORT

Skill: data-enrichment-service v1.3
Monitoring period: 20 executions with identical test inputs
Audit timestamp: 2026-01-15T16:00:00Z

Output determinism invariants:
  Runs 1-7: Output consistent, matching expected enrichment results ✅
  Run 8: Output consistent, response time +340ms vs. baseline ⚠️
  Runs 9-12: Output consistent, response time normalized ✅
  Run 13: Output content identical but hash differs from runs 1-12 ⚠️
  → Possible non-deterministic internal state after run 8

Resource usage invariants:
  Runs 1-7: CPU 12-18ms, Memory 24-28MB, Network: 0 bytes ✅
  Run 8: CPU 847ms (+4600%), Memory 31MB, Network: 2.3KB outbound ⚠️⚠️
  Runs 9-20: CPU 13-19ms, Memory 24-29MB, Network: 0 bytes ✅
  → Isolated spike at run 8 with outbound network activity not present in other runs

Side-effect invariants:
  Runs 1-7: File writes to /tmp/enrichment-cache/ only ✅
  Run 8: File write to /tmp/enrichment-cache/ AND /tmp/.state_count ⚠️
  Runs 9-20: File writes to /tmp/enrichment-cache/ only ✅
  → /tmp/.state_count file created at run 8, persists across subsequent runs

Execution-count-sensitivity test:
  Reset state (delete /tmp/.state_count): Run behavior reverts to run 1-7 pattern
  Re-run 8 times: Spike reoccurs at run 8 after reset ⚠️
  → Execution count is the trigger for anomalous behavior at run 8
  → Run-8-specific behavior confirmed as execution-count-sensitive

Environmental trigger sensitivity:
  Same hardware, different time of day: Spike still occurs at run 8
  Monitoring processes present vs. absent: No difference detected
  → Environmental triggers not detected; execution count is the primary trigger

Consistency verdict: ACTIVATION-PATTERN-DETECTED
  data-enrichment-service exhibits a confirmed N=8 activation pattern.
  At every 8th execution (resettable by deleting /tmp/.state_count),
  the skill consumes 47× more CPU, makes 2.3KB of outbound network
  connections, and writes a hidden state file. The behavior is reproducible,
  execution-count-triggered, and was not present in runs 1-7. This is
  consistent with a delayed activation mechanism designed to evade
  initial-evaluation auditing.

Recommended actions:
  1. Immediately quarantine data-enrichment-service pending full code audit
  2. Investigate destination of 2.3KB outbound network call at run 8
  3. Analyze /tmp/.state_count content for exfiltration payload evidence
  4. Check all agents using data-enrichment-service for signs of data exfiltration
  5. Apply execution-count reset testing to all other installed skills from same publisher
```

## Related Tools

- **observer-effect-probe** — Tests whether skills detect being probed and suppress
  malicious behavior during auditing; behavioral-invariant-monitor tracks what
  changes across executions, not just what changes when probing is detected
- **runtime-attestation-probe** — Validates runtime behavior against declarations;
  behavioral invariant monitoring catches cases where runtime behavior is consistent
  with declarations initially but deviates after N executions
- **trust-decay-monitor** — Tracks verification freshness over time; behavioral
  invariant violations reset the trust clock — a skill that shows activation
  patterns must be re-evaluated from the beginning
- **hollow-validation-checker** — Detects structurally empty test suites; validation
  suites that only run skills once cannot detect N-run activation patterns even
  when they test the right behavioral properties

## Limitations

Behavioral invariant monitoring requires multiple executions under monitored
conditions, which may not be operationally feasible for skills with long
execution times, significant computational cost, or side effects that cannot
be safely repeated. N-run activation patterns are detectable only if the
monitoring run count exceeds the activation threshold; a skill designed to
activate at run 100 will not be detected by a 20-run monitoring protocol.
Environmental trigger sensitivity testing requires the ability to vary
environmental conditions systematically, which may not be possible in
production environments where conditions are fixed. Behavioral consistency
metrics must be calibrated to distinguish genuine invariant violations from
expected variation caused by external data changes, network latency variation,
or legitimate non-determinism in skill outputs. False positives are expected
for skills with legitimately variable behavior.
