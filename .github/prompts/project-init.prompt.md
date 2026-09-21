---
mode: agent
description: "Initialize project scaffolding and governance structure"
---

# Command: Init (v1.3.0 Rich)
- **Usage**: `/project-init`
- **Agent**: System Architect

## 🧠 Phase 0: The Thinking Process
1.  **Environment Check**: Is this a fresh folder or legacy project?
2.  **Compliance**: Does the user need `.github/pactkit.yaml`?
3.  **Strategy**: If legacy, I must prioritize `pactkit query --explore` to capture Reality.

## 🛡️ Phase 0.5: Git Repository Guard
> **INSTRUCTION**: Check if the directory is inside a git repository. This check is non-interactive — never prompt the user.
1.  **Check**: Run `git rev-parse --is-inside-work-tree` (suppress stderr).
2.  **If NOT a git repo** (command fails):
    - Print warning: "⚠️ No git repository detected. Git operations (commit, branch) will not work. Run `git init` to initialize one."
    - Continue with the rest of init. Do NOT prompt or block.
3.  **If already a git repo**: Skip silently to Phase 1.

## 🎬 Phase 1: Environment & Config
> **NOTE**: This playbook is pre-rendered per-format during deployment. All paths below are already resolved for **GitHub Copilot** (`copilot`). No runtime IDE detection needed.
1.  **Check CLI Availability**: Run `pactkit version` to check if CLI is available.
    - **If available**: Proceed to Step 2.
    - **If NOT available** (command fails): Print warning: "⚠️ pactkit CLI not found. Install with: `pip install pactkit`". Then manually create a minimal `.github/pactkit.yaml` in `.github/` with `stack: <detected>`, `root: .`, `developer: ""` and skip to Step 3.
2.  **Generate Config**: Check if `.github/pactkit.yaml` exists.
    - **If missing**: Run `pactkit init --format copilot`
    - **If exists**: Run `pactkit init --format copilot` from the terminal to reinstall
3.  **Stack Detection** (config-first, then file-based fallback):
    - **Config-first**: If `.github/pactkit.yaml` exists and has a `stack` value set (including `auto`), use that value and skip file-based detection.
    - **File-based detection** (only if no config value):
      - Valid values: `python`, `node`, `go`, `java`, `auto`
      - If `pyproject.toml` or `requirements.txt` or `setup.py` exists → `stack: python`
      - If `package.json` exists → `stack: node`
      - If `go.mod` exists → `stack: go`
      - If `pom.xml` or `build.gradle` exists → `stack: java`
    - **Safe fallback**: If none match and no config exists, default to `stack: auto` and print warning: "⚠️ No stack detected, defaulting to auto. You can set `stack:` in `.github/pactkit.yaml` later."
    - Do NOT block on user input for stack selection mid-flow.
4.  **Project Instructions File**: Check/Create `./.github/copilot-instructions.md` if missing (do NOT overwrite).
    - Use the directory name as the project name. Fill test_runner and lint_command from the detected language stack in LANG_PROFILES.
    - Include: venv instructions, dev commands, and the context continuation update in ignored `.pactkit/context.md` — set `last-command` to the last PDCA command and `phase` to the current phase in the continuation section, for session handoff as the cold-start bootstrap; do not `@import` generated Context.

## 🔌 Phase 1.5: External Dependencies (STORY-slim-137)
> Runs BEFORE Phase 3 — Discovery (codegraph) depends on these tools.
1.  Run `pactkit deps check`. If all present, skip silently.
2.  If anything is missing, list items + purposes and ask the user: "Install now?"
3.  On explicit yes: run `pactkit deps install`. NEVER improvise install commands — the CLI owns the registry.
4.  If declined/failed/refused (`enterprise.no_external`): print the manual commands and continue — MUST NOT block init.

## 🎬 Phase 2: Architecture Governance
1.  **Scaffold**: Run `python3 .github/skills/pactkit-visualize/scripts/visualize.py init_arch`.
    - *Result*: Folders created. Placeholders (`system_design.mmd`) created.
2.  **Ensure**: `mkdir -p docs/product docs/specs docs/test_cases tests/e2e/api tests/e2e/browser tests/unit`.

## 🎬 Phase 3: Discovery (Reverse Engineering)
1.  **Scan Reality**: Run `pactkit query --explore <root-module> --json --explain`.
    - *Goal*: Existing project? Read the REAL structure via `pactkit query --explore` immediately.
2.  **Class Scan**: Run `pactkit query --chain <class> --json --explain` for structure.
3.  **Module Scan**: Run `pactkit query --explore <module> --json --explain` for module overviews.
4.  **Verify**: Query the structure via `pactkit query --explore <module>` (system_design.mmd remains for human diagrams).
    - *Check*: Is it still "No code yet"? If files exist in src, this graph MUST contain classes.

## 🎬 Phase 4: Project Skeleton
1.  **Story Facts**: Create `docs/product/stories/`. Do not create a writable Board; render one explicitly with `pactkit board render` only when configured. For an existing aggregate project, preview `pactkit governance migrate`, then ask before applying `pactkit governance migrate --apply`.
    - This ensures the board has all three section headers: `## 📋 Backlog`, `## 🔄 In Progress`, `## ✅ Done`.

## 🎬 Phase 5: Knowledge Base (The Law)
1.  **Law**: Write `docs/architecture/governance/rules.md`.
2.  **History**: Create `docs/architecture/governance/lessons/`; every Lesson is a create-only record written by `pactkit lesson-append`.

## 🎬 Phase 6: Session Context Bootstrap
1.  **Generate Context**: Run the context continuation update in ignored `.pactkit/context.md` — set `last-command` to the last PDCA command and `phase` to the current phase in the continuation section, for session handoff to generate ignored local `.pactkit/context.md`; never stage it.

## 🎬 Phase 7: Next Step
1.  **Output**: "✅ PactKit Initialized. Reality Graph captured. Knowledge Base ready."
2.  **Advice**: "⚠️ IMPORTANT: Continue with `/project-plan 'Reverse engineer'` in this session when requested; a new session is optional."


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

# Bootstrap Contract

## Entry
- explicit initialization request

## Inputs
- project root
- selected host profile

## Outputs
- project governance scaffold

## Invariants
- preserve existing project and user files

## Completion Evidence
- required project markers exist

## Failure Semantics
- incomplete_continue

## Allowed Next
- project-plan
- project-design

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