# Graphify Usage Guide

This repository uses Graphify to maintain a knowledge graph of the codebase.

## Graphify Outputs

```
graphify-out/
├── graph.json         # The knowledge graph (nodes + edges)
├── GRAPH_REPORT.md    # Human-readable architecture overview
├── graph.html        # Interactive visualization
├── manifest.json      # Extraction metadata
├── cache/             # Cached extraction artifacts
└── memory/            # Saved Q&A results for graph feedback
```

## When to Rebuild

Rebuild when:
- Major refactors have added/removed many files
- The graph is missing (`graph.json` absent)
- The user explicitly requests a rebuild
- `graphify check-update .` reports `needs_update: true`

Do NOT rebuild automatically during normal work sessions.

## Rebuild Commands

```bash
# Full rebuild with clustering and LLM-named communities
graphify .

# Force overwrite even if fewer nodes
graphify update . --force

# Re-cluster and regenerate report without re-extracting
graphify cluster-only .

# Skip clustering, write raw extraction only
graphify update . --no-cluster
```

## Current Status

- Graph exists: `graphify-out/graph.json`
- Graph report exists: `graphify-out/GRAPH_REPORT.md`
- Graph HTML exists: `graphify-out/graph.html`
- Safe query wrapper exists: `scripts/graphify-query-safe.sh`
- Current graph size is large enough that `graphify cluster-only .` may skip HTML unless `GRAPHIFY_VIZ_NODE_LIMIT` is raised

## Safe Querying

**Always use the timeout-wrapped wrapper, not raw `graphify query`:**

```bash
scripts/graphify-query-safe.sh "<question>"
```

The wrapper:
- Sets a 60-second timeout (override: `GRAPHIFY_TIMEOUT_SEC=30 scripts/graphify-query-safe.sh "..."`)
- Points to `graphify-out/graph.json` by default (override: `GRAPHIFY_GRAPH=path/to/graph.json`)
- Streams output so partial results are visible on timeout
- Returns exit code 124 on timeout

For focused architecture questions, prefer the wrapper first. It keeps queries bounded and avoids hanging on large graphs.

## Raw Query (if safe wrapper unavailable)

```bash
graphify query "<question>" --graph graphify-out/graph.json --budget 2000
```

## Query Options

```bash
--dfs              # Use depth-first instead of breadth-first traversal
--context R        # Filter by edge relation type (repeatable)
--budget N         # Cap output at N tokens (default 2000)
```

## Other Graphify Commands

```bash
# Path between two nodes
graphify path "src/environment/runtime_model.py" "src/agents/"

# Plain-language explanation of a node
graphify explain "simulation/environment.py"

# Nodes impacted by a change
graphify affected "src/agents/lstm_agent.py" --depth 3

# Reverse traversal with custom relations
graphify affected "src/training/" --relation "calls" --relation "imports" --depth 2

# Save a Q&A result for graph feedback
graphify save-result --question "..." --answer "..." --type query --nodes "X" "Y" --outcome useful

# Check if extraction is stale
graphify check-update .
```

## OpenCode Graphify Plugin

A project-local plugin (`graphify.js`) injects a knowledge-graph reminder before bash tool calls when the graph exists. This is safe and read-only.

OpenCode should prefer the graph before raw file browsing when the user asks about architecture, dependencies, call paths, or module relationships.

## Graph HTML

Open `graphify-out/graph.html` in a browser for interactive visualization:
- Zoom, pan, search
- Filter by node type or community
- Inspect node connections

## Troubleshooting

| Problem | Solution |
|---|---|
| Query times out | Use `scripts/graphify-query-safe.sh` with lower budget or `--dfs` flag |
| Graph is stale | Run `graphify update . --force` |
| Missing nodes after rebuild | Run `graphify update . --force` to force overwrite |
| Graph report is too large | Read GRAPH_REPORT.md section headers; use targeted query instead |
| graph.html won't load | Increase browser memory, raise `GRAPHIFY_VIZ_NODE_LIMIT`, or use `--no-viz` for large graphs |

## Graph Size

- ~15MB `graph.json`
- ~247KB `GRAPH_REPORT.md`
- ~7MB `graph.html`

## Safety

- Graphify reads and indexes source files only.
- It does not modify source files.
- It does not access secrets, `.env`, or credential files.
- Do not run `graphify hook install` or `graphify uninstall` without explicit approval.
- Do not rebuild the graph casually during routine editing.
