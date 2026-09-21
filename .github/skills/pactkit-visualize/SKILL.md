---
name: pactkit-visualize
description: "Code analysis: provider-routed graph queries, cyclomatic complexity, layer violations, blast radius (JSON reports)"
model: haiku
---

# PactKit Visualize

Machine code queries route through `pactkit query` (Codegraph-first);
MMD diagrams are VIEWS rendered from the Codegraph index by
`python3 .github/skills/pactkit-visualize/scripts/visualize.py --lazy` (file, `--mode class`, `--mode call` if source changed) (never from a self-built scanner). This skill's script
carries the still-consumed analysis surfaces.

> **Script location**: Use the base directory from the skill invocation header to resolve script paths.

## Prerequisites
- The project must have source files for analysis to produce meaningful output
- The `docs/architecture/graphs/` directory is created by `init_arch`

## Command Reference

### init_arch -- Initialize architecture directory
```
python3 .github/skills/pactkit-visualize/scripts/visualize.py init_arch
```
- Creates `docs/architecture/graphs/` and `docs/architecture/governance/`
- Generates placeholder file `system_design.mmd` (manual diagrams live here;
  machine code graphs are NOT generated anymore)

### impact -- Test files impacted by a changed function
```
python3 .github/skills/pactkit-visualize/scripts/visualize.py impact --entry <func>
```
- Reverse-BFS over callers, mapped to test files (STORY-053)

### blast_radius -- Files/functions affected by a change
```
python3 .github/skills/pactkit-visualize/scripts/visualize.py blast_radius --target <file> | --entry <func> [--depth N]
```
- JSON output; feeds `pactkit-report`'s `--overlay` (STORY-slim-089)

### complexity -- Cyclomatic complexity report
```
python3 .github/skills/pactkit-visualize/scripts/visualize.py complexity [--threshold N] [--format table|json] [--all]
```

### layers -- Architectural layer violations
```
python3 .github/skills/pactkit-visualize/scripts/visualize.py layers
```
- JSON output (violations + layer summary); also feeds `--overlay`

### list_rules -- List governance rules
```
python3 .github/skills/pactkit-visualize/scripts/visualize.py list_rules
```

## Code diagrams: rendered views over Codegraph

`python3 .github/skills/pactkit-visualize/scripts/visualize.py --lazy` (file, `--mode class`, `--mode call` if source changed) renders MMD diagrams
**from the Codegraph index** — Codegraph is the single source of code
facts; the diagrams are regenerable projections for human reading, never a
parallel data source. No index → a clear error (`pactkit sync` first);
there is no fallback scanner. Manual diagrams (system_design, workflow,
Spec diagrams) are unaffected.

## Usage Scenarios
- `project-plan`, `project-act`, and `pactkit-trace` use `pactkit query --json --explain` for analysis.
- `pactkit-doctor` checks graph-provider health and old-MMD cleanup advice.
- `pactkit-audit` consumes complexity/layers; `pactkit-report` consumes the JSON overlays.

## Graph Query Protocol

> **MUST NOT `Read` a full `.mmd` graph file** — graph files are large (50K–120K, 1000–2000+ lines). Full reads waste tokens before any work begins.

### Unified Query Router

```bash
pactkit query --callers atomic_write --json --explain
pactkit query --callees deploy --json --explain
pactkit query --chain atomic_write --json --explain
pactkit query --chain deploy --down --json --explain
pactkit query --explore deployer --json --explain
pactkit query --impact deploy --json --explain
```

The router owns Codegraph health, bounded sync, and provider selection. Configured Codegraph fails closed. Only an explicit `--allow-fallback` may select `text_search`; a healthy empty result never triggers fallback. The MMD-based `builtin_graph` provider is retired and answered with a migration notice.
