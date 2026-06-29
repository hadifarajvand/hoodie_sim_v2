# Health Check AI Command Center — Plan

## Task Classification
- **Type:** audit / health-check
- **Routing Rule:** OpenCode + RuFlo built-in agents (no custom OpenCode agents)
- **Complexity:** medium
- **Security / Production Sensitivity:** read-only by default

## RuFlo Status
- RuFlo v3.12.4 confirmed running
- Daemon / system status: healthy (uptime 0h 2m)
- Hive-mind: offline (unhealthy queen, degraded workers)
- Swarm: swarm-1782667711753-z3fue8 — terminated (0 active agents)
- Memory: unknown (not measured by system_status)
- No active agents currently running

## Routing Output (hooks.route)
- Matched Pattern: `testing-task` (score 0.32)
- Primary Agent: `coder` (confidence 0.70)
- Alternative Agents: `researcher` (0.60), `tester` (0.50)
- Swarm Recommendation: hierarchical topology; agents: coder, researcher, tester
- Estimated: 30–60 min, medium complexity, success probability 0.70

## Memory Findings
- AgentDB `hierarchicalMemory` queried (episodic, semantic): no prior episodes for this exact task
- Working memory stored at `health-check-agents-status` with 7 registered agents

## Graphify Findings
- `graphify-out/` exists with `graph.json`, `GRAPH_REPORT.md`, `manifest.json`, cache
- Graphify structural memory available; not read in detail this pass to keep scope read-only

## Selected RuFlo Built-In Agents Spawned
1. `coordinator-1` (coordinator)
2. `planner-1` (planner)
3. `coder-1` (coder)
4. `tester-1` (tester)
5. `reviewer-1` (reviewer)
6. `security-auditor-1` (security-auditor)
7. `performance-engineer-1` (performance-engineer)

## Affected Files/Modules
- `AGENTS.md` (project policy)
- `docs/ai-stack/` (AI stack configuration and reports)
- `.opencode/commands/` (command surface)
- `.opencode/agents/` (archived duplicates)
- `.claude-flow/swarm/swarm-state.json` (swarm state)

## Implementation Steps (Health Check)
1. ✅ Run safe status checks
2. ✅ Verify RuFlo system status (daemon/hive/swarm/agent list)
3. ✅ Verify routing behavior with `hooks.route` and `hooks.explain`
4. ✅ Spawn required built-in RuFlo agents
5. ✅ Store agent registration status in working memory
6. ⏳ Generate plan and run log
7. ⏳ Validate findings (read-only checks on command center structure)

## Validation Gates
- [x] Daemon status: healthy
- [x] Agent registration: 7 agents registered
- [x] Hive-mind init status: registered but offline; not needed for this audit
- [x] Routing output present and non-empty
- [ ] Optional: trigger `worker-dispatch` for deepdive or testgaps if desired

## Security Gates
- None triggered; this is a read-only audit
- No auth, payment, secrets, deployment, database, or MCP/tool permission changes

## Production Gates
- None triggered; this is a read-only audit

## Rollback Plan
- No mutations performed; no rollback needed

## Acceptance Criteria
- [x] Task is classified correctly
- [x] Hierarchical coordinator concept is used (coordinator agent spawned)
- [x] RuFlo daemon/hive/swarm status is known
- [x] Routing output is recorded
- [x] Memory findings are recorded
- [x] Graphify availability is confirmed
- [x] Built-in RuFlo agents are spawned/used
- [x] Files changed: none (read-only)
- [x] Validation results recorded
- [ ] Review/security/performance result: no issues (read-only)
- [x] Memory entries stored (`health-check-agents-status`)
- [ ] Run log path: see `docs/run-logs/`
