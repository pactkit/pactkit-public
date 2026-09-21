from __future__ import annotations
import abc, re, os, sys, json, datetime, argparse, subprocess, shutil, ast
from collections import deque
from dataclasses import dataclass
from pathlib import Path

def nl(): return chr(10)


import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Import schema constants (STORY-slim-007: single source of truth)
try:
    from pactkit.schemas import (
        DEP_SURFACE_FIELDS,
        DEP_SURFACE_SECTION,
        ITEM_ID_PATTERN,
        SPEC_AC_PATTERN,
        SPEC_GIVEN_WHEN_THEN,
        SPEC_REQUIRED_METADATA_FIELDS,
        SPEC_REQUIRED_SECTIONS,
        SPEC_REQUIREMENT_PATTERN,
        SPEC_RFC_KEYWORDS,
        SPEC_RFC_PATTERN,
        SPEC_SEC_PATTERN,
        SPEC_SECURITY_SCOPE_SECTION,
        SPEC_VALID_STATUSES,
    )
except ImportError:
    # Fallback for standalone execution without pactkit installed
    # Keep in sync with src/pactkit/schemas.py
    SPEC_REQUIRED_METADATA_FIELDS = ("ID", "Status", "Priority", "Release")
    SPEC_REQUIRED_SECTIONS = ("## Requirements", "## Acceptance Criteria", "## Security Scope")
    SPEC_REQUIREMENT_PATTERN = r"### R\d+[:\s]"
    SPEC_AC_PATTERN = r"### AC\d+[:\s]|### Scenario\s+\d+[:\s]"
    SPEC_GIVEN_WHEN_THEN = ("Given", "When", "Then")
    SPEC_RFC_KEYWORDS = ("MUST", "SHOULD", "MAY", "SHALL", "REQUIRED", "RECOMMENDED", "OPTIONAL")
    SPEC_RFC_PATTERN = re.compile(r"\b(" + "|".join(SPEC_RFC_KEYWORDS) + r")\b")
    SPEC_VALID_STATUSES = ("Draft", "In Progress", "Done")
    SPEC_SECURITY_SCOPE_SECTION = "Security Scope"
    SPEC_SEC_PATTERN = r"\|\s*SEC-|^###\s*SEC-"
    DEP_SURFACE_SECTION = "Dependency Surface"
    DEP_SURFACE_FIELDS = ("Depends on", "Provides", "Touches", "Conflict risk")
    ITEM_ID_PATTERN = r"(?:STORY|HOTFIX|BUG)(?:-[a-z]+)?-\d+"

# Bump when check semantics change (rule added/removed/retuned).  Recorded on
# spec_lint run events so diagnosis can segment telemetry across rule
# generations instead of mixing them into one rate.
# 2026-09.2: W013 (Permission Matrix) + W014 (Trust Boundaries) added —
# security-design dimension (review 2026-09-06).
# 2026-09.3: W013/W014 content validation — placeholder-only sections and
# prose assertions no longer satisfy the artifacts (review 6).
RULES_VERSION = "2026-09.3"


def _touches_entries(raw: str) -> list[str]:
    """Split a Touches cell into normalized path entries.

    Reuses ``spec_graph._parse_touches`` (STORY-slim-20260824dd23a0ed3b4c R5)
    via a LAZY import to avoid a load-time cycle (spec_graph imports
    ``section_text``/``strip_code_blocks`` from this module). Falls back to an
    inline copy when pactkit is not importable (standalone script).
    """
    try:
        from pactkit.spec_graph import _parse_touches
    except ImportError:
        _parse_touches = None
    if _parse_touches is not None:
        return _parse_touches(raw)
    out: list[str] = []
    for part in raw.split(","):
        p = part.strip().strip("`").strip()
        if p and p.lower() != "none" and p not in out:
            out.append(p)
    return out

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class LintIssue:
    rule_id: str
    message: str
    line: int | None = None


@dataclass
class LintResult:
    errors: list[LintIssue] = field(default_factory=list)
    warnings: list[LintIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_RFC2119 = SPEC_RFC_PATTERN
_METADATA_ROW = re.compile(r"^\|\s*(\w[\w\s]*\w|\w)\s*\|\s*(.+?)\s*\|", re.MULTILINE)
_METADATA_HEADER = re.compile(r"^\|\s*Field\s*\|\s*Value\s*\|", re.MULTILINE | re.IGNORECASE)
_REQ_SUBSECTION = re.compile(SPEC_REQUIREMENT_PATTERN, re.MULTILINE)
_AC_SUBSECTION = re.compile(SPEC_AC_PATTERN, re.MULTILINE | re.IGNORECASE)


_FENCED_BLOCK = re.compile(r"^```[^\n]*\n.*?^```", re.MULTILINE | re.DOTALL)
# R10 (STORY-slim-052): Fallback for unclosed code fences — strip from opening fence to EOF
_UNCLOSED_FENCE = re.compile(r"^```[^\n]*\n.*", re.MULTILINE | re.DOTALL)


def _strip_code_blocks(text: str) -> str:
    """Replace fenced code block content with blank lines (preserving line count)."""

    def _blank(m: re.Match) -> str:
        return "\n" * m.group(0).count("\n")

    result = _FENCED_BLOCK.sub(_blank, text)
    # R10: If there's still an unclosed fence, strip it to EOF
    result = _UNCLOSED_FENCE.sub(_blank, result)
    return result


def _find_section(text: str, heading: str, result: LintResult | None = None) -> tuple[int, int] | None:
    """Return (start_idx, end_idx) of a ## heading block, or None if absent.

    ``text`` should already have code blocks stripped via ``_strip_code_blocks``
    so that headings inside examples don't confuse parsing.

    R10: If ``## Heading`` is not found but ``### Heading`` exists, report a
    specific warning about wrong heading level (when ``result`` is provided).
    """
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE | re.IGNORECASE)
    m = pattern.search(text)
    if not m:
        # R13 (STORY-slim-052): Check all heading levels (#, ###, ####) — not just ###
        for _, hashes in [("#", 1), ("###", 3), ("####", 4)]:
            wrong_level = re.compile(rf"^{re.escape(hashes * '#')}\s+{re.escape(heading)}\s*$", re.MULTILINE | re.IGNORECASE)
            wm = wrong_level.search(text)
            if wm and result is not None:
                line = _line_number(text, wm.start())
                result.warnings.append(
                    LintIssue("W009", f"Section '{heading}' found at wrong heading level ({hashes * '#'} instead of ##)", line=line)
                )
                break  # Report the first wrong-level match only
        return None
    start = m.start()
    next_h2 = re.search(r"^##\s+", text[m.end() :], re.MULTILINE)
    end = m.end() + next_h2.start() if next_h2 else len(text)
    return start, end


def _section_text(text: str, heading: str, result: LintResult | None = None) -> str | None:
    """Return the body text of a ## heading block, or None if absent.

    ``text`` should already have code blocks stripped.
    """
    bounds = _find_section(text, heading, result=result)
    if bounds is None:
        return None
    return text[bounds[0] : bounds[1]]


def _line_number(text: str, idx: int) -> int:
    return text[:idx].count("\n") + 1


# Public API for pactkit.spec_graph (STORY-slim-143). Module-design rule:
# external modules MUST NOT access _private members — these aliases are the
# supported surface. Bodies stay single-sourced above.
strip_code_blocks = _strip_code_blocks
section_text = _section_text


# ---------------------------------------------------------------------------
# Validation rules
# ---------------------------------------------------------------------------


def _check_metadata(text: str, result: LintResult) -> dict[str, str]:
    """E001, E002, E008 — metadata table structure and required fields."""
    fields: dict[str, str] = {}

    # E001: metadata table must exist (Field | Value header)
    if not _METADATA_HEADER.search(text):
        result.errors.append(LintIssue("E001", "Missing metadata table (| Field | Value | header not found)"))
        return fields

    # Parse all metadata rows
    for m in _METADATA_ROW.finditer(text):
        key = m.group(1).strip()
        val = m.group(2).strip()
        # R12: Filter out separator rows (|---|---| patterns) and header row
        if key.lower() in ("field",) or re.match(r"^-+$", key):
            continue
        fields[key] = val

    # E002: required fields must be present and non-empty (from schemas.SPEC_REQUIRED_METADATA_FIELDS)
    for req in SPEC_REQUIRED_METADATA_FIELDS:
        if req not in fields or not fields[req]:
            result.errors.append(LintIssue("E002", f"Missing or empty required metadata field: {req}"))

    # E008: Release must not be TBD
    if fields.get("Release", "").upper() == "TBD":
        result.errors.append(LintIssue("E008", "Release field is 'TBD' — must be a concrete version before Act"))

    # W006: Status value must be in SPEC_VALID_STATUSES (STORY-slim-018 R3)
    status_val = fields.get("Status", "")
    if status_val and status_val not in SPEC_VALID_STATUSES:
        result.warnings.append(
            LintIssue("W006", f"Status value '{status_val}' not in allowed set: {', '.join(SPEC_VALID_STATUSES)}")
        )

    return fields


def _check_requirements_section(text: str, result: LintResult) -> None:
    """E003, E004, W003 — Requirements section."""
    body = _section_text(text, "Requirements", result=result)

    # E003: section must exist
    if body is None:
        result.errors.append(LintIssue("E003", "Missing '## Requirements' section"))
        return

    # E004: must contain at least one ### R{N}: subsection
    if not _REQ_SUBSECTION.search(body):
        result.errors.append(LintIssue("E004", "Requirements section has no '### R{N}:' subsections"))

    # W003: requirements should use RFC 2119 keywords
    if not _RFC2119.search(body):
        result.warnings.append(LintIssue("W003", "No RFC 2119 keywords (MUST/SHOULD/MAY) found in Requirements"))


def _check_acceptance_criteria(text: str, result: LintResult, raw_text: str | None = None) -> None:
    """E005, E006, E007 — Acceptance Criteria section."""
    body = _section_text(text, "Acceptance Criteria", result=result)

    # E005: section must exist
    if body is None:
        result.errors.append(LintIssue("E005", "Missing '## Acceptance Criteria' section"))
        return

    # E006: must contain at least one ### AC{N}: or ### Scenario {N}: subsection
    if not _AC_SUBSECTION.search(body):
        result.errors.append(
            LintIssue("E006", "Acceptance Criteria has no '### AC{N}:' or '### Scenario {N}:' subsections")
        )
        return

    # E007: each AC subsection must contain Given, When, Then keywords (per-subsection check)
    # Use raw_text (with code blocks) for GWT search — specs may wrap Gherkin in ```gherkin fences
    raw_body = (_section_text(raw_text, "Acceptance Criteria") if raw_text else None) or body
    ac_matches = list(_AC_SUBSECTION.finditer(body))
    raw_ac_matches = list(_AC_SUBSECTION.finditer(raw_body)) if raw_body != body else ac_matches
    for i, m in enumerate(ac_matches):
        # Extract AC ID from the heading (e.g., "AC1" or "Scenario 1")
        ac_heading = m.group(0).strip()
        ac_id_match = re.search(r"(AC\d+|Scenario\s+\d+)", ac_heading, re.IGNORECASE)
        ac_id = ac_id_match.group(0) if ac_id_match else ac_heading
        # Get subsection text from raw (preserves code block content for GWT search)
        if i < len(raw_ac_matches):
            raw_start = raw_ac_matches[i].end()
            raw_end = raw_ac_matches[i + 1].start() if i + 1 < len(raw_ac_matches) else len(raw_body)
            subsection_lower = raw_body[raw_start:raw_end].lower()
        else:
            start = m.end()
            end = ac_matches[i + 1].start() if i + 1 < len(ac_matches) else len(body)
            subsection_lower = body[start:end].lower()
        # Word-boundary match to prevent "whenever" matching "when"
        missing = [kw for kw in SPEC_GIVEN_WHEN_THEN if not re.search(r"\b" + kw.lower() + r"\b", subsection_lower)]
        if missing:
            result.errors.append(LintIssue("E007", f"{ac_id} missing keyword(s): {', '.join(missing).upper()}"))


_PIPE_TABLE_ROW = re.compile(r"^\|.+\|.+\|", re.MULTILINE)

# STORY-slim-024: R{N} ID extraction pattern
# Uses \s+ instead of SPEC_REQUIREMENT_PATTERN's literal space to tolerate minor
# whitespace variations in hand-written specs (e.g., tab or double-space after ###).
# Adds capture group (R\d+) for ID extraction — SPEC_REQUIREMENT_PATTERN is match-only.
_REQ_ID_PATTERN = re.compile(r"###\s+(R\d+)[:\s]", re.MULTILINE)


def _extract_requirement_ids(req_section: str) -> dict[str, str]:
    """Extract R{N} IDs and their body text from Requirements section.

    Returns dict mapping R{N} (e.g., "R1") to the requirement body text.
    """
    result: dict[str, str] = {}
    # Find all ### R{N}: headers
    matches = list(_REQ_ID_PATTERN.finditer(req_section))
    for i, m in enumerate(matches):
        req_id = m.group(1).upper()  # Normalize to uppercase (R1, R2, etc.)
        # Body is from end of this header to start of next (or end of section)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(req_section)
        body = req_section[start:end].strip()
        result[req_id] = body
    return result


def _check_req_ac_coverage(text: str, result: LintResult) -> None:
    """W007 — Check that all R{N} are referenced by at least one AC."""
    req_section = _section_text(text, "Requirements")
    ac_section = _section_text(text, "Acceptance Criteria")

    if req_section is None or ac_section is None:
        return  # Missing sections are handled by E003/E005

    # Extract all R{N} IDs and their bodies
    req_map = _extract_requirement_ids(req_section)
    if not req_map:
        return  # No requirements found (handled by E004)

    # Check each R{N} for coverage in AC section (word-boundary match)
    for req_id, req_body in req_map.items():
        # STORY-slim-025 R4: use \b word boundary to prevent R1 matching R10/CR1/ERROR1
        if not re.search(rf"\b{re.escape(req_id)}\b", ac_section, re.IGNORECASE):
            # STORY-slim-025 R5: use SPEC_RFC_PATTERN (same as W003) for word-boundary keyword match
            rfc_match = _RFC2119.search(req_body)
            emphasis = f" ({rfc_match.group(0)})" if rfc_match else ""
            result.warnings.append(
                LintIssue("W007", f"Requirement {req_id} has no corresponding AC reference{emphasis}")
            )


def _check_implementation_steps(text: str, result: LintResult) -> None:
    """W005 — Implementation Steps table format validation (STORY-055)."""
    section = _section_text(text, "Implementation Steps")
    if section is None:
        return  # section absent — no warning
    if not _PIPE_TABLE_ROW.search(section):
        result.warnings.append(
            LintIssue(
                "W005",
                "## Implementation Steps exists but has no pipe table "
                "(expected columns: Step, File, Action, Dependencies, Risk)",
            )
        )


# Canonical: src/pactkit/schemas.py SPEC_TEMPLATE
_SCAFFOLD_PLACEHOLDERS = {
    "Background": "(Description of the problem or feature)",
    "Target Call Chain": "(Trace call chain here)",
}


def _check_optional_sections(text: str, result: LintResult) -> None:
    """W001, W002, W004, W008 — recommended sections and placeholder detection."""
    bg = _section_text(text, "Background")
    if bg is None:
        result.warnings.append(LintIssue("W001", "Missing '## Background' section (recommended)"))
    elif _SCAFFOLD_PLACEHOLDERS["Background"] in bg:
        result.warnings.append(LintIssue("W008", "## Background still contains scaffold placeholder text"))

    tcc = _section_text(text, "Target Call Chain")
    if tcc is None:
        result.warnings.append(LintIssue("W002", "Missing '## Target Call Chain' section (recommended)"))
    elif _SCAFFOLD_PLACEHOLDERS["Target Call Chain"] in tcc:
        result.warnings.append(LintIssue("W008", "## Target Call Chain still contains scaffold placeholder text"))

    has_out_of_scope = _section_text(text, "Out of Scope") is not None or _section_text(text, "Non-Goals") is not None
    if not has_out_of_scope:
        result.warnings.append(LintIssue("W004", "Missing '## Out of Scope' or '## Non-Goals' section (recommended)"))


_SEC_ROW = re.compile(SPEC_SEC_PATTERN, re.MULTILINE)


def _check_security_scope(text: str, result: LintResult) -> None:
    """E009 — Security Scope section must exist with SEC-* entries."""
    body = _section_text(text, SPEC_SECURITY_SCOPE_SECTION, result=result)
    if body is None:
        result.errors.append(LintIssue("E009", f"Missing '## {SPEC_SECURITY_SCOPE_SECTION}' section"))
        return
    if not _SEC_ROW.search(body):
        result.errors.append(LintIssue("E009", f"{SPEC_SECURITY_SCOPE_SECTION} section has no SEC-* entries"))


def _check_lateral_scan(text: str, result: LintResult) -> None:
    """W010 — Technical Design should include Lateral Scan Results."""
    tech_design = _section_text(text, "Technical Design")
    if tech_design is None:
        return
    if "### Lateral Scan Results" not in text:
        result.warnings.append(
            LintIssue("W010", "## Technical Design exists but missing '### Lateral Scan Results' subsection")
        )


# Dependency-file and framework signals that make a capability assessment
# meaningful (STORY-slim-2026090301691dea72e8: assessment was produced 1 time
# in 56 /project-plan runs — the trigger judgment needs a code-level nudge).
_FRAMEWORK_SIGNAL = re.compile(
    r"pyproject\.toml|package\.json|go\.mod|pom\.xml|build\.gradle|"
    r"requirements\.txt|cargo\.toml|framework",
    re.IGNORECASE,
)


def _telemetry_context(
    spec_path: str | None, project_root: Path | None = None
) -> tuple[Path, str] | None:
    """(events root, spec id) when *spec_path* is the PROJECT'S OWN spec.

    Attribution (review 6 2026-09-06, live-caught): the spec must live
    under ``<root>/docs/specs/`` — the scaffolded spec home and the
    ``--all`` default.  "Anywhere under the root" was not enough: tooling
    that lints fixtures INSIDE the project (the rules corpus) recorded
    hundreds of warnings into the project's real telemetry and distorted
    its W012 rate.  Specs outside the project's specs dir are not the
    project's specs — no event, regardless of path form.
    """
    if not spec_path:
        return None
    root = Path(project_root) if project_root is not None else Path.cwd()
    spec = Path(spec_path)
    if not spec.is_absolute():
        spec = root / spec
    try:
        spec.relative_to(root / "docs" / "specs")
    except ValueError:
        return None
    return root, spec.stem


def _record_rule_warning(
    rule_id: str,
    spec_path: str | None,
    project_root: Path | None,
    spec_hash: str | None,
) -> None:
    """Best-effort rule-warning telemetry with content binding; never raises.

    Shared by W012/W013/W014 (STORY-slim-2026090699752886f924 follow-up,
    review 2026-09-06): one recorder, one binding contract.
    """
    ctx = _telemetry_context(spec_path, project_root)
    if ctx is None:
        return
    root, spec_id = ctx
    try:
        from pactkit.rule_events import append_rule_event

        append_rule_event(root, "rule_warning", {
            "rule": rule_id,
            "spec": spec_id,
            "spec_hash": spec_hash,
            "rules_version": RULES_VERSION,
        })
    except Exception:
        pass


def _check_capability_assessment(
    text: str,
    result: LintResult,
    spec_path: str | None = None,
    project_root: Path | None = None,
    spec_hash: str | None = None,
) -> None:
    """W012 — Technical Design with framework/dependency signals should
    include a Capability Assessment subsection.

    Non-blocking by design: Capability Assessment is an L3 (SHOULD)
    semantic, so an E-level rule would lock Act Phase 0.5 on incidental
    keyword matches. The warning surfaces in Act Phase 0.5 output as a
    pre-implementation reminder.
    """
    tech_design = _section_text(text, "Technical Design")
    if tech_design is None:
        return
    if not _FRAMEWORK_SIGNAL.search(tech_design):
        return
    if "### Capability Assessment" not in tech_design:
        result.warnings.append(
            LintIssue(
                "W012",
                "## Technical Design mentions frameworks/dependencies but missing "
                "'### Capability Assessment' subsection (Need | Source | Decision)",
            )
        )
        # Telemetry (STORY-slim-20260903a4ef6915ed62): best-effort, never
        # blocks.  The spec identifier lets diagnosis correlate warnings
        # with specs (false-positive sampling, W012 rate denominator) —
        # without it the rate degraded to a distinct-spec denominator
        # (review 2026-09-06).
        _record_rule_warning("W012", spec_path, project_root, spec_hash)


# Security-design dimension signals (review 2026-09-06 gap: permission
# matrix + trust boundaries as ENFORCED spec artifacts, not prose).  The
# signal scan covers Requirements + Technical Design only — concrete
# sections, never Background prose, to avoid incidental copy-paste matches.
_AUTH_SIGNAL = re.compile(
    r"\b(auth|authentication|authorization|permissions?|credentials?|rbac"
    r"|tenants?|multi-tenant)\b|权限|凭据|租户",
    re.IGNORECASE,
)
_EXTERNAL_BOUNDARY_SIGNAL = re.compile(
    r"external (api|service|tool|system)|webhook|third[- ]party|untrusted"
    r"|user input|tool output|\bmcp\b|\bllm\b|外部服务|第三方|用户输入|工具输出",
    re.IGNORECASE,
)
_PERMISSION_MATRIX_SECTION = "Permission Matrix"
_TRUST_BOUNDARIES_SECTION = "Trust Boundaries"
_PLACEHOLDER_LINE = re.compile(r"^(TODO|TBD|placeholder|待补|待定)$", re.IGNORECASE)


def _is_placeholder_section(section: str) -> bool:
    """True when every non-empty line is a bare placeholder.

    Review 6 2026-09-06: '## Trust Boundaries\\nTODO' satisfied the bare
    existence check — a placeholder section is a missing section.
    """
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    return bool(lines) and all(_PLACEHOLDER_LINE.fullmatch(line) for line in lines)


def _table_data_rows(section: str) -> list[str]:
    """Non-separator table rows (2+ cells) in a section — prose lines and
    separator rows are not data (review 6: 'We do not deny any request.'
    satisfied a bare keyword search)."""
    rows = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2 or not any(cells):
            continue
        if all(re.fullmatch(r"[-: ]*", cell) for cell in cells):
            continue  # separator row
        rows.append(stripped)
    return rows


def _concern_text(text: str) -> str:
    """Requirements + Technical Design bodies (the concrete sections)."""
    parts = []
    for heading in ("Requirements", "Technical Design"):
        section = _section_text(text, heading)
        if section:
            parts.append(section)
    return "\n".join(parts)


def _check_permission_matrix(
    text: str,
    result: LintResult,
    spec_path: str | None = None,
    project_root: Path | None = None,
    spec_hash: str | None = None,
) -> None:
    """W013 — auth/tenant signals require a Permission Matrix design
    artifact carrying at least one Deny decision.

    The deny row is the point: negative paths (unauthorized actor,
    cross-tenant access) are what break, and they only exist in acceptance
    when the matrix declares them (review 2026-09-06 security-design gap).
    Non-blocking (L3 SHOULD) — an E-level rule would lock Plan on
    incidental keyword matches.
    """
    if not _AUTH_SIGNAL.search(_concern_text(text)):
        return
    matrix = _section_text(text, _PERMISSION_MATRIX_SECTION)
    if matrix is None or _is_placeholder_section(matrix):
        result.warnings.append(
            LintIssue(
                "W013",
                "Auth/tenant signals present but no '## Permission Matrix' section "
                "(or placeholder-only) — Actor | Action | Resource | Decision data "
                "rows, at least one carrying Deny",
            )
        )
        _record_rule_warning("W013", spec_path, project_root, spec_hash)
        return
    deny_rows = [
        row for row in _table_data_rows(matrix)
        if re.search(r"\bdeny\b|拒绝", row, re.IGNORECASE)
    ]
    if not deny_rows:
        result.warnings.append(
            LintIssue(
                "W013",
                "'## Permission Matrix' has no table data row carrying a Deny "
                "decision — prose assertions and all-allow matrices leave "
                "negative paths (unauthorized actor, cross-tenant access) untested",
            )
        )
        _record_rule_warning("W013", spec_path, project_root, spec_hash)


def _check_trust_boundaries(
    text: str,
    result: LintResult,
    spec_path: str | None = None,
    project_root: Path | None = None,
    spec_hash: str | None = None,
) -> None:
    """W014 — external-boundary signals require a Trust Boundaries
    declaration: source → boundary validation → sink for each untrusted
    input.

    External content (API responses, tool output, MCP/LLM content,
    third-party data) must not silently widen authorization or trigger
    outbound effects — the declaration is where that decision becomes
    reviewable (review 2026-09-06 security-design gap).
    """
    if not _EXTERNAL_BOUNDARY_SIGNAL.search(_concern_text(text)):
        return
    boundaries = _section_text(text, _TRUST_BOUNDARIES_SECTION)
    if boundaries is None or _is_placeholder_section(boundaries):
        result.warnings.append(
            LintIssue(
                "W014",
                "External-boundary signals present but no '## Trust Boundaries' "
                "section (or placeholder-only) — one source → boundary "
                "validation → sink line per untrusted input",
            )
        )
        _record_rule_warning("W014", spec_path, project_root, spec_hash)
        return
    if not re.search(r"→|->", boundaries):
        result.warnings.append(
            LintIssue(
                "W014",
                "'## Trust Boundaries' has no source → boundary validation → "
                "sink line — a bare section name does not declare where "
                "untrusted content is validated",
            )
        )
        _record_rule_warning("W014", spec_path, project_root, spec_hash)


_ITEM_ID_RE = re.compile(ITEM_ID_PATTERN)


def _check_dependency_surface(text: str, result: LintResult, spec_path: str | None = None) -> None:
    """E010, W011 — Dependency Surface section (STORY-slim-143).

    W011: section missing, or its table lacks required fields.
    E010: a `Depends on` entry references a story ID with no spec file
          (dangling dependency — ordering decisions rely on these edges).
    """
    body = _section_text(text, DEP_SURFACE_SECTION)
    if body is None:
        result.warnings.append(
            LintIssue("W011", f"Missing '## {DEP_SURFACE_SECTION}' section (recommended for parallel scheduling)")
        )
        return

    fields: dict[str, str] = {}
    for m in _METADATA_ROW.finditer(body):
        key = m.group(1).strip()
        if key.lower() == "field" or re.match(r"^-+$", key):
            continue
        fields[key] = m.group(2).strip()

    missing = [f for f in DEP_SURFACE_FIELDS if f not in fields]
    if missing:
        result.warnings.append(
            LintIssue("W011", f"Dependency Surface missing field(s): {', '.join(missing)}")
        )
        return  # Without Depends on there is nothing to resolve

    # STORY-slim-20260824dd23a0ed3b4c R5 — reject pathological Touches entries.
    # Runs before the Depends-on early-return so a spec with no dependencies
    # still gets its Touches surface validated.
    touches_raw = fields.get("Touches", "")
    if touches_raw and touches_raw.lower() != "none":
        for entry in _touches_entries(touches_raw):
            if entry == "**" or entry.startswith("/") or ".." in entry:
                result.errors.append(
                    LintIssue(
                        "E011",
                        f"Dependency Surface 'Touches' entry {entry!r} is pathological "
                        f"(repo-wide '**', absolute, or parent-traversal) — not a valid write scope",
                    )
                )

    depends_val = fields.get("Depends on", "")
    if not depends_val or depends_val.lower() == "none":
        return

    specs_dir = Path(spec_path).parent if spec_path else Path("docs/specs")
    for dep_id in sorted(set(_ITEM_ID_RE.findall(depends_val))):
        if not (specs_dir / f"{dep_id}.md").exists():
            result.errors.append(
                LintIssue("E010", f"Depends on references '{dep_id}' but no such spec exists in {specs_dir}")
            )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate_spec(spec_path: str, *, project_root: Path | None = None) -> LintResult:
    """Validate a spec file and return a LintResult.

    Parameters
    ----------
    spec_path:
        Path to the spec Markdown file.
    project_root:
        Project the lint run is attributed to (telemetry).  The CLI passes
        it explicitly; standalone runs fall back to the cwd.

    Returns
    -------
    LintResult
        ``.passed`` is ``True`` iff there are zero ERROR-level issues.
    """
    try:
        raw = Path(spec_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        result = LintResult()
        result.errors.append(LintIssue("E000", f"File not found: {spec_path}"))
        return result
    # Strip fenced code blocks once so all checks operate on the same clean text.
    # This prevents headings inside code examples from confusing section detection.
    text = _strip_code_blocks(raw)
    # Content binding for telemetry (review 5 2026-09-06): warnings and run
    # records carry the hash of the content they describe, so retrospective
    # diagnosis can tell "spec unchanged since the event" from "spec edited
    # after the event" instead of judging edited specs against old events.
    spec_hash: str | None = None
    try:
        from pactkit.rule_events import spec_content_hash

        spec_hash = spec_content_hash(raw)
    except Exception:
        pass
    result = LintResult()
    _check_metadata(text, result)
    _check_requirements_section(text, result)
    _check_acceptance_criteria(text, result, raw_text=raw)
    _check_optional_sections(text, result)
    _check_implementation_steps(text, result)
    _check_req_ac_coverage(text, result)  # STORY-slim-024: W007
    _check_security_scope(text, result)  # STORY-slim-025: E009
    _check_lateral_scan(text, result)  # STORY-slim-106: W010
    _check_capability_assessment(
        text, result, spec_path=spec_path, project_root=project_root,
        spec_hash=spec_hash,
    )  # STORY-slim-2026090301691dea72e8: W012
    _check_permission_matrix(
        text, result, spec_path=spec_path, project_root=project_root,
        spec_hash=spec_hash,
    )  # review 2026-09-06 security design: W013
    _check_trust_boundaries(
        text, result, spec_path=spec_path, project_root=project_root,
        spec_hash=spec_hash,
    )  # review 2026-09-06 security design: W014
    _check_dependency_surface(text, result, spec_path=spec_path)  # STORY-slim-143: E010/W011
    _record_lint_run(spec_path, result, project_root=project_root, spec_hash=spec_hash)
    return result


def _record_lint_run(
    spec_path: str,
    result: LintResult,
    project_root: Path | None = None,
    spec_hash: str | None = None,
) -> None:
    """Record one spec_lint run event — the W012-rate denominator.

    One event per validate_spec invocation: the event itself is the run
    identity; warning events correlate via spec + ts.  Attribution follows
    _telemetry_context (the spec must live inside the project); never
    raises (review 2026-09-06: the rate divided warnings by distinct
    warned specs — 6 warnings on one spec read as "6 of 1 lint runs").
    """
    root = _telemetry_context(spec_path, project_root)
    if root is None:
        return
    events_root, spec_id = root
    try:
        from pactkit.rule_events import append_rule_event

        append_rule_event(events_root, "spec_lint", {
            "spec": spec_id,
            "result": "pass" if result.passed else "fail",
            "errors": len(result.errors),
            "warnings": len(result.warnings),
            "rules_version": RULES_VERSION,
            "spec_hash": spec_hash,
        })
    except Exception:
        pass


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _format_result(path: str, result: LintResult) -> str:
    lines = [path]
    for e in result.errors:
        loc = f" (line {e.line})" if e.line else ""
        lines.append(f"  [ERROR] {e.rule_id}: {e.message}{loc}")
    for w in result.warnings:
        loc = f" (line {w.line})" if w.line else ""
        lines.append(f"  [WARN]  {w.rule_id}: {w.message}{loc}")
    status = "PASS" if result.passed else f"FAIL ({len(result.errors)} error(s), {len(result.warnings)} warning(s))"
    lines.append(f"  Result: {status}")
    return "\n".join(lines)


def main(argv: list[str] | None = None, project_root: Path | None = None) -> int:
    """Run the linter.  *project_root* scopes telemetry (CLI passes it)."""
    parser = argparse.ArgumentParser(description="PactKit Spec Linter — structural validation for spec files")
    parser.add_argument("spec", nargs="?", help="Path to spec file to validate")
    parser.add_argument("--all", action="store_true", help="Validate all specs in specs dir")
    parser.add_argument(
        "--specs-dir",
        default="docs/specs",
        help="Directory containing spec files (default: docs/specs)",
    )
    args = parser.parse_args(argv)

    if args.all:
        specs_dir = Path(args.specs_dir)
        if not specs_dir.exists():
            print(f"Error: specs directory '{specs_dir}' not found", file=sys.stderr)
            return 1
        # R11: Filter to files matching ITEM_ID_RE pattern (skip TEMPLATE.md, README.md, etc.)
        _item_id_pattern = re.compile(r"^(?:STORY|HOTFIX|BUG)(?:-[a-z]+)?-\d+\.md$")
        spec_files = sorted(f for f in specs_dir.glob("*.md") if _item_id_pattern.match(f.name))
        if not spec_files:
            print(f"No spec files found in '{specs_dir}'")
            return 0
        any_failure = False
        for spec_file in spec_files:
            result = validate_spec(str(spec_file), project_root=project_root)
            print(_format_result(str(spec_file), result))
            if not result.passed:
                any_failure = True
        return 1 if any_failure else 0

    if not args.spec:
        parser.print_help()
        return 1

    result = validate_spec(args.spec, project_root=project_root)
    print(_format_result(args.spec, result))
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
