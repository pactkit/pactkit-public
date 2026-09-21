---
mode: agent
description: "Sequential PDCA in the current session"
---

# Command: Sprint (Current-Session PDCA Orchestrator)
- **Usage**: `/project-sprint "$ARGUMENTS"`
- **Execution**: Continue sequentially in this conversation. Keep all phase
  evidence in the current session unless the user explicitly chooses another
  supported execution mode.

## Resolve work

In single-story mode, resolve an existing Story ID from the argument. For a new
requirement, run `pactkit generate-id`, carry that STORY-ID into Plan, and use
its `docs/specs/{STORY_ID}.md` as the file-driven contract.

In Wave Mode (empty arguments), inspect the board and `pactkit spec-graph
--json` to produce a deterministic Wave Plan. Process eligible Stories
sequentially by dependency order. Do not use `max_parallel` unless the user
explicitly requests parallel execution; unknown or conflicting touch surfaces
remain serialized.

## Phase capsule lifecycle

Keep exactly one active phase. Before entering a phase, use the host Read tool
to read its managed capsule below; do not treat this list as Markdown imports:

- Plan: `.github/skills/_rules/phases/plan-contract.md`
- Act: `.github/skills/_rules/phases/act-contract.md`
- Check: `.github/skills/_rules/phases/check-contract.md`
- Done: `.github/skills/_rules/phases/done-contract.md`

Then execute the corresponding native command playbook in order:

1. Plan — create or update the Spec and Story.
2. Act — implement and produce fresh, adequate behavior evidence.
3. Check — perform QA for security, quality, scope, tests, and Spec alignment.
4. Done — close the Story only when requested external effects are authorized.

When a phase finishes, mark its capsule historical and activate only the next
capsule. A failed Check returns to Act for repair in this same session. Missing
evidence makes completion incomplete; it does not lock reading, implementation,
testing, or repair and does not require restarting Sprint.

## Completion

Report the active Story, changed files, phase evidence, tests, and remaining
gaps. Never infer success from an old workflow state or an agent response.


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

# Sprint Orchestrator

Keep exactly one phase active at a time in the current session. Before each
stage, load that phase's managed capsule using the host-native instruction in
the Sprint command. A completed or failed capsule becomes historical evidence
and cannot constrain later safe work. Check failures return to Act for repair;
external effects remain subject to current authorization.

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