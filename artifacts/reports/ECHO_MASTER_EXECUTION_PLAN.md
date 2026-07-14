# ECHO Master Execution Plan — Closed-Loop Agent Runbook

## 1. Document control

| Field | Value |
|---|---|
| Plan version | `ECHO-MEP-v4.1` |
| Plan status | `FINAL CLOSED-LOOP RUNBOOK — EXECUTOR + INDEPENDENT REVIEWER/CONTROLLER` |
| Repository | `hadifarajvand/hoodie_sim_v2` |
| Planning-start branch | `main` |
| Planning-start HEAD | `36b2e19ec8dcc422a3ce906e37ef5ff460ac34fe` |
| Planning-start plan blob | `98bd39843dcfddbec429b7bbca1ff6a368e4e116` |
| Audited pre-implementation baseline | `d8dbf131dc4cff3879636853cafa9371a0914d99` |
| Live document title | `مقاله` |
| Live document ID | `17iqZWA0bF5unbyuVYnRiW1IUcr0Ctb2KFw1f5XE2poE` |
| Live proposed-method tab ID | `t.iav4589yyeo7` |
| Live content heading | `III. Proposed Effective Completion via Hybrid Offloading Framework (ECHO)` |
| Google Drive current revision | `270` |
| Google Drive modified time | `2026-07-14T05:40:38.691Z` |
| Connector method revision | `ALtnJHz611-DqkvSCGUC_z6Fe7oTOtKddqKX28Uy-8yxMUchKHt1qIK0ynQUDlus57gMvnBz5VJeXCNzVUVbhwab1h05IlKz0AKes7cQJg` |
| Superseded connector revision | `ALtnJHzzm4hFNZK8DdBeKreoGaZ2RSO7F5oymwXZTjamK8fUxsa71RdvAu-7KkfW25xxeNA3C-Ns0TIbs-kwgO8FwUg1U68nloS7CIA1sg` |
| Historical repository-export revision | `ALtnJHyTLdhKaOnVqfvxB74eKtegK8Hrsx5l2yaYdk68tSHgf-QdYtM6nrsTZrwFDm3DbTUFkeWajyCFP0Eevns2d7r0_twwuuYjD4ZcMQ` |

No tab title is asserted. This file supersedes every earlier plan and `resources/ECHO_multi_agent_phase_runbook.md` whenever they disagree.

## 2. Goal and final deliverables

The goal is to reproduce HOODIE faithfully, freeze a neutral cloud-edge physical simulator, attach ECHO without contaminating HOODIE, verify every ECHO equation and algorithm line, run fair paired evaluation, generate Figures 4–8 from retained outputs, and deliver a clean reproducible artifact set.

Final deliverables are:

1. immutable ECHO and HOODIE authority bundles;
2. canonical HOODIE configuration and topology;
3. immutable paired traces;
4. neutral synchronized physical kernel;
5. faithful per-EA HOODIE learner and six isolated heuristic baselines;
6. frozen HOODIE/base release manifest;
7. ECHO adapter, ERT scheduling, masks, state, reward, event-SMDP, masked DDQL, LSTM, and ECHO-NoLSTM;
8. equation/algorithm coverage and paired pilot evidence;
9. machine-readable evaluation schemas, immutable trace bank, lineages, checkpoints, raw logs, metrics, and confidence intervals;
10. Figures 4–8, fifteen panels, vector/PDF and deterministic 300-dpi PNG exports;
11. final reports, archive redirects, artifact index, and exact rerun script.

## 3. Scientific contracts

### 3.1 Authority order

1. current live ECHO proposed-method tab at the identifiers above;
2. original HOODIE paper PDF/OCR for inherited base mechanics and learning;
3. `research/ECHO_evaluation_spec.md` when it does not conflict with the current live method;
4. topology and PNG-export authorizations;
5. repository code/tests as implementation evidence only;
6. historical reports, snapshots, smoke outputs, checkpoints, and figures as non-authoritative evidence.

A test cannot override a paper equation. Existing code cannot define the method. A new live revision blocks ECHO acceptance until `SRC-001` is repeated.

### 3.2 ECHO non-negotiable behavior

The source lock must verify Equations (1)–(67), Algorithm 1 with 23 numbered lines, and Algorithm 2 with 12 numbered lines. The implementation must preserve:

- independent Bernoulli arrival opportunity for every EA in every decision slot;
- `d_i = t_i^a + δ_i - 1`;
- one direct route decision at arrival and no second destination decision;
- one local waiting queue and one outbound waiting queue per source, excluding active operations;
- one non-preemptive local CPU and one non-preemptive transmitter per source;
- transmission finishing at end of slot `t` is admitted to the destination at the boundary opening `t+1`;
- source-indexed FIFO destination queues and equal public-CPU sharing;
- remaining destination workload in CPU cycles;
- fresh status preferred and LSTM used only for stale/missing status;
- constructive deterministic `O(q²)` ERT ordering: smallest nonnegative ERT, otherwise minimum lateness, then FIFO/stable-ID tie break;
- 30 padded destination feature blocks and 32 canonical outputs: local, horizontal positions 1–30, cloud;
- reward from Equations (55)–(58);
- Equation (59) as one discounted source-EA interval between consecutive actual decisions of that EA;
- no overlapping task-level replay transitions;
- target discount `γ^Δ_(n,m)`;
- masked Dueling Double-DQL from Equations (61)–(67);
- separate supervised LSTM forecasting and no held-out evaluation data in fitting.

### 3.3 Boundary chronology

At the boundary opening slot `t`:

1. apply service/transmission completions generated at the end of `t-1` and admissions due at `t`;
2. resolve outcomes and attach task rewards to the source-EA interval already open;
3. obtain fresh status or stale/missing LSTM estimate;
4. remove expired waiting tasks without preempting active work;
5. observe all same-slot arrivals;
6. for each arriving EA, close its previous interval before opening the new decision;
7. estimate, mask, choose, and admit;
8. rebuild affected waiting orders and start idle source resources;
9. schedule destination queues;
10. execute exactly one slot of active service;
11. update histories/LSTM and perform learning/target-copy work;
12. at `T+1`, resolve terminal outcomes and close every open interval.

## 4. Current code ownership map

| Current repository condition | Owning task |
|---|---|
| `src/environment/gym_adapter.py` imports `src.echo_action_space` and `src.echo_ert` | `BASE-005` removes ECHO imports before freeze |
| `src/environment/evaluation_gym_adapter.py` contains ECHO-specific conditional scheduling | `BASE-005` extracts neutral hooks; `ECHO-001` later attaches ECHO without changing frozen files |
| mutable trace dataclasses / possible regeneration | `BASE-004` |
| one source transmitter not yet proven independently of destination keys | `BASE-008` |
| next-boundary admission requires exact event staging tests | `BASE-010` |
| `HOODIE` alias resolves to generic `ADAPTIVE` policy | `BASE-019` |
| paper-state builder contains placeholder zero forecast behavior | `BASE-015` |
| shared policy/learner path does not prove one learner per EA | `BASE-016` |
| 32-output ECHO action code exists but is not source-locked acceptance | `ECHO-009` |
| event-SMDP accumulator exists but boundary ownership needs full test | `ECHO-014` and `ECHO-018` |
| ECHO training processes decision events before same-boundary resolution events | `ECHO-018` |
| logging/evaluation schemas currently appear after pilot in the old sequence | `EVAL-001` now runs before `ECHO-011` |

Existing implementation is retained as candidate code. Each owner task must accept unchanged, repair, isolate, or supersede it based on authority and tests.

## 5. Deterministic path grammars

Directory wildcards are not permissions. A card may write only explicitly listed files or files generated by one of these exact grammars.

### G1 — Executor evidence

For task `<ID>`:

- `artifacts/task_evidence/<ID>/report.md`
- `artifacts/task_evidence/<ID>/status.json`
- `artifacts/task_evidence/<ID>/commands.txt`
- `artifacts/task_evidence/<ID>/test_output.txt`
- `artifacts/task_evidence/<ID>/changed_files.json`
- `artifacts/task_evidence/<ID>/hashes.json`
- `artifacts/task_evidence/<ID>/git_diff.patch`

### G2 — Reviewer evidence

For task `<ID>` and attempt `<A>`:

- `artifacts/task_reviews/<ID>/attempt_<A>/review.md`
- `artifacts/task_reviews/<ID>/attempt_<A>/status.json`
- `artifacts/task_reviews/<ID>/attempt_<A>/commands.txt`
- `artifacts/task_reviews/<ID>/attempt_<A>/test_output.txt`
- `artifacts/task_reviews/<ID>/attempt_<A>/diff_audit.json`

### G3 — Control state

- `artifacts/control/EXECUTION_STATE.json`
- `artifacts/control/NEXT_TASK.json`

`EXECUTION_STATE.json` stores plan version, current main SHA, status and attempt for all 73 IDs, review SHA, merge SHA, and blocker. `NEXT_TASK.json` stores exactly one authorized task ID or `null`.

### G4 — Trace-bank file

For `trace_id = <scenario_id>__seed<two_digit_seed>__<config_sha12>`:

- `artifacts/evaluation/trace_bank/<trace_id>.json`
- `artifacts/evaluation/trace_bank/<trace_id>.sha256`

The index is `artifacts/evaluation/trace_bank/index.json`.

### G5 — Run output

For `run_id = <method>__<scenario_id>__n<N>__seed<two_digit_seed>__<config_sha12>`:

- `artifacts/evaluation/runs/<run_id>/run_manifest.json`
- `artifacts/evaluation/runs/<run_id>/task_log.jsonl`
- `artifacts/evaluation/runs/<run_id>/decision_log.jsonl`
- `artifacts/evaluation/runs/<run_id>/episode_metrics.csv`
- `artifacts/evaluation/runs/<run_id>/training_metrics.csv` only for learning runs;
- `artifacts/evaluation/runs/<run_id>/checkpoint.pt` only for learning runs;
- `artifacts/evaluation/runs/<run_id>/DONE.sha256`

No other filename under a run directory is permitted.

### G6 — Aggregated panel output

For panel ID in `f5a,f5b,f6a,f6b,f6c,f6d,f6e,f7a,f7b,f7c,f7d,f7e,f7f,f8`:

- `artifacts/metrics/seed_level/<panel_id>.csv`
- `artifacts/metrics/panel_level/<panel_id>.csv`
- `artifacts/metrics/confidence_intervals/<panel_id>.csv`

### G7 — Figure output

For figure number `<N>`:

- `artifacts/figures/vector/figure<N>.svg`
- `artifacts/figures/vector/figure<N>.pdf`
- `artifacts/figures/png_300dpi/figure<N>.png`
- `artifacts/figures/manifests/figure<N>.json`

Panel CSVs are `artifacts/figures/panel_exports/<panel_id>.csv`.

### G8 — Archive output

For an approved source path with SHA-256 `<sha>` and basename `<name>`:

- `artifacts/archive/superseded/<sha>__<name>`

The only archive index is `artifacts/archive/archive_manifest.json`. Eligibility must come from `artifacts/classification/artifact_inventory.json`.

## 6. Closed-loop execution protocol

### 6.1 Roles

- **Executor:** receives one explicit task ID and attempt, edits only its card allowlist plus G1, commits, and stops.
- **Independent reviewer/controller:** inspects the task branch read-only, reruns commands, grants PASS/REWORK/BLOCKED, merges only on PASS, updates plan status plus G2/G3, computes one next task, and stops.
- The executor and reviewer must be different agent invocations. The reviewer must not repair implementation code.

Default execution is sequential. Parallel execution is disabled.

### 6.2 Executor branch and stop rules

The controller authorizes branch `task/<lowercase-id>-r<attempt>` from the `main_head` in `NEXT_TASK.json`.

The executor must:

1. verify the current plan version and `NEXT_TASK.json`;
2. verify clean tree and exact starting SHA;
3. create/check out the authorized branch;
4. read only the card's required reads;
5. edit only the card's explicit writes plus G1;
6. run the exact command;
7. write complete evidence;
8. set evidence status to `IMPLEMENTED_PENDING_REVIEW`, `BLOCKED_EXTERNAL`, `REWORK`, `PLAN_CHANGE_REQUIRED`, or `STALE_BRANCH`;
9. commit `<ID>: <exact title>`;
10. stop without merge, push to main, plan edit, or next-task execution.

A `SRC-001` executor that lacks source access writes `BLOCKED_EXTERNAL` evidence and stops. It must not execute `BASE-001` in that invocation.

### 6.3 Controller bootstrap

Before the first executor, the reviewer/controller runs in `BOOTSTRAP` mode:

1. verify `main` equals the planning-start HEAD or refresh this plan through a planning-only change;
2. initialize `artifacts/control/EXECUTION_STATE.json` from the 73 registry rows;
3. set `artifacts/control/NEXT_TASK.json` to `SRC-001`, attempt 1, branch `task/src-001-r1`, and the current main SHA;
4. commit only G3 with `CONTROL BOOTSTRAP: initialize execution state`;
5. stop after printing the exact `SRC-001` executor invocation.

### 6.4 Reviewer/controller algorithm

The reviewer/controller is the only actor allowed to write the master plan and G2/G3.

For task `<ID>` attempt `<A>`:

1. read plan, control state, task evidence, task branch, and starting/main SHAs;
2. verify branch ancestry; if main changed after authorization, record `STALE_BRANCH`, do not merge, and authorize a new attempt from current main;
3. compute `git diff --name-only <start_sha>..<task_sha>`;
4. require exact equality with `changed_files.json`;
5. require every changed path to be in the card allowlist or G1;
6. inspect every diff and evidence claim;
7. rerun the exact card command in a clean review worktree;
8. evaluate every pass criterion;
9. write G2 only; never edit task implementation;
10. on failure: do not merge, set `REWORK` or the exact blocker, increment attempt, and authorize the same task when repair is possible;
11. on PASS: merge with `--no-ff`, write G2/G3, update only the selected registry status and dashboard in this plan, and commit `CONTROL <ID>: verify and advance`;
12. recompute statuses and exactly one `NEXT_TASK`;
13. stop after printing the next executor invocation.

If repository policy prevents merge, record `MERGE_BLOCKED` and stop. Do not substitute a different merge process.

### 6.5 Status recomputation

`VERIFIED_COMPLETE` remains complete unless explicitly reopened by source/code invalidation.

For every other task:

- `READY` when every dependency is `VERIFIED_COMPLETE` and the task has no unresolved blocker;
- `BLOCKED` otherwise;
- `REWORK` remains selected for the next attempt;
- `BLOCKED_EXTERNAL` remains blocked until access is restored;
- `PLAN_CHANGE_REQUIRED` stops the whole controller;
- `STALE_BRANCH` creates a new attempt from current main.

When multiple tasks are READY, select the earliest task in the registry order. `NEXT_TASK.json` is the sole execution authorization; other READY tasks must not run.

### 6.6 Source change and frozen-base invalidation

- A changed live ECHO revision reopens `SRC-001` and blocks all incomplete ECHO/evaluation/figure tasks.
- Any change to a file hashed by `FREEZE-001` invalidates the freeze and reopens the owning base task plus downstream tasks.
- Any unaudited implementation commit to main reopens `AUDIT-002` before further execution.

## 7. Master task registry — source of truth

Initial status totals: 5 `VERIFIED_COMPLETE`, 2 `READY`, 66 `BLOCKED`; total 73.

### Phase 0 — source, audit, and control (6)

| ID | Status | Dependencies | Title |
|---|---|---|---|
| SRC-001 | READY | NONE | Lock current live ECHO source and close 69-row audit |
| SRC-002 | VERIFIED_COMPLETE | NONE | Maintain HOODIE paper evidence registry |
| AUDIT-001 | VERIFIED_COMPLETE | NONE | Maintain current code-path inventory |
| AUDIT-002 | VERIFIED_COMPLETE | NONE | Reconcile historical completion claims |
| PLAN-001 | VERIFIED_COMPLETE | NONE | Maintain closed-form execution plan |
| CLEAN-001 | VERIFIED_COMPLETE | NONE | Classify existing artifacts |

### Phase 1 — faithful base HOODIE (23)

| ID | Status | Dependencies | Title |
|---|---|---|---|
| BASE-001 | READY | PLAN-001, CLEAN-001 | Freeze canonical HOODIE Table-4 configuration |
| BASE-002 | BLOCKED | BASE-001 | Freeze approved topology and scalable topology rule |
| BASE-003 | BLOCKED | BASE-002 | Validate independent per-EA arrivals and 100+10 slots |
| BASE-004 | BLOCKED | BASE-003 | Make paired traces immutable and directly consumable |
| BASE-006 | BLOCKED | BASE-004 | Freeze hand-calculated base slot contract |
| BASE-005 | BLOCKED | BASE-006 | Extract neutral synchronized multi-EA kernel and remove ECHO contamination |
| BASE-007 | BLOCKED | BASE-006 | Implement/accept private FIFO waiting and active separation |
| BASE-008 | BLOCKED | BASE-006 | Implement/accept one outbound FIFO/transmitter per source |
| BASE-009 | BLOCKED | BASE-008 | Preserve one selected destination through transmission |
| BASE-010 | BLOCKED | BASE-009 | Enforce next-boundary destination admission |
| BASE-011 | BLOCKED | BASE-006 | Implement source-indexed destination FIFO queues |
| BASE-012 | BLOCKED | BASE-011 | Implement equal public-CPU sharing |
| BASE-013 | BLOCKED | BASE-005, BASE-007, BASE-010, BASE-012 | Implement exact HOODIE action semantics |
| BASE-014 | BLOCKED | BASE-013 | Implement exact HOODIE state/history |
| BASE-015 | BLOCKED | BASE-014 | Implement real HOODIE LSTM forecast |
| BASE-016 | BLOCKED | BASE-015 | Implement one independent HOODIE learner per EA |
| BASE-017 | BLOCKED | BASE-016 | Implement original HOODIE reward/replay timing |
| BASE-018 | BLOCKED | BASE-017 | Implement paper-correct HOODIE Dueling Double-DQN |
| BASE-019 | BLOCKED | BASE-018 | Validate RO/FLC/VO/HO/BCO/MLEO isolation |
| BASE-020 | BLOCKED | BASE-019 | Run complete deterministic base invariant suite |
| BASE-021 | BLOCKED | BASE-020 | Run bounded HOODIE runtime/learner smoke |
| BASE-022 | BLOCKED | BASE-021 | Reproduce HOODIE experiment organization/trends |
| FREEZE-001 | BLOCKED | BASE-022 | Freeze validated neutral simulator and HOODIE baseline |

### Phase 2 — ECHO on frozen base (20)

| ID | Status | Dependencies | Title |
|---|---|---|---|
| ECHO-001 | BLOCKED | FREEZE-001, SRC-001 | Attach ECHO adapter to frozen neutral hooks |
| ECHO-002 | BLOCKED | ECHO-001 | Implement Equations (1)–(8) lifecycle/dispatch |
| ECHO-003 | BLOCKED | ECHO-002 | Implement Equations (9)–(11) local estimate |
| ECHO-004 | BLOCKED | ECHO-003 | Implement Equations (12)–(16) outbound estimate |
| ECHO-005 | BLOCKED | ECHO-004 | Implement Equations (17)–(25) destination model |
| ECHO-006 | BLOCKED | ECHO-005 | Implement Equations (26)–(28) history/LSTM inputs |
| ECHO-007 | BLOCKED | ECHO-006 | Implement Equation (29) local queue ERT ordering |
| ECHO-008 | BLOCKED | ECHO-007 | Implement Equation (30) outbound ERT ordering |
| ECHO-009 | BLOCKED | ECHO-008 | Implement 32-position canonical action space |
| ECHO-010 | BLOCKED | ECHO-009 | Implement Equations (42)–(46) mask/fallback |
| ECHO-011 | BLOCKED | ECHO-010, EVAL-001 | Implement Equations (47)–(50) pending records and schema-compliant decision logs |
| ECHO-012 | BLOCKED | ECHO-011 | Implement Equations (51)–(54) normalized state |
| ECHO-013 | BLOCKED | ECHO-012 | Implement Equations (55)–(58) task reward |
| ECHO-014 | BLOCKED | ECHO-013 | Implement Equations (59)–(60) event intervals |
| ECHO-015 | BLOCKED | ECHO-014 | Implement Equations (61)–(67) masked DDQL |
| ECHO-016 | BLOCKED | ECHO-015 | Implement fresh/stale status and LSTM training |
| ECHO-017 | BLOCKED | ECHO-016 | Implement isolated ECHO-NoLSTM |
| ECHO-018 | BLOCKED | ECHO-017 | Implement exact Algorithm 1/2 chronology |
| ECHO-019 | BLOCKED | ECHO-018 | Run deterministic ECHO unit/smoke suite |
| ECHO-020 | BLOCKED | ECHO-019 | Produce equation coverage and paired pilot gate |

### Phase 3 — schemas and authoritative evaluation (12)

| ID | Status | Dependencies | Title |
|---|---|---|---|
| EVAL-001 | BLOCKED | SRC-001, BASE-004 | Freeze logging, evaluation, and 15-panel schemas before ECHO logging |
| EVAL-002 | BLOCKED | ECHO-020, EVAL-001 | Generate immutable paired trace bank |
| EVAL-003 | BLOCKED | EVAL-002 | Freeze config/topology/checkpoint lineage |
| EVAL-004 | BLOCKED | EVAL-003 | Validate all method adapters on common inputs |
| EVAL-005 | BLOCKED | EVAL-004 | Measure throughput and freeze shard budget |
| EVAL-006 | BLOCKED | EVAL-005 | Run Figure-5 validation sweeps |
| EVAL-007 | BLOCKED | EVAL-006 | Train equal-budget final method checkpoints |
| EVAL-008 | BLOCKED | EVAL-007 | Run 10×200 held-out paired evaluation |
| EVAL-009 | BLOCKED | EVAL-008 | Validate generated/completed/dropped accounting |
| EVAL-010 | BLOCKED | EVAL-008 | Validate no masked ECHO action |
| EVAL-011 | BLOCKED | EVAL-008 | Validate trace/config/topology/checkpoint hashes |
| EVAL-012 | BLOCKED | EVAL-009, EVAL-010, EVAL-011 | Aggregate seed metrics and 95% CIs |

### Phase 4 — figures, reports, cleanup, handoff (12)

| ID | Status | Dependencies | Title |
|---|---|---|---|
| FIG-001 | BLOCKED | BASE-002 | Render Figure 4 topology |
| FIG-002 | BLOCKED | EVAL-006 | Render Figure 5(a–b) |
| FIG-003 | BLOCKED | EVAL-012 | Render Figure 6(a–e) |
| FIG-004 | BLOCKED | EVAL-012 | Render Figure 7(a–f) |
| FIG-005 | BLOCKED | EVAL-012 | Render Figure 8 |
| FIG-006 | BLOCKED | FIG-001, FIG-002, FIG-003, FIG-004, FIG-005 | Validate all vector/PNG exports and lineage |
| REPORT-001 | BLOCKED | BASE-022, FREEZE-001 | Write final HOODIE reproduction report |
| REPORT-002 | BLOCKED | ECHO-020 | Write final ECHO implementation report |
| REPORT-003 | BLOCKED | EVAL-012, FIG-006 | Write final evaluation/figure report |
| CLEAN-002 | BLOCKED | REPORT-001, REPORT-002, REPORT-003 | Archive superseded artifacts without deletion |
| CLEAN-003 | BLOCKED | CLEAN-002 | Remove canonical-path ambiguity without deletion |
| HANDOFF-001 | BLOCKED | CLEAN-003 | Produce final artifact index and exact rerun commands |

## 8. Complete task cards

### SRC-001 — Lock current live ECHO source and close 69-row audit

- Dependencies: NONE.
- Required reads: Section 1 identifiers; current live Google Doc tab; `research/ECHO_method_spec.md`; existing `research/authority/echo/live/ECHO_PROPOSED_METHOD.md`; this plan.
- Allowed writes: `research/authority/echo/live/ECHO_PROPOSED_METHOD.md`; `research/authority/echo/live/source_metadata.json`; `research/authority/echo/live/SHA256SUMS`; `artifacts/audits/echo_live_revision_audit.md`; `scripts/authority/verify_echo_source_lock.py`; `tests/unit/test_echo_source_lock.py`; G1.
- Ordered operations: Confirm Drive revision remains 270 and connector revision remains the recorded value; export only the proposed-method tab; normalize line endings only; hash raw and normalized content; enumerate Equations 1–67 and Algorithms 1–2; verify line counts 23/12; classify 69 rows as MATCH/CHANGED/ADDED/REMOVED/AMBIGUOUS; map every non-MATCH row to one task and one exact test path.
- Exact command: `python3 scripts/authority/verify_echo_source_lock.py --snapshot research/authority/echo/live/ECHO_PROPOSED_METHOD.md --metadata research/authority/echo/live/source_metadata.json --checksums research/authority/echo/live/SHA256SUMS --audit artifacts/audits/echo_live_revision_audit.md && python3 -m pytest tests/unit/test_echo_source_lock.py -q`.
- Acceptance: Identifiers/revisions match; hashes verify; 67 equations and 2 algorithms present; 69/69 rows classified; no unsupported tab title; every change has task/test consequence.
- Stop/rollback: If access is absent, write G1 with `BLOCKED_EXTERNAL` and stop. If the revision changed, write `PLAN_CHANGE_REQUIRED` and stop without replacing authority files.

### SRC-002 — Maintain HOODIE paper evidence registry

- Dependencies: NONE.
- Required reads: `resources/papers/hoodie/ocr/merged.md`; `resources/papers/hoodie/ocr/merged.txt`; `artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json`; `src/analysis/paper_mechanism_registry.py`.
- Allowed writes: `src/analysis/paper_mechanism_registry.py`; `artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json`; `artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.md`; `tests/unit/test_paper_mechanism_registry.py`; `tests/integration/test_paper_mechanism_registry_flow.py`; G1.
- Ordered operations: Preserve exact page/table/equation provenance; classify values PAPER_EXPLICIT/PAPER_DERIVED/APPROVED_CLARIFICATION/UNRESOLVED; exclude ECHO-only semantics.
- Exact command: `python3 -m pytest tests/unit/test_paper_mechanism_registry.py tests/integration/test_paper_mechanism_registry_flow.py -q`.
- Acceptance: Every Phase-1 mechanism has a source location and classification; no ECHO behavior is attributed to HOODIE.
- Stop/rollback: Already VERIFIED_COMPLETE. Execute only when the controller reopens it after a paper-evidence change.

### AUDIT-001 — Maintain current code-path inventory

- Dependencies: NONE.
- Required reads: `src`; `tests`; `src/analysis/hoodie_proposed_fidelity/implementation_scan.py`; existing implementation-scan outputs.
- Allowed writes: `src/analysis/hoodie_proposed_fidelity/implementation_scan.py`; `tests/unit/test_hoodie_proposed_fidelity_implementation_scan.py`; `artifacts/analysis/hoodie-proposed-fidelity-implementation-scan.json`; `artifacts/analysis/hoodie-proposed-fidelity-implementation-scan.md`; G1.
- Ordered operations: Enumerate runtime entry points, clocks, queue/resource ownership, policy/learner paths, evaluation runners, and artifact producers; verify every path at the tested SHA.
- Exact command: `python3 -m pytest tests/unit/test_hoodie_proposed_fidelity_implementation_scan.py -q`.
- Acceptance: Every implementation area maps to one task owner; no completion inferred from names or commit titles.
- Stop/rollback: Already VERIFIED_COMPLETE. Reopen after a material path or architecture change.

### AUDIT-002 — Reconcile historical completion claims

- Dependencies: NONE.
- Required reads: Git history after the last audited SHA; `artifacts/reports`; `artifacts/test_triage`; readiness-audit outputs.
- Allowed writes: `src/analysis/hoodie_training_foundation_readiness_audit/readiness.py`; `tests/unit/test_hoodie_training_foundation_readiness_audit.py`; `artifacts/analysis/hoodie-training-foundation-readiness-audit/hoodie-training-foundation-readiness-audit.json`; `artifacts/analysis/hoodie-training-foundation-readiness-audit/hoodie-training-foundation-readiness-audit.md`; G1.
- Ordered operations: Classify every implementation commit as accepted evidence, potentially reusable, premature, historical, unresolved, or revert candidate; map changed files to task cards.
- Exact command: `python3 -m pytest tests/unit/test_hoodie_training_foundation_readiness_audit.py -q`.
- Acceptance: No unaudited implementation commit remains; every current file has one owner task.
- Stop/rollback: Already VERIFIED_COMPLETE. Any unaudited implementation commit to main reopens this card.

### PLAN-001 — Maintain closed-form execution plan

- Dependencies: NONE.
- Required reads: This plan; current Git HEAD; G3 when it exists.
- Allowed writes: This plan; G1 only.
- Ordered operations: Validate 73 unique registry IDs, 73 unique cards, dependency existence, acyclic graph, status total, required controller/executor prompts, BASE-005 decontamination, ECHO-001 frozen-hook restriction, ECHO-011 dependency on EVAL-001, and absence of wildcard permissions.
- Exact command: `python3 - <<'PY'
import pathlib,re
p=pathlib.Path('artifacts/reports/ECHO_MASTER_EXECUTION_PLAN.md').read_text()
reg=re.findall(r'^\| ((?:SRC|AUDIT|PLAN|CLEAN|BASE|FREEZE|ECHO|EVAL|FIG|REPORT|HANDOFF)-\d{3}) \|',p,re.M)
cards=re.findall(r'^### ((?:SRC|AUDIT|PLAN|CLEAN|BASE|FREEZE|ECHO|EVAL|FIG|REPORT|HANDOFF)-\d{3}) —',p,re.M)
assert len(reg)==73 and len(set(reg))==73
assert len(cards)==73 and set(cards)==set(reg)
assert not any('*' in line for line in p.splitlines() if line.startswith('- Allowed writes:'))
assert 'ECHO-011 | BLOCKED | ECHO-010, EVAL-001' in p
assert 'Independent reviewer/controller prompt' in p
print('plan structure PASS')
PY`.
- Acceptance: All assertions pass; registry/card IDs equal; no missing/self dependency; DAG is acyclic; initial totals are 5/2/66.
- Stop/rollback: Already VERIFIED_COMPLETE for v4.1. Any change requires a planning-only commit and fresh validation.

### CLEAN-001 — Classify existing artifacts

- Dependencies: NONE.
- Required reads: `artifacts`; `research`; existing artifact indexes and triage outputs.
- Allowed writes: `src/analysis/artifact_classifier.py`; `tests/unit/test_artifact_classification.py`; `artifacts/classification/artifact_inventory.json`; `artifacts/classification/artifact_inventory.md`; `artifacts/classification/reference_inventory.json`; G1.
- Ordered operations: Classify every artifact authoritative/historical/superseded/smoke/synthetic/unresolved; create exact `archive_eligible_paths` and `editable_reference_files` arrays; never delete.
- Exact command: `python3 -m pytest tests/unit/test_artifact_classification.py -q`.
- Acceptance: No historical figure/checkpoint/report is cited as final; every cleanup path is manifest-controlled.
- Stop/rollback: Already VERIFIED_COMPLETE. Reopen after new unclassified artifact families appear.

### BASE-001 — Freeze canonical HOODIE Table-4 configuration

- Dependencies: PLAN-001, CLEAN-001.
- Required reads: `resources/papers/hoodie/ocr/merged.md`; `resources/papers/hoodie/ocr/merged.txt`; `configs/simulation.yaml`; `configs/runtime_model.yml`; `configs/experiments/exp_small_deterministic.json`; paper registry; topology authorization.
- Allowed writes: `configs/authoritative/hoodie_table4.yaml`; `configs/authoritative/hoodie_table4.schema.json`; `tests/unit/test_hoodie_table4_config.py`; `artifacts/authority/hoodie/table4_manifest.json`; G1.
- Ordered operations: Encode 20 EAs; 100 decision + 10 drain slots; independent arrivals P=.5; task sizes 2.0–5.0 Mbits by .1; density .297 Gcycles/Mbit; slot .1s; timeout 20 slots/2s; paper-supported edge/cloud capacities, rates, and learning parameters; classify each value and compare current configs.
- Exact command: `python3 -m pytest tests/unit/test_hoodie_table4_config.py -q`.
- Acceptance: Schema validates; every value has unit/source/classification; hashes recorded; no unresolved value promoted; smoke configs remain non-authoritative.
- Stop/rollback: Unresolved Table-4 value yields REWORK; never guess or borrow ECHO values.

### BASE-002 — Freeze approved topology and scalable topology rule

- Dependencies: BASE-001.
- Required reads: `src/environment/topology.py`; `resources/papers/hoodie/recovered/user-approved-assumption-registry.json`; topology authorization; BASE-001 outputs.
- Allowed writes: `configs/authoritative/hoodie_topology.json`; `tests/unit/test_hoodie_topology_authority.py`; `artifacts/authority/hoodie/topology/adjacency.csv`; `artifacts/authority/hoodie/topology/edge_list.csv`; `artifacts/authority/hoodie/topology/topology.json`; `artifacts/authority/hoodie/topology/topology.svg`; `artifacts/authority/hoodie/topology/topology_300dpi.png`; `artifacts/authority/hoodie/topology/SHA256SUMS`; update `src/environment/topology.py` only when the test proves mismatch; G1.
- Ordered operations: Freeze exact 20-EA anchor; verify `G_N=5K_(N/5)` only for N divisible by 5; deterministic N=10/15/20/25/30 generation, coordinates, metrics, and direct SVG/PNG export.
- Exact command: `python3 -m pytest tests/unit/test_hoodie_topology_authority.py -q`.
- Acceptance: N=20 equals approved anchor; deterministic hashes; no self/illegal edge; exact output files exist.
- Stop/rollback: Never replace the anchor with a visually similar graph.

### BASE-003 — Validate independent per-EA arrivals and 100+10 slots

- Dependencies: BASE-002.
- Required reads: `src/evaluation/trace_protocol.py`; BASE-001/002 outputs; `tests/unit/test_trace_protocol_paper_semantics.py`.
- Allowed writes: `src/evaluation/trace_protocol.py`; `tests/unit/test_trace_protocol_paper_semantics.py`; `tests/unit/test_trace_expected_arrivals.py`; G1.
- Ordered operations: Verify one Bernoulli draw per EA per decision slot; no drain arrivals; exact sizes/density/deadline; stable `(arrival,source,task_id)` ordering; deterministic metadata.
- Exact command: `python3 -m pytest tests/unit/test_trace_protocol_paper_semantics.py tests/unit/test_trace_expected_arrivals.py -q`.
- Acceptance: P=0 gives 0; P=1 gives N×100; repeated-seed N=20,P=.5 mean is centered on 1000; same seed gives exact blueprints; slots 100–109 contain none.
- Stop/rollback: Do not alter draw order to force a preferred single-seed count.

### BASE-004 — Make paired traces immutable and directly consumable

- Dependencies: BASE-003.
- Required reads: `src/evaluation/trace_protocol.py`; `src/environment/trace_source.py`; `src/evaluation/runner.py`; `src/environment/evaluation_gym_adapter.py`.
- Allowed writes: `src/evaluation/trace_protocol.py`; `src/environment/trace_source.py`; `src/evaluation/runner.py`; `src/environment/evaluation_gym_adapter.py`; `tests/unit/test_trace_immutability.py`; `tests/integration/test_paired_trace_identity.py`; G1.
- Ordered operations: Make blueprint/trace frozen; add canonical serialization/SHA; consume supplied traces without regeneration; instantiate fresh mutable runtime Task objects per method.
- Exact command: `python3 -m pytest tests/unit/test_trace_immutability.py tests/integration/test_paired_trace_identity.py -q`.
- Acceptance: Mutation raises; bytes/hash identical across methods; supplied trace bypasses generation; runtime mutation cannot change blueprint.
- Stop/rollback: Do not cache mutable runtime Task objects in the trace bank.

### BASE-006 — Freeze hand-calculated base slot contract

- Dependencies: BASE-004.
- Required reads: HOODIE registry; `src/environment/gym_adapter.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/slot_engine.py`; queue files.
- Allowed writes: `docs/contracts/hoodie_slot_contract.md`; `tests/fixtures/hoodie_slot_timelines.json`; `tests/unit/test_hoodie_slot_contract_vectors.py`; G1.
- Ordered operations: Manually specify same-slot arrivals, local service, outbound wait, transmission, next-boundary admission, destination service, waiting expiration, late active completion, and drain chronology without ECHO reward/mask/ERT semantics.
- Exact command: `python3 -m pytest tests/unit/test_hoodie_slot_contract_vectors.py -q`.
- Acceptance: All hand vectors are internally consistent and distinguish boundary events from end-of-slot service.
- Stop/rollback: Runtime code is read-only here; mismatches belong to BASE-005/007–012.

### BASE-005 — Extract neutral synchronized multi-EA kernel and remove ECHO contamination

- Dependencies: BASE-006.
- Required reads: BASE-006 contract; `src/environment/gym_adapter.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/slot_engine.py`; `src/echo_action_space.py`; `src/echo_ert.py`; `src/echo_queue_ordering.py`.
- Allowed writes: `src/environment/gym_adapter.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/slot_engine.py`; `src/environment/method_hooks.py`; `tests/unit/test_hoodie_slot_engine.py`; `tests/integration/test_same_slot_multi_ea.py`; `tests/integration/test_neutral_kernel_imports.py`; `docs/contracts/neutral_kernel_contract.md`; G1.
- Ordered operations: Remove every shared-kernel import of `src.echo_*`, event-SMDP, ECHO state/mask/reward, and method-name-prefix branching; define neutral hook protocols with FIFO/no-op defaults; process all same-slot decisions then one physical advance; preserve ECHO modules outside the kernel for later attachment.
- Exact command: `python3 -m pytest tests/unit/test_hoodie_slot_engine.py tests/integration/test_same_slot_multi_ea.py tests/integration/test_neutral_kernel_imports.py -q`.
- Acceptance: K arrivals yield K decisions and one advance; previous-boundary events precede decisions; AST/import scan finds zero ECHO imports in shared kernel; base behavior matches BASE-006.
- Stop/rollback: If neutral hooks cannot support later ECHO without modifying frozen files, return PLAN_CHANGE_REQUIRED now; do not defer decontamination to ECHO-001.

### BASE-007 — Implement/accept private FIFO waiting and active separation

- Dependencies: BASE-006.
- Required reads: `src/environment/private_queue.py`; `src/environment/execution_helper.py`; `src/environment/evaluation_gym_adapter.py`; BASE-006 vectors.
- Allowed writes: `src/environment/private_queue.py`; `src/environment/execution_helper.py`; `src/environment/evaluation_gym_adapter.py`; `tests/unit/test_private_queue_lifecycle.py`; `tests/unit/test_fifo_ordering.py`; `tests/unit/test_queue_waiting_time.py`; G1.
- Ordered operations: Separate waiting and active task; admission is not service start; active non-preemptive; waiting FIFO; expire waiting before selection; late active outcome per contract.
- Exact command: `python3 -m pytest tests/unit/test_private_queue_lifecycle.py tests/unit/test_fifo_ordering.py tests/unit/test_queue_waiting_time.py -q`.
- Acceptance: Start timestamp on first CPU slot only; active never reordered; inclusive completion exact; waiting tasks consume no cycles.
- Stop/rollback: ERT ordering is forbidden in HOODIE private queues.

### BASE-008 — Implement/accept one outbound FIFO/transmitter per source

- Dependencies: BASE-006.
- Required reads: `src/environment/offloading_queue.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/link_rate_config.py`.
- Allowed writes: `src/environment/offloading_queue.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/link_rate_config.py`; `tests/unit/test_single_source_transmitter.py`; `tests/integration/test_outbound_fifo.py`; G1.
- Ordered operations: Represent one physical outbound FIFO/transmitter per source; destination remains task metadata; admission is not transmission start; active transfer non-preemptive; waiting FIFO.
- Exact command: `python3 -m pytest tests/unit/test_single_source_transmitter.py tests/integration/test_outbound_fifo.py -q`.
- Acceptance: Different-destination tasks from one source never overlap; different sources may transmit; head starts only when source transmitter is idle.
- Stop/rollback: Do not use `(source,destination)` as physical resource identity.

### BASE-009 — Preserve one selected destination through transmission

- Dependencies: BASE-008.
- Required reads: `src/environment/task.py`; `src/environment/environment.py`; `src/environment/gym_adapter.py`; `src/environment/evaluation_gym_adapter.py`.
- Allowed writes: `src/environment/task.py`; `src/environment/environment.py`; `src/environment/gym_adapter.py`; `src/environment/evaluation_gym_adapter.py`; `tests/unit/test_destination_retention.py`; G1.
- Ordered operations: Store destination at arrival decision; preserve through queue, completion event, admission, serialization, and logs; reject second route choice.
- Exact command: `python3 -m pytest tests/unit/test_destination_retention.py -q`.
- Acceptance: Destination immutable after admission; task reaches exactly selected queue; route lineage survives serialization.
- Stop/rollback: Do not infer destination from current topology later.

### BASE-010 — Enforce next-boundary destination admission

- Dependencies: BASE-009.
- Required reads: `src/environment/slot_engine.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/public_queue.py`; BASE-006 vectors.
- Allowed writes: `src/environment/slot_engine.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/public_queue.py`; `tests/unit/test_next_boundary_admission.py`; `tests/integration/test_transmission_timeline.py`; G1.
- Ordered operations: Stage transmission completion at end t; admit at opening t+1; prohibit destination CPU in t; cover one/multi-slot transfer and terminal drain.
- Exact command: `python3 -m pytest tests/unit/test_next_boundary_admission.py tests/integration/test_transmission_timeline.py -q`.
- Acceptance: Timestamps match vectors; no same-slot destination processing; no duplicate/lost completion.
- Stop/rollback: Metadata-only off-by-one fixes are insufficient.

### BASE-011 — Implement source-indexed destination FIFO queues

- Dependencies: BASE-006.
- Required reads: `src/environment/public_queue.py`; `src/environment/gym_adapter.py`; `src/environment/evaluation_gym_adapter.py`.
- Allowed writes: `src/environment/public_queue.py`; `src/environment/gym_adapter.py`; `src/environment/evaluation_gym_adapter.py`; `tests/unit/test_source_indexed_public_queues.py`; G1.
- Ordered operations: Key destination queues by `(destination,source)`; FIFO within each; explicit active head; one task in one queue.
- Exact command: `python3 -m pytest tests/unit/test_source_indexed_public_queues.py -q`.
- Acceptance: Edge destination has N−1 external source queues; cloud N; queues do not merge; FIFO deterministic.
- Stop/rollback: Source ERT must not reorder destination queues.

### BASE-012 — Implement equal public-CPU sharing

- Dependencies: BASE-011.
- Required reads: `src/environment/execution_helper.py`; `src/environment/runtime_model.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/public_queue.py`.
- Allowed writes: `src/environment/execution_helper.py`; `src/environment/runtime_model.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/public_queue.py`; `tests/unit/test_public_cpu_sharing.py`; `tests/integration/test_destination_capacity_sharing.py`; G1.
- Ordered operations: Find active nonempty source queues; allocate capacity/k; update remaining cycles; complete simultaneous heads deterministically; recompute after boundary changes.
- Exact command: `python3 -m pytest tests/unit/test_public_cpu_sharing.py tests/integration/test_destination_capacity_sharing.py -q`.
- Acceptance: Each of k active queues gets capacity/k; no over-allocation; no empty allocation; deterministic completion.
- Stop/rollback: Sequential full-capacity approximation fails.

### BASE-013 — Implement exact HOODIE action semantics

- Dependencies: BASE-005, BASE-007, BASE-010, BASE-012.
- Required reads: HOODIE registry; `src/policies/action_masking.py`; `src/policies/policy_interface.py`; `src/environment/gym_adapter.py`; topology.
- Allowed writes: `src/policies/action_masking.py`; `src/policies/policy_interface.py`; `src/environment/gym_adapter.py`; `src/agents/hoodie_action_space.py`; `tests/unit/test_hoodie_action_space.py`; G1.
- Ordered operations: Encode local, every legal horizontal destination, and cloud; physical mask only; stable IDs; no ECHO deadline mask or fallback.
- Exact command: `python3 -m pytest tests/unit/test_hoodie_action_space.py -q`.
- Acceptance: All connected destinations individually selectable; self/disconnected illegal; no first-neighbor collapse.
- Stop/rollback: Do not import ECHO action/mask/ERT modules.

### BASE-014 — Implement exact HOODIE state/history

- Dependencies: BASE-013.
- Required reads: HOODIE registry; `src/agents/paper_state_builder.py`; `src/agents/history_builder.py`; `src/environment/gym_adapter.py`.
- Allowed writes: `src/agents/paper_state_builder.py`; `src/agents/history_builder.py`; `src/environment/gym_adapter.py`; `configs/authoritative/hoodie_state_schema.json`; `tests/unit/test_hoodie_state_contract.py`; `tests/unit/test_paper_state_builder.py`; `tests/unit/test_paper_state_vector_real.py`; G1.
- Ordered operations: Implement paper task one-hot/density, private/offload waits, public queue/load features, W=10 history/forecast, exact order/dimension, and documented no-arrival behavior; exclude ECHO features.
- Exact command: `python3 -m pytest tests/unit/test_hoodie_state_contract.py tests/unit/test_paper_state_builder.py tests/unit/test_paper_state_vector_real.py -q`.
- Acceptance: Shape/order/schema exact; features derive from current snapshot; normalization classified.
- Stop/rollback: Placeholder zero forecasts must be removed by BASE-015.

### BASE-015 — Implement real HOODIE LSTM forecast

- Dependencies: BASE-014.
- Required reads: `src/agents/lstm_dueling_dqn.py`; `src/agents/hoodie_model.py`; `src/agents/neural_net_hoodie_model.py`; BASE-014 schema; HOODIE paper.
- Allowed writes: `src/agents/lstm_dueling_dqn.py`; `src/agents/hoodie_model.py`; `src/agents/neural_net_hoodie_model.py`; `src/agents/hoodie_load_forecaster.py`; `tests/unit/test_hoodie_load_forecaster.py`; `tests/agents/test_lstm_dueling_dqn.py`; G1.
- Ordered operations: Implement W=10 forecast input/output/loss/optimizer, deterministic initialization, checkpoint save/load, and real state integration; exclude held-out data.
- Exact command: `python3 -m pytest tests/unit/test_hoodie_load_forecaster.py tests/agents/test_lstm_dueling_dqn.py -q`.
- Acceptance: Forecast changes with history; finite gradients/loss; exact checkpoint round-trip; no hard-coded zeros/leakage.
- Stop/rollback: Unresolved paper training detail stops task; do not borrow ECHO behavior.

### BASE-016 — Implement one independent HOODIE learner per EA

- Dependencies: BASE-015.
- Required reads: `src/agents/hoodie_agent.py`; replay/target/model files; `src/training/training_loop.py`.
- Allowed writes: `src/agents/hoodie_agent.py`; `src/agents/hoodie_agent_manager.py`; `src/agents/replay_buffer.py`; `src/agents/target_network.py`; `src/training/training_loop.py`; `tests/unit/test_per_ea_hoodie_learners.py`; G1.
- Ordered operations: Instantiate N independent agents with private replay, online/target networks, optimizer, epsilon, seed, and checkpoint namespace; route source events only to its agent.
- Exact command: `python3 -m pytest tests/unit/test_per_ea_hoodie_learners.py -q`.
- Acceptance: Mutation/replay for EA n cannot affect m; exactly N states/checkpoints; deterministic per-EA seeds.
- Stop/rollback: One shared policy/learner object fails.

### BASE-017 — Implement original HOODIE reward/replay timing

- Dependencies: BASE-016.
- Required reads: HOODIE registry; `src/environment/reward_timing.py`; `src/training/delayed_reward_training.py`; `src/training/training_loop.py`; `src/agents/replay_buffer.py`.
- Allowed writes: `src/environment/reward_timing.py`; `src/training/delayed_reward_training.py`; `src/training/training_loop.py`; `src/agents/replay_buffer.py`; `tests/unit/test_hoodie_reward_replay_timing.py`; G1.
- Ordered operations: Implement paper reward sign/delivery/next-state/terminal and ordinary discount; remove ECHO interval return, risk, deadline fallback, and gamma-delta from HOODIE.
- Exact command: `python3 -m pytest tests/unit/test_hoodie_reward_replay_timing.py -q`.
- Acceptance: Hand trace exact; each decision resolves once in correct EA replay; terminal flush; no ECHO-only field.
- Stop/rollback: Unresolved Bellman timing yields REWORK.

### BASE-018 — Implement paper-correct HOODIE Dueling Double-DQN

- Dependencies: BASE-017.
- Required reads: `src/agents/double_dqn.py`; `src/agents/target_network.py`; `src/agents/hoodie_model.py`; `src/agents/neural_net_hoodie_model.py`; `src/agents/torchrl_hoodie_learner.py`; BASE-001 learning config.
- Allowed writes: `src/agents/double_dqn.py`; `src/agents/target_network.py`; `src/agents/hoodie_model.py`; `src/agents/neural_net_hoodie_model.py`; `src/agents/torchrl_hoodie_learner.py`; `tests/unit/test_hoodie_double_dqn_contract.py`; G1.
- Ordered operations: Use real online/target networks, dueling aggregation, Double-DQN selection/evaluation, epsilon schedule, target copy, finite optimizer, normal discount; remove heuristic-Q authoritative path.
- Exact command: `python3 -m pytest tests/unit/test_hoodie_double_dqn_contract.py tests/unit/test_agent_components.py -q`.
- Acceptance: Online selects/target evaluates; target no gradient; exact epsilon/copy; deterministic-batch loss decreases; checkpoint round-trip.
- Stop/rollback: Stub or heuristic model cannot be accepted.

### BASE-019 — Validate RO/FLC/VO/HO/BCO/MLEO isolation

- Dependencies: BASE-018.
- Required reads: `src/policies/ro.py`; `src/policies/flc.py`; `src/policies/vo.py`; `src/policies/ho.py`; `src/policies/bco.py`; `src/policies/mleo.py`; `src/evaluation/policy_registry.py`; shared kernel.
- Allowed writes: `src/policies/ro.py`; `src/policies/flc.py`; `src/policies/vo.py`; `src/policies/ho.py`; `src/policies/bco.py`; `src/policies/mleo.py`; `src/evaluation/policy_registry.py`; `tests/integration/test_baseline_method_isolation.py`; `docs/contracts/baseline_definitions.md`; G1.
- Ordered operations: Define allowed information/action/tie/fallback; replace HOODIE→ADAPTIVE alias with real HOODIE adapter; heuristics do not train/import ECHO.
- Exact command: `python3 -m pytest tests/integration/test_baseline_method_isolation.py -q`.
- Acceptance: FLC local; VO cloud; HO horizontal/fallback; RO physical; BCO deterministic; MLEO own latency; same traces/accounting; no ECHO import.
- Stop/rollback: ECHO mask/ERT/reward import fails.

### BASE-020 — Run complete deterministic base invariant suite

- Dependencies: BASE-019.
- Required reads: All Phase-1 cards/tests and BASE-006 fixtures.
- Allowed writes: `tests/integration/test_base_physical_invariants.py`; `tests/integration/test_base_differential_trace.py`; `artifacts/validation/base/invariant_results.json`; `artifacts/validation/base/differential_trace.md`; `artifacts/validation/base/test_manifest.json`; G1.
- Ordered operations: Run local/horizontal/cloud lifecycles, simultaneous arrivals, expiration, late active, drain, accounting, one-location, trace identity, neutral-kernel import scan, and method isolation; runtime code is read-only.
- Exact command: `python3 -m pytest tests/unit/test_hoodie_table4_config.py tests/unit/test_hoodie_topology_authority.py tests/unit/test_trace_protocol_paper_semantics.py tests/unit/test_trace_immutability.py tests/unit/test_hoodie_slot_contract_vectors.py tests/unit/test_hoodie_slot_engine.py tests/integration/test_neutral_kernel_imports.py tests/unit/test_private_queue_lifecycle.py tests/unit/test_single_source_transmitter.py tests/unit/test_destination_retention.py tests/unit/test_next_boundary_admission.py tests/unit/test_source_indexed_public_queues.py tests/unit/test_public_cpu_sharing.py tests/unit/test_hoodie_action_space.py tests/unit/test_hoodie_state_contract.py tests/unit/test_hoodie_load_forecaster.py tests/unit/test_per_ea_hoodie_learners.py tests/unit/test_hoodie_reward_replay_timing.py tests/unit/test_hoodie_double_dqn_contract.py tests/integration/test_baseline_method_isolation.py tests/integration/test_base_physical_invariants.py tests/integration/test_base_differential_trace.py -q`.
- Acceptance: All pass; generated=completed+dropped; one outcome/location; no invalid action/NaN/Inf/ECHO import.
- Stop/rollback: Failures reopen owning task; BASE-020 cannot patch runtime.

### BASE-021 — Run bounded HOODIE runtime/learner smoke

- Dependencies: BASE-020.
- Required reads: Phase-1 implementation; BASE-020 evidence; smoke conventions.
- Allowed writes: `configs/experiments/hoodie_smoke.yaml`; `scripts/smoke/run_hoodie_smoke.py`; `tests/integration/test_hoodie_smoke_runner.py`; G5 for method `hoodie`, scenario `hoodie_smoke`, N=20, seed=00; G1.
- Ordered operations: Run bounded real-learning smoke with all route types, checkpoint save/load, task/decision/episode/training logs using schemas when available.
- Exact command: `python3 -m pytest tests/integration/test_hoodie_smoke_runner.py -q && python3 scripts/smoke/run_hoodie_smoke.py --config configs/experiments/hoodie_smoke.yaml --output-root artifacts/evaluation/runs`.
- Acceptance: Finite loss/Q/reward; replay grows; target copies; reload deterministic; accounting exact; run labeled smoke.
- Stop/rollback: Do not tune from smoke.

### BASE-022 — Reproduce HOODIE experiment organization/trends

- Dependencies: BASE-021.
- Required reads: HOODIE paper figure/table registry; BASE-021 run; frozen candidate config.
- Allowed writes: `configs/experiments/hoodie_reproduction.yaml`; `scripts/reproduction/run_hoodie_reproduction.py`; `artifacts/reproduction/hoodie/run_manifest.json`; `artifacts/reproduction/hoodie/task_log.jsonl`; `artifacts/reproduction/hoodie/episode_metrics.csv`; `artifacts/reproduction/hoodie/trend_comparison.csv`; `artifacts/reproduction/hoodie/SHA256SUMS`; `docs/reports/hoodie_reproduction_evidence.md`; G1.
- Ordered operations: Reproduce paper experiment organization and direction/trend using real simulation; retain configs/seeds/raw outputs; document deviations without fabricating pixel-perfect values.
- Exact command: `python3 scripts/reproduction/run_hoodie_reproduction.py --config configs/experiments/hoodie_reproduction.yaml --output artifacts/reproduction/hoodie`.
- Acceptance: Every trend has raw lineage; deviations explicit; no hard-coded paper result; paired inputs.
- Stop/rollback: Failed trend blocks freeze and cannot be described as reproduced.

### FREEZE-001 — Freeze validated neutral simulator and HOODIE baseline

- Dependencies: BASE-022.
- Required reads: All Phase-1 evidence; BASE-022; tested commit.
- Allowed writes: `scripts/release/freeze_hoodie_baseline.py`; `artifacts/releases/hoodie_base_v1/manifest.json`; `artifacts/releases/hoodie_base_v1/SHA256SUMS`; `docs/contracts/hoodie_base_freeze.md`; G1.
- Ordered operations: Record commit, config, topology, trace/schema, test results, checkpoints, neutral hook interfaces, forbidden imports, limitations, and exact hashes; verify shared files contain no ECHO imports.
- Exact command: `python3 scripts/release/freeze_hoodie_baseline.py --manifest artifacts/releases/hoodie_base_v1/manifest.json --checksums artifacts/releases/hoodie_base_v1/SHA256SUMS`.
- Acceptance: Hashes verify; Phase-1 suite passes; no unresolved S0/S1; neutral interfaces versioned; frozen file list explicit.
- Stop/rollback: Any later frozen-file change invalidates release and reopens owner task.

### ECHO-001 — Attach ECHO adapter to frozen neutral hooks

- Dependencies: FREEZE-001, SRC-001.
- Required reads: `artifacts/releases/hoodie_base_v1/manifest.json`; `docs/contracts/neutral_kernel_contract.md`; `src/environment/method_hooks.py`; `src/echo_action_space.py`; `src/echo_ert.py`; `src/echo_queue_ordering.py`; current policy registry.
- Allowed writes: `src/echo_adapter.py`; `src/evaluation/method_registry.py`; `tests/integration/test_echo_adapter_attachment.py`; `docs/contracts/echo_adapter_contract.md`; G1.
- Ordered operations: Implement an ECHO adapter satisfying the frozen neutral hooks; register ECHO explicitly; do not edit any file listed in the freeze manifest; verify HOODIE path remains byte-identical.
- Exact command: `python3 -m pytest tests/integration/test_echo_adapter_attachment.py tests/integration/test_base_physical_invariants.py -q`.
- Acceptance: ECHO can be selected through adapter; frozen-file hashes unchanged; shared/HOODIE modules import no ECHO code.
- Stop/rollback: If frozen hooks are insufficient, return PLAN_CHANGE_REQUIRED and reopen BASE-005; never patch frozen shared files here.

### ECHO-002 — Implement Equations (1)–(8) lifecycle/dispatch

- Dependencies: ECHO-001.
- Required reads: `research/authority/echo/live/ECHO_PROPOSED_METHOD.md`; `artifacts/audits/echo_live_revision_audit.md`; `src/echo_types.py`; `src/echo_ert.py`; `src/environment/task.py`; `src/echo_adapter.py`.
- Allowed writes: `src/echo_types.py`; `src/echo_ert.py`; `src/environment/task.py`; `src/echo_adapter.py`; `tests/unit/test_echo_equations_01_08.py`; G1.
- Ordered operations: Encode task variables, deadline, route set, one-time direct dispatch, stored destination, success/drop lifecycle, and inclusive slot arithmetic exactly as Equations 1–8.
- Exact command: `python3 -m pytest tests/unit/test_echo_equations_01_08.py -q`.
- Acceptance: Equation examples/edges exact; no second action; deadline off-by-one exact; one terminal resolution.
- Stop/rollback: No queue estimator or learner changes.

### ECHO-003 — Implement Equations (9)–(11) local estimate

- Dependencies: ECHO-002.
- Required reads: Live Equations 9–11; `src/echo_ert.py`; private queue and active state.
- Allowed writes: `src/echo_ert.py`; `tests/unit/test_echo_local_estimate.py`; G1.
- Ordered operations: Compute local service slots, active residual, predecessor wait, inclusive completion, ERT, and lateness using correct units/remaining cycles.
- Exact command: `python3 -m pytest tests/unit/test_echo_local_estimate.py -q`.
- Acceptance: Empty/active/multiple-predecessor hand cases exact; no deadline truncation; units consistent.
- Stop/rollback: Do not reorder queues.

### ECHO-004 — Implement Equations (12)–(16) outbound estimate

- Dependencies: ECHO-003.
- Required reads: Live Equations 12–16; `src/echo_ert.py`; link rates; outbound state; next-boundary contract.
- Allowed writes: `src/echo_ert.py`; `tests/unit/test_echo_outbound_estimate.py`; G1.
- Ordered operations: Compute residual/predecessor transmission, horizontal/cloud rate, inclusive transfer, explicit next-boundary admission, destination contribution, completion, ERT, and lateness.
- Exact command: `python3 -m pytest tests/unit/test_echo_outbound_estimate.py -q`.
- Acceptance: Horizontal/cloud hand cases exact; boundary +1 applied exactly once; destination work not omitted.
- Stop/rollback: Destination workload details belong to ECHO-005.

### ECHO-005 — Implement Equations (17)–(25) destination model

- Dependencies: ECHO-004.
- Required reads: Live Equations 17–25; public queues; runtime capacity; status interface.
- Allowed writes: `src/echo_destination_model.py`; `src/echo_ert.py`; `tests/unit/test_echo_destination_model.py`; G1.
- Ordered operations: Compute remaining workload in cycles, active source-queue count, hypothetical admission, effective capacity, waiting/service, and destination completion without future information.
- Exact command: `python3 -m pytest tests/unit/test_echo_destination_model.py -q`.
- Acceptance: Cycles and cycles/slot units; active count adjustment exact; zero/one/many queues; no future leakage.
- Stop/rollback: Destination FIFO must remain unchanged.

### ECHO-006 — Implement Equations (26)–(28) history/LSTM inputs

- Dependencies: ECHO-005.
- Required reads: Live Equations 26–28; `src/environment/runtime_model.py`; current history/load code.
- Allowed writes: `src/echo_load_forecast.py`; `src/echo_status.py`; `tests/unit/test_echo_load_history.py`; G1.
- Ordered operations: Create ordered fixed-length history, freshness timestamp/status, stale/missing flag, forecasting target record, and deterministic bootstrap; no model fitting.
- Exact command: `python3 -m pytest tests/unit/test_echo_load_history.py -q`.
- Acceptance: W/order exact; fresh chosen over prediction; stale/missing explicit; held-out trace IDs excluded.
- Stop/rollback: Neural architecture/optimizer belongs to ECHO-016.

### ECHO-007 — Implement Equation (29) local queue ERT ordering

- Dependencies: ECHO-006.
- Required reads: Live Equation 29/ties; `src/echo_queue_ordering.py`; private queue.
- Allowed writes: `src/echo_queue_ordering.py`; `tests/unit/test_echo_local_queue_ordering.py`; G1.
- Ordered operations: Freeze active task; construct waiting order position-by-position; smallest nonnegative ERT else minimum lateness; arrival/stable-ID final tie; count evaluations.
- Exact command: `python3 -m pytest tests/unit/test_echo_local_queue_ordering.py -q`.
- Acceptance: Hand order/all-late exact; active untouched; evaluations q(q+1)/2.
- Stop/rollback: HOODIE FIFO path unchanged.

### ECHO-008 — Implement Equation (30) outbound ERT ordering

- Dependencies: ECHO-007.
- Required reads: Live Equation 30; `src/echo_queue_ordering.py`; outbound queue; destination model.
- Allowed writes: `src/echo_queue_ordering.py`; `tests/unit/test_echo_outbound_queue_ordering.py`; G1.
- Ordered operations: Freeze active transfer; include cumulative source transmission plus destination workload/service for each provisional position; same feasible/lateness/tie rules; retain destination.
- Exact command: `python3 -m pytest tests/unit/test_echo_outbound_queue_ordering.py -q`.
- Acceptance: Mixed-destination/all-late hand cases exact; one transmitter; O(q²) count.
- Stop/rollback: Do not create one physical queue/transmitter per destination.

### ECHO-009 — Implement 32-position canonical action space

- Dependencies: ECHO-008.
- Required reads: Live scalability/action section; `src/echo_action_space.py`; `src/echo_types.py`; frozen topology.
- Allowed writes: `src/echo_action_space.py`; `src/echo_types.py`; `tests/unit/test_echo_canonical_action_space.py`; G1.
- Ordered operations: Map index 0 local, 1–30 horizontal positions, 31 cloud; mask absent/self/disconnected positions physically; maintain shape 32 and separate checkpoint per tested N.
- Exact command: `python3 -m pytest tests/unit/test_echo_canonical_action_space.py -q`.
- Acceptance: 32 outputs for N=10/15/20/25/30; stable mapping; padding masked; cloud final.
- Stop/rollback: Do not use runtime-varying N+2 tensor.

### ECHO-010 — Implement Equations (42)–(46) mask/fallback

- Dependencies: ECHO-009.
- Required reads: Live Equations 42–46; candidate estimates; canonical action space.
- Allowed writes: `src/echo_action_mask.py`; `src/echo_action_space.py`; `tests/unit/test_echo_deadline_mask.py`; G1.
- Ordered operations: Intersect physical candidates with ERT>=0; when empty choose singleton minimum-lateness candidate with deterministic tie; expose one immutable decision-time mask for exploration/exploitation/target.
- Exact command: `python3 -m pytest tests/unit/test_echo_deadline_mask.py -q`.
- Acceptance: Feasible set/fallback exact; never all-zero on arrival; invalid physical actions absent; same mask hash across selection paths.
- Stop/rollback: No behavior leaks into HOODIE/baselines.

### ECHO-011 — Implement Equations (47)–(50) pending records and schema-compliant decision logs

- Dependencies: ECHO-010, EVAL-001.
- Required reads: Live Equations 47–50; `experiments/schemas/decision_log.schema.json`; `experiments/schemas/task_log.schema.json`; action/mask/estimate types; ECHO adapter.
- Allowed writes: `src/echo_pending.py`; `src/echo_logging.py`; `src/echo_types.py`; `src/echo_adapter.py`; `tests/unit/test_echo_pending_records.py`; `tests/unit/test_echo_decision_log_schema.py`; G1.
- Ordered operations: At decision store source, state hash, action, mask hash, candidate estimates, risk, decision slot, task, destination, and schema version; emit schema-valid decision/task log records; one pending record per task.
- Exact command: `python3 -m pytest tests/unit/test_echo_pending_records.py tests/unit/test_echo_decision_log_schema.py -q`.
- Acceptance: Fields and hashes exact; no duplicate/overwritten pending record; logs validate against EVAL-001 schemas.
- Stop/rollback: If schema is insufficient, return PLAN_CHANGE_REQUIRED and reopen EVAL-001; do not invent fields.

### ECHO-012 — Implement Equations (51)–(54) normalized state

- Dependencies: ECHO-011.
- Required reads: Live Equations 51–54; schema/log contract; status/candidate/pending modules.
- Allowed writes: `src/echo_state.py`; `src/echo_types.py`; `configs/authoritative/echo_state_schema.json`; `tests/unit/test_echo_state_contract.py`; G1.
- Ordered operations: Build normalized fixed state with task, local/outbound queue/residual, destination workload/load, history/LSTM, min ERT, candidate ERT, and mask; zero task/candidate on no arrival while queue/load remain live.
- Exact command: `python3 -m pytest tests/unit/test_echo_state_contract.py -q`.
- Acceptance: Exact order/shape for N=10/15/20/25/30; bounds and clipping exact; no-arrival distinction; no future leakage.
- Stop/rollback: Do not alter action dimension or logging schema here.

### ECHO-013 — Implement Equations (55)–(58) task reward

- Dependencies: ECHO-012.
- Required reads: Live Equations 55–58; task resolutions; pending records; evaluation log schemas.
- Allowed writes: `src/echo_reward.py`; `src/echo_pending.py`; `src/echo_logging.py`; `tests/unit/test_echo_reward.py`; G1.
- Ordered operations: Compute realized system duration, predicted-risk indicator, realized-drop indicator, and `-duration-lambda_R*risk-lambda_D*drop`; attach exactly once at resolution and log components.
- Exact command: `python3 -m pytest tests/unit/test_echo_reward.py -q`.
- Acceptance: Hand rewards exact; one reward/task; success/drop/late-active cases; schema-valid fields.
- Stop/rollback: Do not close replay intervals here.

### ECHO-014 — Implement Equations (59)–(60) event intervals

- Dependencies: ECHO-013.
- Required reads: Live Equations 59–60; `src/training/event_smdp.py`; pending/reward events; boundary contract.
- Allowed writes: `src/training/event_smdp.py`; `tests/unit/test_event_smdp_interval_contract.py`; G1.
- Ordered operations: Maintain one open interval per source EA; add each resolving task reward with within-interval discount; close only at next actual decision of same EA or T+1; emit one non-overlapping transition with delta.
- Exact command: `python3 -m pytest tests/unit/test_event_smdp_interval_contract.py -q`.
- Acceptance: Multiple rewards aggregate; other-EA decisions do not close; no overlapping task transitions; terminal and boundary-before-decision ownership exact.
- Stop/rollback: Older task-level next-decision interpretation is forbidden.

### ECHO-015 — Implement Equations (61)–(67) masked DDQL

- Dependencies: ECHO-014.
- Required reads: Live Equations 61–67; replay/DQN utilities; ECHO state/action/mask/interval modules.
- Allowed writes: `src/agents/echo_model.py`; `src/agents/echo_agent.py`; `src/agents/replay_buffer.py`; `src/agents/double_dqn.py`; `src/agents/target_network.py`; `tests/unit/test_echo_masked_ddql.py`; G1.
- Ordered operations: Implement 32-output dueling network, mean advantage, online masked argmax, target evaluation, gamma^delta, terminal mask, optimizer, target copy, and exploration inside mask only.
- Exact command: `python3 -m pytest tests/unit/test_echo_masked_ddql.py -q`.
- Acceptance: Hand target exact; masked high-Q never selected; target no gradient; finite update; checkpoint round-trip; separate agent/checkpoint per EA and N.
- Stop/rollback: No heuristic-Q fallback.

### ECHO-016 — Implement fresh/stale status and LSTM training

- Dependencies: ECHO-015.
- Required reads: Live LSTM section; `src/echo_load_forecast.py`; `src/echo_status.py`; ECHO state/model/config.
- Allowed writes: `src/echo_load_forecast.py`; `src/echo_status.py`; `src/agents/echo_load_lstm.py`; `tests/unit/test_echo_load_lstm.py`; G1.
- Ordered operations: Implement supervised forecasting loss, separate optimizer/state, training-only histories, freshness threshold, fresh override, stale/missing prediction, deterministic checkpoint, and held-out guard.
- Exact command: `python3 -m pytest tests/unit/test_echo_load_lstm.py -q`.
- Acceptance: Fresh ignores prediction; stale/missing uses it; finite loss/gradients; no held-out IDs; checkpoint reproducible.
- Stop/rollback: Do not hide forecast loss in Q loss unless source requires it.

### ECHO-017 — Implement isolated ECHO-NoLSTM

- Dependencies: ECHO-016.
- Required reads: Live ablation definition; ECHO adapter/status/state/model; method registry.
- Allowed writes: `src/policies/echo_no_lstm.py`; `src/evaluation/method_registry.py`; `tests/integration/test_echo_no_lstm_isolation.py`; G1.
- Ordered operations: Create ECHO-NoLSTM identical to ECHO except the source-defined load-estimate replacement; same kernel/state/action/mask/reward/learner/budget.
- Exact command: `python3 -m pytest tests/integration/test_echo_no_lstm_isolation.py -q`.
- Acceptance: Differential trace shows only load-estimation-dependent fields/actions differ; no hidden parameter/budget change.
- Stop/rollback: Do not classify as generic heuristic.

### ECHO-018 — Implement exact Algorithm 1/2 chronology

- Dependencies: ECHO-017.
- Required reads: Source-locked Algorithm 1/2; `src/echo_adapter.py`; `src/training/training_loop.py`; interval/reward logic; neutral hooks.
- Allowed writes: `src/echo_adapter.py`; `src/training/training_loop.py`; `tests/integration/test_echo_algorithm_order.py`; `tests/integration/test_echo_boundary_reward_ownership.py`; G1.
- Ordered operations: Implement Section 3.3 order; resolutions before new decision closure; decisions then scheduling/service; T+1 flush; inference same physical order without learning and highest masked Q.
- Exact command: `python3 -m pytest tests/integration/test_echo_algorithm_order.py tests/integration/test_echo_boundary_reward_ownership.py -q`.
- Acceptance: Event trace maps every 23/12 algorithm line; boundary reward belongs to old interval; no same-slot double service; train/inference physical order equal.
- Stop/rollback: Formula defects reopen owner equation task; no shared frozen-file edit.

### ECHO-019 — Run deterministic ECHO unit/smoke suite

- Dependencies: ECHO-018.
- Required reads: All Phase-2 tests; source lock; frozen base; EVAL-001 schemas.
- Allowed writes: `tests/integration/test_echo_hand_trace.py`; `configs/experiments/echo_smoke.yaml`; `scripts/smoke/run_echo_smoke.py`; G5 for method `echo`, scenario `echo_smoke`, N=2, seed=00; G1.
- Ordered operations: Run 2-EA+cloud hand trace with all routes, contention, feasible/late candidates, fallback, ERT reorder, expiration, late active; short finite learner/checkpoint smoke with schema-valid logs.
- Exact command: `python3 -m pytest tests/unit/test_echo_equations_01_08.py tests/unit/test_echo_local_estimate.py tests/unit/test_echo_outbound_estimate.py tests/unit/test_echo_destination_model.py tests/unit/test_echo_load_history.py tests/unit/test_echo_local_queue_ordering.py tests/unit/test_echo_outbound_queue_ordering.py tests/unit/test_echo_canonical_action_space.py tests/unit/test_echo_deadline_mask.py tests/unit/test_echo_pending_records.py tests/unit/test_echo_decision_log_schema.py tests/unit/test_echo_state_contract.py tests/unit/test_echo_reward.py tests/unit/test_event_smdp_interval_contract.py tests/unit/test_echo_masked_ddql.py tests/unit/test_echo_load_lstm.py tests/integration/test_echo_no_lstm_isolation.py tests/integration/test_echo_algorithm_order.py tests/integration/test_echo_boundary_reward_ownership.py tests/integration/test_echo_hand_trace.py -q && python3 scripts/smoke/run_echo_smoke.py --config configs/experiments/echo_smoke.yaml --output-root artifacts/evaluation/runs`.
- Acceptance: All pass; manual trace exact; finite metrics; all routes; no masked action; accounting exact; deterministic reload; logs validate.
- Stop/rollback: Failures reopen owner task; no runtime patches here.

### ECHO-020 — Produce equation coverage and paired pilot gate

- Dependencies: ECHO-019.
- Required reads: Source audit; all Phase-2 evidence; frozen base; ECHO/HOODIE smoke; schemas.
- Allowed writes: `scripts/audit/build_echo_coverage.py`; `artifacts/audits/echo_equation_coverage.json`; `artifacts/audits/echo_equation_coverage.md`; `configs/experiments/echo_pilot.yaml`; `scripts/pilot/run_echo_pilot.py`; `artifacts/pilot/echo_v4/run_manifest.json`; `artifacts/pilot/echo_v4/task_log.jsonl`; `artifacts/pilot/echo_v4/decision_log.jsonl`; `artifacts/pilot/echo_v4/episode_metrics.csv`; `artifacts/pilot/echo_v4/SHA256SUMS`; G1.
- Ordered operations: Map every equation/algorithm line to code/test/evidence; run paired ECHO/HOODIE/ECHO-NoLSTM pilot on same traces; audit route, mask, reward, interval, accounting, stability, and schema.
- Exact command: `python3 scripts/audit/build_echo_coverage.py --source-audit artifacts/audits/echo_live_revision_audit.md --output-json artifacts/audits/echo_equation_coverage.json --output-md artifacts/audits/echo_equation_coverage.md && python3 scripts/pilot/run_echo_pilot.py --config configs/experiments/echo_pilot.yaml --output artifacts/pilot/echo_v4`.
- Acceptance: 69/69 rows have code+test; no unresolved S0/S1; paired hashes equal; finite pilot; no superiority claim.
- Stop/rollback: Any uncovered row/invariant blocks evaluation.

### EVAL-001 — Freeze logging, evaluation, and 15-panel schemas before ECHO logging

- Dependencies: SRC-001, BASE-004.
- Required reads: `research/ECHO_evaluation_spec.md`; SRC-001 snapshot/audit; BASE-004 trace schema; Section 9 constants.
- Allowed writes: `experiments/manifest.yaml`; `experiments/figure_manifest.yaml`; `experiments/schemas/run_manifest.schema.json`; `experiments/schemas/task_log.schema.json`; `experiments/schemas/decision_log.schema.json`; `experiments/schemas/resolution_event.schema.json`; `experiments/schemas/episode_metrics.schema.json`; `experiments/schemas/seed_metrics.schema.json`; `experiments/schemas/panel_values.schema.json`; `experiments/schemas/artifact_manifest.schema.json`; `experiments/schemas/checkpoint_manifest.schema.json`; `src/evaluation/config.py`; `src/evaluation/log_schema.py`; `tests/unit/test_evaluation_manifests.py`; `tests/unit/test_log_schemas.py`; `docs/contracts/evaluation_logging_contract.md`; G1.
- Ordered operations: Encode all 15 panels, exact methods/x/fixed values, retraining/checkpoint rule, seeds, 200 held-out episodes, metrics, CI, raw/export paths; freeze decision/task/resolution log fields before ECHO-011; define training/validation/test split and held-out guard; do not run experiments.
- Exact command: `python3 -m pytest tests/unit/test_evaluation_manifests.py tests/unit/test_log_schemas.py -q`.
- Acceptance: 15 unique panels; no placeholder; Figure-6 timeout 2s; Figure-7 c/f swept; Figure-8 exact; all schemas validate; ECHO-011 required fields represented.
- Stop/rollback: Unresolved retraining/checkpoint/log field yields PLAN_CHANGE_REQUIRED; do not guess.

### EVAL-002 — Generate immutable paired trace bank

- Dependencies: ECHO-020, EVAL-001.
- Required reads: BASE-004 immutable trace protocol; EVAL-001 manifests.
- Allowed writes: `scripts/evaluation/build_trace_bank.py`; `tests/integration/test_trace_bank.py`; G4 for every manifest scenario/seed; `artifacts/evaluation/trace_bank/index.json`; G1.
- Ordered operations: Generate each required trace once using G4; canonical JSON; stable hashes; read-only consumption; no per-method regeneration; include drain/arrival metadata.
- Exact command: `python3 -m pytest tests/integration/test_trace_bank.py -q && python3 scripts/evaluation/build_trace_bank.py --manifest experiments/manifest.yaml --output artifacts/evaluation/trace_bank`.
- Acceptance: Expected scenario/seed count; stable hashes; methods load same bytes; no duplicate ID with different bytes.
- Stop/rollback: Never overwrite an existing trace ID with different content.

### EVAL-003 — Freeze config/topology/checkpoint lineage

- Dependencies: EVAL-002.
- Required reads: EVAL-002 index; frozen base; ECHO pilot; manifests; environment metadata.
- Allowed writes: `scripts/evaluation/build_lineage_manifest.py`; `tests/unit/test_lineage_manifest.py`; `artifacts/evaluation/lineage/lineage_manifest.json`; `artifacts/evaluation/lineage/SHA256SUMS`; G1.
- Ordered operations: Map every planned run to config, topology, trace, method/code, checkpoint, source revision, software environment, and schema hashes; assign deterministic run IDs per G5.
- Exact command: `python3 -m pytest tests/unit/test_lineage_manifest.py -q && python3 scripts/evaluation/build_lineage_manifest.py --manifest experiments/manifest.yaml --trace-index artifacts/evaluation/trace_bank/index.json --output artifacts/evaluation/lineage/lineage_manifest.json --checksums artifacts/evaluation/lineage/SHA256SUMS`.
- Acceptance: No missing hash; unique/resumable IDs; checkpoint compatible with method/N/scenario.
- Stop/rollback: No mutable latest-checkpoint reference.

### EVAL-004 — Validate all method adapters on common inputs

- Dependencies: EVAL-003.
- Required reads: Method registry; frozen neutral kernel; EVAL-003 lineage; trace bank.
- Allowed writes: `tests/integration/test_all_method_common_inputs.py`; `artifacts/evaluation/adapter_validation/validation.json`; `artifacts/evaluation/adapter_validation/differential_trace.md`; G1.
- Ordered operations: Run one deterministic common trace for ECHO, ECHO-NoLSTM, HOODIE, RO, FLC, VO, HO, BCO, MLEO; compare input hashes, physical accounting, and method isolation; runtime source is read-only.
- Exact command: `python3 -m pytest tests/integration/test_all_method_common_inputs.py -q`.
- Acceptance: Identical inputs; method-specific behavior only; heuristics do not train; no ECHO import in HOODIE/heuristics.
- Stop/rollback: Runtime defect reopens owning BASE/ECHO card; EVAL-004 does not patch it.

### EVAL-005 — Measure throughput and freeze shard budget

- Dependencies: EVAL-004.
- Required reads: Validated adapters; manifests; available compute; expected run count.
- Allowed writes: `scripts/evaluation/benchmark_throughput.py`; `artifacts/evaluation/compute_budget.json`; `artifacts/evaluation/compute_budget.md`; `experiments/shard_plan.yaml`; G1.
- Ordered operations: Benchmark representative train/eval jobs; calculate exact job count, CPU/GPU/RAM/storage/wall time; define shard IDs, checkpoint frequency, completion marker, retry/resume rules; launch no full job.
- Exact command: `python3 scripts/evaluation/benchmark_throughput.py --manifest experiments/manifest.yaml --lineage artifacts/evaluation/lineage/lineage_manifest.json --output-json artifacts/evaluation/compute_budget.json --output-md artifacts/evaluation/compute_budget.md --shards experiments/shard_plan.yaml`.
- Acceptance: Budget derives from measured throughput; every run assigned once; resume/rerun deterministic; feasibility explicit.
- Stop/rollback: Infeasible matrix blocks EVAL-006 pending plan-approved reduction.

### EVAL-006 — Run Figure-5 validation sweeps

- Dependencies: EVAL-005.
- Required reads: Figure-5 manifest; trace bank; shard plan; validation split.
- Allowed writes: `configs/experiments/figure5_sweep.yaml`; `scripts/evaluation/run_figure5_sweep.py`; G5 for each Figure-5 learning run; `artifacts/evaluation/figure5/selection.json`; `artifacts/evaluation/figure5/SHA256SUMS`; G1.
- Ordered operations: Run learning rates 1e-9,5e-9,1e-8,1e-7,5e-7,7e-7 and gamma .2,.4,.6,.8,.99 with source-locked budget; select using validation only; retain all runs/checkpoints.
- Exact command: `python3 scripts/evaluation/run_figure5_sweep.py --config configs/experiments/figure5_sweep.yaml --output-root artifacts/evaluation/runs --selection artifacts/evaluation/figure5/selection.json --checksums artifacts/evaluation/figure5/SHA256SUMS`.
- Acceptance: All points complete/resumable; no held-out trace; finite metrics; deterministic documented selection.
- Stop/rollback: Never select from final test performance.

### EVAL-007 — Train equal-budget final method checkpoints

- Dependencies: EVAL-006.
- Required reads: EVAL-006 selection; manifests; shard plan; training trace bank.
- Allowed writes: `configs/experiments/final_training.yaml`; `scripts/evaluation/run_final_training.py`; G5 for every ECHO/HOODIE/ECHO-NoLSTM training run; `artifacts/checkpoints/final/index.json`; `artifacts/checkpoints/final/SHA256SUMS`; G1.
- Ordered operations: Train required learning methods with equal declared budgets and separate seeds/N/scenarios; exclude heuristics; write immutable completion markers and checkpoint index.
- Exact command: `python3 scripts/evaluation/run_final_training.py --config configs/experiments/final_training.yaml --output-root artifacts/evaluation/runs --checkpoint-index artifacts/checkpoints/final/index.json --checksums artifacts/checkpoints/final/SHA256SUMS`.
- Acceptance: Every checkpoint has config/source/code/trace lineage; no budget mismatch/NaN/Inf; resume stable.
- Stop/rollback: Failed shard resumes only from same-hash checkpoint.

### EVAL-008 — Run 10×200 held-out paired evaluation

- Dependencies: EVAL-007.
- Required reads: Final checkpoint index; held-out G4 traces; evaluation manifest; schemas.
- Allowed writes: `configs/experiments/heldout_evaluation.yaml`; `scripts/evaluation/run_heldout_evaluation.py`; G5 for every method/panel/seed held-out run; `artifacts/evaluation/heldout_index.json`; G1.
- Ordered operations: For every reported point/method run 10 fixed seeds × 200 held-out episodes on identical paired traces; no optimizer/training; log action/mask/ERT/outcome/reward/delta and all hashes.
- Exact command: `python3 scripts/evaluation/run_heldout_evaluation.py --config configs/experiments/heldout_evaluation.yaml --output-root artifacts/evaluation/runs --index artifacts/evaluation/heldout_index.json`.
- Acceptance: Expected run count complete; no training calls; manifests immutable; every log validates.
- Stop/rollback: Partial shard is not averaged or relabeled.

### EVAL-009 — Validate generated/completed/dropped accounting

- Dependencies: EVAL-008.
- Required reads: EVAL-008 index and G5 logs.
- Allowed writes: `scripts/evaluation/audit_accounting.py`; `tests/unit/test_evaluation_accounting.py`; `artifacts/evaluation/audits/accounting.json`; `artifacts/evaluation/audits/accounting.md`; G1.
- Ordered operations: Audit generated=successful+dropped; one terminal outcome; no duplicate/missing task; horizon/drain; pooled task counts.
- Exact command: `python3 -m pytest tests/unit/test_evaluation_accounting.py -q && python3 scripts/evaluation/audit_accounting.py --index artifacts/evaluation/heldout_index.json --output-json artifacts/evaluation/audits/accounting.json --output-md artifacts/evaluation/audits/accounting.md`.
- Acceptance: Zero invariant violation across all runs.
- Stop/rollback: Any violation blocks aggregation and reopens owner runtime card.

### EVAL-010 — Validate no masked ECHO action

- Dependencies: EVAL-008.
- Required reads: EVAL-008 ECHO decision/task logs.
- Allowed writes: `scripts/evaluation/audit_masks.py`; `tests/unit/test_evaluation_mask_audit.py`; `artifacts/evaluation/audits/masks.json`; `artifacts/evaluation/audits/masks.md`; G1.
- Ordered operations: Verify selected mask bit=1, physical legality, fallback identity, and same mask hash for decision/exploration/exploitation/target metadata.
- Exact command: `python3 -m pytest tests/unit/test_evaluation_mask_audit.py -q && python3 scripts/evaluation/audit_masks.py --index artifacts/evaluation/heldout_index.json --output-json artifacts/evaluation/audits/masks.json --output-md artifacts/evaluation/audits/masks.md`.
- Acceptance: Zero masked/invalid/disconnected/self action.
- Stop/rollback: Violation reopens ECHO-009/010/015/018.

### EVAL-011 — Validate trace/config/topology/checkpoint hashes

- Dependencies: EVAL-008.
- Required reads: Run/lineage manifests; G5 logs; checkpoint/trace/config/topology/source hashes.
- Allowed writes: `scripts/evaluation/audit_lineage.py`; `tests/unit/test_evaluation_lineage_audit.py`; `artifacts/evaluation/audits/lineage.json`; `artifacts/evaluation/audits/lineage.md`; G1.
- Ordered operations: Cross-check every row/run against expected hashes; verify paired methods share inputs and no held-out trace trained a checkpoint.
- Exact command: `python3 -m pytest tests/unit/test_evaluation_lineage_audit.py -q && python3 scripts/evaluation/audit_lineage.py --lineage artifacts/evaluation/lineage/lineage_manifest.json --index artifacts/evaluation/heldout_index.json --output-json artifacts/evaluation/audits/lineage.json --output-md artifacts/evaluation/audits/lineage.md`.
- Acceptance: Zero missing/mismatched hash and zero leakage.
- Stop/rollback: Exclude/rerun mismatched run; never relabel.

### EVAL-012 — Aggregate seed metrics and 95% CIs

- Dependencies: EVAL-009, EVAL-010, EVAL-011.
- Required reads: PASS accounting/mask/lineage audits; G5 logs; figure manifest.
- Allowed writes: `src/evaluation/statistics.py`; `scripts/evaluation/aggregate_results.py`; `tests/unit/test_evaluation_statistics.py`; G6 for all 14 metric panel IDs; `artifacts/metrics/aggregation_manifest.json`; G1.
- Ordered operations: Aggregate task→episode→seed; preserve negative-delay convention; pool drop counts within seed; seed means and 95% CIs; no episode pseudo-replication; deterministic sort/serialization.
- Exact command: `python3 -m pytest tests/unit/test_evaluation_statistics.py -q && python3 scripts/evaluation/aggregate_results.py --manifest experiments/figure_manifest.yaml --run-index artifacts/evaluation/heldout_index.json --output artifacts/metrics --aggregation-manifest artifacts/metrics/aggregation_manifest.json`.
- Acceptance: Each point has 10 seed rows and CI; formulas tested; byte-identical regeneration.
- Stop/rollback: No imputation or partial-job averaging.

### FIG-001 — Render Figure 4 topology

- Dependencies: BASE-002.
- Required reads: BASE-002 frozen topology files and hash.
- Allowed writes: `scripts/figures/render_figure4.py`; G7 for figure 4; `artifacts/figures/panel_exports/f4.csv`; G1.
- Ordered operations: Render actual 20-EA topology from JSON using deterministic coordinates; no hand-drawn edges.
- Exact command: `python3 scripts/figures/render_figure4.py --topology configs/authoritative/hoodie_topology.json --svg artifacts/figures/vector/figure4.svg --pdf artifacts/figures/vector/figure4.pdf --png artifacts/figures/png_300dpi/figure4.png --panel-csv artifacts/figures/panel_exports/f4.csv --manifest artifacts/figures/manifests/figure4.json`.
- Acceptance: Edge list/hash match topology; vector/PDF/300-dpi PNG exist; repeat hashes equal.
- Stop/rollback: No visual-only data alteration.

### FIG-002 — Render Figure 5(a–b)

- Dependencies: EVAL-006.
- Required reads: EVAL-006 G5 outputs and selection.
- Allowed writes: `scripts/figures/render_figure5.py`; G7 for figure 5; `artifacts/figures/panel_exports/f5a.csv`; `artifacts/figures/panel_exports/f5b.csv`; G1.
- Ordered operations: Plot reward vs learning rate and gamma from retained CSV/metrics; include configured seed summaries; mark selected values.
- Exact command: `python3 scripts/figures/render_figure5.py --run-root artifacts/evaluation/runs --selection artifacts/evaluation/figure5/selection.json --svg artifacts/figures/vector/figure5.svg --pdf artifacts/figures/vector/figure5.pdf --png artifacts/figures/png_300dpi/figure5.png --panel-a artifacts/figures/panel_exports/f5a.csv --panel-b artifacts/figures/panel_exports/f5b.csv --manifest artifacts/figures/manifests/figure5.json`.
- Acceptance: 2 panels/all points; plotted values equal CSV; vector/PDF/300-dpi and lineage.
- Stop/rollback: No manually entered y-values.

### FIG-003 — Render Figure 6(a–e)

- Dependencies: EVAL-012.
- Required reads: EVAL-012 G6 f6a–f6e and Figure-6 manifest.
- Allowed writes: `scripts/figures/render_figure6.py`; G7 for figure 6; `artifacts/figures/panel_exports/f6a.csv`; `artifacts/figures/panel_exports/f6b.csv`; `artifacts/figures/panel_exports/f6c.csv`; `artifacts/figures/panel_exports/f6d.csv`; `artifacts/figures/panel_exports/f6e.csv`; G1.
- Ordered operations: Render five exact P/capacity/N/traffic/rate-profile panels with timeout 2s and seed CIs.
- Exact command: `python3 scripts/figures/render_figure6.py --metrics artifacts/metrics --manifest experiments/figure_manifest.yaml --svg artifacts/figures/vector/figure6.svg --pdf artifacts/figures/vector/figure6.pdf --png artifacts/figures/png_300dpi/figure6.png --panel-dir artifacts/figures/panel_exports --figure-manifest artifacts/figures/manifests/figure6.json`.
- Acceptance: 5 panels; x/series exact; each point traces to 10 seed rows; files obey G7.
- Stop/rollback: No unapproved smoothing/interpolation.

### FIG-004 — Render Figure 7(a–f)

- Dependencies: EVAL-012.
- Required reads: EVAL-012 G6 f7a–f7f and Figure-7 manifest.
- Allowed writes: `scripts/figures/render_figure7.py`; G7 for figure 7; `artifacts/figures/panel_exports/f7a.csv`; `artifacts/figures/panel_exports/f7b.csv`; `artifacts/figures/panel_exports/f7c.csv`; `artifacts/figures/panel_exports/f7d.csv`; `artifacts/figures/panel_exports/f7e.csv`; `artifacts/figures/panel_exports/f7f.csv`; G1.
- Ordered operations: Render delay a–c and pooled-drop d–f with exact fixed/swept timeout rules, methods, and seed CIs.
- Exact command: `python3 scripts/figures/render_figure7.py --metrics artifacts/metrics --manifest experiments/figure_manifest.yaml --svg artifacts/figures/vector/figure7.svg --pdf artifacts/figures/vector/figure7.pdf --png artifacts/figures/png_300dpi/figure7.png --panel-dir artifacts/figures/panel_exports --figure-manifest artifacts/figures/manifests/figure7.json`.
- Acceptance: 6 panels; negative-delay and pooled-drop preserved; no timeout contradiction; G7 valid.
- Stop/rollback: Do not average episode drop ratios instead of pooled counts.

### FIG-005 — Render Figure 8

- Dependencies: EVAL-012.
- Required reads: EVAL-012 G6 f8 and Figure-8 manifest.
- Allowed writes: `scripts/figures/render_figure8.py`; G7 for figure 8; `artifacts/figures/panel_exports/f8.csv`; G1.
- Ordered operations: Render ECHO vs ECHO-NoLSTM at N=20,P=.3,timeout 1s, episodes 0–3000 with selected LR/gamma and seed convergence/final-delay/stability.
- Exact command: `python3 scripts/figures/render_figure8.py --metrics artifacts/metrics --manifest experiments/figure_manifest.yaml --svg artifacts/figures/vector/figure8.svg --pdf artifacts/figures/vector/figure8.pdf --png artifacts/figures/png_300dpi/figure8.png --panel artifacts/figures/panel_exports/f8.csv --figure-manifest artifacts/figures/manifests/figure8.json`.
- Acceptance: Exact two methods; values equal CSV; no hidden smoothing; G7 valid.
- Stop/rollback: No LSTM-superiority claim without statistics.

### FIG-006 — Validate all vector/PNG exports and lineage

- Dependencies: FIG-001, FIG-002, FIG-003, FIG-004, FIG-005.
- Required reads: All G7 figure files and 15 panel CSVs.
- Allowed writes: `scripts/figures/validate_figure_exports.py`; `tests/unit/test_figure_lineage.py`; `artifacts/figures/figure_lineage_index.json`; G1.
- Ordered operations: Validate 15 panels, CSV→plot equality, SVG/PDF, PNG 300 dpi, hashes, run IDs, labels/units, deterministic regeneration.
- Exact command: `python3 -m pytest tests/unit/test_figure_lineage.py -q && python3 scripts/figures/validate_figure_exports.py --figures artifacts/figures --output artifacts/figures/figure_lineage_index.json`.
- Acceptance: 15/15 valid; no missing lineage; deterministic hashes.
- Stop/rollback: Invalid panel reopens its FIG task.

### REPORT-001 — Write final HOODIE reproduction report

- Dependencies: BASE-022, FREEZE-001.
- Required reads: Freeze manifest; BASE-022 evidence; base tests/smoke.
- Allowed writes: `docs/reports/HOODIE_REPRODUCTION_REPORT.md`; `artifacts/reports/hoodie_reproduction_lineage.json`; G1.
- Ordered operations: Describe exact base mechanics, evidence, trends, deviations, limitations, frozen SHA; cite raw/test/freeze evidence; no ECHO results.
- Exact command: `python3 - <<'PY'
from pathlib import Path
p=Path('docs/reports/HOODIE_REPRODUCTION_REPORT.md'); assert p.exists() and 'Lineage' in p.read_text(); print('PASS')
PY`.
- Acceptance: Every claim cites evidence; no unsupported exact-match claim.
- Stop/rollback: Report cannot compensate for failed reproduction.

### REPORT-002 — Write final ECHO implementation report

- Dependencies: ECHO-020.
- Required reads: SRC-001/ECHO coverage; ECHO-020 pilot; all Phase-2 evidence.
- Allowed writes: `docs/reports/ECHO_IMPLEMENTATION_REPORT.md`; `artifacts/reports/echo_implementation_lineage.json`; G1.
- Ordered operations: Document equation/algorithm map, chronology, state/mask/reward/interval/DDQL/LSTM, isolation, tests, limitations; no final superiority claim.
- Exact command: `python3 - <<'PY'
from pathlib import Path
p=Path('docs/reports/ECHO_IMPLEMENTATION_REPORT.md'); assert p.exists() and 'Equations (1)–(67)' in p.read_text(); print('PASS')
PY`.
- Acceptance: 69 source rows linked; current revisions/frozen base recorded; no historical authority.
- Stop/rollback: Uncovered equation blocks completion.

### REPORT-003 — Write final evaluation/figure report

- Dependencies: EVAL-012, FIG-006.
- Required reads: EVAL-012 metrics/audits; FIG-006 lineage; run manifests.
- Allowed writes: `docs/reports/ECHO_EVALUATION_REPORT.md`; `artifacts/reports/evaluation_lineage.json`; G1.
- Ordered operations: Document methods, budgets, held-out protocol, statistics, 15 panels, invariants, limitations; derive every number from preserved artifacts.
- Exact command: `python3 - <<'PY'
from pathlib import Path
p=Path('docs/reports/ECHO_EVALUATION_REPORT.md'); assert p.exists() and '15 panels' in p.read_text(); print('PASS')
PY`.
- Acceptance: Every numerical claim has run/CSV/figure lineage; all seeds present; claims bounded by evidence.
- Stop/rollback: Failed audit/figure blocks report.

### CLEAN-002 — Archive superseded artifacts without deletion

- Dependencies: REPORT-001, REPORT-002, REPORT-003.
- Required reads: Three final reports; `artifacts/classification/artifact_inventory.json`; replacement hashes.
- Allowed writes: `scripts/cleanup/archive_superseded_artifacts.py`; G8 only for paths listed in `archive_eligible_paths`; `artifacts/archive/archive_manifest.json`; `artifacts/classification/artifact_inventory.json`; `artifacts/classification/artifact_inventory.md`; G1.
- Ordered operations: Read exact eligible list; archive each to G8; record source/replacement/reason/time/hashes; never delete; canonical paths untouched.
- Exact command: `python3 scripts/cleanup/archive_superseded_artifacts.py --inventory artifacts/classification/artifact_inventory.json --archive-root artifacts/archive/superseded --manifest artifacts/archive/archive_manifest.json`.
- Acceptance: Actual changed paths equal script plus inventory files plus G8 expansion; every archive has replacement and hashes; no raw authoritative data removed.
- Stop/rollback: Ambiguous item remains and is marked unresolved.

### CLEAN-003 — Remove canonical-path ambiguity without deletion

- Dependencies: CLEAN-002.
- Required reads: `artifacts/archive/archive_manifest.json`; `artifacts/classification/reference_inventory.json`; final reports/index candidates.
- Allowed writes: `scripts/cleanup/update_canonical_references.py`; `artifacts/archive/path_redirects.json`; `artifacts/FINAL_CANONICAL_PATHS.json`; exactly the paths listed in `editable_reference_files` in `artifacts/classification/reference_inventory.json`; G1.
- Ordered operations: Update only manifest-listed reference files to canonical paths; generate redirects and canonical-path index; verify final reports contain no legacy target; preserve archived bytes.
- Exact command: `python3 scripts/cleanup/update_canonical_references.py --references artifacts/classification/reference_inventory.json --archive-manifest artifacts/archive/archive_manifest.json --redirects artifacts/archive/path_redirects.json --canonical-index artifacts/FINAL_CANONICAL_PATHS.json`.
- Acceptance: Actual diff equals script, two exact outputs, manifest-listed editable files, and G1; one canonical path/type; all redirects resolve.
- Stop/rollback: Any behavior/source algorithm change yields PLAN_CHANGE_REQUIRED.

### HANDOFF-001 — Produce final artifact index and exact rerun commands

- Dependencies: CLEAN-003.
- Required reads: All final manifests/reports/figures/archive maps/tested SHAs/environment.
- Allowed writes: `artifacts/FINAL_ARTIFACT_INDEX.md`; `artifacts/FINAL_ARTIFACT_INDEX.json`; `scripts/reproduce_all.sh`; `docs/reports/FINAL_HANDOFF.md`; G1.
- Ordered operations: Enumerate source locks, configs, topology, traces, checkpoints, G5 runs, G6 metrics, G7 figures, reports, hashes, environment, and exact commands; script validates/reproduces in dependency order and rejects hash mismatch.
- Exact command: `bash scripts/reproduce_all.sh --verify-only`.
- Acceptance: All paths/hashes resolve from clean checkout; no hidden manual step; final handoff distinguishes facts/limitations.
- Stop/rollback: Missing artifact/hash blocks handoff.

## 9. Evaluation and figure constants

- Figure 4: actual frozen 20-EA topology.
- Figure 5(a): learning rate `{1e-9,5e-9,1e-8,1e-7,5e-7,7e-7}`.
- Figure 5(b): gamma `{0.2,0.4,0.6,0.8,0.99}`.
- Figure 6(a): reward vs P `{.1,.3,.5,.7,.9}`, N `{10,15,20}`.
- Figure 6(b): local/horizontal/cloud action counts vs P, N=20.
- Figure 6(c): reward vs EA capacity `{4,5,6,7,8,9}` GHz, N `{10,15,20}`.
- Figure 6(d): reward vs N `{10,15,20,25,30}` with moderate `(1–3 Mbits,P=.5)`, heavy `(2–5,P=.7)`, extreme `(3–7,P=.9)`.
- Figure 6(e): reward vs N with balanced `(R_H=10,R_V=30)`, horizontal-centric `(20,20)`, vertical-centric `(5,40)` Mbps.
- Figure 6 default timeout: 20 slots = 2 seconds.
- Figure 7(a): delay vs P `{.1,.3,.5,.7,.9}`, timeout 10s.
- Figure 7(b): delay vs capacity `{3,4,5,6,7}` GHz, timeout 10s.
- Figure 7(c): delay vs timeout `{9.6,9.8,10.0,10.2,10.4}`s; no fixed timeout.
- Figure 7(d): pooled drop ratio vs P, timeout 2s.
- Figure 7(e): pooled drop ratio vs capacity, timeout 2s.
- Figure 7(f): pooled drop ratio vs timeout `{1.6,1.8,2.0,2.2,2.4}`s; no fixed timeout.
- Figure 8: ECHO vs ECHO-NoLSTM; N=20, P=.3, timeout 1s, episodes 0–3000.
- Methods: ECHO, HOODIE, RO, FLC, VO, HO, BCO, MLEO; ECHO-NoLSTM only where specified.
- Every reported point: 10 fixed seeds × 200 held-out paired episodes.
- Confidence intervals: across seed-level metrics.
- Average delay: approved negative-delay convention.
- Drop ratio: pool task counts within each seed before cross-seed summaries.

## 10. Exact executor prompt

```text
You are the single-task executor for repository hadifarajvand/hoodie_sim_v2.

Inputs:
- TASK_ID=<exact ID from artifacts/control/NEXT_TASK.json>
- ATTEMPT=<exact integer from artifacts/control/NEXT_TASK.json>
- PLAN=artifacts/reports/ECHO_MASTER_EXECUTION_PLAN.md
- PLAN_VERSION=ECHO-MEP-v4.1

Execute exactly TASK_ID and nothing else.

1. Read the entire plan and NEXT_TASK.json.
2. Verify NEXT_TASK.task_id, attempt, plan_version, main_head, and authorized branch.
3. Verify clean working tree and HEAD==NEXT_TASK.main_head.
4. Create/check out task/<lowercase-task-id>-r<attempt>.
5. Read only the task card's Required reads.
6. Edit only the task card's Allowed writes and G1(TASK_ID).
7. Perform Ordered operations exactly.
8. Run Exact command without substitution, suppression, xfail, or skip.
9. Verify every Acceptance item.
10. Write all seven G1 files. changed_files.json must equal the actual diff.
11. Set evidence status to one of IMPLEMENTED_PENDING_REVIEW, BLOCKED_EXTERNAL, REWORK, PLAN_CHANGE_REQUIRED, or STALE_BRANCH.
12. Commit `<TASK_ID>: <exact registry title>`.
13. Stop. Do not merge, push to main, edit the plan, select another task, or execute a fallback.

For SRC-001 source-access failure: write BLOCKED_EXTERNAL evidence, commit, and stop. BASE-001 requires a separate controller authorization and separate executor invocation.
```

## 11. Independent reviewer/controller prompt

```text
You are the independent reviewer/controller for repository hadifarajvand/hoodie_sim_v2.
You did not implement the task.

Mode:
- BOOTSTRAP, or
- REVIEW with TASK_ID, ATTEMPT, and TASK_BRANCH.

Inputs in REVIEW mode:
- TASK_ID=<ID reviewed>
- ATTEMPT=<attempt reviewed>
- TASK_BRANCH=task/<lowercase-task-id>-r<attempt>
- PLAN=artifacts/reports/ECHO_MASTER_EXECUTION_PLAN.md
- PLAN_VERSION=ECHO-MEP-v4.1

Allowed writes:
- G2(TASK_ID,ATTEMPT)
- artifacts/control/EXECUTION_STATE.json
- artifacts/control/NEXT_TASK.json
- artifacts/reports/ECHO_MASTER_EXECUTION_PLAN.md

You must not modify implementation, tests, configs, generated scientific outputs, or task evidence.

BOOTSTRAP:
1. Require G3 to be absent.
2. Verify main equals the planning-start HEAD.
3. Initialize all 73 statuses/attempts from the registry.
4. Write NEXT_TASK for SRC-001 attempt 1 on branch task/src-001-r1.
5. Commit `CONTROL BOOTSTRAP: initialize execution state`.
6. Stop and print the exact executor invocation.

REVIEW:
1. Verify current main SHA, task start SHA, branch ancestry, plan version, task ID, and attempt.
2. If main changed after authorization, record STALE_BRANCH, do not merge, increment attempt, authorize the same task from current main, and stop.
3. Compare `git diff --name-only <start_sha>..<task_sha>` to changed_files.json; require exact equality.
4. Expand the card allowlist and G1 path grammar; reject every unlisted path.
5. Inspect every changed line and every evidence claim.
6. Re-run the card's Exact command in a clean review worktree.
7. Verify all Acceptance criteria, hashes, command output, and rollback statement.
8. Write G2 only.

Decision:
- PASS: merge TASK_BRANCH into main with `git merge --no-ff`; then update the task row to VERIFIED_COMPLETE, update the dashboard/status totals, write G3, commit `CONTROL <TASK_ID>: verify and advance`, recompute statuses, choose one next task, and stop.
- REWORK: do not merge; set task REWORK in plan/G3, increment attempt, authorize the same task, and stop.
- BLOCKED_EXTERNAL: require the task diff to contain G1 files only; merge that evidence-only branch with `--no-ff`; set task BLOCKED_EXTERNAL in plan/G3; recompute unrelated readiness; authorize the earliest unrelated READY task in a new invocation; and stop.
- PLAN_CHANGE_REQUIRED: do not merge; set global execution blocked, NEXT_TASK.task_id=null, and stop.
- MERGE_BLOCKED: record blocker, NEXT_TASK.task_id=null, and stop.

Status recomputation:
- keep VERIFIED_COMPLETE;
- READY iff all dependencies are VERIFIED_COMPLETE and no blocker exists;
- otherwise BLOCKED;
- REWORK keeps priority over other READY tasks;
- select the earliest registry task among eligible tasks;
- write exactly one NEXT_TASK or null.

Print only:
- verdict;
- reviewed task/attempt/SHAs;
- merge SHA or none;
- plan/control commit SHA or none;
- changed-path audit result;
- test result;
- updated status totals;
- next authorized task and exact executor invocation.
```

## 12. Structural validation and dashboard

The v4.1 plan is valid only when all checks below pass:

| Check | Required result |
|---|---|
| Registry task IDs | 73 unique |
| Card task IDs | same 73 unique IDs |
| Phase totals | 6 / 23 / 20 / 12 / 12 |
| Initial statuses | 5 VERIFIED_COMPLETE / 2 READY / 66 BLOCKED |
| Missing dependency IDs | 0 |
| Self dependencies | 0 |
| DAG cycles | 0 |
| Wildcards in Allowed writes | 0 |
| Default parallel executors | disabled |
| SRC blocked fallback in same executor | prohibited |
| Reviewer/controller prompt | present |
| Pre-freeze ECHO decontamination owner | BASE-005 |
| Post-freeze ECHO attachment owner | ECHO-001 |
| Frozen shared files writable by ECHO-001 | no |
| Early schema dependency | ECHO-011 depends on EVAL-001 |
| Evaluation execution before ECHO-020 | no |
| Permanent deletion | prohibited |

Initial next authorization is `SRC-001`, attempt 1. `BASE-001` is logically READY but is not executable until the controller writes it into `NEXT_TASK.json`.

## 13. Final execution meaning

Following this runbook will:

1. lock the current manuscript rather than implement from memory;
2. validate and freeze HOODIE before accepting ECHO;
3. remove current ECHO imports/conditionals from the shared kernel before the freeze;
4. attach ECHO afterward only through frozen neutral hooks;
5. freeze logs and evaluation schemas before pending/reward/interval logging;
6. implement ECHO in equation/algorithm dependency order;
7. review and merge one task at a time through an independent controller;
8. stop rather than improvise on missing authority, files, permissions, or failed tests;
9. evaluate all methods on paired immutable traces without held-out leakage;
10. generate all 15 panels from retained machine-readable evidence;
11. archive superseded outputs without deletion;
12. finish with hashes, reports, artifact index, and exact verification/reproduction commands.
