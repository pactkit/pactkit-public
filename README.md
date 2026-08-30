<p align="center">
  <img src="https://raw.githubusercontent.com/pactkit/pactkit-src/main/docs/assets/logo.png" alt="PactKit" width="480" />
</p>

<p align="center">
  <a href="https://pypi.org/project/pactkit/"><img src="https://img.shields.io/pypi/v/pactkit" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/pactkit/"><img src="https://img.shields.io/pypi/pyversions/pactkit" alt="Python" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT" /></a>
</p>

<p align="center"><strong>CODE is the Law. Data is the Truth. Prompt is ONLY instruction. AI is ONLY creativity.</strong></p>

> **PactKit** (Pact 契约 + Kit) is a governance framework that enforces the **P.A.C.T.** contract between humans and AI agents. Deterministic operations run as code, not prompts. Decisions are grounded in data, not memory. AI does what it's best at — creativity and language — while code handles everything that must be repeatable and correct.
>
> 26 CLI subcommands, 9 specialized agents, 11 commands, 10 skills, and a full Plan-Act-Check-Done lifecycle. One `pip install` deploys to all 3 supported IDEs.

### Supported AI Tools

| Tool | Format | Command |
|------|--------|---------|
| **Claude Code** | Classic | `pactkit init` |
| **OpenCode** | OpenCode | `pactkit init` |
| **Codex CLI** | Codex | `pactkit init` |

> `pactkit init` deploys all 3 IDEs at once. Use `--format <name>` to target a single IDE.

### What it looks like

```
You:  /project-sprint "Add OAuth2 login"

 Plan   System Architect scans codebase, writes Spec, updates Board
 Act    Senior Developer writes tests first (RED), then code (GREEN)
 Check  QA Engineer runs 6-phase audit (security + quality + spec alignment)
 Done   Repo Maintainer gates regression, archives story, commits
```

## The P.A.C.T. Governance Contract

The name says it all — **Pact** means covenant. These four principles define the boundary between human intent and AI execution:

```
P   Prompt   is ONLY instruction   Tells AI how to act — defines process, never state
A   AI       is ONLY creativity    Formatting, summarization, language — never deterministic logic
C   Code     is the Law            Sole executor of deterministic operations — no bypass, no approximation
T   Truth    Data is the Truth     Factual basis for all judgment — no memory, no inference, no fabrication
```

- If a script exists → **use it**. Never reimplement in natural language. (C)
- If data is available → **read it**. Never guess or recall from memory. (T)
- Prompts define HOW, never WHAT. Current state comes from data, not docs. (P)
- AI formats, summarizes, and creates. AI does not parse, compute, or fabricate. (A)

> Read the full philosophy: [docs/architecture/governance/philosophy.md](docs/architecture/governance/philosophy.md)

## Why PactKit?

- **P.A.C.T. Governance** — A contract between humans and AI agents, with clear boundaries
- **Multi-Agent Ensemble** — 9 specialized agents collaborate, each with constrained tools
- **Full PDCA Lifecycle** — Plan -> Act -> Check -> Done, with quality gates at every stage
- **Safe by Design** — TDD-first, safe regression, pre-existing test protection
- **Multi-Tool Support** — Works with Claude Code, OpenCode, and Codex CLI

## Installation

```bash
pip install pactkit
```

Requires Python 3.10+ and one of:
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- [OpenCode](https://opencode.ai)
- [Codex CLI](https://github.com/openai/codex)

> `pip install pactkit` automatically installs adapters for all 3 IDEs.

### Optional Extras

```bash
pip install pactkit[lint]        # Includes ruff for lint gate
pip install pactkit[visualize]   # Includes tree-sitter for AST analysis
pip install pactkit[all]         # Everything above + IDE adapters
```

### Recommended External Tools

These tools enhance PactKit but cannot be distributed via pip. Run `pactkit deps check` to see what's missing and `pactkit deps install` for guided platform-aware installation:

| Tool | Purpose | Install |
|------|---------|---------|
| [gh](https://cli.github.com) | GitHub CLI (issue sync, release, PR) | `brew install gh` |
| [codegraph](https://www.npmjs.com/package/codegraph) | Code symbol index & call chain analysis | `npm install -g codegraph` |

## Quick Start

```bash
# Deploy to all 3 IDEs at once
pactkit init

# Update to latest playbooks (preserves your custom content in CLAUDE.md)
pactkit update
```

<details>
<summary>Single-IDE deployment</summary>

```bash
# Deploy to one IDE only
pactkit init --format classic    # Claude Code
pactkit init --format opencode   # OpenCode
pactkit init --format codex      # Codex CLI
```
</details>

Then in any project:

```bash
# Clarify — Surface ambiguities before planning
/project-clarify "Add user authentication"

# Plan — Analyze requirements, create Spec
/project-plan "Add user authentication"

# Act — Spec lint + consistency check + TDD implementation
/project-act STORY-001

# Check — Security scan + quality audit (P0-P3 severity)
/project-check

# Done — Regression gate + auto-PR + conventional commit
/project-done
```

Or run the full cycle in one command:

```bash
/project-sprint "Add user authentication"
```

## PDCA+ Workflow

| Phase | Command | Agent | What Happens |
|-------|---------|-------|-------------|
| **Clarify** | `/project-clarify` | System Architect | Ambiguity detection -> Structured questions -> Clarified brief |
| **Plan** | `/project-plan` | System Architect | Clarify gate -> Codebase scan -> Spec generation -> Board entry |
| **Act** | `/project-act` | Senior Developer | Spec lint -> Consistency check -> TDD loop -> Regression check |
| **Check** | `/project-check` | QA + Security | 8-item security checklist + quality audit + spec alignment |
| **Done** | `/project-done` | Repo Maintainer | Regression gate -> Archive -> Conventional commit |
| **Release** | `/project-release` | Repo Maintainer | Version bump -> Snapshot -> Git tag -> GitHub Release |
| **PR** | `/project-pr` | Repo Maintainer | Push branch -> Create pull request via gh CLI |
| **Sprint** | `/project-sprint` | Team Lead | One-command automated PDCA orchestration; empty args = Wave Mode (parallel backlog stories via `spec-graph` waves + conflict matrix) |
| **Hotfix** | `/project-hotfix` | Senior Developer | Fast-track fix bypassing PDCA (with traceability) |
| **Init** | `/project-init` | System Architect | Bootstrap project structure and governance |
| **Design** | `/project-design` | Product Designer | PRD generation -> Story decomposition -> Board setup |

### When to Use What

The core loop is **Plan → Act → Done**. Other commands plug in as needed:

```
You have a task
  │
  ├─ Vague idea, multiple features? ──→ /project-design
  │
  ├─ Unclear requirement? ──→ /project-clarify → /project-plan
  │
  ├─ Clear feature or bug?
  │   │
  │   ├─ Small fix (1 file, obvious)? ──→ /project-hotfix
  │   │
  │   └─ Needs design? ──→ /project-plan → /project-act
  │       │
  │       ├─ Security-sensitive? ──→ /project-check (QA audit)
  │       │
  │       └─ /project-done
  │           │
  │           ├─ On feature branch? ──→ /project-pr
  │           └─ Ready to release? ──→ /project-release
  │
  └─ Fully automated? ──→ /project-sprint (runs all phases)
```

**Solo developer?** Start with `/project-plan` → `/project-act` → `/project-done`. Add `/project-hotfix` for small fixes and `/project-check` when security matters.

### Embedded Skills (auto-invoked by commands)

| Skill | Embedded In | Purpose |
|-------|-------------|---------|
| Trace | Plan Phase 1, Act Phase 1 | Deep code tracing and execution flow analysis |
| Release | Release Phase 1 | Version release: snapshot, archive, Git tag |

### Agent Skills (invoked via agent roles)

| Skill | Available To | Purpose |
|-------|-------------|---------|
| Draw | visual-architect, system-architect | Generate Draw.io XML architecture diagrams |
| Status | system-medic | Project state overview |
| Doctor | system-medic | Diagnose project health |
| Review | qa-engineer | PR Code Review |
| Analyze | senior-developer (Act inline) | Cross-artifact consistency check: Spec <-> Board <-> Test Cases |

## Agent Ensemble

PactKit deploys 9 specialized agents, each with constrained tools and focused responsibilities:

| Agent | Role | Core Capability |
|-------|------|----------------|
| System Architect | Architecture design | Maintain Intent Graph, write Specs |
| Senior Developer | Full-stack development | TDD loop, call chain analysis, hotfix |
| QA Engineer | Quality gates | Deep check (P0-P3), PR review |
| Security Auditor | Security audit | OWASP scanning, threat modeling |
| Repo Maintainer | Repository ops | Cleanup, archiving, Git conventions, releases |
| System Medic | System diagnostics | Configuration drift repair |
| Visual Architect | Architecture visualization | Draw.io XML generation |
| Code Explorer | Code tracing | Call graph + sequence diagram |
| Product Designer | Product design | PRD, story decomposition, board init |

## Skills

PactKit deploys 10 skills (3 scripted + 7 prompt-only), auto-invoked by commands:

| Skill | Type | Purpose |
|-------|------|---------|
| **pactkit-visualize** | Scripted | Code dependency graph (Mermaid .mmd): file-level, class-level, call-level |
| **pactkit-board** | Scripted | Sprint board operations: add story, update task, archive |
| **pactkit-scaffold** | Scripted | File scaffolding: create spec, test files, git branches, skills |
| **pactkit-trace** | Prompt-only | Deep code tracing and execution flow analysis |
| **pactkit-draw** | Prompt-only | Generate Draw.io XML architecture diagrams |
| **pactkit-analyze** | Prompt-only | Cross-artifact consistency check: Spec <-> Board <-> Test Cases |
| **pactkit-status** | Prompt-only | Cold-start project overview (sprint + git + health) |
| **pactkit-doctor** | Prompt-only | Configuration drift detection and health report |
| **pactkit-review** | Prompt-only | PR code review with SOLID/Security/Quality checklists |
| **pactkit-release** | Prompt-only | Version bump, architecture snapshot, git tag |

## CLI Subcommands

PactKit ships 45 deterministic CLI subcommands — operations that were previously delegated to AI prompts are now enforced in Python code (the "C" in P.A.C.T.):

| Command | Purpose |
|---------|---------|
| `pactkit init` | Deploy toolkit to AI coding assistant |
| `pactkit update` | Update playbooks (preserves config) |
| `pactkit upgrade` | Upgrade with format selection |
| `pactkit version` | Show installed version |
| `pactkit schema` | Print document schemas |
| `pactkit doctor` | Diagnose project health (HLD drift, board, config, deployment content parity, adapter skew) |
| `pactkit spec-lint` | Validate spec structure (E001-E010, W001-W011; incl. dependency surface checks) |
| `pactkit spec-graph` | Story dependency DAG: topological execution waves + file-conflict matrix (`--json` for orchestrators, `--write-graph` for Mermaid) |
| `pactkit spec-status` | Update spec Status field (Draft/In Progress/Done) |
| `pactkit guard` | Check project init markers |
| `pactkit generate-id [--type story\|hotfix\|bug]` | Generate a decentralized time-prefixed item ID |
| `pactkit context` | Generate `context.md` from project state |
| `pactkit clean` | Remove stack-specific temp artifacts |
| `pactkit lint` | Stack-aware lint with auto-fix and blocking modes |
| `pactkit regression` | Classify changes (SKIP/FULL/IMPACT) |
| `pactkit test-map` | Map source files to test files |
| `pactkit coverage-gate` | Enforce 3-tier coverage thresholds (80/50/block) |
| `pactkit visualize` | Conditional graph regeneration (lazy mode) |
| `pactkit query` | Query call graph via codegraph: `--callers`, `--callees`, `--chain [--down]` (requires `graph_provider: codegraph`) |
| `pactkit lesson-append` | Append lesson with specificity check and dedup |
| `pactkit invariants-refresh` | Update test count invariant in rules.md |
| `pactkit sec-scope` | Detect security scope for changed files |
| `pactkit backfill-release` | Replace Release: TBD in completed specs |
| `pactkit issue-sync` | GitHub issue lifecycle for BUG/HOTFIX items |
| `pactkit lint-context` | Validate context.md structure |
| `pactkit lint-lessons` | Validate lessons.md structure |
| `pactkit lint-testcase` | Validate test case structure |
| `pactkit done-verify` | Archive honesty gate: requirement→test evidence chain, checkbox↔case consistency, status machine (blocks `/project-done` on FAIL) |
| `pactkit commit-gate` | Pre-commit test gate with skip≠pass transparency; stack-aware (pytest/npm test/go test/mvn/gradle); PreToolUse hook + git pre-commit/pre-push channels, auto-installed per format |
| `pactkit gate` | Session context hooks (`--hook session-start/pre-compact`) + external-effect authorization (`pactkit gate <scope> [--ttl-minutes N]`) |
| `pactkit deps` | External dependency check (`deps check`) and guided install (`deps install`) for node/codegraph/gh |
| `pactkit schema config` | List every pactkit.yaml key with default, effective value, and source |
| `pactkit sync` | Sync codegraph index |

### Enforcement Gates (2.25.0)

The hook layer enforces the rules prompt text can only state — protected branches, specs, credentials, and external effects survive a conflicting instruction instead of losing to it:

| Gate | Blocks | Bypass (human/config only) |
|------|--------|---------------------------|
| `push_gate` | Direct push to a protected branch (default `main`/`master`) | `PACTKIT_ALLOW_DIRECT_PUSH=1` or `enforcement.allow_direct_push` |
| `commit_gate` | Commits on protected branches (default) and RED test suites | same as push_gate; `develop` keeps the full-suite rule |
| `spec_guard` | Editing a spec that has an active preflight receipt (Spec is Law during Act) | `PACTKIT_ALLOW_SPEC_EDIT=1` or `pactkit gate spec_edit` |
| `auth_gate` | External-effect commands (PR/release/publish/repo) until the user confirms | `pactkit gate <scope>` TTL token or `PACTKIT_AUTHORIZED=1` |
| `secrets_gate` | Literal credential material in commands (env-var indirection is exempt) | `PACTKIT_ALLOW_SECRET=1` |
| `tamper_guard` | Modifying enforcement artifacts (hooks, gate registrations, audit records) | `PACTKIT_ALLOW_CONFIG_EDIT=1` |

All blocks/bypasses are audited (`.pactkit/enforcement/`) and feed `pactkit stats` as gate telemetry (per-gate block counts, per-command invocation counts, authorization pairs) — the friction data that decides what to tune next.

## Deployment Architecture

PactKit supports three deployment formats:

### Claude Code (Classic)

```
~/.claude/
├── CLAUDE.md                 <- Project context entry point
├── rules/                    <- 8 rule modules (loaded per-command, not globally)
├── skills/                   <- 21 skill packages (11 commands + 10 embedded)
└── agents/                   <- 9 agent definitions
```

Commands are deployed as skills (`skills/project-*/SKILL.md`), invoked with `/project-plan`.

### OpenCode

```
~/.config/opencode/
├── AGENTS.md                 <- On-demand @reference index (lazy rule loading)
├── rules/                    <- 8 rule modules (3 core always-load + 6 on-demand)
├── commands/                 <- 11 command playbooks (auto-discovered, invoked via /)
├── agents/                   <- 9 agent definitions (mode: subagent)
├── skills/                   <- 10 skill packages (AI agent loads on demand)
└── opencode.json             <- Global config (model routing, instructions)
```

OpenCode uses dual mechanism: `commands/` for user-facing PDCA entry points, `skills/` for AI-invoked tools.

### Codex CLI

```
~/.codex/
├── AGENTS.md                 <- Global constitution
├── config.toml               <- Model, sandbox, MCP config
├── rules/                    <- 8 rule modules
├── skills/                   <- 21 skill packages (11 commands + 10 embedded)
└── .pactkit-version          <- Version marker for updates
```

Commands are deployed as skills (`skills/project-*/SKILL.md`), invoked with `$project-plan`.

## Multi-Developer Collaboration

PactKit supports multi-developer workflows with Story ID prefixing:

```yaml
# In pactkit.yaml
developer: alice
```

Story IDs become `STORY-alice-001`, preventing merge conflicts when multiple developers work on separate branches.

## Project Structure (PDCA-managed)

PactKit's PDCA lifecycle manages a `docs/` directory:

```
docs/
├── product/
│   ├── stories/                 <- One workflow/task fact file per Story
│   └── sprint_board.md          <- Optional generated read-only projection
├── specs/                       <- The Law — requirement specifications
├── test_cases/                  <- Gherkin acceptance scenarios
└── architecture/
    ├── graphs/                  <- Architecture graph files (Mermaid .mmd)
    ├── governance/
    │   ├── rules.md             <- Architecture decisions and invariants
    │   └── lessons/             <- One immutable record per lesson
    └── snapshots/               <- Versioned architecture graph snapshots
```

Session context is generated locally at `.pactkit/context.md` and is ignored by Git.

### pactkit.yaml Configuration Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `stack` | string | auto-detected | Project stack (`python`, `node`, `go`, `java`) |
| `developer` | string | `""` | Developer prefix for Story IDs (multi-developer collaboration) |
| `agents` | list | all 9 | Agent definitions to deploy |
| `commands` | list | all 11 | Command playbooks to deploy |
| `skills` | list | all 10 | Skills to deploy |
| `rules` | list | all 8 | Constitution rule modules to deploy |
| `exclude` | object | `{}` | Components to exclude (e.g., `exclude.agents: [agent-name]`) |
| `visualize.graph_provider` | string | (absent) | Graph query backend. Set `codegraph` to use `.codegraph/codegraph.db` for `pactkit query`. Absent = grep `.mmd` |
| `ci` | object | `provider: none` | CI/CD pipeline generation (`github`, `gitlab`, `none`). Sub-fields: `runner` (default: `ubuntu-latest`), `language_version` (default: auto per stack), `github_host` (GHE server address), `actions_ref` (GHE actions prefix) |
| `issue_tracker` | object | `provider: none` | External issue tracker (`github`, `none`) |
| `hooks` | object | disabled | Opt-in hook templates (pre-commit, post-test, pre-push) |
| `lint_blocking` | bool | `false` | Whether lint failures block commits |
| `auto_fix` | bool | `false` | Whether to auto-fix lint errors |
| `agent_models` | object | `{}` | Per-agent model overrides (`haiku`, `sonnet`, `opus`, `inherit`) |
| `command_models` | object | defaults | Per-command model overrides for OpenCode deployment |
| `write_scope` | object | (absent) | Declare `source_roots`/`test_roots`/`docs_roots` for non-standard directory layouts (e.g. `frontend/src`, `backend/`, `directus-extensions/`). It informs optional workflow integrations and project tooling; normal `project-act` work remains in the current session and is never blocked by a stale workflow scope. |

## Safe Regression

PactKit's safe regression system prevents agents from blindly modifying pre-existing tests:

- **TDD Loop** — Only iterates on tests created in the current story
- **Regression Check** — Read-only gate; pre-existing test failure = STOP and report
- **Done Gate** — Full regression by default; incremental only when ALL safety conditions are met

## Hierarchy of Truth (the "T" in P.A.C.T.)

```
Tier 1: Specs & Test Cases           <- The Law (CODE is the Law)
Tier 2: Tests                        <- The Verification (DATA is the Truth)
Tier 3: Implementation               <- The Mutable Reality
```

When conflicts arise: Spec wins. Always. The agent modifies code, never the spec.

## MCP Integration

PactKit conditionally integrates with MCP servers when available:

| MCP Server | Purpose | PDCA Phase |
|------------|---------|------------|
| Context7 | Library documentation lookup | Act |
| shadcn | UI component search/install | Design |
| Playwright | Browser automation testing | Check |
| Chrome DevTools | Performance/console/network | Check |
| Memory | Cross-session knowledge graph | Plan/Act/Done |
| Draw.io | Architecture diagram instant preview | Plan, Design |

All MCP instructions are conditional — gracefully skipped when unavailable.

## Upgrading

```bash
pip install --upgrade pactkit
pactkit update    # Updates all deployed IDEs
```

Use `pactkit update --format <name>` to update a single IDE.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE)
