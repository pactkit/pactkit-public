---
mode: agent
description: "Hotfix fast track: lightweight fix path that bypasses PDCA"
---

# Command: Hotfix (v1.3.0 Traceable Fast Track)
- **Usage**: `/project-hotfix "$ARGUMENTS"`
- **Agent**: Senior Developer

> **PRINCIPLE**: This command is a lightweight fast-fix channel with traceability.
> Lightweight Spec + Board entry are auto-created. No TDD workflow required.
> Suitable for typos, configuration changes, style adjustments, obvious bugs, and other minor fixes.
> **Spec Lint Gate exemption**: This path SKIPS the Spec Lint Gate (Phase 0.5 in `/project-act`). Hotfix Specs use a lightweight format and are not subject to full structural validation.

## ⚠️ Scope of Application
- ✅ Fix typos / spelling errors
- ✅ Modify configuration files
- ✅ Adjust style / formatting
- ✅ Fix obvious small bugs (single file, clear logic)
- ❌ New feature development → use `/project-plan` + `/project-act`
- ❌ Multi-module refactoring → use `/project-plan` + `/project-act`

## 🧠 Phase 0: Locate & Register
1.  **Parse**: Understand what needs to be fixed from `$ARGUMENTS`.
2.  **Locate**: Use `Grep` or `Glob` to quickly locate the target file and code line.
3.  **Assess**: Confirm this is a minor fix (suitable for Hotfix), not a change requiring full PDCA.
    - If the assessment reveals a complex change, **proactively suggest the user switch to** `/project-plan`.
4.  **Assign HOTFIX-ID**: Run `pactkit generate-id --type hotfix` to allocate a decentralized time-prefixed HOTFIX ID.
5.  **Create Spec**: Create a lightweight Spec at `docs/specs/HOTFIX-{NNN}.md` with:
    - Title, Background (one sentence), Target file/line, and what was fixed.
6.  **Add Board Entry**: Add the hotfix to the Board:
    - `python3 .github/skills/pactkit-board/scripts/board.py add_story HOTFIX-{NNN} "Short title" "Fix description"`

## 🔍 Phase 0.5: Impact Check (Lightweight)
> **PURPOSE**: Data-driven side-effect awareness — read existing call graphs to surface upstream callers before modifying code. This is advisory (L3 SHOULD), non-blocking.
1.  **Query Callers**: Run `pactkit query --callers <target> --json --explain` for the function/file identified in Phase 0.
    - If the query fails or the index is unavailable: log "No call graph available — skipping impact check" and proceed to Phase 1.
2.  **Identify Callers**: Count the callers the query returns (machine fan-in).
3.  **High-Fan-In Warning**: If the target has **3+ callers**, SHOULD warn the user:
    > "⚠️ Target has {N} callers in the call graph. Changes may affect upstream consumers. Consider `/project-act` for full impact analysis."
    - This warning is advisory — the user can acknowledge and proceed.
4.  **Proceed**: Continue to Phase 1 regardless of findings.

## 🔧 Phase 1: Fix
1.  **Fix**: Use `Edit` or `Write` to directly fix the target code.
2.  **Scope**: Keep the modification scope as small as possible — only change what must be changed, no extra optimization or refactoring.
3.  **No Side Effects**: Ensure the modification does not introduce new dependencies or change interface signatures.

## ✅ Phase 2: Verify
1.  **Run Tests (Incremental)**: Run `pactkit test-map <changed-files>` to find related test files, then run only those tests (e.g., `pytest tests/unit/test_foo.py -q`). Fallback to full suite if no mapping.
2.  **Run Lint**: Run the project linter (e.g., `ruff check src/ tests/`) to verify no lint errors in changed files. If the project linter (e.g., `ruff check src/ tests/`) is unavailable, fall back to the stack's lint command directly.
3.  **On Failure**: If tests or lint fail:
    - Output the failing test name and error message
    - **Do not auto-rollback** — let the user decide whether to continue
    - Suggestion: check whether the fix is correct, or switch to `/project-act` for the full workflow

## 📦 Phase 3: Commit
1.  **Conventional Commit**: Generate a standardized commit message:
    - Format: `fix(scope): short description for HOTFIX-{NNN}`
    - Infer scope from the modified file path (e.g. `config`, `auth`, `ui`)
2.  **Confirm**: **Must ask the user for confirmation** before executing `git commit`.
    - Output: "Suggested commit: `fix(scope): description`. Confirm commit?"
3.  **Execute**: After user confirmation, execute git add + git commit.
4.  **Update Board**: Run `python3 .github/skills/pactkit-board/scripts/board.py update_task HOTFIX-{NNN} "Task Name"` for each task to mark it done.

## 📋 Phase 3.5: Session Context Update
1.  **Update Context**: Run the context continuation update in ignored `.pactkit/context.md` — set `last-command` to the last PDCA command and `phase` to the current phase in the continuation section, for session handoff to refresh ignored local `.pactkit/context.md`; never stage it.

## 📊 Phase 3.6: Codegraph Sync
1.  Run `pactkit sync` to update the codegraph index (auto-skips if codegraph is not configured).

## 🔥 Phase 3.7: Postmortem Check (Conditional)
> A hotfix that ends at "tests pass" leaves the defect class armed for the next session.
1.  **Trigger (ANY)**: user-visible impact; same defect pattern in related modules (`grep`); data-loss risk.
2.  **If triggered**: write `docs/architecture/governance/postmortems/{ITEM_ID}.md` — Timeline, Root cause (mechanism, not symptom), Blast radius, Why defenses missed it, Recurrence-prevention action items — each MUST become a Board story (`python3 .github/skills/pactkit-board/scripts/board.py add_story`), never a bare note. Blameless: mechanisms, not people.
3.  **Else**: log `"Postmortem: SKIP — no user-visible impact / no recurrence / no data risk"`.

## 🚫 What This Command Does NOT Do
- Does not require writing tests before code (no TDD)
- Does not run `visualize` to update architecture graphs


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

# Hotfix Contract

## Entry
- explicit bounded repair request

## Inputs
- reproduced symptom
- affected scope

## Outputs
- minimal repair
- focused regression test

## Invariants
- escalate when product behavior or architecture expands

## Completion Evidence
- reported failure is fixed
- affected tests pass

## Failure Semantics
- incomplete_continue

## Allowed Next
- project-check
- project-done

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