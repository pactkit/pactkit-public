---
mode: agent
description: "Hypothesis-driven troubleshooting: structured debug from symptom to root cause"
---

# Command: Debug (v1.0.0 Hypothesis-Driven)
- **Usage**: `/project-debug "$SYMPTOM"`
- **Agent**: Senior Developer

> **PRINCIPLE**: Debug by scientific method — not by reading everything.
> Every file read must be justified by a hypothesis. Every hypothesis must have a verification step.
> If 3 iterations don't converge, escalate to `/project-plan` for full architectural trace.

## ⚠️ Scope of Application
- ✅ Runtime errors (exceptions, crashes, unexpected behavior)
- ✅ Test failures (assertion errors, unexpected output)
- ✅ Logic bugs ("code runs but result is wrong")
- ✅ Regression ("it worked before, now it doesn't")
- ❌ Environment/config issues → use `system-medic` + `pactkit-doctor`
- ❌ Performance issues → out of scope (different diagnostic approach)
- ❌ Feature design → use `/project-plan`

## 🧠 Phase 1: Symptom Structuring
> **PURPOSE**: Minimize user input burden — extract structure from whatever they provide.

1.  **Parse Input**: Extract from `$SYMPTOM`:
    - **Symptom**: What's happening? (error message, traceback, unexpected behavior)
    - **Expected**: What should happen instead?
    - **Reproduction**: How to trigger it? (command, input, URL)
    - **Context**: What changed recently? (recent commit, deploy, dependency update)

2.  **If input is unstructured** (e.g., "接口报500了"):
    - Extract what you can into the 4-field template
    - Ask for **only** the critical missing field(s) — typically Reproduction
    - Do NOT ask for all 4 fields if 2-3 are inferable

3.  **If reproduction command exists**: Run it to capture the actual error output.
    - This is evidence, not exploration. The output feeds Phase 2.

4.  **Output checkpoint**:
    ```
    📋 Symptom Summary:
    - Symptom: {extracted}
    - Expected: {extracted or "TBD"}
    - Reproduction: {command or "need from user"}
    - Context: {recent changes or "unknown"}
    ```

## 🔍 Phase 2: Hypothesis Generation
> **CONSTRAINT**: Maximum 3 hypotheses. Ranked by probability. Each MUST have a verification step.

1.  **Analyze signals** from Phase 1 output:
    - Error type (KeyError → data shape; ImportError → dependency; AssertionError → logic)
    - Stack trace location (if available)
    - Recency of changes (if Context provided)

2.  **Generate ≤3 hypotheses**, format:
    ```
    H1 (probability%): {one-sentence hypothesis}
       Verify: {executable command or specific file:line to check}
       Expected if true: {what the verification would show}
       Expected if false: {what it would show instead}

    H2 (probability%): ...
    H3 (probability%): ...
    ```

3.  **Hypothesis quality rules**:
    - Each hypothesis MUST be falsifiable (there must be a way to disprove it)
    - Verification MUST be a concrete action (not "investigate further" or "look into")
    - Probabilities must sum to ≤100% (leave room for unknown unknowns)

4.  **Provider-Routed Trace (R7)**: Run `pactkit query --callers <function> --json --explain` and `pactkit query --callees <function> --json --explain`. The router enforces configured Codegraph priority and fails closed; fallback requires explicit `--allow-fallback` authorization.

## 🔬 Phase 3: Verification Loop
> **CONSTRAINT**: One hypothesis at a time. Execute → Observe → Conclude before moving to next.

For each hypothesis (highest probability first):

1.  **Justify** (one line): "Testing H{N}: checking if {hypothesis} by {action}"
2.  **Execute**: Run the verification command or read the specific file:line
    - **Evidence-Gated Read (R2)**: Every `Read` call MUST be preceded by:
      `"H{N} verification: reading {file}:{line} to check {specific thing}"`
    - MUST NOT read files "for context" or "to understand" without hypothesis link
3.  **Observe**: Record actual vs expected output
4.  **Conclude**:
    - **Confirmed**: Evidence matches "expected if true" → proceed to Phase 4
    - **Eliminated**: Evidence matches "expected if false" → mark H{N} as eliminated, proceed to next
    - **Inconclusive**: Neither matches → refine hypothesis, re-verify once

5.  **After each iteration**: State remaining hypothesis space:
    ```
    ❌ H1: eliminated (reason)
    🔍 H2: testing next
    ⏳ H3: pending
    ```

## 🚨 Phase 3.5: Convergence Escalation (R4)
> **TRIGGER**: All initial hypotheses eliminated OR 3 iterations without confirmation.

**Round 1 escalation**:
- All 3 hypotheses eliminated → generate 2 new hypotheses from a DIFFERENT angle:
  - If initial hypotheses were "code logic" → try "data/state" angle
  - If initial were "recent change" → try "upstream dependency" angle
- Ask user: "Initial hypotheses eliminated. Any additional symptoms or reproduction info?"

**Round 2 escalation** (still stuck after Round 1):
- Output summary of what was tried and ruled out
- Nudge: "This looks like a cross-module issue that needs full architectural trace."
- Recommend: `/project-plan "{problem summary}"` for deep analysis with pactkit-trace

## ✅ Phase 4: Conclusion Report (R6)
> **TRIGGER**: A hypothesis is confirmed with evidence.

Output structured conclusion:
```
🎯 Root Cause
{One-sentence statement of what's wrong}

📎 Evidence
{The verification step that confirmed it — command + output}

🔧 Fix Path
{Concrete next action: file:line to change, or command to run}

💡 Next Step
{PDCA nudge — recommend /project-hotfix for single-file fix, /project-act for multi-file}
```

## 🚫 What This Command Does NOT Do
- Does NOT fix the code — only locates the root cause
- Does NOT read files without justification — every read is hypothesis-linked
- Does NOT loop indefinitely — max 2 escalation rounds then hands off to /project-plan
- Does NOT replace /project-plan — it's fast triage, not deep architecture analysis
- Does NOT handle environment issues — those go to system-medic


---

## Rules Reference

# PDCA Lifecycle

## Entry
Activate a phase only when the user invokes its skill or explicitly asks for
that workflow. Resolve the current objective, project root, and relevant Story
from the current request and repository evidence; old run state is advisory.

## Execution
Work in the current conversation. Reuse valid evidence already produced in this
session. Do not repeat a completed step unless inputs changed or verification
shows a reason. Ask only when a missing decision would materially change the
result or authorize an external or destructive action.

## Reuse Classification
Before repeating a load, decision, or verification, classify what is available:
- Availability: content is present in context from a source still authoritative for this
  version; remembering a filename or a past read is not availability.
- Applicability: the change actually triggers the requirement; "simple task", an exhausted
  guide budget, and familiarity never justify skipping an applicable one.
- Decisions: a still-applicable decision may be reused; a decision is not verification.
- Evidence: reuse a verification only while it covers the requirement and its code, tests,
  config, role, and environment; otherwise the gap stays open.
Load events, restatement, self-reported compliance, and a clean worktree never prove a
requirement is met.

## Recovery
After a phase switch, requirement change, or context compaction, re-confirm decisions and
evidence from the Spec, Story, and records; anything whose source, implementation,
environment, or freshness stays unconfirmed keeps its item pending. A missing cache never
gates work, and reuse never waives an applicable requirement.

## Transition
Finishing one phase does not automatically authorize the next phase. Continue
into another phase only when the user's request includes it, such as Sprint, or
when the user explicitly invokes the next skill. A new session is optional.

## Completion
Report complete only when that phase's required outputs and evidence exist.
Missing evidence means incomplete-with-next-action, not a lock on reading,
diagnosis, implementation, testing, or repair.

## Interruption and Change
If the user interrupts, replaces the request, or changes a requirement, stop
the superseded work and follow the latest instruction. Update stale artifacts
when authorized; never force execution against a known-obsolete Spec or state.

## Exit
End with the achieved outcome, remaining evidence gaps, and the smallest useful
next action. Do not manufacture a handoff, background run, or separate session.

# Debug Contract

## Entry
- explicit diagnosis request

## Inputs
- observable symptom
- bounded target

## Outputs
- reproduced symptom
- ranked root-cause conclusion

## Invariants
- test hypotheses against evidence before proposing a cause

## Completion Evidence
- cause and uncertainty are stated

## Failure Semantics
- incomplete_continue

## Allowed Next
- project-hotfix
- project-plan

## External Effects
- none

# Shared Execution

## Project Contract Preflight
Except in `/project-init`, before project mutation run `pactkit project-preflight --apply-safe`. It may
reconcile safe changes. UNADOPTED requires an authorized `pactkit adopt` after
its `--check` preview; `/project-init` remains optional. BLOCKED stops mutation.
`pactkit init --format copilot` from the terminal to reinstall updates host assets, never project state. Use
`pactkit reconcile --check` for a read-only migration preview.

## Hierarchy of Truth
Code is not the law. Tier 1: Specs (`docs/specs/*.md`) and Test Cases;
Tier 2: Tests; Tier 3: Implementation. On conflict, the higher tier
takes precedence — modify the lower tier, never the reverse. When the
Spec itself is wrong, fix the Spec first, then sync tests and code; never
patch code around a known-bad Spec.

## Execution
Use the current session. Failure classification is: current regression,
pre-existing failure, obsolete contract/test, or environment failure. Only a
hard risk blocks its exact action; otherwise record evidence and continue.