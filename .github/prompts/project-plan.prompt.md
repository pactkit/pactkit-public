---
mode: agent
description: "Analyze requirements, create Spec and Story"
---

# Command: Plan (v1.3.0 Integrated Trace)
- **Usage**: `/project-plan "$ARGUMENTS"`
- **Agent**: System Architect

Previous workflow/checkpoint records are optional historical context only. They
must not block planning, require a new session, or determine this command's
completion.

## 🧠 Phase 0: The Thinking Process
> **Execution Style**: Work through each phase incrementally — output progress as you go. Do NOT try to plan the entire Spec in your head before producing output. Start each phase, show your findings, then move to the next.
> **Tool Integration Note**: If the request involves adapting PactKit to a new AI coding tool (new `format` value like `cursor`, `trae`, etc.), **always start** by consulting `docs/guides/tool-integration-checklist.md`. Complete Dimension 0 (capability matrix) before writing any code.

1.  **Analyze Intent**: New feature (Expansion) or Bugfix/Refactor (Modification)?
2.  **Strategy**:
    - If **New Feature**: Focus on `system_design.mmd` (Architecture).
    - If **Modification**: Focus on pactkit-trace skill (Logic Flow).
3.  **Greenfield Detection**: Check if the request is a greenfield product ideation:
    - **Signals**: Keywords ("from scratch", "MVP", "创业", "从零开始"); multi-story scope; empty sprint board; no source files.
    - **If greenfield signals are detected**: Suggest to the user: "This looks like a greenfield product design. Consider using `/project-design` instead, which generates a full PRD and decomposes into multiple stories."
    - Ask the user to confirm the redirect. Do NOT auto-redirect.
    - **If user declines**: Proceed with `/project-plan` normally.
    - **If existing project** (stories on board, source files present): Skip this check — greenfield detection does not apply to established projects.

## 🛡️ Phase 0.5: Init Guard (Auto-detect)
1. Run `pactkit project-preflight --apply-safe`; check .github/pactkit.yaml via `.github/pactkit.yaml`, schema, `docs/product/stories/`, `docs/architecture/graphs/`, config completeness (`ci`, `issue_tracker`).
2. If UNADOPTED (not initialized), do not create the Spec yet. Preview `pactkit adopt --check`; report and require explicit authorization; safe inspection and initialization repair remain available; `/project-init` is optional.
3. RECONCILE safely fixes stale state; `pactkit reconcile --check` previews. BLOCKED stops.
4. `pactkit init --format copilot` from the terminal to reinstall changes host assets; explicit authorization is required; otherwise continue planning. PASS proceeds.

## 🧠 Phase 0.7: Clarify Gate (Auto-detect Ambiguity)
> **PURPOSE**: Surface and resolve requirement ambiguity before the Spec is written. Better to clarify now than rewrite a Spec.
1.  **Detect Ambiguity**: Analyze the user's input (`$ARGUMENTS`) against these signals:
    - [High] No quantitative metrics ("高并发" without QPS)
    - [High] No boundary conditions ("user management" without specifying which operations)
    - [Medium] No technical constraints (no auth method, no framework specified)
    - [Low] Single sentence input (< 15 words) — likely under-specified but not blocking
    - [Medium] Vague quantifiers ("some", "大量", "简单")
    - [Medium] No target user specified
2.  **Trigger Logic**:
    - 2 High + ≥ 1 Medium signals → **Auto-trigger** Clarify
    - ≥ 2 High signals (no Medium) → **Suggest** Clarify (ask user: "Input may be underspecified. Clarify? yes/skip")
    - 1 High + ≥ 2 Medium signals → **Suggest** Clarify
    - Otherwise → **Silent skip**
3.  **Greenfield Force-Trigger**: If Phase 0 detected a Greenfield project and the user chose to continue with `/project-plan` (not `/project-design`), **always trigger** Clarify regardless of score.
4.  **If triggered**: Generate 3–6 structured questions covering:
    - **Scope**: "What specific operations are included? Please list them."
    - **Users**: "Who is the target user? Are there multiple roles?"
    - **Constraints**: "Any technical constraints? (required framework, compatibility requirements)"
    - **Scale**: "Expected data volume / concurrency / user count?"
    - **Edge Cases**: "What should happen when [failure scenario]?"
    - **Non-Goals**: "What is explicitly NOT in scope?"
    - Ask questions in the user's language (Language Matching rule).
5.  **User Response**:
    - User answers all/some → merge into `enriched_input`; proceed to Phase 1 with `enriched_input`
    - User inputs "skip" or declines → proceed with original input (Clarify MUST NOT block Plan)
6.  **Output**: The enriched_input (original + answers) is used as context for Phase 1 onwards.
7.  **Checkpoint**: Record `intent_clarified` with the original input fingerprint and the sanitized confirmed answers.

## 🎬 Phase 1: Archaeology (The "Know Before You Change" Step)
> **Subagent Scope Rule**: When delegating research to an Explore subagent, always provide a **bounded** prompt: target function/class, directory scope, file limit, and expected output. Never delegate open-ended "trace the whole codebase" tasks.

1.  **Provider-Routed Scan**: Run `pactkit query --explore <target> --json --explain`. The router enforces configured Codegraph priority, freshness and fail-closed behavior. Do not invoke `visualize`, Codegraph, SQLite or `rg` directly. Use `--allow-fallback` only after explicitly recording why degradation is acceptable.
2.  **Logic Trace (CRITICAL)** — use pactkit-trace skill:
    - If modifying existing logic, trace the current implementation.
    - *Goal*: Identify the exact function/class responsible for the logic.
    - **Delegation Template**: When using an Explore subagent for trace, formulate the prompt with:
      - **Target**: specific function or class name to trace
      - **Scope**: specific directory (e.g., `src/pactkit/generators/`)
      - **Limit**: read at most 8-10 files
      - **Output**: what to return (entry file, call chain, key data transformations)
      - Example: `Agent(subagent_type="Explore", prompt="Find deploy() in src/pactkit/generators/deployer.py, trace to file writes, ≤8 files, return entry + chain + transforms.")`
3.  **Topology-Aware Trace (Conditional)** — if `detect_topology(root)` includes `api_call` or `agent`:
    - For **api_call**: Run `api_convention_summary(root)` and include path prefixes, fetch function names, and total call count in the Archaeologist Report. This prevents API path convention bugs in downstream implementation.
    - For **agent**: Note orchestration edges from AgentParser (LangGraph/YAML/MCP) in the report so downstream changes respect agent flow.
4.  **Lateral Scan (MUST for Modification)** — after tracing the target, scan horizontally for existing implementations of the same operation pattern:
    - Identify the core operation(s) the requirement involves (e.g., "write to OWL", "send notification", "create DB record").
    - Use a tiered strategy to count existing implementations in the project:
      - **Prefer LSP** (if available): `incomingCalls` or `findReferences` on the core operation's function/method — gives type-aware, zero-false-positive results.
      - **Fallback query**: `pactkit query --callers <operation> --json` — fan-in via the router.
      - **Fallback grep**: `grep -rn "<operation>" src/` — text-level search when neither LSP nor the router is available.
    - **Output checkpoint**:
      ```
      Lateral Scan:
      - Operation: {name}
      - Existing implementations: {N} ({file1}:{func1}, {file2}:{func2}, ...)
      - Assessment: {Reuse existing | Extract shared abstraction | New is justified}
      ```
    - **Threshold**: If the same operation has **≥ 3 independent implementations**, the Spec's Technical Design MUST include a shared abstraction evaluation before adding the Nth implementation.
    - **Skip condition**: Pure greenfield features with no existing codebase analog — log "Lateral Scan: no existing pattern found" and proceed.
5.  **Solution Design Protocol (Conditional)** — if the requirement involves frameworks already used by the project:
    - Execute the **Capability Design** module from `.github/skills/_rules/design/capability-design.md` to evaluate capability delta (framework native + project existing vs. needs implementation).
    - Include the Capability Assessment output in Phase 2 Spec writing.
6.  **Checkpoint**: Record `archaeology` with provider decision, freshness, query targets, and bounded trace summary.

## 🎬 Phase 2: Design & Impact
1.  **Diff**: Compare User Request vs Current Reality (from Phase 1).
2.  **Duplication Audit**: Run the Duplication Audit from system-architect protocol — if this is the Nth same-kind implementation, grep existing implementations and assess shared abstraction needs before writing Spec.
3.  **Engineering Concerns Assessment** — keywords are candidate signals, not obligations:
    - Reference the Engineering Concerns trigger index (`.github/skills/_rules/engineering/index.md`) keyword table.
    - Confirm each candidate against the requirement, repository evidence, and the planned behavior and boundaries; a document that only mentions a topic adds no implementation duty.
    - For concerns that can affect correctness, user data, or delivery, write the decision, applicable constraints, and expected verification into Technical Design / Requirements / Acceptance Criteria, reusing still-applicable project decisions with their source.
    - No fixed count caps the key concerns; unmatched topics are not padded in (avoid noise).
    - **Output checkpoint**: `"Engineering concerns identified: {list}. Decisions will be included in Technical Design."`
    - **Best-Practice Research (MUST for non-trivial design)**: consult current industry practice — Context7 (framework patterns) or web search — and cite references in Technical Design; memory-only designs are flagged "unreferenced".
4.  **Domain Material Declaration** — if the requirement touches domain logic (business rules, data models, semantic layers, domain terms):
    - The Spec MUST declare the governing domain material (data dictionaries, semantic layers, docs) in its `## Implementation Inputs` table (path + purpose), so Act Phase 0.7 spec-preflight loads it before the first source write.
    - Infrastructure/tooling changes MUST state the skip reason.
    - **Output checkpoint**: `"Domain material: {list} | skip: {reason}"`
5.  **Update HLD**: Modify `docs/architecture/graphs/system_design.mmd`.
    - *Rule*: Machine graphs retired — code queries use `pactkit query`.
6.  **Durable decisions become ADRs (Conditional)**: a durable architectural choice (data store, protocol, boundary, dependency) established or overturned here MUST also become an ADR: `python3 .github/skills/pactkit-scaffold/scripts/scaffold.py create_adr {N} "{title}"` — fill the four sections, Status accepted, then `pactkit lint-adr`; overturning an old one passes `--supersedes {old id}`.

## 🎬 Phase 3.1: Story ID Generation
1.  Run `pactkit generate-id` to allocate a decentralized time-prefixed Story ID; it preserves the `developer` prefix from .github/pactkit.yaml.
2.  **Output checkpoint**: Print "Story ID determined: {ID}. Writing Spec now."
3.  **Record the identity locally**: State the generated Story ID before creating its Spec. Any optional local checkpoint is historical evidence only and never controls a future session.

## 🎬 Phase 3.2a: Scaffold + Metadata Table & Requirements
1.  **Scaffold**: Run `python3 .github/skills/pactkit-scaffold/scripts/scaffold.py create_spec "{ID}" "{title}"` in the current session.
2.  **Read**: Read `docs/specs/{ID}.md` to see the scaffolded template.
3.  **Edit placeholders** (use Edit tool, NOT Write):
    - Edit `Release | TBD` → `Release | {version}` (from `pyproject.toml`/`package.json`, NOT `.github/pactkit.yaml`)
    - Edit `(Description of the problem or feature)` → actual Background content from your Trace findings
    - Edit `## Target Call Chain` placeholder → actual call chain from Phase 1
    - Edit `### R1: (Requirement Name) (MUST)` → actual requirements using RFC 2119 keywords (MUST/SHOULD/MAY). Add more R{N} sections as needed.
    - Edit `## Dependency Surface` fields (dangling ID = E010; feeds `pactkit spec-graph`)
4.  **Journey Segment (Conditional)**: If `docs/e2e/journey.md` exists in the project:
    - Read `docs/e2e/journey.md` to identify defined journeys and their steps.
    - Assess whether this Story's scope touches any journey step (e.g., modifies a UI flow, changes an API endpoint used in a journey).
    - If yes: add a `## Journey Segment` section to the Spec with the format:
      ```
      ## Journey Segment

      - Journey: {Journey Name}
      - Steps: {step numbers, e.g., "2-3" or "4"}
      - Impact: {brief description of how this story affects the journey}
      ```
    - If the Story does not affect any journey: do NOT add this section (Act Phase 4 Journey Sync will auto-skip).
5.  **Output checkpoint**: Print "Spec skeleton filled. Adding acceptance criteria."
6.  **Milestone output**: Report `spec_scaffolded`, then `requirements_written` in your progress output; each milestone claim must be verifiable against the real Spec file.

## 🎬 Phase 3.2b: Acceptance Criteria & Implementation Steps
1.  **Edit AC** (use Edit tool): Replace `### AC1: (Scenario Name) (R1)` and its Given/When/Then placeholders with actual scenarios. The template already provides the `- **Given**` / `- **When**` / `- **Then**` structure — fill in the content. Add more AC{N} sections as needed.
    - Each Scenario SHOULD map to a verifiable test case in `docs/test_cases/`.
2.  **Edit Implementation Steps** (optional): If Phase 1 Trace identifies 2+ files to modify, replace the placeholder rows in `## Implementation Steps` with actual steps. The table skeleton (headers + separator) is already in the template.
3.  **Output checkpoint**: Print "Acceptance criteria written. Running security scope."
4.  **Checkpoint**: Record `acceptance_written`; placeholders or missing Given/When/Then MUST fail.

## 🎬 Phase 3.2c: Security Scope
1.  **MUST**: Run `pactkit sec-scope <changed-files>` to auto-detect SEC-1~SEC-8 applicability.
2.  **Edit** the `## Security Scope` section already in the template: replace the placeholder SEC-1 row with actual SEC-* assessments from the output above. The table skeleton (Check/Applicable/Reason headers) is already in the template.
3.  **Fallback**: If `pactkit sec-scope` is unavailable, manually Edit each SEC-1 through SEC-8 entry. Apply docs/tests-only shortcut if applicable (mark ALL N/A with Reason "docs/tests only").
4.  **Output checkpoint**: Print "Security scope filled. Running lint."
5.  **Checkpoint**: Record `security_scoped` from the real Spec.

## 🎬 Phase 3.2d: Spec Lint Self-Check
1.  Run `pactkit spec-lint docs/specs/{ID}.md`. If `pactkit` is not on `$PATH`, use `python3 -m pactkit spec-lint docs/specs/{ID}.md` instead.
2.  If any ERROR or WARNING rules fire, self-correct the Spec immediately (you wrote it — you have authority to fix it). Re-run until `pactkit spec-lint` reports 0 errors AND 0 warnings.
3.  This prevents the Spec from being rejected at Act Phase 0.5.
4.  **Output checkpoint**: Print "Spec lint passed (0 errors AND 0 warnings)."
5.  **Checkpoint**: Record `spec_linted`; the engine reruns canonical lint and rejects warnings.

## 🎬 Phase 3.3: Board, Memory & Current-Session Continuation
1.  **Board**: Run `python3 .github/skills/pactkit-board/scripts/board.py add_story "{STORY_ID}" "{title}" "{task1}|..."` in the current session.
2.  **Memory MCP (Conditional)**: IF Memory MCP is available, use create_entities to store design context (decisions, target files, rationale) under entity `{STORY_ID}`. Record story dependencies if applicable.
3.  **Session Context Update**: Run the context continuation update in ignored `.pactkit/context.md` — set `last-command` to the last PDCA command and `phase` to the current phase in the continuation section, for session handoff to refresh ignored `.pactkit/context.md` with canonical sections `- `## Sprint Status`
- `## Current Stories`
- `## Recent Completions`
- `## Active Branches`
- `## Key Decisions`
- `## Next Recommended Action`
- `## Agent Continuation``. Never stage or commit it.
4.  **Continue**: "Trace complete. Spec created. Continue with Act in this session when requested; a new session is optional."
5.  **Completion evidence**: Report the exact title and ordered task list created. If validation fails, fix the local artifacts where safe or report the concrete gap; never create a workflow block that prevents a later session from continuing.


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

# Plan Contract

## Entry
- explicit planning request for one bounded change

## Inputs
- current user intent
- repository evidence

## Outputs
- Spec
- Story record
- change risk profile

## Invariants
- requirements are testable and scope is explicit
- the Spec never instructs the implementer to amend it during Act (findings land in the commit message or a docs/ note)

## Completion Evidence
- Spec lint passes
- requirements map to acceptance criteria

## Failure Semantics
- incomplete_continue

## Allowed Next
- project-act

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