# Changelog

All notable changes to PactKit will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [2.9.12] - 2026-04-01

### Added
- **GitHub Copilot adapter** — `pactkit init --format copilot` deploys skills, commands, agents, and `copilot-instructions.md` to `.github/`.
- **Multi-stack auto-detection** — `pactkit init` auto-detects multiple stacks (e.g. `stack: [python, typescript]`).
- **Module-level architecture graph** — `pactkit visualize --mode module` generates dimension-based subgraphs.

## [2.9.0] - 2026-03-28

### Added
- **All-IDE default deployment** — `pactkit init` now deploys Claude Code + OpenCode + Codex configs in one shot by default. No need to specify `--format` per IDE.

### Fixed
- **Entry-point deployer circular import** — Lazy-load adapter deployers to fix `ValueError` when running via pipx.

## [2.8.0] - 2026-03-27

### Added
- **3-IDE default install** — `pip install pactkit` now installs all three IDE adapters (Claude Code + OpenCode + Codex) out of the box.

### Changed
- **Cross-IDE command architecture** — Claude Code uses skills-only, OpenCode uses commands + skills, Codex uses skills-only with `$` prefix.

## [2.7.0] - 2026-03-27

### Added
- **Commands → Skills migration** — 11 PDCA commands now deploy as `skills/{name}/SKILL.md` for Claude Code format. Legacy command files auto-removed on upgrade.
- **Codex FormatProfile** — Re-added `codex` profile for thin adapter pattern support.

## [2.6.0] - 2026-03-26

### Added
- **Plugin adapter architecture** — `DeployerProtocol` and `DeployerBase` with registry pattern (`register_deployer()`). New IDE formats can be added as standalone pip packages via `entry_points`.
- **pactkit-opencode adapter** — OpenCode deployer extracted into standalone `pactkit-opencode` package.

## [2.5.0] - 2026-03-26

### Added
- **100% E2E CLI coverage** — 60 subprocess-based tests covering all CLI subcommands.
- **`python -m pactkit`** — Module entry point support.

### Fixed
- **Robustness sweep** — Atomic file writes for `.mmd` and `pactkit.yaml`, O(1) callee resolution, large file OOM guard (1MB limit), Windows encoding compatibility.

## [2.4.1] - 2026-03-26

### Added
- **Automated PyPI Publish** — GitHub Actions workflow triggers on `v*` tags with trusted publisher (OIDC).
- **Board `move_story` command** — Move stories between Backlog/In Progress/Done sections.

### Changed
- **Closed-source migration** — Source repo moved to private; public entry point at `pactkit/pactkit-public`.

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
