# Changelog

## [2.25.1] - 2026-09-01

### Fixed
- **`pactkit gate authorize <scope>` parses as documented** — 2.25.0's parser accepted only the bare positional form (`pactkit gate <scope>`), so the form printed by every block message and the L1 Override Protocol failed with "unrecognized arguments"; both forms now parse (HOTFIX-slim-20260830bbb5bc219d35).
- **Cross-repo commands are judged by the repo they operate on** — `cd <other-repo> && git push` was evaluated against the session cwd's enforcement config; `hook_entry` now resolves the last `cd` target before the git command and evaluates gates against that repository (HOTFIX-slim-20260830bbb5bc219d35).
- **commit-gate no longer misfires on docs/meta-only commits** — three defects that blocked a zero-code design-baseline commit three times and forced test-writing before allowing it (HOTFIX-slim-20260901469666ef23a8): `.gitignore`/`.claude/**`/`.codex/**` are now doc-only (repo/agent metadata carries no runtime code and no longer disqualifies the change set from the skip path); the full-suite target falls back from `tests/unit/` to `tests/` when only a flat layout exists, and a zero-collected run reports "no tests collected" instead of implying failures (still RED — the TDD contract is unchanged); "No module named pytest" from the venv-less fallback interpreter raises `GateUnavailable` → WARN + allow, matching the missing-binary path (R3 self-lock protection).

## [2.25.0] - 2026-08-30

### Added
- **Protected-branch push gate** — `git push` to a protected branch (default `main`/`master`) is intercepted across all three channels (PreToolUse, codex hooks.json, git pre-push) and blocked with an actionable message: the sanctioned path (feature branch + PR), the human bypass (`PACTKIT_ALLOW_DIRECT_PUSH=1` via the `!` prefix), and the repo-owner config (`enforcement.allow_direct_push`). Direct commits on protected branches block by default instead of merely running the full suite; `--no-verify` is no longer a free PreToolUse bypass (the agent can type it; only the env var proves a human channel). Every block and bypass is audited under `push_gate`.
- **Tamper guard** — agent modification of enforcement artifacts is blocked: `.git/hooks/**`, `.pactkit/enforcement/**`, `.codex/hooks.json` fully; `.claude/settings.json` only when the edit removes a gate registration. Bypass: `PACTKIT_ALLOW_CONFIG_EDIT=1` or `enforcement.tamper_guard: false`.
- **L1 Hard-Rule Override Protocol** — core rules now state that L1 rules are never waivable in conversation: a conflicting user instruction is refused (not obeyed), and editing rules/hooks/gate config to comply is itself L1 tampering. Sanctioned channels: do it the sanctioned way, the human runs the command via `!`, or the repo owner changes the config.
- **Stack-aware commit-gate test commands** — the gate runs the detected stack's real suite (`npm test` / `go test ./...` / `mvn|gradle test`) instead of forcing pytest onto Node/Go/Java repos; `pactkit doctor` probes report stack-specific availability. Python keeps the venv-aware pytest path verbatim (monorepos included).
- **Session context hooks** — `pactkit gate --hook session-start` regenerates `.pactkit/context.md` and prints it (SessionStart injects stdout as context; fires post-compaction too), `--hook pre-compact` refreshes state as a side effect and never blocks compaction. Cold-start orientation is deterministic instead of prompt-hoped.
- **Spec tampering guard** — during Act, editing a spec with an active preflight receipt is blocked ("Spec is Law", L1); Plan-phase spec writing is unaffected (no receipt exists yet). Bypass: `PACTKIT_ALLOW_SPEC_EDIT=1` or `pactkit gate authorize spec_edit`.
- **Authorization gate** — external-effect commands (`gh pr create`, `gh release create|delete|upload`, `gh repo create|delete`, `npm`/`pnpm`/`yarn`/`cargo publish`, `twine upload`, `docker push`) block until the user authorizes: ask first, then `pactkit gate authorize <scope>` opens a short-TTL audited window; the strict human channel is `PACTKIT_AUTHORIZED=1` via `!`. Read-only variants never match. Honest threat model: prevents forgetting, not malice — all uses leave records.
- **Secrets gate** — Bash commands containing literal credential material (AWS `AKIA…`, `ghp_`/`github_pat_`, `glpat-`, `xox?-`, `sk-…`, private keys, `password=`/`pwd=`/`passwd=` with a literal value) block by default; env-var indirection (`password=$DB_PASS`) is exempt as the sanctioned pattern. Bypass: `PACTKIT_ALLOW_SECRET=1` or `enforcement.secrets_gate: false`.
- **`pactkit gate` command** — one entry for session hooks and `authorize <scope> [--ttl-minutes N]` (token lives in the tamper-guard-protected `.pactkit/enforcement/`).
- **Gate telemetry** — gate blocks, authorizations, and Skill invocations feed the run-event stream (`gate_blocked` / `authorization_asked` / `authorization_granted` / `command_invoked`) so `pactkit stats` reflects real direct-PDCA usage, not only the workflow engine: per-gate block counts, per-command invocation counts, and the authorization pair at project scope. Telemetry is best-effort and never blocks a gate verdict.
- **`enforcement` config section** — `protected_branches` (default `[main, master]`), `allow_direct_push` (false), `tamper_guard` (true), `spec_guard` (true), `auth_gate` (true), `secrets_gate` (true), `auth_ttl_minutes` (30). Missing/malformed values fall back to safe defaults.

### Fixed
- **Git hooks no longer lock out machines without pactkit** — generated pre-commit/pre-push scripts probe `command -v pactkit` and WARN + allow when the binary is missing (was: exit 127 blocking every commit for teammates/CI in non-Python teams).
- **Audit records no longer persist credentials** — command-derived text is redacted (`[REDACTED:{pattern}]`) before any persistence (enforcement reasons, event details, stderr); `pactkit clean` scrubs legacy records once. Found in the 2026-08-30 fleet inspection: a blocked `PGPASSWORD=…` command had written the literal password into the on-disk audit record.

### Changed
- **Behavior change (intentional)**: direct commits on `main`/`master` that previously "just ran more tests" now block by default — set `enforcement.allow_direct_push: true` (PactKit's own repo does) or use the bypass env var.
- `pactkit stats` output gains a project-scoped `Gate telemetry` section (JSON: `gate_telemetry`).
- Constitution baseline: core protocol word budget 735→900 (L1 Override Protocol + authorize channel).

## [2.24.2] - 2026-08-27

### Fixed
- **`--format all` installs the codex hooks channel** — the default `pactkit update`/`pactkit init` path deploys codex files but 2.24.1 only installed `.codex/hooks.json` for an explicit `--format codex`; "all" now installs both native channels (Claude settings.json + codex hooks.json).

## [2.24.1] - 2026-08-27

### Fixed
- **Enforcement probes resolve the project venv's pytest** — 2.24.0's static probes checked `importlib` in the *current* interpreter, so a pipx-installed CLI (whose venv has no pytest) reported commit-gate and coverage-gate as `unavailable` even though the gates themselves run the project venv's pytest perfectly. Probes now resolve the interpreter the same way the gates do (`pytest_command`).

## [2.24.0] - 2026-08-27

### Added
- **Run event streams (append-only)** — every workflow-state mutation appends a typed event (`step_entered`, `checkpoint_written`, `evidence_invalidated`, `blocker_raised/cleared`, `run_completed`, `run_archived`) beside its checkpoint, written inside the same lock. The checkpoint JSON stays the projection; the event log holds the history the overwrite-style checkpoint cannot. Crash-tolerant: a torn trailing line is skipped and counted, never corrupts earlier lines.
- **`pactkit stats`** — per-run friction metrics (duration, blocker dwell by kind, step rework, authorization decisions) with `--format json` for dashboards; pre-2.24 runs degrade to `events: unavailable` instead of failing. `/project-done` now records a friction snapshot per story. `pactkit continuation events <story>` inspects a run's stream.
- **Gate enforcement completeness reporting** — every gate declares `full / degraded / unavailable` instead of degrading silently through a WARN line: commit-gate and coverage-gate record their observed status, `pactkit doctor --json` exposes an `enforcement` section (plus orphaned specs, config drift, graph provider, deploy parity, codex capabilities), and human doctor output gains per-gate summary lines. Self-lock degradation is now queryable, not silent.
- **Codex native hooks thin registration** — `pactkit init --format codex` merges a PreToolUse→`pactkit commit-gate --hook` entry into the project's `.codex/hooks.json` (Codex's hooks engine is deliberately Claude-wire-compatible: tool_name `Bash`, exit 2 + stderr block — verified against 0.149.1; hooks.json discovery requires ≥0.114.0). User entries are preserved verbatim, unmergeable structures are left byte-identical, `config.toml` is never touched, deployment output carries the one-time trust-confirmation notice, and the git pre-commit fallback stays active until trust is confirmed. `pactkit doctor` probes the local Codex version and reports engine/deployment/trust state.
- **Authorization audit trail** — `authorization_asked`/`authorization_granted` events fire automatically at authorization-blocker transitions (asked carries the sanitized question), and `pactkit continuation deny <story> --reason` records the state machine's first machine-expressible "no": an `authorization_denied` audit event plus a blocked-checkpoint rewrite (`denied: <reason>`), with double-deny and non-authorization denials rejected. `pactkit stats` reports per-run decision counts.
- **outcome_unknown crash recovery** — commit-gate opens an attempt fence (with pid) *before* running; the terminal record closes it. A crash between the two leaves a machine-observable open fence: `resume` blocks with an actionable reason (live pid → "still active, wait"; dead pid → "re-run the gate") — no time-window guessing. Re-running the gate closes the fence and restores normal decisions. Projects without fences behave exactly as before.
- **Command manifest v2 (reference digests)** — the ownership ledger for codex command skills records the sha256 of every deployed reference file (`record_deployed_reference`/`read_command_references`); stale-reference cleanup consumes these proofs, restoring the whole-directory retirement of disabled commands that core's 5311c56 ownership narrowing had inadvertently broken. v1 manifests read compatibly; corrupt manifests degrade to empty proofs.

### Fixed
- **pactkit-codex 2.23.0 ownership regression** (never published) — `skills/*/references/**` files dropped out of the deployed manifest's files table after the ownership narrowing, so stale references could never be retired; the command manifest v2 reference ledger (above) repairs deletion proofs without re-render comparisons (the codex render pipeline depends on deploy-time `enabled_commands`, making content replay structurally unusable as ownership evidence).
- **`pactkit continuation events` path traversal** — story IDs are validated before the event-stream path is built (QA follow-up).
- **hooks.json merge safety** — invalid user structures (`hooks` non-dict, `PreToolUse` non-list) are left byte-identical with an explicit report instead of being rewritten; merges run under a best-effort inter-process lock that proceeds unlocked on timeout (deployment never hangs).
- **Blocker dwell undercount** — consecutive re-raises within one blocker episode no longer restart the dwell measurement; the episode is anchored at its first raise.

### Changed
- **`hook_entry` dual-host normalization** — legacy codex array-form commands are joined before matching, and the payload `cwd` overrides the CLI-resolved project root on both hosts.
- **Golden CLI surface** — pins the new `stats` subcommand, `continuation deny`/`events` actions, and `doctor --json`.

## [2.23.0] - 2026-08-27

### Added
- **Spec preflight + native sessions** — `/project-act` Phase 0.7 deterministically inlines the Spec's referenced implementation inputs and constraints (with receipts) before any source edit; prose basenames resolving to table-declared paths no longer double-add; oversized prose references downgrade to WARN instead of aborting; native session execution restored.
- **Progressive PDCA rule loading** — the 16 on-demand rules load on trigger instead of always; every rule now states its specific trigger and evidence (doctor no longer prints generic "when referenced" boilerplate); the on-demand set is enumerated per-format in pactkit.yaml `rules:`.
- **Unified deployment ownership safety** — the manifest-hash ownership proof (previously rules/guides only) now covers skills, command prompts, agents, CLAUDE.md and rollback: deletions require manifest proof, user-modified files are preserved as `.pactkit-new` candidates, Ctrl-C rolls back atomically, and bare adapter calls fail safe.
- **Machine-checked prompt-to-CLI consistency** — every `pactkit <subcommand>` reference in prompts/ must be a registered CLI subcommand (drift fails CI instead of failing an AI mid-session); mid-story task additions get a governed `add_task` path that reopens a done story.
- **Legacy-engine usage counter** — machine-local counter (`~/.pactkit/legacy-engine-usage.json`) on the three explicit legacy entry points; `pactkit doctor` surfaces the invocation count that gates the frozen legacy package's deletion decision.

### Fixed
- **Gates fail closed** — pip-audit verdicts parsed correctly (vulnerabilities no longer read as pass), word-boundary requirement/test identity matching (R1 no longer satisfied by R10), coverage probe failures and "block" verdicts actually block, commit-gate git-collection failure is an error rather than a doc-only skip, config path arguments no longer silently swallowed.
- **No bricked runs** — a vanished artifact fails with `artifact_vanished` instead of bricking the run forever; corrupt unrelated run files are skipped with a warning while matching runs still fail closed; Windows engine mutations no longer crash on the fcntl import; cross-run story binding serialized.
- **pactkit.yaml multi-copy sync** — syncs from the copy readers actually load (user edits to the loaded copy were silently destroyed on every update) and writes atomically.
- **Superseded-constitution warning** — machines still carrying the pre-slim-112 constitution alongside the Runtime Kernel get an explicit retirement warning instead of two conflicting governance layers silently co-loading.
- **Prompts off the legacy surface** — /project-act and /project-plan no longer instruct agents to invoke the deprecated `continuation`/checkpoint commands (self-inflicted counter noise would keep the legacy deletion gate open forever); handover notes use the maintained `pactkit context --continuation` mechanism.
- **Publish workflow unblocked** — the release test job installs `.[visualize,lint]` instead of `.[all]` (adapter extras are unresolvable before adapters publish — core-first order); five stale test deselects removed after their flakiness was fixed.

### Changed
- **Shared deploy-arg builder + golden-pinned CLI surface** — init/update/upgrade share one argument builder; the full argparse surface is pinned byte-for-byte by a golden help-snapshot test; dead `generators/adapter.py` removed; doctor's project deploy directories derive from FORMAT_PROFILES.

### Removed
- **Preflight guard** (the PreToolUse mutation-enforcement hook): freshness-only
  checking, one-shot binding, and warn-by-default gave it near-zero enforcement
  value while producing hook noise during Act sessions. The Spec preflight
  LOADER (deterministic input inlining + receipts) is kept in full. The
  `pactkit preflight-guard` subcommand and `spec-preflight --activate` are gone;
  Act playbooks updated. (HOTFIX 2026-08-26)

### Deprecated
- Legacy workflow engine (`pactkit workflow` / `work-unit` / explicit `continuation`
  subcommands) moved to the frozen `pactkit.legacy` package — deletion candidate.
  Removal is gated on one release cycle of zero explicit invocations; run
  `pactkit doctor` to see your machine's invocation count. Public import paths
  (`pactkit.workflow_engine`, `pactkit.host_continuation`) keep working via
  compatibility shims. Default PDCA execution paths are unaffected.

All notable changes to PactKit will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [Withdrawn] - 2.21.0 / 2.22.0 - 2026-08-27

- **v2.21.0 and v2.22.0 were withdrawn from PyPI.** Both were published on
  2026-08-24 and deliberately removed shortly afterwards due to serious
  defects: workflow runs could brick mid-flight, gates failed open (including
  an inverted pip-audit verdict), and the preflight guard hook produced noise
  during Act sessions. All of these are fixed in [Unreleased] and will ship in
  2.23.0.
- `pactkit-codex` 2.21.0 was withdrawn alongside. `pactkit-opencode` and
  `pactkit-copilot` never published 2.21/2.22 — all adapter packages remain at
  2.20.0 on PyPI.
- **Guidance:** pin `pactkit==2.20.0` until 2.23.0 is available. Git tags
  v2.21.0/v2.22.0 and their GitHub Releases remain as historical record.

## [2.22.0] - 2026-08-24

### Added
- **Unified WorkUnit scope derivation for non-standard directory layouts** — WorkUnit read/write scope is no longer a hardcoded `src/**`|`tests/**` whitelist. A `resolve_scope` SSoT unions each unit's frozen template floor with project-declared `write_scope` roots (`source_roots`/`test_roots`/`docs_roots`) and the Spec's `Touches`, so projects with `frontend/src/`, `backend/`, `directus-extensions/` layouts no longer block `project-act`/`project-hotfix`. Union (not intersection): the Spec (Tier-1) is never clipped by mutable config. `spec_linter` rejects pathological `Touches` (`**`, absolute, `..`); runtime path-escape stays in `_safe_repo_path`.

### Fixed
- **Completed runs survive legitimate cross-workflow projection evolution** — after Plan → Act, `project-check`/`project-done` start and `pactkit work-unit status <plan-run>` no longer crash with `invalid_workflow_state`. `_completed_run_for_story` scans sibling journals leniently (existence lookups don't re-validate projection fingerprints), and `finalize-workflow` regenerates `context.md` to the post-completion canonical. Execution reads (`_read`) stay strict, so genuine tampering is still detected.

## [2.21.0] - 2026-08-24

### Added
- **Core-owned lifecycle WorkUnits for every project command** — all 12 `project-*` entry points now run through a versioned Core scheduler with bounded leases, deterministic EvidenceReceipts, durable ExecutionAttempts, command-specific validators, and journaled completion. Plan, Act, Check, Done, Sprint, Init, Hotfix, Design, Clarify, Debug, Release, and PR share one completion authority instead of relying on model prose.
- **Official Codex App Server execution bridge** — `pactkit-codex-work-unit` starts and resumes persisted App Server threads, requests schema-constrained results, retries malformed or out-of-scope receipts without losing workflow state, and supports cross-process `thread/resume`.
- **Resumable Codex capability contract** — deployment manifests and `pactkit doctor` now report the verified `resumable` guarantee independently of weaker project-local hosts, while retaining per-host capability details.

### Changed
- **Act completion is Core-governed** — RED must fail, GREEN must pass, regression/lint/coverage must be accepted, and canonical Story tasks plus the Board projection are completed by an idempotent `validated → governance → completed` finalizer with crash recovery and tamper detection.
- **Explicit side-effect authorization** — commit, push, pull request, tag, publish, release, and Sprint orchestration pause as `await_user` before a model turn unless the exact operation was authorized.
- **Distributed IDs** — removed the sequential `next-id` command; `pactkit generate-id` creates time-prefixed, collision-resistant Story, Hotfix, and Bug IDs without a shared counter.

### Fixed
- **Premature Codex termination** — an agent response can no longer mark a workflow complete; only Core's finish guard and journaled finalizer can return `done`. Artifact drift, lease expiry, malformed model output, and process restarts fail closed into a recoverable retry.
- **Cross-host deployment parity** — all managed command facades consume the same lifecycle contract, OpenCode no longer receives Claude-only skill paths, and Sprint has a serialized Plan → Act → Check → Done fallback where native orchestration is unavailable.

## [2.20.0] - 2026-08-22

### Added
- **Verified resumable Act checkpoints** (STORY-slim-146) — PactKit now persists Story-scoped continuation state with validated Spec, Board, test, regression, and lint evidence. `pactkit continuation status/verify/resume/checkpoint` supports safe cross-process recovery, stale-state detection, terminal completion, fresh-cycle archival, secret/path sanitization, and Story-level locking. All 13 runtime skills and the Classic, OpenCode, Codex, and Copilot deployments share the recovery contract.

### Fixed
- **Adapter-safe command rendering and deployment gates** (STORY-slim-145) — operation-aware prompt rendering preserves PactKit CLI semantics across adapters, rejects lossy command transformations, checks generated prompt integrity before writing, and blocks incompatible Core/adapter versions unless skew is explicitly acknowledged.

## [2.19.0] - 2026-08-17

### Added
- **Spec Dependency Surface** (STORY-slim-143) — every scaffolded Spec now carries a machine-readable `## Dependency Surface` table (`Depends on` / `Provides` / `Touches` / `Conflict risk`). Story dependencies and file-level conflict surface are no longer implicit in the architect's head — they're data.
- **`pactkit spec-graph`** (STORY-slim-143) — deterministic story dependency DAG from all Specs: topological **execution waves** (wave N depends only on waves < N; same-wave stories are parallelizable), a **file-overlap conflict matrix** (same-wave overlaps flagged unsafe-parallel), cycle detection with non-zero exit, and Mermaid output to `docs/architecture/graphs/story_graph.mmd`. Stdlib only (`graphlib`, `fnmatch`), zero new dependencies.
- **Spec linter rules E010/W011** (STORY-slim-143) — dangling `Depends on` references (story ID with no Spec file) are now an Act-blocking ERROR; missing Dependency Surface is a WARNING. Reuses spec_linter's section-parsing helpers (newly public: `strip_code_blocks` / `section_text`).
- **Sprint Wave Mode** (STORY-slim-144) — `/project-sprint` with empty arguments scans the backlog, consumes `pactkit spec-graph --json` (new flag), and runs conflict-free same-wave stories as parallel worktree subagents (cap `sprint.max_parallel`, default 3). Stories with same-wave conflicts or undeclared Touches are serialized safe-by-default. Wave gate: wave N+1 starts only after wave N is fully merged green; fail-fast with no auto-retry; resume by re-running (idempotent). Single-story mode with arguments is byte-for-byte unchanged.
- **Plan playbook Dependency Surface step** (STORY-slim-143) — `/project-plan` Phase 3.2a now fills the table from Phase 1 trace findings, so every new Spec ships scheduling data.

## [2.18.0] - 2026-08-17

### Added
- **Deployment manifest content hashes** (STORY-slim-141) — `write_deploy_manifest` now records a per-file sha256 under a `files` field (skills/commands-as-skills/agents/managed rules/guides; merge-semantics files like `CLAUDE.md` and user configs are structurally excluded). `pactkit doctor` deepens the parity check from component-name lists to content level: hash mismatch or missing-on-disk becomes an explicit `Content drift:` report, so "version stamp says new, content is old" deployments can no longer pass silently. Pre-2.18 manifests degrade to a warning; unreadable files and corrupted `files` fields degrade per SEC-7 and never crash doctor. Manifest keys are POSIX-normalized for cross-platform consistency.
- **Adapter version skew warning in doctor** (STORY-slim-142) — doctor now reads adapter package metadata (`pactkit-opencode` etc.) and warns when an installed adapter lags behind core, with a `pipx inject` upgrade hint. The manifest's version field is core-stamped and could never reveal adapter skew.

### Fixed
- **`deploy(format="all", target=...)` no longer deploys adapters** (STORY-slim-142) — adapter deployers cannot honor `-t` and previously always wrote into real home dirs, which let test-suite or preview `init` calls silently overwrite live deployments (root cause of repeated `~/.config/opencode` stale-content incidents). With an explicit target, adapters are skipped with a printed notice; `target=None` behavior is unchanged.

## [2.17.0] - 2026-08-13

### Added
- **`pactkit done-verify`** (STORY-slim-136) — Mechanical archive-honesty gate for `/project-done`. Verifies requirement→test evidence chains, checkbox↔case-file consistency (with code-span stripping), zero-production-caller components (WARN), and Spec/Board/archive status consistency. Any FAIL blocks archiving and commit (exit 1). Wired into project-done Phase 3 as a mandatory step.
- **`pactkit commit-gate`** (STORY-slim-138, STORY-slim-140) — Pre-commit test gate with skip≠pass transparency (passed/failed/skipped reported separately; skips always listed). Two channels sharing one pipeline: Claude Code PreToolUse hook (auto-installed into `.claude/settings.json` by init/update) and git pre-commit (auto-installed for non-Claude formats). Self-lock protection: gate-internal failures always allow with a loud WARN. Direct commits on main/master/develop force the full unit suite.
- **`pactkit deps check/install`** (STORY-slim-137) — External dependency registry (node/codegraph/gh) with platform-aware guided install. `pactkit init` CLI only reports (CI/air-gap safe); `/project-init` Phase 1.5 asks before installing. `enterprise.no_external` refuses installs.
- **`pactkit schema config`** (STORY-slim-135) — Discoverability report for every pactkit.yaml key: default, effective value, and source file.
- **Deployment parity check in `pactkit doctor`** (STORY-slim-139) — Every deploy writes `.pactkit-deployed.json`; doctor compares per-format manifests against the registry and FormatProfile capability matrix, turning silent deployment drift into explicit `Deployed drift:` reports.

### Changed
- **Schema-driven pactkit.yaml** (STORY-slim-135) — `CONFIG_SCHEMA` is now the single source for defaults, validation, deep-merge behavior, and rendering. Fresh `pactkit init` writes a minimal yaml (stack + developer only) instead of a 94-line default wall; absent keys resolve through defaults. Multi-copy sync keeps `.claude`/`.codex`/`.github`/`.opencode` copies identical (canonical = `.claude` first); doctor reports copy drift.
- **Skill deployment single source** (STORY-slim-139) — `SKILL_MANIFEST` + public `get_skill_manifest()` contract; codex/copilot adapters consume it (restoring pactkit-garden/audit/report which a stale hardcoded list had silently dropped), opencode already conformant.
- **Rule map migration** — `COMMAND_RULES_MAP` keys migrated to the merged `pactkit` rule file; inline embedding no longer duplicates globally-loaded constitution content per command.

### Fixed
- **Codex adapter never touches an existing `config.toml`** — after two wipe incidents (custom TOML writer stringified arrays; parse-failure path rewrote managed-only content), the policy is now create-if-absent only. Existing files stay byte-identical.
- **OpenCode global instructions** — the merge logic no longer strips `rules/pactkit.md` from the always-load layer.
- **`install_git_hook` idempotency** — re-running no longer clobbers chained third-party pre-commit hooks.
- **Config copy precedence incident** — canonical selection uses explicit preference order, not key-count heuristics (an inflated default-wall copy could otherwise overwrite hand-curated config).

## [2.16.1] - 2026-07-23

### Fixed
- **Bedrock VS Code plugin model compatibility** (STORY-slim-134) — Removed `model:` field from all `/project-*` command frontmatter. Claude Code was resolving `model: sonnet/opus` to Anthropic's latest model ID (e.g., `us.anthropic.claude-sonnet-4-5-20250929-v1:0`), bypassing `ANTHROPIC_DEFAULT_SONNET_MODEL` env var in VS Code plugin environments. Commands now inherit the session default model set by the user's provider env vars.

## [2.16.0] - 2026-07-13

### Added
- **`/project-debug` command** (STORY-slim-133) — Hypothesis-driven troubleshooting skill. Structured loop: Symptom → Hypothesize (≤3) → Verify (executable commands) → Narrow → Root Cause. Enforces evidence-gated file access (no aimless reading) and convergence guarantees (escalates to `/project-plan` if stuck after 3 iterations). Uses sonnet model with structured protocol.

## [2.15.2] - 2026-07-02

### Changed
- **Codegraph commands decoupled from prompts** (STORY-slim-132) — Replaced hardcoded codegraph CLI command lists with runtime `codegraph --help` discovery. PactKit no longer needs updates when codegraph changes its command signatures.

### Fixed
- **Act Phase 0.6 board move command** (HOTFIX-slim-132) — Added explicit `board.py move_story` command template to prevent AI from guessing wrong subcommand syntax.
- **Prompt deployer** (HOTFIX-slim-131) — Insert @ references after YAML frontmatter so model: field is parsed correctly.
- **Skill frontmatter** (HOTFIX-slim-130) — Move @ references below YAML frontmatter in project-* skills.

### Refactored
- **Prompt rules** — Moved large rules from @inject to on-demand Read to reduce initial context size.

## [2.15.1] - 2026-06-10

### Added
- **Engineering Concerns guide system** (STORY-slim-128) — On-demand NFR guide loading via trigger index. Plan Phase 2 scans requirement keywords and includes NFR decisions in Spec; Act Phase 1.5 loads matched guides (1-3 max). Initial 13 concerns: concurrency, async, configuration, observability, module-design, database, caching, api-integration, event-driven, resilience, memory-management, code-review-first, component-reuse.
- **6 additional engineering guides** (STORY-slim-129) — error-recovery (retry/backoff/idempotency), data-consistency (transactions/saga/optimistic lock), backwards-compatibility (API versioning/non-breaking migration), performance-antipatterns (N+1/unbounded queries/indexing), graceful-shutdown (SIGTERM/drain/cleanup order), testing-strategy (boundary/mock vs real/isolation). Total: 19 guides.

### Fixed
- **Spec linter** — Accept heading format for Security Scope `SEC-*` entries.
- **CI** — Remove obsolete `.opencode/pactkit.yaml` test.

## [2.15.0] - 2026-06-04

### Added
- **`lint` optional dependency group** — `pip install pactkit[lint]` now includes `ruff>=0.4`. The `all` extra also includes `lint`. Users no longer need to install ruff separately for the lint gate to work.
- **External tools documentation** — README and pactkit.dev installation pages now document recommended external tools (gh, codegraph) with install commands and fallback behavior.

### Fixed
- **CI: tree-sitter tests skip when not installed** — `test_story_slim032`, `test_story_slim033`, `test_story_slim034` now use `pytest.importorskip("tree_sitter")` so they skip gracefully in CI environments without the `visualize` extra.

## [2.14.2] - 2026-06-01

### Added
- **Managed-block update for project CLAUDE.md** (STORY-slim-127) — `pactkit update` now uses `<!-- pactkit:start -->` / `<!-- pactkit:end -->` markers. User content outside the managed block is preserved across updates. Supports four migration paths: fresh install, existing markers, legacy PactKit template, and user-modified files.
- **Codegraph sync enforcement via code** (STORY-slim-126) — `pactkit visualize --lazy` and `pactkit sync` now run `codegraph sync` automatically when `.codegraph/` exists. Removed prompt-based instructions that relied on AI compliance.
- **Codegraph priority in generated CLAUDE.md** — When `.codegraph/` exists, the generated project CLAUDE.md includes a "Code Intelligence" section instructing AI to prefer codegraph over grep/find.

### Changed
- **MCP strategy trimmed to Context7 + Memory** — Removed Playwright, Chrome DevTools, Draw.io, and shadcn from MCP rules and recommendations. These remain as conditional no-ops in command prompts but are no longer actively promoted.
- **Config backfill removed** — `pactkit update` no longer backfills default sections into `pactkit.yaml`. Absent keys now mean "accept default", keeping config files minimal.

### Fixed
- **Stale rule warnings** — Removed obsolete rule names from `.opencode/pactkit.yaml` that caused "Unknown rule" warnings on every `pactkit update`.

## [2.14.1] - 2026-05-28

### Fixed
- **Codegraph sync missing from project-done and project-hotfix** (HOTFIX-slim-127) — STORY-slim-124 added `codegraph sync` to project-act but missed project-done (Phase 2) and project-hotfix. Workflows bypassing project-act left the codegraph index stale. Fixed in source templates (`commands.py`, `workflows.py`); next `pactkit init` deploy propagates the fix to all users.

## [2.14.0] - 2026-05-26

### Added
- **Codegraph integration** (STORY-slim-124) — `pactkit query` now reads from `.codegraph/codegraph.db` (generated by `@colbymchenry/codegraph`) when `visualize.graph_provider: codegraph` is configured. Provides 2.6x more edges than pactkit's own suffix-match resolution (6580 vs 2483 in real projects), with qualified names, line numbers, and type-aware resolution.
- **Auto-init codegraph** — When `graph_provider: codegraph` is set and `.codegraph/codegraph.db` is missing, `pactkit query` auto-runs `codegraph init -i` if the CLI is on PATH. Plan/Act phases also auto-setup codegraph when detected.
- **Graph Query Protocol dual-mode** — PDCA commands now support two modes: Codegraph Mode (`pactkit query` + codegraph CLI + MCP tools) and Grep Mode (default fallback on `.mmd` files).

### Removed
- **`_write_sqlite_db()`** — Pactkit no longer generates its own `call_graph.db`. The upstream codegraph tool produces a superior graph with tree-sitter + import-aware resolution.
- **`visualize.sqlite_output` config** — Replaced by `visualize.graph_provider: codegraph`. Existing configs should migrate.

### Changed
- **`pactkit query`** — Now reads `.codegraph/codegraph.db` (codegraph schema with hash IDs, JOIN edges+nodes) instead of pactkit's own `call_graph.db`.
- **PDCA prompts updated** — All references to `call_graph.db` / "SQLite Mode" removed from Plan, Act, Check, Done, Hotfix, and Trace skills. Impact analysis uses `pactkit query --callers` (codegraph) or grep `.mmd` (default).

## [2.13.0] - 2026-05-25

### Added
- **Call graph SQLite output** (STORY-slim-121) — `pactkit visualize --mode call` now optionally writes `call_graph.db` alongside the existing `.mmd` file. Enable via `visualize.sqlite_output: true` in `pactkit.yaml`. Atomic write (tmp+rename), zero new dependencies (`sqlite3` stdlib).
- **`pactkit query` CLI** (STORY-slim-121) — New subcommand for structured call graph queries: `--callers <func>` (fan-in), `--callees <func>` (fan-out), `--chain <func> [--down]` (transitive upstream/downstream via recursive CTE). Reads from `call_graph.db`; exits with helpful message when db is missing.
- **Graph Query Protocol upgrade** (STORY-slim-121) — `SKILL_VISUALIZE_MD` now routes to `pactkit query` as primary path when `call_graph.db` exists, with grep as fallback for mmd-only projects.
- **Enhanced Python call graph coverage** (STORY-slim-119) — `_extract_calls` now captures non-self attribute calls (`engine.run()`), function references in list/tuple/keyword/assign contexts, and nested functions via `ast.walk` + parent map. Edge count on medium-large projects: 1,360 → 3,764 (+177%).
- **Test and script scanning in call graph** (STORY-slim-120) — `visualize --mode call` now scans `tests/`, `scripts/`, and `alembic/` directories in addition to `src/`. Locality-based `_resolve_callee` prefers same-file/same-package candidates when multiple matches exist.
- **`pactkit interface-summary` CLI** (STORY-slim-113) — AST-based interface extraction that physically outputs only signatures, types, and docstrings. Enforces "Code Enforces, Prompt Instructs" for Act Phase 1 layered loading — AI receives truncated content by design.
- **Journey Sync in Act Phase 4** (STORY-slim-114) — Conditional step that updates `docs/e2e/journey.md` when a Story modifies journey-relevant steps. Closes the create→consume→update lifecycle gap.
- **Journey Segment in Plan Phase 3.2a** (STORY-slim-114) — Conditional Spec annotation that links Stories to journey steps, enabling Act Phase 4 auto-detection.

## [2.12.0] - 2026-05-06

### Changed
- **Rules architecture refactor** (STORY-slim-112) — Merged 6 global core rules into single `pactkit.md`; on-demand rules renumbered 01-06 and moved to `~/.claude/skills/_rules/`. Reduces context window usage by ~60% per conversation.
- **Auto-deploy on version mismatch** — After `pipx upgrade pactkit`, the next CLI command auto-syncs deployed files without requiring explicit `pactkit init`.

### Fixed
- **Hardcoded paths in deployer** — `_build_command_rules_header()` now uses `FormatProfile.rules_dir` / `skills_dir` instead of hardcoded `~/.claude/` paths.
- **Stale filename references** — Updated cross-references in visualize.py, commands.py, lazy_visualize.py, and test files to match new rule filenames.

## [2.11.0] - 2026-04-25

### Added
- **Lateral Scan** (STORY-slim-106) — Plan Phase 1 now scans for duplicate patterns before writing Specs. If overlap > 30% with existing implementations, Spec must include `R0: Extract shared abstraction` or declare tech debt accepted. Removed dead hooks code from rules.
- **DEFERRED comment mechanism** (STORY-slim-105) — When skipping a SHOULD requirement, code must include `# DEFERRED(SHOULD): R{N} — reason` comment. Coverage table output added to Check phase for tracking deferred items.

### Fixed
- **Residual pactkit.yaml version operations** (HOTFIX-slim-107) — Removed `update_version()` function and CLI subcommand from board.py, plus all stale references in prompts, agents, and skills docs. Version is now exclusively managed in pyproject.toml + __init__.py with deploy marker at ~/.claude/.pactkit-version.
- **CI tree-sitter deps** — Install tree-sitter optional dependencies in CI workflow to prevent import failures.

## [2.10.6] - 2026-04-22

### Fixed
- **L3 SHOULD semantics** (STORY-slim-104) — Signal Strength Convention L3 Recommended changed from "Violation = warning, non-blocking" to "Default required — skip only with stated reason" (RFC 2119). Added clarification bullet that SHOULD is not optional. Prevents AI from systematically deferring SHOULD tasks.

## [2.10.5] - 2026-04-21

### Added
- **Solution Design Protocol** (STORY-slim-101) — New rule `12-solution-design.md` requires capability delta assessment before implementation. Prevents framework blindness, project blindness, and hardcoded coupling. Includes Implementation Constraints (no magic values, OCP, SRP, dependency direction). Integrated into Plan Phase 1 and Act Phase 1.

### Changed
- **Global version tracking** (STORY-slim-102) — Version tracking moved from project-level `pactkit.yaml` to global `~/.claude/.pactkit-version` marker. Eliminates cross-project desync when PactKit is upgraded. `auto_merge_config_file()` now removes stale `version` field from existing project yamls.

## [2.10.4] - 2026-04-20

### Added
- **Hotfix Impact Check** (STORY-slim-100) — `/project-hotfix` now includes Phase 0.5 that reads existing `.mmd` call graph files before fixing. Warns when target function has 3+ callers. Advisory (L3), non-blocking, gracefully skips when no graphs exist.

## [2.10.3] - 2026-04-20

### Fixed
- **Protected parent dirs in `pactkit clean`** — `rglob("dist")` was matching `node_modules/*/dist`, destroying npm dependency internals. Added `_inside_protected()` guard for `node_modules/` and `.git/`; explicit path patterns (e.g., `node_modules/.cache`) now use direct matching instead of rglob.

## [2.10.2] - 2026-04-20

### Added
- **PDCA Nudge Protocol** (STORY-slim-098) — AI proactively recommends PDCA commands when free conversation yields actionable conclusions. Trigger matrix maps signals to commands; suppression rules prevent noise.

### Fixed
- **Shared Protocols Context.md reference** (STORY-slim-099) — Added missing `Act Phase 4` to the Context.md Canonical Format "Referenced by" line. Ensures context.md reflects Act progress for session continuity.
- **Semantic version comparison** (HOTFIX-slim-099) — Version mismatch warning now uses tuple comparison instead of string equality, giving correct upgrade/downgrade direction.

## [2.10.1] - 2026-04-16

### Added
- **Dual-dimension Harness Audit** (STORY-slim-097) — Audit now scores two dimensions: Config (project + global `~/.claude/` config, 50pts) and Code (tests, lint, complexity, git hygiene, 50pts). Score went from 52 to 97/100 for PactKit itself. JSON output includes `dimensions` breakdown field.
- **Unified HTML Report Dashboard** (STORY-slim-094) — Single `report.html` with tab switching, D3 force-directed graph, harness score ring, layer bars, and hotspot panel. Self-contained offline HTML with inline D3.js.

### Fixed
- **Focus call graph empty output** (STORY-slim-095) — Fixed focus resolution to use `LANG_PROFILES[stack].source_dirs` instead of hardcoded `src/` prefix. Added subdirectory and single-root-module fallback.
- **Report --all tab overload** (HOTFIX-slim-096) — Filtered unified dashboard to core PDCA graphs only (code_graph, class_graph, call_graph, system_design). Reduced from 9 tabs to 4.
- **Mermaid `<br/>` tag rendering** (HOTFIX-slim-096) — Strip Mermaid `<br/>` tags from node labels before HTML escape, preventing `&lt;br/&gt;` raw text in SVG.

## [2.9.13] - 2026-04-15

### Fixed
- **Slim core dependencies** (STORY-slim-088) — Moved adapter packages (`pactkit-opencode`, `pactkit-codex`) and tree-sitter bindings to `[project.optional-dependencies]`. Core `pip install pactkit` now only requires `pyyaml`. Install extras with `pip install pactkit[all]`, `pactkit[visualize]`, `pactkit[opencode]`, or `pactkit[codex]`.
- **Spec-lint CLI fallback** (STORY-slim-088) — Playbooks now include `python3 -m pactkit spec-lint` fallback for environments where `pactkit` is not on `$PATH`, preventing P.A.C.T. violation (AI "manual lint" replacing deterministic code validation).
- **Board add_story signature** (STORY-slim-088) — Plan playbook Phase 3.3 now shows complete `add_story` invocation with required ID, title, and tasks arguments.

## [2.9.12] - 2026-04-01

### Added
- **Copilot deployer adapter** (STORY-slim-083) — `pactkit-copilot` adapter package registered via entry_points. `pactkit update --format copilot` deploys skills, commands, agents, and `copilot-instructions.md` to `.github/`.
- **OCP-compliant rules header dispatch** (STORY-slim-083 R6) — `_build_command_rules_header()` dispatches on `profile.rules_import_style` (`@import`/`inline`/`instructions`) instead of hardcoded profile name checks. New adapters get correct rule injection automatically.
- **Multi-stack auto-detection** (STORY-slim-080) — `pactkit init` auto-detects multiple stacks and writes `stack: [python, typescript]` list syntax to `pactkit.yaml`. `pactkit visualize` supports stack list.
- **Two-tier module graph** (STORY-slim-081) — `visualize --mode module` generates dimension-based subgraphs (Code/PDCA/Service/Frontend Topology).
- **Prompt template sync** (STORY-slim-082) — Canonical prompt templates rendered consistently across all deployer formats.

### Fixed
- **OpenCode `rules_import_style`** — Corrected from `"instructions"` to `"inline"` to match actual behavior (commands inline rule content).

## [2.9.11] - 2026-04-01

### Fixed
- **Rules template variables** — `_deploy_rules()` now renders `{PROJECT_CONFIG_DIR}` and other template variables via `_render_prompt()`. Previously rules were deployed with raw template strings, causing unresolved `{PROJECT_CONFIG_DIR}` in Codex/OpenCode deployments.

## [2.9.10] - 2026-04-01

### Fixed
- **Skill script `__future__` import** — `load_script()` now hoists `from __future__ import annotations` above `_SHARED_HEADER`, fixing SyntaxError in deployed `spec_linter.py`. Added `# === SCRIPT BODY ===` marker to `spec_linter.py`.
- **Lessons table auto-repair** — `append_lesson()` now calls `_repair_table_structure()` before appending, fixing: missing header, wrong header format, data rows before header, stray text in table area.

## [2.9.9] - 2026-04-01

### Added
- **GitHub Copilot adapter support** — New `copilot` FormatProfile in `profiles.py`. `pactkit init --format copilot` deploys to project `.github/` directory.
- **Dynamic `--format` CLI choices** — `init`, `update`, `upgrade` commands now derive `--format` choices from `VALID_FORMATS` instead of hardcoded list. Adding a new format profile auto-exposes it in CLI.

### Fixed
- **Excluded command stripping** — `strip_excluded_command_references()` in `DeployerBase` now strips `/project-sprint` references from all rendered prompts for formats that exclude it (Copilot, Codex, OpenCode).

## [2.9.4] - 2026-03-31

### Fixed
- **Init playbook DIP violation** (STORY-slim-074) — Eliminated `DETECTED_ENV` runtime IDE detection; all hardcoded paths replaced with template variables (`{FORMAT_NAME}`, `{PROJECT_CONFIG_DIR}`, etc.). Adding a new IDE format now requires zero playbook changes.
- **Full DIP audit** — Fixed hardcoded IDE paths in doctor skill, core-protocol rule, and done command.
- **tree-sitter promoted to core dependency** — No longer optional; CI install updated to include `tree-sitter-go`, `tree-sitter-java`, `tree-sitter-typescript`.
- **`--focus` scan optimization** — `_scan_files` now scans only the focused subdirectory, not the full project root. `pactkit visualize --focus` without `--mode` now correctly passes focus through.
- **SCAN_EXCLUDES expanded** — From 13 to 30+ entries covering Go (`vendor`), Java (`target`, `.gradle`, `.mvn`), Node (`.next`, `.nuxt`, `.turbo`), IDE (`.idea`, `.vscode`), VCS (`.svn`, `.hg`), and more.
- **Codex pactkit.yaml candidates** — 3 functions in `visualize.py` now include `.codex/pactkit.yaml` in search paths.
- **Topology markers** — `_TOPOLOGY_MARKERS` and `PdcaParser.markers` now include all 3 IDE format directories.

## [2.9.3] - 2026-03-31

### Added
- **Multi-language call chain fix** (STORY-slim-069) — Dispatch hint comment parsing (`pactkit-trace: dispatches_to`) and inheritance edge linking extended from Python-only to Go (struct embedding), Java (extends/implements), and TypeScript (class extends) tree-sitter analyzers.
- **CLI visualize args exposed** (HOTFIX-slim-070) — `--entry`, `--focus`, `--reverse`, `--depth`, `--max-nodes` now reachable from `pactkit visualize` CLI.

### Fixed
- **4 call chain断链** (STORY-slim-068) — dict.update scan collision, dynamic dispatch hints, abstract method orphan nodes, cross-package stub edges.
- **CI install command** — Fallback from `.[multilang]` to `.[dev]` in generated pactkit.yml.

## [2.9.2] - 2026-03-30

### Fixed
- **FormatProfile.excluded_commands** — `project-sprint` excluded for OpenCode/Codex (requires subagent team, Claude Code only). Doctor `check_config_drift` now respects format-level exclusions.
- **Redundant pactkit.yaml component lists** — Removed explicit agents/commands/skills/rules lists from `.opencode/pactkit.yaml` (absence = deploy all).
- **Orphaned spec cleanup** — Removed 7 pre-developer-prefix spec files that were already archived under old IDs.

## [2.9.1] - 2026-03-30

### Added
- **Topology-aware trace** (STORY-slim-066) — ApiCallParser (tree-sitter-typescript) and AgentParser (LangGraph/YAML/MCP) for multi-topology code tracing. Plan/Act phases now include topology gate.

### Fixed
- **Monorepo subdirectory detection** — TopologyParser.detect() now scans immediate subdirectories, fixing false negatives for monorepo layouts (e.g., `web/package.json`).
- **Doctor false drift warnings** — `check_config_drift()` now searches global deploy directories (`~/.claude/`, `~/.config/opencode/`, `~/.codex/`) instead of only project-local paths.
- **Canonical lessons.md header** — Init Phase 5 now enforces `| Date | Lesson | Context |` table header, preventing AI-invented column names like `| Source |`.

## [2.9.0] - 2026-03-28

### Added
- **`pactkit init` deploys all IDEs by default** — `--format all` is now the CLI default, deploying Claude Code + OpenCode + Codex configs in one shot. No need to specify `--format` per IDE. Packaging modes (plugin, marketplace) excluded from "all".

### Fixed
- **Entry_point deployer circular import** — Lazy-load entry_point deployers to fix `ValueError` when running `pactkit init` via pipx. Module-level `ep.load()` caused circular import between deployer.py and adapter packages.

## [2.8.0] - 2026-03-27

### Added
- **3-IDE default install** — `pip install pactkit` now installs all three IDE adapters (Claude Code + OpenCode + Codex) out of the box.

### Fixed
- **OpenCode command architecture** — Reverted OpenCode from skills-only back to `commands/` + `skills/` dual architecture. OpenCode auto-discovers commands from `commands/*.md` (invoked via `/project-plan`), while embedded skills in `skills/` are loaded by AI agent on demand. `opencode.json` command entries now only contain model routing (no `template` field — it was incorrectly treated as file path, but is actually inline text).
- **Spec version confusion** — `/project-plan` Phase 3.2a no longer reads version from `pactkit.yaml` (PactKit toolkit version). Now explicitly reads from project's package manifest (`pyproject.toml`, `package.json`, `Cargo.toml`).
- **OpenCode path isolation** — All deployed OpenCode files reference `~/.config/opencode/` paths, CLI commands replaced with `python3 ~/.config/opencode/skills/*/scripts/*.py` invocations.
- **pactkit.yaml simplification** — Removed redundant component lists (agents/commands/skills/rules) from yaml template. Absence = deploy all from `VALID_*` sets. `pactkit doctor` drift check skips absent keys.

### Changed
- **Cross-IDE command architecture**:
  - Claude Code: skills-only (`skills/project-*/SKILL.md`), prefix `/`
  - OpenCode: commands + skills (`commands/project-*.md` + `skills/pactkit-*/SKILL.md`), prefix `/`
  - Codex: skills-only (`skills/project-*/SKILL.md`), prefix `$`

## [2.7.0] - 2026-03-27

### Added
- **Commands → Skills Migration** (STORY-slim-063) — 11 PDCA commands now deploy as `skills/{name}/SKILL.md` subdirectories instead of flat `commands/{name}.md` files for Claude Code format. `VALID_SKILLS` expanded from 10 to 21 entries (10 embedded + 11 commands).
- **Legacy Command Cleanup** — `_cleanup_legacy_commands()` auto-removes old `project-*.md` from `commands/` on upgrade, preserving non-PactKit files.
- **Codex FormatProfile** (STORY-slim-060) — Re-added `codex` profile to core for thin adapter pattern support (`pactkit-codex` package).

### Fixed
- **board.py update_task** (HOTFIX-slim-061) — `update_task` now recognizes bullet-format Done entries (`- **STORY-xxx**:`), not just heading format.
- **visualize --lazy focus** (HOTFIX-slim-062) — Removed hardcoded `--focus cli` refresh; added stem matching for focus target resolution.

### Changed
- **Deploy summary** — Output now shows unified `Skills (embedded + commands)` count instead of separate Commands/Skills lines.
- **Cross-format isolation** — OpenCode and Codex profiles unaffected; commands still deploy as flat `.md` files for non-classic formats.

## [2.6.1] - 2026-03-26

### Fixed
- **OpenCode backward compatibility** — `pactkit-opencode` added as core dependency so `pip install pactkit` automatically includes OpenCode deployment support. Users upgrading from 2.5.0 no longer lose `--format opencode`.
- **Version sync** — `pactkit-opencode` version aligned to 2.6.0 to match core versioning.

## [2.6.0] - 2026-03-26

### Added
- **DeployerProtocol & DeployerBase** (STORY-slim-057) — Extracted deployer interface (`typing.Protocol`) and shared base class with registry pattern (`register_deployer()`, `get_deployer()`), enabling adapter-based plugin architecture.
- **pactkit-opencode Adapter Package** (STORY-slim-058) — Extracted all 8 OpenCode-specific functions into standalone `pactkit-opencode` package with `entry_points`-based auto-registration. `pip install pactkit-opencode` activates OpenCode format automatically.
- **Entry Point Auto-Discovery** — `_load_entry_point_deployers()` scans `pactkit.deployers` entry_point group at import time for zero-config adapter registration.

### Removed
- **Codex Profile** (STORY-slim-059) — Removed dead `codex` FormatProfile, YAML candidates, and all codex references from source. VALID_FORMATS auto-shrinks via `FORMAT_PROFILES.keys()`.
- **OpenCode Functions from Core** — 8 OpenCode-specific functions (~300 lines) moved to `pactkit-opencode` adapter. `deployer.py` reduced from 1754 to 1448 lines (-17%).

### Changed
- **deployer.py Dispatch** — `deploy()` now dispatches via `_DEPLOYER_REGISTRY` instead of if/elif chain. New formats only need to call `register_deployer()`.
- **Architecture Principles** — Updated rule templates to reflect adapter pattern (class-based deployers, no codex references).

## [2.5.0] - 2026-03-26

### Added
- **E2E CLI Coverage 100%** (STORY-slim-056) — 60 subprocess-based E2E tests covering all 25 CLI subcommands, including parametrized `--help` consistency check, error path validation, and Unicode project path support.
- **`__main__.py`** — `python -m pactkit` now works as an alternative to the `pactkit` entry point.

### Fixed
- **Mermaid Quote Injection** (STORY-slim-053 R1) — File/function names containing `"` no longer break `.mmd` graph rendering; escaped via `#quot;` HTML entity at 4 label sites.
- **O(N×E) Callee Resolution** (STORY-slim-053 R2) — `_resolve_callee()` now uses a pre-built `suffix_index` dict for O(1) lookup instead of linear scan.
- **Module Index Collision** (STORY-slim-053 R3) — `module_index` changed from `dict[str, Path]` to `dict[str, list[Path]]` with `_best_match()` same-package preference, fixing silent node loss for same-name files in different directories.
- **Focus Substring False Positives** (STORY-slim-053 R4) — `--focus auth.py` no longer matches `oauth.py`; changed to exact path-tail matching with `_extract_node_id()` set lookup.
- **BFS O(N²) Pop** (STORY-slim-053 R5) — All 4 BFS sites now use `collections.deque.popleft()` instead of `list.pop(0)`.
- **`_rewrite_yaml` Non-Atomic Write** (STORY-slim-054 R1) — `config.py` now uses tmp+rename pattern, preventing `pactkit.yaml` corruption on crash/disk-full.
- **`_deploy_ci` Dict Mutation** (STORY-slim-054 R2) — Changed `.pop("_ghe_override")` to `.get()`, preventing caller dict mutation across multi-call scenarios.
- **`atomic_write` .tmp Residual** (STORY-slim-054 R3) — Added try/except cleanup so `.tmp` files are removed on `os.replace()` failure.
- **Visualize Non-Atomic .mmd Writes** (STORY-slim-055 R1) — All 4 `.mmd` output sites now use `_atomic_mmd_write()` (tmp+rename).
- **Deployer Bare `read_text()`** (STORY-slim-055 R2) — 3 sites in `deployer.py` now specify `encoding='utf-8'` for Windows compatibility.
- **Large File OOM** (STORY-slim-055 R3) — Added `MAX_FILE_BYTES=1MB` guard to `PythonAnalyzer` and `_build_class_graph()`, skipping auto-generated mega-files.
- **Sprint Redundant Operations** (STORY-slim-050) — Eliminated duplicate visualize/clean/context runs in sprint orchestration.
- **Skill Script Robustness** (STORY-slim-051, 052) — Hardened board.py, scaffold.py, spec_linter.py, visualize.py with encoding, error handling, and call-chain fixes.

## [2.4.1] - 2026-03-26

### Fixed
- **CI Template Override** (HOTFIX-slim-051) — `_build_github_workflow()` now reads `ci.install_cmd` from `pactkit.yaml` before falling back to `CI_PROFILES` default, preventing `pactkit update` from reverting custom install commands.
- **Board ITEM_ID_RE** (HOTFIX-slim-052) — Regex now supports developer-prefixed IDs (`HOTFIX-slim-052`, `STORY-alice-001`), matching the pattern already used by `backfill.py` and `doctor.py`.

### Added
- **Board `move_story` Command** (HOTFIX-slim-052) — New `board.py move_story <ID> <target>` CLI subcommand moves stories between Backlog/In Progress/Done sections regardless of checkbox state.
- **Automated PyPI Publish** — New `publish.yml` GitHub Actions workflow triggers on `v*` tags; runs full test matrix (Python 3.10-3.13) then publishes via PyPI trusted publisher (OIDC).

### Changed
- **Closed-Source Migration** — Source repo moved to `pactkit/pactkit-src` (private); public entry point at `pactkit/pactkit-public` (README, issues, install guide). PyPI distribution unchanged.

## [2.4.0] - 2026-03-25

### Added
- **Multi-Architecture Topology System** (STORY-slim-039~048) — 10 stories implementing a complete topology analysis framework:
  - **TopologyParser ABC** — Abstract base class with `detect()` + `parse()` and zero-config auto-detection via `_TOPOLOGY_MARKERS`
  - **PdcaParser** — Refactored Epic 1 logic into TopologyParser; added PDCA sequence edges (Plan→Act→Check→Done dashed arrows)
  - **ServiceParser** — Parses `docker-compose.yml`, `openapi.yaml`, `*.proto`; extracts service→api→service dependency graph with MQ topic support
  - **FrontendParser** — Parses Next.js (App/Pages Router), Vue Router routes; extracts page→component→hook→store dependency chain
  - **Cross-topology Impact** — `reverse_reach()` works across all topologies; `regression_workflow_impact()` detects service/hook/store changes
  - **Unified Layered Graph** — `build_unified_graph()` merges code + topology dimensions with bridge edges; `to_mermaid()` renders dimension-based subgraphs
  - **MAX_WORKFLOW_NODES=500** — Performance ceiling for unified graph node count

### Fixed
- **detect_topology() DRY fix** — Now delegates to parser's own `detect()` method first, falling back to `_TOPOLOGY_MARKERS` for unregistered topologies only. Fixes empty workflow graph on pactkit's own project.
- **pyproject.toml metadata** — Moved `authors/keywords/classifiers` from `[project.optional-dependencies]` back to `[project]` (caused CI hatchling validation failure)
- **CI multilang deps** — Both CI workflows now install `[multilang]` extras for tree-sitter test coverage
- **Spec/PRD consistency** (HOTFIX-slim-049) — Fixed 040 AC1 wording, 042 markers, PRD database/reads_db removal, PRD roadmap checkboxes

## [2.3.6] - 2026-03-24

### Fixed
- **Issue Sync Substring Matching** (STORY-slim-027 R1) — `issue_sync.py` now uses word-boundary regex instead of `in` substring check, preventing `STORY-1` from matching `STORY-10`.
- **E007 Per-Subsection GWT Check** (R3) — Spec linter E007 now validates Given/When/Then keywords per AC subsection instead of flat-scanning the entire Acceptance Criteria section. Uses raw text (with code fences) to avoid false positives on specs wrapping Gherkin in ` ```gherkin ` blocks.
- **W008 Scaffold Placeholder Detection** (R4) — New warning W008 fires when `## Background` or `## Target Call Chain` still contains default scaffold placeholder text.
- **Schema-Linter Alignment** (R2/R10) — `## Security Scope` moved from OPTIONAL to REQUIRED in `schemas.py` to match E009 enforcement; `## Non-Goals` added to OPTIONAL.
- **RFC Pattern Consistency** (R11) — Spec linter fallback RFC pattern now derived from `SPEC_RFC_KEYWORDS` tuple instead of a separate hardcoded regex.
- **Scaffold Skill Path** (R8) — `scaffold.py` usage hint now uses resolved `root` path instead of hardcoded `~/.claude/skills/`.

### Changed
- **Design Prompt** (R5) — Phase 3 now includes `pactkit sec-scope` step after filling each Spec.
- **Act Prompt** (R6/R7) — Phase 0.6 adds "Move to In Progress" board step; Phase 3 adds lint gate before regression.

## [2.3.5] - 2026-03-23

### Fixed
- **W007 RFC 2119 Detection** — W007 now detects all RFC 2119 keywords (MUST, SHOULD, MAY, SHALL, REQUIRED, RECOMMENDED, OPTIONAL) using canonical `SPEC_RFC_KEYWORDS` from schemas.py, instead of hardcoding only SHOULD.

## [2.3.4] - 2026-03-23

### Added
- **Spec Lint W007 — Req-AC Coverage** (STORY-slim-024) — New warning rule fires when `### R{N}:` requirements are not referenced by any `### AC{M}:` body. Helps catch SHOULD requirements that get overlooked. Message includes `(SHOULD)` indicator for unreferenced SHOULD requirements.

### Fixed
- **E2E Config Fields** — `api_spec` and `compose_file` now included in `generate_default_yaml()` output (were commented out, breaking roundtrip tests).
- **Test Fixtures** — Updated test fixtures to include `e2e` section after HOTFIX-slim-025 added new fields.

## [2.3.3] - 2026-03-23

### Added
- **Auto Version Sync** (STORY-slim-023) — `pactkit update --if-needed` compares `pactkit.yaml` version vs installed `__version__`. If match, skips redeploy; if mismatch, proceeds with full deploy. Core Protocol prompt updated to run this at session start for zero-friction upgrades.

### Fixed
- **Guard Version Mismatch Detection** (HOTFIX-slim-024) — `pactkit guard` now checks version mismatch and prints warning with suggestion to run `pactkit update`. Also adds `e2e` to `_BACKFILL_KEYS` so new config section is auto-added during update.

## [2.3.2] - 2026-03-23

### Added
- **E2E Testing Framework** (STORY-slim-022) — Config-driven E2E strategy in `pactkit.yaml` (`e2e.type`: none/cli/frontend/backend/fullstack). `/project-check` Phase 4 rewritten from hardcoded Strategy A/B to config-driven table. `env_file` field (default `.env.test`) for test credential isolation. Non-blocking by default (`e2e.blocking: false`).

### Fixed
- **Visualize CLI --mode** (HOTFIX-slim-023) — `pactkit visualize --mode class/call` previously failed with "unrecognized arguments". Added `--mode` parameter and wired non-lazy mode to execute graphs directly.
- **Board Archive Section Headers** (HOTFIX-slim-021) — `archive_stories()` now preserves `## 🔄 In Progress` and `## ✅ Done` section headers when archiving removes all stories from a section.

## [2.3.1] - 2026-03-23

### Fixed
- **Plan Phase 3.2 Stall** (STORY-slim-019) — Split monolithic Spec-writing phase into 4 sub-steps (3.2a Skeleton, 3.2b Acceptance Criteria, 3.2c Security Scope, 3.2d Spec Lint) with output checkpoints between each, eliminating AI buffering stall on large Spec generation.
- **Explore Subagent Stall** (STORY-slim-020) — Added Bounded Delegation template to Plan Phase 1 (target/scope/limit/output constraints for Explore subagents), reduced `code-explorer` maxTurns from 50 to 15, and added scope-limiting instructions to prevent unbounded codebase exploration.
- **CI Workflow** — Reverted `actions/checkout` and `actions/setup-python` from v6 back to v4/v5 for CI stability after Dependabot upgrades caused failures.

## [2.3.0] - 2026-03-22

### Added
- **Deterministic CLI Subcommands** (STORY-slim-014) — Migrated 7 Done-phase operations from prompt-delegated to Python CLI: `clean`, `regression`, `context`, `sec-scope`, `guard`, `next-id`, `visualize --lazy`.
- **Doctor, Backfill-Release, Issue-Sync CLI** (STORY-slim-015) — `pactkit doctor` diagnoses project health (HLD drift, board structure, config completeness). `pactkit backfill-release` replaces `Release: TBD` in completed specs. `pactkit issue-sync` handles GitHub issue lifecycle for BUG/HOTFIX items.
- **Test-Map and Lint CLI** (STORY-slim-016) — `pactkit test-map` maps changed source files to test files via `LANG_PROFILES.test_map_pattern`. `pactkit lint` runs stack-aware lint with auto-fix and blocking modes from `pactkit.yaml`.
- **Lesson-Append, Invariants-Refresh, Coverage-Gate CLI** (STORY-slim-017) — `pactkit lesson-append` checks specificity (file/function reference) and dedup (Jaccard < 0.5) before appending. `pactkit invariants-refresh` updates test count invariant. `pactkit coverage-gate` enforces 3-tier coverage thresholds (80/50/block).
- **Systemic Cross-Flow Guards** (STORY-slim-018) — 4 guard test suites: R1 prompt-CLI cross-reference validation, R2 canonical `LANG_PROFILE_REQUIRED_KEYS` SSoT in `schemas.py`, R3 Spec Status lifecycle (`spec-status` CLI + W006 lint rule), R4 declarative cross-flow coverage matrix (12 subcommands × prompt keys).
- **Spec Status CLI** — `pactkit spec-status <spec> <status>` programmatically updates `| Status |` field in spec files. W006 lint rule flags invalid status values.

### Fixed
- **Cross-Flow Integrity** (BUG-slim-003 through BUG-slim-006) — 4 rounds of systematic audits fixed 25+ gaps: dead CLI subcommands with zero prompt references, argparser flags without `deploy()` parity, `visualize --lazy` not calling actual function, double `python3` prefix in HOTFIX_PROMPT, unused LANG_PROFILES keys removed.
- **SSoT Violations** — `backfill.py` imports `BOARD_SECTION_DONE` from schemas (was hardcoded regex). `lessons.py` uses `LESSONS_ROW_FORMAT` from schemas. 5 test files import `LANG_PROFILE_REQUIRED_KEYS` instead of hardcoding key sets.
- **Prompt Cognitive Overload** (STORY-slim-013) — Reduced redundancy across PDCA command prompts.
- **Rules-Commands Collision** (BUG-slim-002) — Resolved instruction conflicts between rules and command playbooks.
- **Draw Skill Stuck** — Added concrete templates to `pactkit-draw` to prevent empty-output behavior.

### Changed
- `SPEC_VALID_STATUSES` and `LANG_PROFILE_REQUIRED_KEYS` canonicalized in `schemas.py` as single source of truth.
- Sprint board required sections enforced: `## 📋 Backlog`, `## 🔄 In Progress`, `## ✅ Done`.
- BUG-017/BUG-029 spec Status fields corrected to valid values per `SPEC_VALID_STATUSES`.

## [2.2.0] - 2026-03-20

### Added
- **Context-Aware Rule Loading** (STORY-slim-011) — `COMMAND_RULES_MAP` maps each of 11 commands to only the rules it needs, reducing per-command token usage by 20-83%. Classic format uses `@import` injection; OpenCode format embeds rule content inline. Credential safety rule (`09`) is force-injected into every command regardless of configuration.
- **Stack-Aware CI Pipeline Generation** (STORY-slim-012) — `CI_PROFILES` in `workflows.py` supports Python, Node.js, Go, and Java stacks with correct setup actions, install commands, and test runners. New `pactkit.yaml` CI config fields: `runner`, `language_version`, `github_host`, `actions_ref`.
- **GitHub Enterprise (GHE) Support** — Explicit `ci.github_host` configuration for GHE Server environments, with `ci.actions_ref` prefix replacement for custom action mirrors. Auto-detection fallback via `_detect_ghe()`.
- **OpenCode CI Parity** — `_deploy_opencode()` now calls `_deploy_ci()`, ensuring CI pipeline files are generated regardless of deployment format.
- **CI Status Feedback** — `/project-done` Phase 4 now includes optional CI status check via `gh run list` after push (non-blocking).
- **GitLab CI Stack-Aware** — GitLab CI templates now use correct Docker images and commands per stack (e.g., `node:20` + `npm ci` for Node projects).

### Changed
- `_deploy_ci()` refactored from hardcoded Python-only templates to parameterized builders (`_build_github_workflow()`, `_build_gitlab_ci()`).
- `generate_default_yaml()` now outputs commented CI configuration fields (`runner`, `language_version`, `github_host`, `actions_ref`) for user discoverability.
- CLAUDE.md no longer contains global rule `@import` directives — rules are now injected at command level.
- OpenCode `opencode.json` instructions reduced to only `09-credential-safety.md` — other rules injected per-command.

## [2.1.1] - 2026-03-18

### Added
- **Lazy Rule Loading** (STORY-slim-009) — Rules split into always-load core (`01-core-protocol`, `02-hierarchy-of-truth`, `09-credential-safety`) and on-demand `@reference` layer (6 files loaded by AI via Read tool when needed). Reduces per-turn system prompt overhead by 62% (7200 → 2800 tokens).
- `RULES_CORE_FILES`, `RULES_ONDEMAND_FILES`, `RULES_INSTRUCTIONS_CORE` constants in `rules.py` for layered rule management.
- AGENTS.md now contains `@rules/xxx.md` reference index with lazy-loading instructions — mirrors Claude Code's `@import` behavior in OpenCode's architecture.

### Changed
- `_update_global_opencode_json()` writes individual core rule paths instead of `rules/*.md` glob. Preserves user's existing instructions via merge strategy.
- `_deploy_agents_md_inline()` generates on-demand `@reference` index from `RULES_ONDEMAND_FILES`.

### Fixed
- `_update_global_opencode_json()` no longer overwrites user's existing `instructions` entries (merge instead of replace).

## [2.1.0] - 2026-03-17

### Added
- **FormatProfile Abstraction** (STORY-slim-005) — Frozen dataclass registry (`profiles.py`) replaces scattered if-else format branching. Adding a new tool format requires only one registry entry. `VALID_FORMATS` and `PACTKIT_YAML_CANDIDATES` auto-generated from `FORMAT_PROFILES`.
- **Prompt Template Variables** (STORY-slim-006) — 48 hardcoded env-specific paths replaced with 11 named placeholders (`{SKILLS_ROOT}`, `{BOARD_CMD}`, `{PACTKIT_YAML}`, etc.) resolved at deploy time by `_render_prompt(template, profile)`.
- **Document Schema Registry** (STORY-slim-007) — New `schemas.py` centralizes all document structure rules (Spec sections, Board headers, context.md sections, lessons.md format). New CLI command `pactkit schema [type]` for rule discovery.
- **Deploy Chain Parity** (STORY-slim-008) — `_deploy_opencode()` now reads `pactkit.yaml` for selective deployment, calls `auto_merge_config_file()`, `_cleanup_legacy()`, generates project-level `AGENTS.md`, prints MCP recommendations. `_generate_config_if_missing(format=)` is format-aware.
- **Architecture Principles Rule** — New `08-architecture-principles.md` codifies 8 principles (SOLID, DRY, 12-Factor, Defense-in-Depth) derived from project practice. `CLAUDE_MD_TEMPLATE` auto-generated from `RULES_FILES`.
- **Codex CLI Pre-Research** (STORY-slim-001) — Tool integration checklist (11 dimensions, 60+ checks) and Codex capability matrix completed. Integration specs (STORY-slim-002/003/004) ready.
- **Daily Retro Skill** — Personal growth feedback loop with 6 dimensions (engineering, architecture, new skills, thinking patterns, process, career). Triggered by cross-day context.md detection.
- **Docker Containers** — Isolated `claude-code` and `opencode` containers for clean deployment verification.

### Fixed
- **BUG-slim-001**: `/project-init` no longer creates `.claude/` directory in OpenCode environment. Environment detection moved before `pactkit init` call. Playbook paths now use `$SKILLS_PATH` variable.
- **Config Priority**: `.opencode/` now takes precedence over `.claude/` in `pactkit.yaml` resolution (newer environment preferred).
- **Scaffold Developer Prefix**: `create_spec`, `git_start`, `create_e2e` auto-inject developer prefix from `pactkit.yaml`.

### Changed
- `opencode_format` boolean parameter removed from `_deploy_agents()`, `_deploy_commands()`, `_deploy_skills()` — replaced by `profile: FormatProfile`.
- `OPENCODE_SKILLS_PREFIX` constant removed — use `get_profile("opencode").skills_path_var`.
- `CLAUDE_ONLY_FIELDS` hardcoded set replaced by `profile.excluded_agent_fields` (extensible per format).
- `TRACE_PROMPT` converted from f-string to regular string for template variable compatibility.
- Spec scaffold template now uses `TBD` as Release placeholder (enforced by spec-lint E008 at Act time).

## [2.0.2] - 2026-03-16

## [1.6.9] - 2026-03-13

### Fixed
- **scaffold.py create_spec() Template Mismatch** — Generated specs failed spec-lint validation (E001, E004, E008); updated template to use `| Field | Value |` metadata table format, `### R1:` requirement subsections, and `{VERSION}` placeholder instead of literal TBD; added 4 new tests in `test_scaffold.py` (BUG-033)

## [1.6.8] - 2026-03-06

### Fixed
- **Stale Docstring in deployer.py** — `_generate_claude_local_md_if_missing()` docstring and template comment claimed "never modified by PactKit" but STORY-064 introduced `_upsert_venv_managed_block()` which modifies the file; updated to accurately describe managed block behavior (BUG-031)
- **Missing E2E CLI Test for spec-lint** — Added 4 E2E subprocess tests (`TestSpecLintCommand`) to `test_cli_e2e.py` covering single-file pass/fail, `--all`, and no-args cases; spec-lint was the only CLI subcommand without E2E coverage (BUG-032)

## [1.6.7] - 2026-03-05

### Added
- **Sprint Stage A Model Consistency** — Split Stage A into A1-Plan (`system-architect`, model: opus) and A2-Act (`senior-developer`, model: sonnet) so model selection rule is enforced; Phase 0 reads `agent_models` from `.claude/pactkit.yaml` with opus/sonnet defaults and fallback to sonnet if model unavailable (STORY-065)
- **Persist Venv Config in CLAUDE.local.md** — `_upsert_venv_managed_block()` in `deployer.py` writes venv instructions into a `<!-- pactkit:venv:start/end -->` managed block in `CLAUDE.local.md` so virtual environment config survives `pactkit update` even when auto-detection fails (STORY-064)

### Fixed
- **Spec Linter Path Broken in External Projects** — Playbook prompts used hardcoded `python3 src/pactkit/skills/spec_linter.py` which only exists inside the pactkit dev repo; replaced with `pactkit spec-lint` installed CLI entry point; added `pactkit spec-lint` subcommand to `cli.py` supporting single-file and `--all` modes (BUG-030)

## [1.6.6] - 2026-03-05

### Fixed
- **project-init CLI Hang on Greenfield Projects** — Replaced blocking "ask the user to specify" stack detection fallback with config-first resolution: reads `stack` from `pactkit.yaml` first, file-based detection only when no config exists, safe fallback to `stack: auto` with warning instead of blocking user input mid-flow (BUG-029)

## [1.6.5] - 2026-03-04

### Fixed
- **Ghost DEV_REF Residual** — Removed unresolvable `DEV_REF_FRONTEND`/`DEV_REF_BACKEND` name references from Check playbook (`commands.py:245`) and Review skill (`workflows.py:373-374`); replaced with inline stack-aware prose; added 17 regression guard tests covering all command playbooks and workflow prompts (BUG-028)

## [1.6.4] - 2026-03-04

### Changed
- **PDCA Playbook Prompt Slimming** — Extracted shared protocols (Lazy Visualize, Test Mapping, Context.md Format) to `rules.py`, eliminating 4-place duplication; rewrote Sprint to Protocol-Only (70% reduction); removed MCP tool signature teaching from Plan/Act/Check/Done; resolved ghost DEV_REF/TEST_REF references; added Spec Lint to Design phase. Total prompt size: 73,511 → 56,939 chars (22.5% reduction) (STORY-063)

### Added
- **Shared Protocols Rule** — New `07-shared-protocols.md` rule module containing Lazy Visualize Protocol, Test Mapping Protocol, and Context.md Canonical Format; deployed to `~/.claude/rules/` and referenced by CLAUDE.md

## [1.6.3] - 2026-03-03

### Fixed
- **Sprint Board Story Heading Tolerance** — `board.py` regex now matches both `###` and `####` story headings for backward compatibility; new `create_board()` scaffold function ensures standardized board generation (BUG-027)
- **PyPI Logo Display** — README logo now uses absolute GitHub raw URL for PyPI rendering

## [1.6.2] - 2026-03-03

### Added
- **MCP Recommendations** — After `pactkit init` and `pactkit update`, displays 6 recommended MCP servers (Context7, Memory, Playwright, Draw.io, shadcn, Chrome DevTools) with purposes and config hint; helps users discover optional integrations (STORY-062)
- **Subagent Model Selection Guidance** — Core protocol now includes model selection guidance (haiku for simple tasks, sonnet for general, opus for complex); balances cost and capability in multi-agent workflows

## [1.6.1] - 2026-03-03

### Fixed
- **Init Hang Prevention** — Phase 0.5 Git Guard now prints warning instead of blocking prompt; enterprise flags (`--no-git`, `--no-external`, `--non-interactive`) wired end-to-end from CLI to deploy(); `visualize.py` scan truncated at 500 files with `--focus` escape hatch (STORY-060)

### Changed
- **Prompt Token Optimization** — Removed 10 redundant `<thinking>` block instructions from PDCA playbooks (4 in commands.py, 6 in workflows.py); Claude's native extended thinking makes explicit instructions unnecessary, saving ~50-100 tokens per invocation (STORY-061)

## [1.6.0] - 2026-02-28

### Added
- **Security Check Scope Filtering** — Plan generates a Security Scope section in Specs; Check phase skips non-applicable SEC-* checks based on the scope table, reducing false positives for prompt-only changes (STORY-056)

### Fixed
- **Routing Table Accuracy** — Split single "Embedded Skills" table into two: command-invoked (trace, release) and agent-only (draw, status, doctor, review, analyze); corrects 5 incorrect "Embedded In" claims (STORY-058)
- **Playbook Implicit Instructions** — Removed unverifiable Step 1.5 (Fast-Suite Shortcut) that referenced unobservable state; added explicit [High]/[Medium] signal labels to Clarify Gate ambiguity detection (STORY-057)
- **Version Sync on Init/Update** — `pactkit.yaml` version field now auto-syncs to `__version__` on every `pactkit init` and `pactkit update` (BUG-026)

### Changed
- **Lesson Scoring Simplified** — Replaced 5-dimension scoring with 2-check gate for lesson quality evaluation in Done phase
- **CI Dependencies** — Bump actions/checkout from 4 to 6, actions/setup-python from 5 to 6

## [1.5.0] - 2026-02-27

### Added
- **PDCA Quality Gates** — Security checklist, lesson scoring threshold, and implementation steps table in Specs; `check.security_checklist` and `done.lesson_quality_threshold` config fields (STORY-055)
- **Deployment Completeness Audit** — E2E tests verify exact counts and names of deployed files using `VALID_*` set equality assertions (STORY-054)
- **Impact-Based Regression** — `visualize impact --entry <func>` traces callers via call graph for targeted test selection; `regression.strategy` and `regression.max_impact_tests` config (STORY-053)
- **Conditional GitHub Release** — `release.github_release` config enables/disables `gh release create` in release workflow (STORY-052)
- **PDCA Workflow Streamlining** — Split overloaded Done command into focused Done + Release + PR commands; `/project-release` re-promoted from skill to command (STORY-051)
- **Doc-Only Regression Shortcut** — Skip full test suite when only non-source files changed; `LANG_PROFILES[stack].source_dirs` classification (STORY-050)
- **Community Standards** — CODE_OF_CONDUCT.md, SECURITY.md, dependabot.yml with content-assertion tests (STORY-049)
- **Worktree Isolation for Sprint** — `isolation="worktree"` for subagent Sprint; merge/copy recovery instructions for Stage A/C (STORY-048)

### Fixed
- **Stale project-release reference** — Updated stale-ref tests after re-promoting `/project-release` from skill to command (BUG-025)

## [1.4.0] - 2026-02-26

### Added
- **Spec Linter (Non-AI Structural Gate)** — `spec_linter.py` enforces 8 ERROR rules (metadata completeness, AC structure, Given/When/Then, no TBD release) and 4 WARN rules before any Act phase; Plan phase runs self-check after Spec generation; `pactkit spec-lint --all` for batch validation (STORY-042)
- **Active Clarify Gate** — Plan Phase 0.7 auto-detects ambiguous requirements using AMBIGUITY_SIGNALS checklist and generates structured questions (Scope/Users/Constraints/Scale/Edge Cases/Non-Goals); Greenfield projects force-trigger clarification; new `/project-clarify` standalone command (STORY-043)
- **Pre-Act Consistency Check** — Act Phase 0.6 advisory check cross-references Spec requirements with Board tasks and AC items with Test Case coverage; non-blocking with alignment matrix output; `pactkit-analyze` skill added (STORY-044)
- **Auto-PR Enhancement** — Done Phase 4.2 generates structured PR body from Spec/Board/test results with Summary, Changes, Acceptance Criteria checklist, and Test Results sections; user confirmation gate; gh CLI fallback (STORY-045)
- **Multi-Agent Compatibility Layer** — `generators/adapter.py` transforms Claude Code playbooks to Cursor (.mdc), GitHub Copilot (single file), and generic (.ai/) formats; `pactkit init/update --agent {claude,cursor,copilot,generic,all}` deploys to agent-specific directories (STORY-046)
- **Enterprise Configuration Flags** — `EnterpriseConfig` dataclass in `pactkit.yaml` supports `no_git`, `no_external`, `non_interactive`, `debug` fields; CLI flags `--no-git`, `--no-external`, `--non-interactive` override yaml config for air-gapped/CI environments (STORY-047)

### Fixed
- **Spec Linter code-block false positive** — Section parser now strips fenced code blocks before heading detection; `## Section` inside ``` examples no longer shadows real sections

## [1.3.1] - 2026-02-25

### Fixed
- **Dynamic version in CLAUDE.md** — CLAUDE_MD_TEMPLATE now uses `__version__` instead of hardcoded "v23.0"; Docker validation confirms correct version display (BUG-018)
- **project-init CLI invocation** — `/project-init` now invokes `pactkit init` CLI for complete config generation instead of partial inline logic (BUG-017)

## [1.3.0] - 2026-02-24

### Added
- **Conditional CI/CD Pipeline Generation** — `ci.provider` config (github/gitlab/none) generates workflow files; disabled by default (STORY-025)
- **Conditional Issue Tracker Integration** — `issue_tracker.provider` config enables GitHub Issue creation in Plan and closure in Done; standalone Sprint Board preserved (STORY-026)
- **Safe Opt-in Hook Templates** — 3 hook templates (pre-commit lint, post-test coverage, pre-push check); command-type only, report-only (exit 0), disabled by default (STORY-027)
- **Context-Aware Rule Scoping** — `rule_scopes` config maps rule IDs to glob patterns; deployer prepends `includeFiles` frontmatter (STORY-028)
- **Enhanced Doctor Diagnostics** — Stale graph detection (7+ days), orphaned/missing spec detection, config drift detection, severity levels (INFO/WARN/ERROR) (STORY-029)
- **Smart Lint Integration** — `lint_blocking` and `auto_fix` config options for Done command; non-blocking warnings by default (STORY-030)
- **TDD Bailout Decision Tree** — Distinguish project-internal modules from third-party packages in autonomous Sprint mode (STORY-022)
- **Test Quality Gate** — QA check detects tautological and over-mocked tests that pass but verify nothing (STORY-023)
- **Native Agent Enhancement** — Smart model defaults (`inherit`), opt-in hooks, Memory MCP integration in agent frontmatter (STORY-024)
- **Use-case validation for marketplace deployment** — Validated 4 deployment personas (solo dev, team lead, open-source maintainer, enterprise) (STORY-031)
- **Marketplace integration testing** — End-to-end deployment verification for marketplace format with correct path rewriting (STORY-032)
- **Config auto-backfill for missing sections** — `auto_merge_config_file` handles both list-type and non-list sections; `_rewrite_yaml` writes all sections (STORY-033)
- **Auto-refresh pactkit.yaml in Plan Init Guard** — Plan Phase 0.5 checks config completeness and runs `pactkit update` before proceeding (STORY-034)
- **README and docs directory documentation** — Complete project structure section, pactkit.yaml configuration reference, all 9 skills listed (STORY-035)

### Fixed
- **Read-only agent hooks removed** — Prompt hooks on qa-engineer, security-auditor, system-medic, code-explorer caused latency and infinite loop risk; tools/disallowedTools already enforce read-only constraint
- **Visualize excludes deployed directories** — `visualize` now excludes PactKit-deployed directories from graph generation to avoid pollution in marketplace mode (BUG-006)
- **Stale command references in prompt templates** — Comprehensive scan fixed 6 demoted command references across agents.py and skills.py (BUG-007, BUG-008)
- **Project-level config backfill** — `pactkit update` now backfills both global and project-level configs (BUG-009)
- **Config serialization data loss** — `_rewrite_yaml`, `generate_default_yaml`, and `_BACKFILL_KEYS` now stay in sync; `agent_models` and `rule_scopes` were validated but never serialized (BUG-010)
- **Stale command references in agent protocols** — Final sweep fixed 7 remaining demoted command references in agent protocol headers and skill Usage lines (BUG-011)
- **Call graph noise filter** — `_extract_calls` skips builtins and non-self attribute calls; `_build_call_graph` only emits edges where callees resolve to `func_registry` (BUG-012)
- **Single-source config consolidation** — Config now reads exclusively from `$CWD/.claude/pactkit.yaml`; removed dual-config architecture (BUG-013)
- **Version hygiene** — Unified 28 stale spec Release fields, 14 prompt template version labels, and 4 missing CHANGELOG entries; eliminated phantom versions 1.1.5 and 1.2.1 that were never released (BUG-014)

## [1.1.4] - 2026-02-24

### Added
- **CI lint gate** — Done and Act commands now run `lint_command` from `LANG_PROFILES` before commit, catching lint errors that CI would reject (STORY-015)
- **Language matching rule** — Core protocol now respects user's language in all PDCA output; project CLAUDE.md cleaned up to be instruction-focused (STORY-016)
- **Project CLAUDE.md generation** — `project-init` now scaffolds a project-level `.claude/CLAUDE.md` with architecture section, dev commands, and context.md reference (STORY-017)
- **Architecture docs staleness prevention** — Done command now verifies `system_design.mmd` component counts, refreshes `rules.md` test count, and checks release snapshots exist (STORY-018)

### Fixed
- **project-init stack detection** — Remove non-standard `language` field from pactkit.yaml schema; constrain `stack` to valid values (`python|node|go|java`)
- **Version tests use dynamic assertions** — Release tests now read canonical version from `pyproject.toml` instead of hardcoding, preventing CI failures on every version bump

## [1.1.3] - 2026-02-24

### Fixed
- **Multi-import graph edges** — `_build_file_graph` now processes all aliases in `import a, b, c` statements and deduplicates edges (BUG-003)
- **Dead code in deployer** — Remove unused `set(enabled_rules)` no-op in `_deploy_rules` (BUG-004)
- **Archive guard for taskless stories** — `archive_stories` now requires at least one `[x]` task before archiving, aligning with `_classify_story` logic (BUG-005)

## [1.1.2] - 2026-02-14

### Fixed
- **Scripted skill paths** — Use absolute paths in SKILL.md prompts for scripted skills; the LLM runs bash from project cwd, not the skill base directory (BUG-001)
- **Plugin mode paths** — Deploy-time path rewriting for plugin/marketplace modes; templates stay canonical, deployer rewrites `~/.claude/skills` to `${CLAUDE_PLUGIN_ROOT}/skills` at write time (BUG-002)

### Added
- **Draw.io MCP Integration** — `pactkit-draw` instant preview via `@drawio/mcp` when MCP server is available (STORY-013)

### Changed
- **Commands → Skills migration** — Demoted 6 commands (trace, draw, status, doctor, review, release) to prompt-only skills; reduces command count from 14 to 8 (STORY-011)
- Lint fixes for CI compliance

## [1.1.1] - 2026-02-13

### Fixed
- Remove downloads badge — PyPI stats not yet indexed
- Remove unused import in test_pdca_slim

### Changed
- Add governance rules and ignore playwright-mcp artifacts
- Sync pactkit.dev, GitHub metadata, and plugin to PDCA Slim architecture (STORY-012)

## [1.1.0] - 2026-02-13

### Added
- **Config Auto-Merge** — `pactkit init` now auto-appends new components to existing `pactkit.yaml`. Users can opt out via an `exclude` section. (STORY-009)
- **`/project-status`** — Cold-start project orientation command. Read-only report of sprint board, git state, and health indicators. (STORY-007)
- **Session Context Protocol** — `context.md` auto-generated by Done/Plan/Init commands for cross-session state awareness. (STORY-006)
- **Plugin & Marketplace Distribution** — `pactkit init --format plugin` and `--format marketplace` for self-contained distribution. (STORY-005)

### Changed
- **Constitution Sharpening** — Removed pseudo-advantages that overlap with LLM native behavior (55% token reduction). Strengthened Hierarchy of Truth and TDD rules. (STORY-008)

## [1.0.0] - 2026-02-01

### Added
- Initial public release on PyPI
- 9 specialized agents, 13 commands, 3 skills, 6 constitution rules
- PDCA+ lifecycle: Plan, Act, Check, Done, Trace, Draw, Doctor, Sprint, Review, Hotfix, Release, Design
- `pactkit.yaml` config schema with load/validate/generate (STORY-001)
- Selective deployment filtered by config (STORY-002)
- Init Guard for project-plan and project-doctor (STORY-003)
- GitHub/PyPI visibility optimization (STORY-004)
