---
mode: agent
description: "Code cleanup, Board update, Git commit"
---

# Command: Done (v1.3.0 Smart Gatekeeper)
- **Usage**: `/project-done`
- **Agent**: Repo Maintainer

## 🧠 Phase 0: The Thinking Process
1.  **Audit**: Are tests passing? Is the Board updated?
2.  **Semantics**: Determine correct Conventional Commit scope.

## 🎬 Phase 1: Context Loading
1.  **Read Spec**: Read `docs/specs/{ID}.md`.
2.  **Read Story Facts**: Run `pactkit board list`; never use the Board projection for completion decisions.

## 🎬 Phase 2: Housekeeping (Deep Clean)
1.  Run language-specific cleanup (e.g., `find . -name '__pycache__' -exec rm -rf {} +`) to remove language-specific temp artifacts.
2.  Run `pactkit sync` when `LANG_PROFILES.source_dirs` changed (Codegraph index refresh; MMD graph generation is retired). Otherwise log: "Graph index up-to-date — no source changes".
3.  **HLD Consistency Check**: Run the project file and structure checks manually and check HLD drift. If doctor reports rule/command conflicts (`.pactkit-new` candidates), resolve with `pactkit accept-candidates`. If drift > 3, WARN user: "system_design.mmd is {N} modules behind — consider updating it."
4.  **Friction Snapshot** (STORY-slim-20260827024e71df170f): Run `pactkit stats --format json`; report this story's run duration, blocker dwell, and step rework in the completion summary (`events: unavailable` for pre-2.24 runs is expected — report and continue).

## 🎬 Phase 2.5: Regression Gate (CRITICAL)
> **CRITICAL**: Do NOT skip this step. This is the safety net before commit.

### Step 0: Source Change Pre-Check
- Run the test suite with impact classification (SKIP/IMPACT/FULL; e.g., `python3 -m pytest tests/ -v`) and route on `decision.verdict` (text fallback: the status prefix):
  - `reuse` (`VERIFIED-CURRENT`) + `record_scope: full` → log `"Regression: SKIP — scope full"`, continue via the Smart Lint Gate (fingerprint ≠ lint); without full scope → Step 1.3 (R2).
  - `supplement` (`STALE — {changed}`) → Step 1.7 impact analysis on `decision.changed`, run the mapped tests; load `decision.guides` as the engineering guides.
  - `re-verify` (`STALE`, incl. git-status unavailable) → Step 2 Decision Tree (full regression by default).
  - `no-baseline` + `evidence_trust: invalid` (`INVALID-RECORD`) → directly to Step 2 (Decision Tree — full regression by default) — a clean worktree proves nothing (committed changes are invisible to a bare HEAD diff); re-record after the next green run.
  - `no-baseline` + `none` (`NO-RECORD`) → classify uncommitted changes at Step 1.3.
- Engineering-guide filtering never overrides these routes: `invalid`, `unavailable`, `supplement`, and `re-verify` keep their meanings. A regression record proves only the verification it covers — not lint, journeys, or other independent acceptance; reuse unaffected evidence and disclose the rest.

### Step 1: Impact Analysis
- Check graph availability through `pactkit query --impact <target> --json --explain`; do not select providers manually.

### Step 1.3: Classification Shortcut
Run the test suite with impact classification (SKIP/IMPACT/FULL; e.g., `python3 -m pytest tests/ -v`) to classify changes (doc-only → SKIP):
- **SKIP** → proceed to Step 2.5 (no regression needed).
- **FULL** → skip impact analysis, proceed directly to Step 3 (full regression).
- **IMPACT** → continue to Step 1.7.

### Step 1.7: Impact-Based Analysis (STORY-053)
With `regression.strategy=impact`, extract changed `def` names from the Step 0 baseline diff (`git diff <recorded-commit> --unified=0` with a record, else `git diff HEAD --unified=0`); run `pactkit query --impact <func_name> --json --explain`, deduplicate mapped tests, and run them when below `regression.max_impact_tests` (default 50). Log `"Regression: IMPACT-BASED — {N} test files based on call graph analysis"`; missing functions, failures, or threshold overflow fall through to Decision Tree.

### Step 2: Decision Tree (Safe-by-Default)
Run full regression by default. Incremental requires a fresh Codegraph index (`pactkit sync`), ≤3 source files, mappings from `LANG_PROFILES[stack].test_map_pattern`, no test-infra changes, and no file with 3+ importers; missing index or fast suite (<500 tests) means full. Log the chosen path as `"Regression: {TYPE} — {reason}"` (SKIP, STORY-ONLY, FULL, IMPACT-BASED, or INCREMENTAL).

### Step 2.3: Coverage Verification (Conditional)
Run `pactkit coverage-gate <changed-files> --tests <mapped test files>` — pass the selection from Step 1.7 (or the record's test set): coverage runs that set, never a second full-suite pass. Verify coverage on changed source files.
- ≥80% PASS; 50–79% WARN with file/coverage; <50% report as an acceptance gap and continue; the user decides whether repair gates acceptance. If unavailable, run equivalent `pytest --cov`; report results.

### Step 2.5: Smart Lint Gate (STORY-030)
If Act already verified lint with no later source/test change, log `"Lint: SKIP — Act already passed lint, no new changes"`. Otherwise run the project linter (e.g., `ruff check src/ tests/`) (or `LANG_PROFILES[stack].lint_command`); honor `auto_fix` and `lint_blocking`, and report non-blocking warnings. No configured command means skip.

### Step 3: Gate
- If any test fails, do not commit or archive. Classify the failure and report the evidence.
- Do not guess at a pre-existing test's intent. A user-authorized repair may continue after reading its governing Spec/Test Case; otherwise leave that failure unchanged and disclose it.
- The agent MUST NOT assume it understands pre-existing test intent — the project may have adopted PDCA mid-way and there is no Spec for older features.
- Report the failure to the user with: which test failed, what it appears to test, and which change likely caused it.
- Proceed to commit/archive only if all required tests and blocking lint checks are green. Safe diagnosis and repair remain available.

## 🎬 Phase 3: Hygiene Check & Fix
1.  **Verify**: Are tasks for this Story marked `[x]`?
2.  **Auto-Fix**:
    - If tests are GREEN but tasks are `[ ]`, verify each task's evidence (test results, coverage table, Spec AC mapping), then run `pactkit board complete-task {STORY_ID} "<exact task>"` for each verified task and report the verification basis in the summary. Ask the user only when a task's evidence cannot be located.
3.  **Lessons Auto-append (MUST)**: Run `pactkit lesson-append --story {STORY_ID} --text "lesson text" [--context "file.py:func"]`.
    - The command checks specificity (references concrete file/function?) and dedup (different from last 5 entries?).
    - If both pass: appends row using format `| {date} | {lesson} | {context} |` where date=YYYY-MM-DD, context={STORY_ID}
    - If either fails: skip with log from command output.
    - If `pactkit lesson-append` is unavailable, report the gap (lesson not recorded; Core upgrade needed) and continue the Done flow. Never write a shared Lesson projection manually.
4.  **Invariants Refresh (MUST)**: Run `pactkit invariants-refresh --test-count {N}` where {N} is the actual count from the most recent test run.
    - The command updates `docs/architecture/governance/rules.md` invariant "All {N}+ tests must pass".
    - If `pactkit invariants-refresh` is unavailable, fall back to manual: read rules.md, find the pattern, replace the number.
5.  **Document Validators (Non-blocking)**: Run document structure checks as warnings:
    - the context continuation update in ignored `.pactkit/context.md` — set `last-command` to the last PDCA command and `phase` to the current phase in the continuation section, for session handoff — validates generation from Story/Lesson facts without writing tracked files
    - `pactkit board render --check` — validates the optional Board projection
    - These are non-blocking: report warnings but do not stop the Done flow.
6.  **Spec Status Update (MUST)**: Run `pactkit spec-status docs/specs/{STORY_ID}.md Done` to update `| Status | Draft |` to `| Status | Done |` in the spec file (accepted values: Draft, In Progress, Done). If `pactkit spec-status` is unavailable, manually edit the spec file.
7.  **Archive Honesty Gate (CRITICAL — STORY-slim-136)**: Run `pactkit done-verify {STORY_ID}` — it mechanically verifies requirement→test evidence, checkbox↔case honesty, and status consistency (Spec Done + Board `[x]` + archive).
    - **Any FAIL (exit ≠ 0)**: Print the evidence lines and do not archive or commit. Continue safe diagnosis or repair when it is within the user's request. WARN-only: print and proceed. CLI too old: warn that the gate was skipped, then proceed.
8.  **Memory MCP (Conditional)**: IF Memory MCP is available, use add_observations to record lessons learned (patterns, pitfalls, key files) on the `{STORY_ID}` entity.
9.  **Harness Audit Refresh (Conditional)**: Run `pactkit audit --append --if-needed {STORY_ID}`. Only refreshes when `harness_audit.json` exists AND its `story_id` matches `{STORY_ID}` (this story owns the audit). Silently skips if no audit was ever run or if the audit belongs to a different story. If it runs and `ready` changed from `true` to `false`, WARN the user.

## 🎬 Phase 3.5: Archive (Optional)
1.  **Check**: Are all tasks for the current Story marked `[x]`?
2.  **Action**: If yes, run `python3 .github/skills/pactkit-board/scripts/board.py archive`.
3.  **Result**: Completed stories are moved to `docs/product/archive/archive_YYYYMM.md`.

## 🎬 Phase 3.5.5: Issue Tracker Verification (BUG/HOTFIX Only)
> **Purpose**: Verify GitHub Issue exists for BUG/HOTFIX items; STORY items are NOT synced to protect IP.
1.  Run `pactkit issue-sync {ITEM_ID}` to handle the full issue lifecycle:
    - STORY items: skipped automatically (IP protection).
    - BUG/HOTFIX items: searches for existing issue, backfill-creates if missing, returns issue URL.
2.  If `pactkit issue-sync` returns a URL, update the Sprint Board entry to include `[#{number}]({url})`.
3.  If `pactkit issue-sync` is unavailable, fall back to manual `gh` CLI commands:
    a. **CLI Check**: Run `gh --version`. If unavailable, print warning and proceed to Phase 3.6.
    b. **Search**: Run `gh issue list --search "{ITEM_ID}" --state all --json number,title,url`.
    c. **If not found**: Create issue via `gh issue create`.
    d. **If any gh command fails**: Print warning, continue to Phase 3.6.

## 🎬 Phase 3.6: Issue Tracker Closure (BUG/HOTFIX Only)
> **Purpose**: Close linked external issues when BUG/HOTFIX is done. STORY items are skipped.
1.  **Check Item Type**: If current item is `STORY-*`, skip this phase silently.
2.  **Check Config**: Read `.github/pactkit.yaml` for `issue_tracker.provider`.
3.  **If `provider: github`**:
    - Parse the Sprint Board entry for a linked issue URL (e.g., `[#123](https://github.com/...)`)
    - If found: run `gh issue close <number> --comment "Completed in $(git rev-parse --short HEAD)"`
    - If `gh` CLI unavailable or closure fails: print warning, continue
4.  **If `provider: none` or section missing**: Skip silently.

## 🎬 Phase 4: Git Commit
0.  **Enterprise Check**: If `enterprise.no_git: true` in `.github/pactkit.yaml`, skip ALL git operations in this phase. Print: "ℹ️ Git operations disabled (enterprise.no_git)". Skip to the Session Context Update phase.
0.5.  **Deployment Verification (self-dev only)**: Only when developing PactKit itself (`pyproject.toml` name == "pactkit"):
    - First perform the deployment smoke-check in a temporary target directory; do not write a real host configuration as part of Done.
    - If validating the installed host is needed, describe the exact update and ask for explicit authorization before running `pactkit init --format copilot` from the terminal to reinstall.
    - Smoke-check: for each AC that references prompt/deployed file content, inspect 1-2 key assertions in the temporary generated files.
    - Report: `Deploy verification: PASS ({N} assertions checked)` or `FAIL (details)`.
    - If FAIL, fix the deployment issue before committing.
    - **If NOT self-dev**: Skip this step silently.
1.  **Format**: `feat(scope): <title from spec>`
2.  **Execute**: Run the git commit command.
3.  **Post-Commit Prompts**:
    - **Version bump?** If `pyproject.toml` version was changed in this Story: "ℹ️ Version bump detected. Run `/project-release` to create snapshot and git tag."
    - **Feature branch?** If current branch is not `main`/`master`: "ℹ️ Working on a feature branch. Run `/project-pr` to push and create a pull request."
    - **CI Status Check (Conditional)**: If `ci.provider` is `github` in `.github/pactkit.yaml` and `gh` CLI is available:
      1. After push, run `gh run list --limit 1 --json status,name,databaseId` to check the latest workflow run.
      2. Report: `CI: [pass/fail/pending] — {workflow_name} #{run_id}`
      3. If CI fails, print a warning but do NOT block the Done flow.
      4. If `gh` CLI is unavailable or command fails, skip silently.

## 🎬 Phase 4.5: Session Context Update
1.  Run the context continuation update in ignored `.pactkit/context.md` — set `last-command` to the last PDCA command and `phase` to the current phase in the continuation section, for session handoff to refresh ignored local `.pactkit/context.md`. This clears its Agent Continuation section because no `--continuation` flag is passed.
2.  **Never Commit Context**: `.pactkit/context.md` is a local cache; do not stage, commit, or amend it.


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

# Done Contract

## Entry
- explicit finalization request for verified work

## Inputs
- fresh verification evidence
- project governance state

## Outputs
- consistent project records
- optional commit

## Invariants
- reuse fresh evidence and disclose every remaining gap
- no engineering-guide selection overrides a verification decision's meaning

## Completion Evidence
- required verification is adequate for the Spec's actor and environment, and current
- status projections agree

## Failure Semantics
- incomplete_continue

## Allowed Next
- none

## External Effects
- commit
- archive

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

# Git Workflow

Use the repository's established commit and branch conventions. Do not push,
create a pull request, tag, publish, or release without current authorization.