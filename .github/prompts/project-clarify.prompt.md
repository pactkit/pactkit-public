---
mode: agent
description: "Standalone requirement clarification before planning"
---

# Command: Clarify (v1.1.0)
- **Usage**: `/project-clarify "$ARGUMENTS"`
- **Agent**: System Architect

> **PURPOSE**: Standalone requirement clarification. Run before `/project-plan` to surface ambiguities and assess risks upfront.

## Phase 1: Ambiguity Analysis
1.  Analyze `$ARGUMENTS` against the AMBIGUITY_SIGNALS checklist (same as Plan Phase 0.7).
2.  Generate 3–6 structured questions (Scope, Users, Constraints, Scale, Edge Cases, Non-Goals).
3.  Ask questions in the user's language.

## Phase 2: Pre-mortem Risk Probe
> **PURPOSE**: Reverse thinking — identify how the plan could fail before it starts.
1.  Based on `$ARGUMENTS` and Phase 1 findings, generate 1–2 pre-mortem questions (pick the most relevant):
    - "If this feature is deemed a failure 1 month after launch, what is the most likely reason?"
    - "What assumptions does this plan rely on? Which assumption is the most fragile?"
    - "What will the person maintaining this code in 6 months complain about the most?"
    - "What is the most likely integration point to break?"
2.  Ask in the user's language, together with Phase 1 questions.
3.  Total questions across Phase 1 + Phase 2 MUST NOT exceed 6. If Phase 1 already has 5–6, pick only 1 pre-mortem question. If Phase 1 has ≤ 4, pick up to 2.

## Phase 3: Clarified Brief Output
1.  After user responses, produce a **Clarified Brief**:
    ```markdown
    ## Clarified Brief: {feature name}
    - **Scope**: {confirmed operations}
    - **Users**: {confirmed target users / roles}
    - **Constraints**: {technical constraints}
    - **Scale**: {performance expectations}
    - **Edge Cases**: {failure scenarios and expected behavior}
    - **Non-Goals**: {explicitly excluded}
    - **Risks**: {top 1-2 identified risks from pre-mortem}
    ```
2.  Output: "Ready for Plan. Run: `/project-plan \"{clarified brief summary}\"`"


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

# Clarify Contract

## Entry
- explicit clarification request or material ambiguity

## Inputs
- current request
- known constraints

## Outputs
- clarified brief

## Invariants
- unanswered questions remain visible and never become invented facts

## Completion Evidence
- decisions and assumptions are distinguishable

## Failure Semantics
- incomplete_continue

## Allowed Next
- project-plan

## External Effects
- none