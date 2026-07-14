# ECHO Master Execution Plan — Final Closed-Loop Agent Runbook

## 1. Document control

| Field | Value |
|---|---|
| Plan version | `ECHO-MEP-v4.2` |
| Plan status | `FINAL — BOOTSTRAPPABLE CLOSED-LOOP RUNBOOK` |
| Repository | `hadifarajvand/hoodie_sim_v2` |
| Branch | `main` |
| Planning-base HEAD | `0a510fc02e335d1f56e604134db8bb6fcf35db7d` |
| Audited pre-implementation baseline | `d8dbf131dc4cff3879636853cafa9371a0914d99` |
| Live document title | `مقاله` |
| Live document ID | `17iqZWA0bF5unbyuVYnRiW1IUcr0Ctb2KFw1f5XE2poE` |
| Live proposed-method tab ID | `t.iav4589yyeo7` |
| Live content heading | `III. Proposed Effective Completion via Hybrid Offloading Framework (ECHO)` |
| Google Drive current revision | `273` |
| Google Drive modified time | `2026-07-14T07:25:15.431Z` |
| Connector method revision | `ALtnJHxLEsnZk9if3bNlbe0zzd4pRY_MBM_8-J9Xu2DeAWi0dUyqL3JaM5jIbn0eN2bBmd5xB0zWp-Xz0W8QL0tzGwNRrhdBWduWJxzecg` |
| Previous Drive revision | `270` |
| Superseded connector revision | `ALtnJHz611-DqkvSCGUC_z6Fe7oTOtKddqKX28Uy-8yxMUchKHt1qIK0ynQUDlus57gMvnBz5VJeXCNzVUVbhwab1h05IlKz0AKes7cQJg` |

No tab title is asserted. This plan supersedes every earlier execution plan and runbook when they disagree.

### 1.1 Bootstrap anchor rule

The plan cannot contain its own future commit SHA. The controller therefore discovers the approved v4.2 plan commit as the unique first descendant of the Planning-base HEAD whose diff changes only `artifacts/reports/ECHO_MASTER_EXECUTION_PLAN.md` and whose content declares `ECHO-MEP-v4.2`. Before the first executor, later bootstrap commits may change only `scripts/control/validate_echo_plan.py` and G3 control files. The controller stores the discovered approved plan commit in `EXECUTION_STATE.json`; all later work must descend from it.

## 2. Goal and final deliverables

The project will faithfully reproduce HOODIE, freeze a neutral synchronized cloud-edge simulator, attach ECHO only through frozen hooks, verify all 67 equations and both algorithms, run fair paired evaluation, generate Figures 4–8 from retained outputs, and deliver exact rerun artifacts.

Final deliverables:
- immutable ECHO and HOODIE authority bundles.
- canonical HOODIE configuration and topology.
- immutable paired traces and a neutral synchronized physical kernel.
- faithful per-EA HOODIE learners and six isolated heuristic baselines.
- a frozen HOODIE/base release manifest.
- an ECHO adapter implementing ERT scheduling, size-specific state/action spaces, masks, reward, event-SMDP, masked DDQL, LSTM, and ECHO-NoLSTM.
- equation/algorithm coverage and paired pilot evidence.
- frozen logging/evaluation schemas, trace bank, lineage, checkpoints, raw logs, metrics, and confidence intervals.
- Figures 4–8 with fifteen panels in SVG/PDF and deterministic 300-dpi PNG.
- final reports, archive redirects, artifact index, and exact verification/reproduction scripts.

## 3. Live-revision reconciliation and scientific contracts

### 3.1 Revision 270 → 273 result

Revision 273 is a **material method change**, not metadata-only. It supersedes the former fixed 30-destination/32-output architecture. The current authoritative scalability contract is:

- for a run with `N` EAs, the canonical action dimension is exactly `N+2`: local, `N` horizontal-destination positions, cloud;
- the state contains exactly the destination blocks present for that run; smaller systems are not padded to 30 destinations;
- the source and disconnected positions remain present but are disabled by the physical-and-deadline mask;
- a separate checkpoint is trained and evaluated for each `N ∈ {10,15,20,25,30}`;
- EAs within the same ECHO run share model parameters, while source-specific interval accumulators, task ownership, and event provenance remain separate;
- no zero-shot checkpoint transfer across different values of `N` is claimed.

The old 30/32 implementation is candidate code only and must be superseded or parameterized by `ECHO-009`, `ECHO-012`, and `ECHO-015`. `SRC-001` still performs the complete 69-row audit before any ECHO task is accepted.

### 3.2 Authority order

1. current live ECHO proposed-method tab at the identifiers in Section 1.
2. original HOODIE paper PDF/OCR for inherited base mechanics and HOODIE learning.
3. `research/ECHO_evaluation_spec.md` when it does not conflict with the current live method.
4. topology and PNG-export authorizations.
5. repository code and tests as implementation evidence only.
6. historical reports, source snapshots, smoke outputs, checkpoints, and figures as non-authoritative evidence.

A passing test cannot override a paper equation. Existing code cannot define the method. A new live revision reopens `SRC-001` and blocks ECHO acceptance.

### 3.3 Non-negotiable ECHO behavior
- independent Bernoulli arrival opportunity for every EA in every decision slot.
- `d_i = t_i^a + δ_i - 1`.
- one direct route decision at arrival and no second destination decision.
- one local waiting queue and one outbound waiting queue per source, excluding active operations.
- one non-preemptive local CPU and one non-preemptive transmitter per source.
- transmission finishing at end of slot `t` is admitted to its stored destination at boundary `t+1`.
- source-indexed FIFO destination queues and equal public-CPU sharing.
- destination workload in remaining CPU cycles.
- fresh status preferred and LSTM used only for stale or missing status.
- constructive deterministic `O(q²)` ERT ordering: smallest nonnegative ERT, otherwise minimum lateness, FIFO/stable-ID tie break.
- size-specific `N+2` action output and size-specific destination state blocks.
- Equations (55)–(58) reward.
- Equation (59) as one discounted source-EA interval between consecutive actual decisions.
- no overlapping task-level replay transitions.
- target discount `γ^Δ_(n,m)`.
- masked Dueling Double-DQL from Equations (61)–(67).
- within-run ECHO parameter sharing plus separate source-specific event ownership.
- separate supervised LSTM forecasting with no held-out fitting.

### 3.4 Boundary chronology
1. apply service/transmission completions produced at end of `t-1` and destination admissions due at `t`.
2. resolve outcomes and add rewards to the already-open source-EA interval.
3. obtain fresh status or stale/missing LSTM estimate.
4. remove expired waiting tasks without preempting active work.
5. observe all same-slot arrivals.
6. for each arriving EA, close its previous interval before opening the new decision.
7. estimate, mask, choose, and admit.
8. rebuild affected waiting orders and start idle source resources.
9. schedule destination queues.
10. execute exactly one slot of active service.
11. update histories/LSTM and perform learning/target-copy work.
12. at `T+1`, resolve terminal outcomes and close all open intervals.

## 4. Current code ownership map

| Current condition | Owning task |
|---|---|
| Shared environment imports ECHO modules and has ECHO conditionals | `BASE-005` removes them before freeze |
| Mutable/recreated traces | `BASE-004` |
| One-transmitter invariant not fully proven | `BASE-008` |
| Next-boundary admission requires exact staging tests | `BASE-010` |
| HOODIE alias resolves to generic ADAPTIVE | `BASE-019` |
| Paper-state builder has placeholder forecast behavior | `BASE-015` |
| Shared HOODIE learner path does not prove one learner per EA | `BASE-016` |
| Existing ECHO action code always exposes 32 outputs | `ECHO-009` supersedes it with N+2 |
| Existing ECHO state code assumes fixed maximum padding | `ECHO-012` supersedes it with N-specific blocks |
| Existing ECHO agent architecture does not prove within-run parameter sharing | `ECHO-015` |
| Event-SMDP exists but boundary ownership remains unproven | `ECHO-014` and `ECHO-018` |
| Decision events are processed before same-boundary resolution events | `ECHO-018` |
| Schemas formerly appeared after pilot | `EVAL-001` now precedes `ECHO-011` |

Existing implementation is retained as candidate code. The owner task must accept unchanged, repair, isolate, or supersede it using authority and tests.

## 5. Deterministic path grammars

Directory wildcards are never permissions. A task may write only explicit paths or one of these grammars.

### G1 — executor evidence
For `<ID>`: `artifacts/task_evidence/<ID>/{report.md,status.json,commands.txt,test_output.txt,changed_files.json,hashes.json,git_diff.patch}`.

### G2 — reviewer evidence
For `<ID>` attempt `<A>`: `artifacts/task_reviews/<ID>/attempt_<A>/{review.md,status.json,commands.txt,test_output.txt,diff_audit.json}`.

### G3 — control and preflight
- `artifacts/control/PREFLIGHT_REPORT.json`
- `artifacts/control/EXECUTION_STATE.json`
- `artifacts/control/NEXT_TASK.json`

### G4 — trace bank
For `trace_id=<scenario_id>__seed<two_digit_seed>__<config_sha12>`: `artifacts/evaluation/trace_bank/<trace_id>.json` and `.sha256`; index: `artifacts/evaluation/trace_bank/index.json`.

### G5 — run outputs
For `run_id=<method>__<scenario_id>__n<N>__seed<two_digit_seed>__<config_sha12>`: `run_manifest.json`, `task_log.jsonl`, `decision_log.jsonl`, `episode_metrics.csv`, optional learning-only `training_metrics.csv` and `checkpoint.pt`, and `DONE.sha256` under `artifacts/evaluation/runs/<run_id>/`.

### G6 — aggregated outputs
For panel IDs `f5a,f5b,f6a,f6b,f6c,f6d,f6e,f7a,f7b,f7c,f7d,f7e,f7f,f8`: one CSV under each of `artifacts/metrics/seed_level`, `panel_level`, and `confidence_intervals`.

### G7 — figures
For figure `<N>`: `artifacts/figures/vector/figure<N>.{svg,pdf}`, `artifacts/figures/png_300dpi/figure<N>.png`, `artifacts/figures/manifests/figure<N>.json`; panel CSV: `artifacts/figures/panel_exports/<panel_id>.csv`.

### G8 — archive
For approved source SHA `<sha>` and basename `<name>`: `artifacts/archive/superseded/<sha>__<name>`; index: `artifacts/archive/archive_manifest.json`.

## 6. Closed-loop executor and reviewer/controller

### 6.1 Roles and status machine

- Executor: executes exactly one authorized card, writes only its allowlist plus G1, commits, and stops.
- Independent reviewer/controller: reviews without repairing implementation, reruns exact commands, merges only on PASS, updates the plan and G2/G3, authorizes exactly one next task, and stops.
- Executor and reviewer are different invocations. Parallel execution is disabled.

Status flow: `BLOCKED → READY → IN_PROGRESS → IMPLEMENTED_PENDING_REVIEW → VERIFIED_COMPLETE`; failures: `BLOCKED_EXTERNAL`, `REWORK`, `PLAN_CHANGE_REQUIRED`, `STALE_BRANCH`, `MERGE_BLOCKED`.

### 6.2 Preflight and bootstrap

Before any executor:
1. discover and store the approved v4.2 plan commit using Section 1.1.
2. verify every later bootstrap commit changes only `scripts/control/validate_echo_plan.py` or G3.
3. run `python3 scripts/control/validate_echo_plan.py --plan artifacts/reports/ECHO_MASTER_EXECUTION_PLAN.md --json artifacts/control/PREFLIGHT_REPORT.json` and require PASS.
4. initialize all 73 statuses and attempts in `EXECUTION_STATE.json`.
5. write `NEXT_TASK.json` for `SRC-001`, attempt 1, branch `task/src-001-r1`.
6. commit control files and stop after printing the exact executor invocation.

The executor branches from the latest `main` only when it descends from the approved plan commit and every intervening path is a permitted bootstrap/control path. The controller records the exact executor start SHA in `NEXT_TASK.json` immediately before launch.

### 6.3 Executor algorithm
1. read this entire plan and G3.
2. verify plan version, authorized task/attempt/branch/start SHA, clean tree, and ancestry.
3. create or check out the exact task branch.
4. read only Required reads and edit only Allowed writes plus G1.
5. perform Ordered operations exactly.
6. run Exact command without substitution or suppressed failure.
7. write complete G1 with exact diff and hashes.
8. commit `<ID>: <exact title>`.
9. stop; do not merge, edit plan, start another card, or push implementation to main.

If `SRC-001` lacks access, it records `BLOCKED_EXTERNAL` in G1 and stops. It must not execute `BASE-001` in the same invocation.

### 6.4 Reviewer/controller algorithm
1. verify task/attempt/start/main/task SHAs and branch ancestry.
2. require exact equality between Git diff paths and `changed_files.json`.
3. expand the card allowlist and reject every unlisted path.
4. inspect every changed line and evidence claim.
5. rerun the exact command in a clean review worktree.
6. evaluate every acceptance criterion and write G2 only.
7. on PASS merge with `--no-ff`, update only the task status/dashboard plus G3, commit `CONTROL <ID>: verify and advance`.
8. on REWORK do not merge; increment attempt and reauthorize the same task.
9. on BLOCKED_EXTERNAL merge evidence-only G1, mark blocked, authorize the earliest unrelated READY task in a new invocation.
10. on PLAN_CHANGE_REQUIRED or MERGE_BLOCKED set `NEXT_TASK.task_id=null` and stop.
11. recompute READY iff all dependencies are VERIFIED_COMPLETE; choose the earliest registry task; write exactly one next task or null; stop.

A changed live revision reopens `SRC-001`; a change to a frozen-base hash reopens its base owner and downstream tasks; any unaudited implementation commit to main reopens `AUDIT-002`.

## 7. Master task registry

Initial totals: 5 `VERIFIED_COMPLETE`, 2 `READY`, 66 `BLOCKED`; total 73.

### Phase 0 — source, audit, and control (6)

| ID | Status | Dependencies | Title |
|---|---|---|---|
| SRC-001 | READY | NONE | Lock current live ECHO source and close 69-row audit |
| SRC-002 | VERIFIED_COMPLETE | NONE | Maintain HOODIE paper evidence registry |
| AUDIT-001 | VERIFIED_COMPLETE | NONE | Maintain current code-path inventory |
| AUDIT-002 | VERIFIED_COMPLETE | NONE | Reconcile historical completion claims |
| PLAN-001 | VERIFIED_COMPLETE | NONE | Maintain closed-loop execution plan |
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
| BASE-007 | BLOCKED | BASE-006 | Implement private FIFO waiting and active separation |
| BASE-008 | BLOCKED | BASE-006 | Implement one outbound FIFO/transmitter per source |
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
| BASE-022 | BLOCKED | BASE-021 | Reproduce HOODIE experiment organization and trends |
| FREEZE-001 | BLOCKED | BASE-022 | Freeze validated neutral simulator and HOODIE baseline |

### Phase 2 — ECHO on frozen base (20)

| ID | Status | Dependencies | Title |
|---|---|---|---|
| ECHO-001 | BLOCKED | FREEZE-001, SRC-001 | Attach ECHO adapter to frozen neutral hooks |
| ECHO-002 | BLOCKED | ECHO-001 | Implement Equations (1)–(8) lifecycle and dispatch |
| ECHO-003 | BLOCKED | ECHO-002 | Implement Equations (9)–(11) local estimate |
| ECHO-004 | BLOCKED | ECHO-003 | Implement Equations (12)–(16) outbound estimate |
| ECHO-005 | BLOCKED | ECHO-004 | Implement Equations (17)–(25) destination model |
| ECHO-006 | BLOCKED | ECHO-005 | Implement Equations (26)–(28) history and LSTM inputs |
| ECHO-007 | BLOCKED | ECHO-006 | Implement Equation (29) local queue ERT ordering |
| ECHO-008 | BLOCKED | ECHO-007 | Implement Equation (30) outbound ERT ordering |
| ECHO-009 | BLOCKED | ECHO-008 | Implement size-specific N+2 canonical action space |
| ECHO-010 | BLOCKED | ECHO-009 | Implement Equations (42)–(46) mask and fallback |
| ECHO-011 | BLOCKED | ECHO-010, EVAL-001 | Implement Equations (47)–(50) pending records and schema-compliant decision logs |
| ECHO-012 | BLOCKED | ECHO-011 | Implement Equations (51)–(54) size-specific normalized state |
| ECHO-013 | BLOCKED | ECHO-012 | Implement Equations (55)–(58) task reward |
| ECHO-014 | BLOCKED | ECHO-013 | Implement Equations (59)–(60) event intervals |
| ECHO-015 | BLOCKED | ECHO-014 | Implement Equations (61)–(67) masked DDQL with within-run parameter sharing |
| ECHO-016 | BLOCKED | ECHO-015 | Implement fresh/stale status and supervised LSTM training |
| ECHO-017 | BLOCKED | ECHO-016 | Implement isolated ECHO-NoLSTM |
| ECHO-018 | BLOCKED | ECHO-017 | Implement exact Algorithm 1 and 2 chronology |
| ECHO-019 | BLOCKED | ECHO-018 | Run deterministic ECHO unit and smoke suite |
| ECHO-020 | BLOCKED | ECHO-019 | Produce equation coverage and paired pilot gate |

### Phase 3 — schemas and authoritative evaluation (12)

| ID | Status | Dependencies | Title |
|---|---|---|---|
| EVAL-001 | BLOCKED | SRC-001, BASE-004 | Freeze logging, evaluation, and 15-panel schemas before ECHO logging |
| EVAL-002 | BLOCKED | ECHO-020, EVAL-001 | Generate immutable paired trace bank |
| EVAL-003 | BLOCKED | EVAL-002 | Freeze config, topology, and checkpoint lineage |
| EVAL-004 | BLOCKED | EVAL-003 | Validate all method adapters on common inputs |
| EVAL-005 | BLOCKED | EVAL-004 | Measure throughput and freeze shard budget |
| EVAL-006 | BLOCKED | EVAL-005 | Run Figure-5 validation sweeps |
| EVAL-007 | BLOCKED | EVAL-006 | Train equal-budget final method checkpoints |
| EVAL-008 | BLOCKED | EVAL-007 | Run 10×200 held-out paired evaluation |
| EVAL-009 | BLOCKED | EVAL-008 | Validate generated, completed, and dropped accounting |
| EVAL-010 | BLOCKED | EVAL-008 | Validate no masked ECHO action |
| EVAL-011 | BLOCKED | EVAL-008 | Validate trace, config, topology, and checkpoint hashes |
| EVAL-012 | BLOCKED | EVAL-009, EVAL-010, EVAL-011 | Aggregate seed metrics and 95% confidence intervals |

### Phase 4 — figures, reports, cleanup, and handoff (12)

| ID | Status | Dependencies | Title |
|---|---|---|---|
| FIG-001 | BLOCKED | BASE-002 | Render Figure 4 topology |
| FIG-002 | BLOCKED | EVAL-006 | Render Figure 5(a–b) |
| FIG-003 | BLOCKED | EVAL-012 | Render Figure 6(a–e) |
| FIG-004 | BLOCKED | EVAL-012 | Render Figure 7(a–f) |
| FIG-005 | BLOCKED | EVAL-012 | Render Figure 8 |
| FIG-006 | BLOCKED | FIG-001, FIG-002, FIG-003, FIG-004, FIG-005 | Validate all vector and PNG exports and lineage |
| REPORT-001 | BLOCKED | BASE-022, FREEZE-001 | Write final HOODIE reproduction report |
| REPORT-002 | BLOCKED | ECHO-020 | Write final ECHO implementation report |
| REPORT-003 | BLOCKED | EVAL-012, FIG-006 | Write final evaluation and figure report |
| CLEAN-002 | BLOCKED | REPORT-001, REPORT-002, REPORT-003 | Archive superseded artifacts without deletion |
| CLEAN-003 | BLOCKED | CLEAN-002 | Remove canonical-path ambiguity without deletion |
| HANDOFF-001 | BLOCKED | CLEAN-003 | Produce final artifact index and exact rerun commands |

## 8. Complete task cards

Each card is an executable specification. `G1`–`G8` mean only the exact grammars in Section 5.

### SRC-001 — Lock current live ECHO source and close 69-row audit

- **Dependencies:** NONE.
- **Required reads:** Section 1 identifiers; live Google Doc tab t.iav4589yyeo7; `research/ECHO_method_spec.md`; existing authority artifacts; this plan.
- **Allowed writes:** `research/authority/echo/live/ECHO_PROPOSED_METHOD.md`; `research/authority/echo/live/source_metadata.json`; `research/authority/echo/live/SHA256SUMS`; `artifacts/audits/echo_live_revision_audit.md`; `scripts/authority/verify_echo_source_lock.py`; `tests/unit/test_echo_source_lock.py`; `G1`.
- **Ordered operations:**
  1. Confirm Drive revision 273 and connector revision recorded in Section 1.
  2. Export only the proposed-method tab; do not invent a tab title.
  3. Normalize line endings only and compute raw/normalized SHA-256.
  4. Verify Equations 1–67, Algorithm 1 lines 1–23, Algorithm 2 lines 1–12.
  5. Create 69 audit rows and map every non-MATCH row to one task and one exact test path.
  6. Explicitly classify the revision-273 scalability change: N+2 size-specific action/state dimensions and parameter sharing among EAs within one run.
- **Exact command:**
```bash
python3 scripts/authority/verify_echo_source_lock.py --snapshot research/authority/echo/live/ECHO_PROPOSED_METHOD.md --metadata research/authority/echo/live/source_metadata.json --checksums research/authority/echo/live/SHA256SUMS --audit artifacts/audits/echo_live_revision_audit.md && python3 -m pytest tests/unit/test_echo_source_lock.py -q
```
- **Acceptance:**
  - Identifiers and revisions match Section 1.
  - 67 equations and 2 algorithms present.
  - 69/69 rows classified.
  - hashes verify.
  - no unsupported tab title.
  - all semantic changes have task/test consequences.
- **Stop/rollback:** If access is absent, write only G1 with BLOCKED_EXTERNAL and stop. If revision differs, write PLAN_CHANGE_REQUIRED and stop.

### SRC-002 — Maintain HOODIE paper evidence registry

- **Dependencies:** NONE.
- **Required reads:** `resources/papers/hoodie/ocr/merged.md`; `resources/papers/hoodie/ocr/merged.txt`; existing paper mechanism registry.
- **Allowed writes:** `src/analysis/paper_mechanism_registry.py`; `artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json`; `artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.md`; `tests/unit/test_paper_mechanism_registry.py`; `tests/integration/test_paper_mechanism_registry_flow.py`; `G1`.
- **Ordered operations:**
  1. Preserve exact page/table/equation provenance.
  2. Classify each value PAPER_EXPLICIT/PAPER_DERIVED/APPROVED_CLARIFICATION/UNRESOLVED.
  3. Exclude ECHO-only semantics.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_paper_mechanism_registry.py tests/integration/test_paper_mechanism_registry_flow.py -q
```
- **Acceptance:**
  - Every Phase-1 mechanism has a source location and classification.
  - No ECHO behavior is attributed to HOODIE.
- **Stop/rollback:** Already complete; execute only if controller reopens it.

### AUDIT-001 — Maintain current code-path inventory

- **Dependencies:** NONE.
- **Required reads:** src; tests; existing implementation-scan artifacts.
- **Allowed writes:** `src/analysis/hoodie_proposed_fidelity/implementation_scan.py`; `artifacts/analysis/hoodie-proposed-fidelity/implementation_scan.json`; `tests/unit/test_hoodie_proposed_fidelity_implementation_scan.py`; `G1`.
- **Ordered operations:**
  1. Enumerate runtime entry points, queues, learner paths, evaluation paths and artifacts.
  2. Verify claims by opening source.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_hoodie_proposed_fidelity_implementation_scan.py -q
```
- **Acceptance:**
  - All paths exist at tested SHA.
  - No completion inferred from names.
- **Stop/rollback:** Reopen only after material repository restructuring.

### AUDIT-002 — Reconcile historical completion claims

- **Dependencies:** NONE.
- **Required reads:** git history; `artifacts/reports`; `artifacts/test_triage`; readiness audit artifacts.
- **Allowed writes:** `src/analysis/hoodie_training_foundation_readiness_audit.py`; `artifacts/analysis/hoodie-training-foundation-readiness-audit/report.json`; `tests/unit/test_hoodie_training_foundation_readiness_audit.py`; `G1`.
- **Ordered operations:**
  1. Classify claims as authoritative/potentially reusable/premature/historical/revert candidate.
  2. Assign each implementation area to one owning task.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_hoodie_training_foundation_readiness_audit.py -q
```
- **Acceptance:**
  - Every current implementation area has one owner and acceptance gate.
- **Stop/rollback:** Any unaudited implementation commit to main reopens this task.

### PLAN-001 — Maintain closed-loop execution plan

- **Dependencies:** NONE.
- **Required reads:** this plan; current git history; current live source metadata.
- **Allowed writes:** `artifacts/reports/ECHO_MASTER_EXECUTION_PLAN.md`; `G1`.
- **Ordered operations:**
  1. Preserve exactly 73 unique task IDs.
  2. Maintain valid acyclic dependencies.
  3. Maintain one exact card per task.
  4. Run structural preflight.
- **Exact command:**
```bash
python3 scripts/control/validate_echo_plan.py --plan artifacts/reports/ECHO_MASTER_EXECUTION_PLAN.md
```
- **Acceptance:**
  - 73 registry IDs equal 73 card IDs.
  - no missing/self dependencies.
  - DAG acyclic.
  - status totals correct.
  - no wildcard permissions.
  - all READY commands exist or are task-created.
- **Stop/rollback:** Plan changes require a planning-only commit; executors may not edit this file.

### CLEAN-001 — Classify existing artifacts

- **Dependencies:** NONE.
- **Required reads:** artifacts; research; existing indexes.
- **Allowed writes:** `artifacts/classification/artifact_inventory.json`; `artifacts/classification/artifact_inventory.md`; `scripts/cleanup/classify_artifacts.py`; `tests/unit/test_artifact_classification.py`; `G1`.
- **Ordered operations:**
  1. Classify each artifact authoritative/historical/superseded/smoke-only/synthetic/unresolved.
  2. Do not delete.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_artifact_classification.py -q
```
- **Acceptance:**
  - No legacy figure/checkpoint/report cited as final evidence.
  - All archive-eligible paths explicit.
- **Stop/rollback:** Reopen when new unclassified artifact families appear.

### BASE-001 — Freeze canonical HOODIE Table-4 configuration

- **Dependencies:** PLAN-001, CLEAN-001.
- **Required reads:** `resources/papers/hoodie/ocr/merged.md`; `resources/papers/hoodie/ocr/merged.txt`; `configs/simulation.yaml`; `configs/runtime_model.yml`; `configs/experiments/exp_small_deterministic.json`; paper registry; topology authorization.
- **Allowed writes:** `configs/authoritative/hoodie_table4.yaml`; `configs/authoritative/hoodie_table4.schema.json`; `tests/unit/test_hoodie_table4_config.py`; `artifacts/authority/hoodie/table4_manifest.json`; `G1`.
- **Ordered operations:**
  1. Encode 20 EAs, 100 decision + 10 drain slots, P=.5, task sizes 2.0–5.0 Mbits step .1, density .297 Gcycles/Mbit, slot .1s, timeout 20 slots/2s.
  2. Copy all rates and learning parameters from exact Table-4 rows.
  3. Classify all values and compare current configs.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_hoodie_table4_config.py -q
```
- **Acceptance:**
  - Schema valid.
  - every value has unit/source/classification.
  - manifest hashes present.
  - no unresolved value promoted.
  - smoke configs remain non-authoritative.
- **Stop/rollback:** Unresolved paper value => REWORK; do not guess.

### BASE-002 — Freeze approved topology and scalable topology rule

- **Dependencies:** BASE-001.
- **Required reads:** `src/environment/topology.py`; topology authorization; canonical config.
- **Allowed writes:** `configs/authoritative/hoodie_topology.json`; `artifacts/authority/hoodie/topology_adjacency.csv`; `artifacts/authority/hoodie/topology_edges.csv`; `artifacts/authority/hoodie/topology.svg`; `artifacts/authority/hoodie/topology.png`; `artifacts/authority/hoodie/topology_manifest.json`; `tests/unit/test_hoodie_topology_authority.py`; `G1`.
- **Ordered operations:**
  1. Freeze exact N=20 adjacency.
  2. Verify G_N=5K_(N/5) for N divisible by 5.
  3. Export deterministic coordinates and hashes.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_hoodie_topology_authority.py -q
```
- **Acceptance:**
  - N=20 equals approved anchor.
  - N=10/15/20/25/30 deterministic.
  - no illegal/self edges.
  - repeated exports hash identically.
- **Stop/rollback:** Never replace approved adjacency with a visually similar graph.

### BASE-003 — Validate independent per-EA arrivals and 100+10 slots

- **Dependencies:** BASE-002.
- **Required reads:** `src/evaluation/trace_protocol.py`; canonical config/topology; `tests/unit/test_trace_protocol_paper_semantics.py`.
- **Allowed writes:** `src/evaluation/trace_protocol.py`; `tests/unit/test_trace_protocol_paper_semantics.py`; `tests/unit/test_trace_expected_arrivals.py`; `G1`.
- **Ordered operations:**
  1. One Bernoulli draw per EA per decision slot.
  2. zero drain arrivals.
  3. exact size/density/deadline.
  4. stable ordering and metadata.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_trace_protocol_paper_semantics.py tests/unit/test_trace_expected_arrivals.py -q
```
- **Acceptance:**
  - P=0 => 0 tasks.
  - P=1 => N×100 tasks.
  - N=20,P=.5 repeated-seed mean centered on 1000.
  - slots 100–109 no arrivals.
- **Stop/rollback:** Do not change draw order to force a preferred sample count.

### BASE-004 — Make paired traces immutable and directly consumable

- **Dependencies:** BASE-003.
- **Required reads:** `src/evaluation/trace_protocol.py`; `src/environment/trace_source.py`; `src/evaluation/runner.py`; `src/environment/evaluation_gym_adapter.py`.
- **Allowed writes:** `src/evaluation/trace_protocol.py`; `src/environment/trace_source.py`; `src/evaluation/runner.py`; `src/environment/evaluation_gym_adapter.py`; `tests/unit/test_trace_immutability.py`; `tests/integration/test_paired_trace_identity.py`; `G1`.
- **Ordered operations:**
  1. Freeze dataclasses.
  2. add canonical serialization and SHA-256.
  3. accept supplied trace without regeneration.
  4. create fresh runtime tasks per method.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_trace_immutability.py tests/integration/test_paired_trace_identity.py -q
```
- **Acceptance:**
  - Mutation raises.
  - same bytes/hash across methods.
  - no regeneration when trace supplied.
  - runtime mutation does not mutate blueprint.
- **Stop/rollback:** Do not cache mutable Task objects inside trace bank.

### BASE-006 — Freeze hand-calculated base slot contract

- **Dependencies:** BASE-004.
- **Required reads:** HOODIE registry; `src/environment/gym_adapter.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/slot_engine.py`; queue files.
- **Allowed writes:** `docs/contracts/hoodie_slot_contract.md`; `tests/fixtures/hoodie_slot_timelines.json`; `tests/unit/test_hoodie_slot_contract_vectors.py`; `G1`.
- **Ordered operations:**
  1. Specify boundary/service order for same-slot arrivals, local/transmission/destination service, expiration, late active completion and drain.
  2. Calculate expected slots manually.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_hoodie_slot_contract_vectors.py -q
```
- **Acceptance:**
  - fixtures internally consistent.
  - boundary versus end-of-slot explicit.
  - no ECHO reward/mask/ERT semantics.
- **Stop/rollback:** No runtime changes in this task.

### BASE-005 — Extract neutral synchronized multi-EA kernel and remove ECHO contamination

- **Dependencies:** BASE-006.
- **Required reads:** BASE-006 contract; `src/environment/gym_adapter.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/slot_engine.py`; `src/echo_action_space.py`; `src/echo_ert.py`.
- **Allowed writes:** `src/environment/gym_adapter.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/slot_engine.py`; `src/environment/method_hooks.py`; `tests/unit/test_hoodie_slot_engine.py`; `tests/integration/test_same_slot_multi_ea.py`; `tests/architecture/test_neutral_kernel_imports.py`; `docs/contracts/neutral_kernel_hooks.md`; `G1`.
- **Ordered operations:**
  1. Process all same-slot arrivals before one global service advance.
  2. Remove all src.echo_* imports and ECHO-name conditionals from shared kernel.
  3. Expose neutral hooks with no ECHO implementation.
  4. Preserve base timeline byte-for-byte.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_hoodie_slot_engine.py tests/integration/test_same_slot_multi_ea.py tests/architecture/test_neutral_kernel_imports.py -q
```
- **Acceptance:**
  - K arrivals => K decisions and one service advance.
  - no global current-task skip.
  - zero ECHO imports in frozen kernel candidates.
  - hook defaults reproduce HOODIE behavior.
- **Stop/rollback:** Any need to modify ECHO modules is out of scope; stop PLAN_CHANGE_REQUIRED.

### BASE-007 — Implement private FIFO waiting and active separation

- **Dependencies:** BASE-006.
- **Required reads:** `src/environment/private_queue.py`; `src/environment/execution_helper.py`; `src/environment/evaluation_gym_adapter.py`; BASE-006 fixtures.
- **Allowed writes:** `src/environment/private_queue.py`; `src/environment/execution_helper.py`; `src/environment/evaluation_gym_adapter.py`; `tests/unit/test_private_queue_lifecycle.py`; `tests/unit/test_fifo_ordering.py`; `tests/unit/test_queue_waiting_time.py`; `G1`.
- **Ordered operations:**
  1. Admission does not start computation.
  2. active task explicit/non-preemptive.
  3. waiting FIFO excludes active.
  4. expired waiting removed before service.
  5. late active result handled by contract.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_private_queue_lifecycle.py tests/unit/test_fifo_ordering.py tests/unit/test_queue_waiting_time.py -q
```
- **Acceptance:**
  - start timestamp only on first service.
  - active never reordered.
  - inclusive completion exact.
  - waiting task gets no cycles.
- **Stop/rollback:** ERT ordering forbidden in HOODIE queues.

### BASE-008 — Implement one outbound FIFO/transmitter per source

- **Dependencies:** BASE-006.
- **Required reads:** `src/environment/offloading_queue.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/link_rate_config.py`.
- **Allowed writes:** `src/environment/offloading_queue.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/link_rate_config.py`; `tests/unit/test_single_source_transmitter.py`; `tests/integration/test_outbound_fifo.py`; `G1`.
- **Ordered operations:**
  1. One physical transmitter per source.
  2. destination is metadata not resource identity.
  3. non-preemptive active transmission.
  4. FIFO waiting.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_single_source_transmitter.py tests/integration/test_outbound_fifo.py -q
```
- **Acceptance:**
  - different-destination tasks from one source never overlap.
  - different sources may transmit concurrently.
  - start only when source transmitter idle.
- **Stop/rollback:** Do not key a physical transmitter by (source,destination).

### BASE-009 — Preserve one selected destination through transmission

- **Dependencies:** BASE-008.
- **Required reads:** `src/environment/task.py`; `src/environment/environment.py`; `src/environment/gym_adapter.py`; `src/environment/evaluation_gym_adapter.py`.
- **Allowed writes:** `src/environment/task.py`; `src/environment/environment.py`; `src/environment/gym_adapter.py`; `src/environment/evaluation_gym_adapter.py`; `tests/unit/test_destination_retention.py`; `G1`.
- **Ordered operations:**
  1. Store destination at arrival decision.
  2. preserve through outbound queue/completion/admission.
  3. reject second route choice.
  4. log action/destination lineage.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_destination_retention.py -q
```
- **Acceptance:**
  - destination immutable.
  - exact selected queue reached.
  - lineage survives serialization.
- **Stop/rollback:** Do not infer destination later from topology.

### BASE-010 — Enforce next-boundary destination admission

- **Dependencies:** BASE-009.
- **Required reads:** `src/environment/slot_engine.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/public_queue.py`; BASE-006 vectors.
- **Allowed writes:** `src/environment/slot_engine.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/public_queue.py`; `tests/unit/test_next_boundary_admission.py`; `tests/integration/test_transmission_timeline.py`; `G1`.
- **Ordered operations:**
  1. Transmission finishing in slot t creates staged event.
  2. admit at boundary t+1.
  3. no destination service in t.
  4. cover one/multi-slot transmission.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_next_boundary_admission.py tests/integration/test_transmission_timeline.py -q
```
- **Acceptance:**
  - timestamps exact.
  - no same-slot destination processing.
  - one terminal transmission event.
  - no lost staged event.
- **Stop/rollback:** Do not hide off-by-one errors in metadata.

### BASE-011 — Implement source-indexed destination FIFO queues

- **Dependencies:** BASE-006.
- **Required reads:** `src/environment/public_queue.py`; `src/environment/gym_adapter.py`; `src/environment/evaluation_gym_adapter.py`.
- **Allowed writes:** `src/environment/public_queue.py`; `src/environment/gym_adapter.py`; `src/environment/evaluation_gym_adapter.py`; `tests/unit/test_source_indexed_public_queues.py`; `G1`.
- **Ordered operations:**
  1. Key by destination and source.
  2. FIFO inside source queue.
  3. active head explicit.
  4. single location per task.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_source_indexed_public_queues.py -q
```
- **Acceptance:**
  - edge destination has N-1 external source queues.
  - cloud has N.
  - queues do not merge.
  - FIFO deterministic.
- **Stop/rollback:** Source-side ERT may not reorder destination queues.

### BASE-012 — Implement equal public-CPU sharing

- **Dependencies:** BASE-011.
- **Required reads:** `src/environment/execution_helper.py`; `src/environment/runtime_model.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/public_queue.py`.
- **Allowed writes:** `src/environment/execution_helper.py`; `src/environment/runtime_model.py`; `src/environment/evaluation_gym_adapter.py`; `src/environment/public_queue.py`; `tests/unit/test_public_cpu_sharing.py`; `tests/integration/test_destination_capacity_sharing.py`; `G1`.
- **Ordered operations:**
  1. Identify active source queues.
  2. split cycles equally.
  3. update remaining cycles.
  4. deterministic simultaneous completions.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_public_cpu_sharing.py tests/integration/test_destination_capacity_sharing.py -q
```
- **Acceptance:**
  - k active queues each get capacity/k.
  - total allocation bounded.
  - empty queue gets none.
  - completion order deterministic.
- **Stop/rollback:** Do not approximate sharing with sequential full-capacity service.

### BASE-013 — Implement exact HOODIE action semantics

- **Dependencies:** BASE-005, BASE-007, BASE-010, BASE-012.
- **Required reads:** HOODIE registry; `src/policies/action_masking.py`; `src/policies/policy_interface.py`; `src/environment/gym_adapter.py`; topology.
- **Allowed writes:** `src/policies/action_masking.py`; `src/policies/policy_interface.py`; `src/environment/gym_adapter.py`; `src/agents/hoodie_action_space.py`; `tests/unit/test_hoodie_action_space.py`; `G1`.
- **Ordered operations:**
  1. Encode local, each connected horizontal destination and cloud.
  2. physical mask only.
  3. stable indexing.
  4. no ECHO deadline mask/fallback.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_hoodie_action_space.py -q
```
- **Acceptance:**
  - each connected destination separately selectable.
  - self/disconnected illegal.
  - stable IDs.
  - no first-neighbor collapse.
- **Stop/rollback:** No ECHO imports.

### BASE-014 — Implement exact HOODIE state/history

- **Dependencies:** BASE-013.
- **Required reads:** HOODIE registry; `src/agents/paper_state_builder.py`; `src/agents/history_builder.py`; `src/environment/gym_adapter.py`.
- **Allowed writes:** `src/agents/paper_state_builder.py`; `src/agents/history_builder.py`; `src/environment/gym_adapter.py`; `configs/authoritative/hoodie_state_schema.json`; `tests/unit/test_hoodie_state_contract.py`; `tests/unit/test_paper_state_builder.py`; `tests/unit/test_paper_state_vector_real.py`; `G1`.
- **Ordered operations:**
  1. Encode paper task/queue/public-load features and W=10 history.
  2. fixed order/dimension.
  3. exclude ECHO features.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_hoodie_state_contract.py tests/unit/test_paper_state_builder.py tests/unit/test_paper_state_vector_real.py -q
```
- **Acceptance:**
  - shape/order exact.
  - no-arrival handling documented.
  - snapshot-only values.
  - normalization paper-supported or classified.
- **Stop/rollback:** Placeholder forecasts must be removed by BASE-015.

### BASE-015 — Implement real HOODIE LSTM forecast

- **Dependencies:** BASE-014.
- **Required reads:** `src/agents/lstm_dueling_dqn.py`; `src/agents/hoodie_model.py`; `src/agents/neural_net_hoodie_model.py`; state schema; HOODIE paper.
- **Allowed writes:** `src/agents/lstm_dueling_dqn.py`; `src/agents/hoodie_model.py`; `src/agents/neural_net_hoodie_model.py`; `src/agents/hoodie_load_forecaster.py`; `tests/unit/test_hoodie_load_forecaster.py`; `tests/agents/test_lstm_dueling_dqn.py`; `G1`.
- **Ordered operations:**
  1. Implement W=10 ordered history, model, loss, optimizer, deterministic init and checkpoint.
  2. connect real forecast.
  3. exclude held-out data.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_hoodie_load_forecaster.py tests/agents/test_lstm_dueling_dqn.py -q
```
- **Acceptance:**
  - forecast changes with history.
  - finite loss/gradients.
  - checkpoint round-trip.
  - no hard-coded zeros.
  - no test leakage.
- **Stop/rollback:** Unresolved paper detail => stop; do not borrow ECHO behavior.

### BASE-016 — Implement one independent HOODIE learner per EA

- **Dependencies:** BASE-015.
- **Required reads:** `src/agents/hoodie_agent.py`; replay/target/model files; `src/training/training_loop.py`.
- **Allowed writes:** `src/agents/hoodie_agent.py`; `src/agents/hoodie_agent_manager.py`; `src/agents/replay_buffer.py`; `src/agents/target_network.py`; `src/training/training_loop.py`; `tests/unit/test_per_ea_hoodie_learners.py`; `G1`.
- **Ordered operations:**
  1. Instantiate N independent HOODIE agents with private replay/online/target/optimizer/epsilon/checkpoint.
  2. route each source event only to its agent.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_per_ea_hoodie_learners.py -q
```
- **Acceptance:**
  - EA n mutation does not affect m.
  - exactly N states/checkpoints.
  - deterministic per-EA seeds.
- **Stop/rollback:** One shared HOODIE policy object is not acceptable.

### BASE-017 — Implement original HOODIE reward/replay timing

- **Dependencies:** BASE-016.
- **Required reads:** HOODIE registry; `src/environment/reward_timing.py`; `src/training/delayed_reward_training.py`; `src/training/training_loop.py`; `src/agents/replay_buffer.py`.
- **Allowed writes:** `src/environment/reward_timing.py`; `src/training/delayed_reward_training.py`; `src/training/training_loop.py`; `src/agents/replay_buffer.py`; `tests/unit/test_hoodie_reward_replay_timing.py`; `G1`.
- **Ordered operations:**
  1. Reproduce paper reward sign/delivery/next-state/terminal behavior and ordinary discount.
  2. remove ECHO interval/risk/fallback/gamma^Delta from base.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_hoodie_reward_replay_timing.py -q
```
- **Acceptance:**
  - hand trace exact.
  - one replay resolution.
  - correct EA ownership.
  - terminal flush complete.
  - no ECHO-only field required.
- **Stop/rollback:** Unresolved Bellman timing stops task.

### BASE-018 — Implement paper-correct HOODIE Dueling Double-DQN

- **Dependencies:** BASE-017.
- **Required reads:** `src/agents/double_dqn.py`; `src/agents/target_network.py`; `src/agents/hoodie_model.py`; `src/agents/neural_net_hoodie_model.py`; `src/agents/torchrl_hoodie_learner.py`; canonical learning config.
- **Allowed writes:** `src/agents/double_dqn.py`; `src/agents/target_network.py`; `src/agents/hoodie_model.py`; `src/agents/neural_net_hoodie_model.py`; `src/agents/torchrl_hoodie_learner.py`; `tests/unit/test_hoodie_double_dqn_contract.py`; `G1`.
- **Ordered operations:**
  1. Implement online/target networks, dueling aggregation, Double-DQN, epsilon, target copy, optimizer and ordinary discount.
  2. remove heuristic authoritative path.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_hoodie_double_dqn_contract.py tests/unit/test_agent_components.py -q
```
- **Acceptance:**
  - online chooses/target evaluates.
  - target no gradient.
  - schedule exact.
  - loss decreases on deterministic batch.
  - checkpoint round-trip.
- **Stop/rollback:** Stubs/heuristics cannot be called paper learner.

### BASE-019 — Validate RO/FLC/VO/HO/BCO/MLEO isolation

- **Dependencies:** BASE-018.
- **Required reads:** `src/policies/ro.py`; `src/policies/flc.py`; `src/policies/vo.py`; `src/policies/ho.py`; `src/policies/bco.py`; `src/policies/mleo.py`; `src/evaluation/policy_registry.py`; shared simulator.
- **Allowed writes:** `src/policies/ro.py`; `src/policies/flc.py`; `src/policies/vo.py`; `src/policies/ho.py`; `src/policies/bco.py`; `src/policies/mleo.py`; `src/evaluation/policy_registry.py`; `tests/integration/test_baseline_method_isolation.py`; `docs/contracts/baseline_definitions.md`; `G1`.
- **Ordered operations:**
  1. Define information/action/tie/fallback per baseline.
  2. replace HOODIE alias-to-ADAPTIVE with real adapter.
  3. no heuristic training or ECHO imports.
- **Exact command:**
```bash
python3 -m pytest tests/integration/test_baseline_method_isolation.py -q
```
- **Acceptance:**
  - FLC local.
  - VO cloud.
  - HO horizontal/documented physical fallback.
  - RO physical only.
  - BCO deterministic.
  - MLEO own latency.
  - same traces/accounting.
- **Stop/rollback:** Any ECHO import fails task.

### BASE-020 — Run complete deterministic base invariant suite

- **Dependencies:** BASE-019.
- **Required reads:** all Phase-1 code/tests; BASE-006 fixtures.
- **Allowed writes:** `tests/integration/test_base_physical_invariants.py`; `tests/integration/test_base_differential_trace.py`; `artifacts/validation/base/summary.json`; `artifacts/validation/base/test_output.txt`; `G1`.
- **Ordered operations:**
  1. Add local/horizontal/cloud hand traces, simultaneous arrivals, expiration, late active, drain, accounting, single-location, trace identity, method isolation.
  2. Run full Phase-1 suite.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_hoodie_table4_config.py tests/unit/test_hoodie_topology_authority.py tests/unit/test_trace_protocol_paper_semantics.py tests/unit/test_trace_immutability.py tests/unit/test_hoodie_slot_contract_vectors.py tests/unit/test_hoodie_slot_engine.py tests/unit/test_private_queue_lifecycle.py tests/unit/test_single_source_transmitter.py tests/unit/test_destination_retention.py tests/unit/test_next_boundary_admission.py tests/unit/test_source_indexed_public_queues.py tests/unit/test_public_cpu_sharing.py tests/unit/test_hoodie_action_space.py tests/unit/test_hoodie_state_contract.py tests/unit/test_hoodie_load_forecaster.py tests/unit/test_per_ea_hoodie_learners.py tests/unit/test_hoodie_reward_replay_timing.py tests/unit/test_hoodie_double_dqn_contract.py tests/integration/test_baseline_method_isolation.py tests/integration/test_base_physical_invariants.py tests/integration/test_base_differential_trace.py -q
```
- **Acceptance:**
  - all tests pass.
  - generated=completed+dropped.
  - one outcome/task.
  - no invalid action.
  - no NaN/Inf.
  - zero ECHO imports in neutral kernel.
- **Stop/rollback:** Failures reopen owning task; no runtime patches here.

### BASE-021 — Run bounded HOODIE runtime/learner smoke

- **Dependencies:** BASE-020.
- **Required reads:** Phase-1 code; smoke conventions.
- **Allowed writes:** `configs/experiments/hoodie_smoke.yaml`; `scripts/smoke/run_hoodie_smoke.py`; `tests/integration/test_hoodie_smoke_runner.py`; `artifacts/smoke/hoodie_v4/run_manifest.json`; `artifacts/smoke/hoodie_v4/task_log.jsonl`; `artifacts/smoke/hoodie_v4/episode_metrics.csv`; `artifacts/smoke/hoodie_v4/checkpoint.pt`; `G1`.
- **Ordered operations:**
  1. Run fixed seed/bounded episodes.
  2. exercise routes.
  3. real updates.
  4. save/load checkpoint.
  5. retain raw logs.
- **Exact command:**
```bash
python3 -m pytest tests/integration/test_hoodie_smoke_runner.py -q && python3 scripts/smoke/run_hoodie_smoke.py --config configs/experiments/hoodie_smoke.yaml --output artifacts/smoke/hoodie_v4
```
- **Acceptance:**
  - finite loss/Q/reward.
  - replay grows.
  - target copies.
  - reload reproduces inference.
  - accounting exact.
  - smoke labels present.
- **Stop/rollback:** Do not tune hyperparameters from smoke.

### BASE-022 — Reproduce HOODIE experiment organization and trends

- **Dependencies:** BASE-021.
- **Required reads:** HOODIE paper figure/table registry; candidate base; smoke evidence.
- **Allowed writes:** `configs/experiments/hoodie_reproduction.yaml`; `scripts/reproduction/run_hoodie_reproduction.py`; `artifacts/reproduction/hoodie/run_manifest.json`; `artifacts/reproduction/hoodie/raw_metrics.csv`; `docs/reports/hoodie_reproduction_evidence.md`; `G1`.
- **Ordered operations:**
  1. Run real simulation matching paper organization.
  2. preserve outputs/config/seeds.
  3. compare trends not pixels.
- **Exact command:**
```bash
python3 scripts/reproduction/run_hoodie_reproduction.py --config configs/experiments/hoodie_reproduction.yaml --output artifacts/reproduction/hoodie
```
- **Acceptance:**
  - every trend has raw lineage.
  - deviations documented.
  - no hard-coded paper values.
  - paired inputs.
- **Stop/rollback:** Failed trend blocks freeze.

### FREEZE-001 — Freeze validated neutral simulator and HOODIE baseline

- **Dependencies:** BASE-022.
- **Required reads:** all Phase-1 evidence; reproduction report; tested commit.
- **Allowed writes:** `scripts/release/freeze_hoodie_baseline.py`; `artifacts/releases/hoodie_base_v1/manifest.json`; `artifacts/releases/hoodie_base_v1/SHA256SUMS`; `docs/contracts/hoodie_base_freeze.md`; `G1`.
- **Ordered operations:**
  1. Record commit/config/topology/trace schemas/tests/checkpoints/interfaces/forbidden ECHO imports/limitations.
  2. hash every frozen file.
- **Exact command:**
```bash
python3 scripts/release/freeze_hoodie_baseline.py --manifest artifacts/releases/hoodie_base_v1/manifest.json --checksums artifacts/releases/hoodie_base_v1/SHA256SUMS
```
- **Acceptance:**
  - hashes verify.
  - full suite passes.
  - no unresolved S0/S1.
  - neutral interfaces versioned.
- **Stop/rollback:** Any later frozen-file change invalidates freeze and reopens owner.

### ECHO-001 — Attach ECHO adapter to frozen neutral hooks

- **Dependencies:** FREEZE-001, SRC-001.
- **Required reads:** frozen base contract; `src/environment/method_hooks.py`; current src/echo_*; policy/training paths.
- **Allowed writes:** `src/echo_adapter.py`; `src/evaluation/policy_registry.py`; `tests/integration/test_echo_method_isolation.py`; `docs/contracts/echo_isolation_matrix.md`; `G1`.
- **Ordered operations:**
  1. Implement ECHO adapter only through frozen hooks.
  2. do not edit frozen files.
  3. register explicit ECHO selection.
  4. prove HOODIE regression unchanged.
- **Exact command:**
```bash
python3 -m pytest tests/integration/test_echo_method_isolation.py tests/integration/test_base_physical_invariants.py -q
```
- **Acceptance:**
  - no frozen file changed.
  - HOODIE bytes/results unchanged.
  - ECHO selectable explicitly.
  - shared kernel imports no ECHO modules.
- **Stop/rollback:** Any required frozen-file change reopens base task and freeze.

### ECHO-002 — Implement Equations (1)–(8) lifecycle and dispatch

- **Dependencies:** ECHO-001.
- **Required reads:** source snapshot/audit; `src/echo_types.py`; `src/echo_ert.py`; `src/environment/task.py`; ECHO adapter.
- **Allowed writes:** `src/echo_types.py`; `src/echo_ert.py`; `src/environment/task.py`; `src/echo_adapter.py`; `tests/unit/test_echo_equations_01_08.py`; `G1`.
- **Ordered operations:**
  1. Encode task variables/deadline/route set/direct dispatch/stored destination/lifecycle/inclusive slots.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_echo_equations_01_08.py -q
```
- **Acceptance:**
  - equation examples exact.
  - no second action.
  - deadline off-by-one exact.
  - one terminal resolution.
- **Stop/rollback:** No queue estimator or learner changes.

### ECHO-003 — Implement Equations (9)–(11) local estimate

- **Dependencies:** ECHO-002.
- **Required reads:** live equations; `src/echo_ert.py`; private queue/active state.
- **Allowed writes:** `src/echo_ert.py`; `tests/unit/test_echo_local_estimate.py`; `G1`.
- **Ordered operations:**
  1. Compute service slots/residual/predecessors/inclusive completion/ERT/lateness.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_echo_local_estimate.py -q
```
- **Acceptance:**
  - empty/active/multi-predecessor hand calculations exact.
  - units consistent.
  - no truncation.
- **Stop/rollback:** Do not reorder queues.

### ECHO-004 — Implement Equations (12)–(16) outbound estimate

- **Dependencies:** ECHO-003.
- **Required reads:** live equations; `src/echo_ert.py`; link rates; outbound state; boundary contract.
- **Allowed writes:** `src/echo_ert.py`; `tests/unit/test_echo_outbound_estimate.py`; `G1`.
- **Ordered operations:**
  1. Compute residual/predecessor transmission, rates, inclusive slots, +1 destination admission, completion/ERT/lateness.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_echo_outbound_estimate.py -q
```
- **Acceptance:**
  - horizontal/cloud hand examples exact.
  - +1 counted once.
  - destination stage not omitted.
- **Stop/rollback:** Destination workload belongs to ECHO-005.

### ECHO-005 — Implement Equations (17)–(25) destination model

- **Dependencies:** ECHO-004.
- **Required reads:** live equations; public queues; runtime capacity; status interface.
- **Allowed writes:** `src/echo_destination_model.py`; `src/echo_ert.py`; `tests/unit/test_echo_destination_model.py`; `G1`.
- **Ordered operations:**
  1. Remaining workload in cycles.
  2. active queue count/hypothetical admission/effective capacity/wait/service/completion.
  3. fresh-or-estimated input interface.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_echo_destination_model.py -q
```
- **Acceptance:**
  - cycle units exact.
  - active-count adjustment exact.
  - zero/one/many queues.
  - no future information.
- **Stop/rollback:** Do not reorder destination FIFO.

### ECHO-006 — Implement Equations (26)–(28) history and LSTM inputs

- **Dependencies:** ECHO-005.
- **Required reads:** live equations; `src/environment/runtime_model.py`; current load/history code.
- **Allowed writes:** `src/echo_load_forecast.py`; `src/echo_status.py`; `tests/unit/test_echo_load_history.py`; `G1`.
- **Ordered operations:**
  1. Fixed ordered history.
  2. freshness timestamp/status.
  3. stale/missing flag.
  4. training target record.
  5. bootstrap behavior.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_echo_load_history.py -q
```
- **Acceptance:**
  - history order exact.
  - fresh preferred.
  - stale/missing explicit.
  - no evaluation IDs in training store.
- **Stop/rollback:** Neural fitting belongs to ECHO-016.

### ECHO-007 — Implement Equation (29) local queue ERT ordering

- **Dependencies:** ECHO-006.
- **Required reads:** live equation/ties; `src/echo_queue_ordering.py`; private queue.
- **Allowed writes:** `src/echo_queue_ordering.py`; `tests/unit/test_echo_local_queue_ordering.py`; `G1`.
- **Ordered operations:**
  1. Freeze active head.
  2. construct position-by-position.
  3. smallest nonnegative else minimum lateness.
  4. FIFO/stable ID tie.
  5. count evaluations.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_echo_local_queue_ordering.py -q
```
- **Acceptance:**
  - hand order exact.
  - all-late fallback exact.
  - active untouched.
  - q(q+1)/2 evaluations.
- **Stop/rollback:** HOODIE FIFO unchanged.

### ECHO-008 — Implement Equation (30) outbound ERT ordering

- **Dependencies:** ECHO-007.
- **Required reads:** live equation; `src/echo_queue_ordering.py`; offloading queue; destination model.
- **Allowed writes:** `src/echo_queue_ordering.py`; `tests/unit/test_echo_outbound_queue_ordering.py`; `G1`.
- **Ordered operations:**
  1. Freeze active transmission.
  2. include cumulative transmission and destination estimate.
  3. same feasible/lateness/tie rules.
  4. preserve destination.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_echo_outbound_queue_ordering.py -q
```
- **Acceptance:**
  - mixed-destination/all-late hand cases exact.
  - one transmitter/source.
  - O(q²) count.
- **Stop/rollback:** No per-destination physical transmitter.

### ECHO-009 — Implement size-specific N+2 canonical action space

- **Dependencies:** ECHO-008.
- **Required reads:** revision-273 source section; `src/echo_action_space.py`; `src/echo_types.py`; topology.
- **Allowed writes:** `src/echo_action_space.py`; `src/echo_types.py`; `tests/unit/test_echo_canonical_action_space.py`; `G1`.
- **Ordered operations:**
  1. For each N build local + N horizontal positions + cloud.
  2. retain source/disconnected positions but mask them.
  3. no padding to 30 for smaller N.
  4. stable mapping within N.
  5. separate checkpoint per N.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_echo_canonical_action_space.py -q
```
- **Acceptance:**
  - dimensions 12/17/22/27/32 for N=10/15/20/25/30.
  - source/disconnected masked.
  - cloud final.
  - mapping deterministic.
  - existing fixed-32 code superseded where N<30.
- **Stop/rollback:** Do not claim zero-shot transfer across N.

### ECHO-010 — Implement Equations (42)–(46) mask and fallback

- **Dependencies:** ECHO-009.
- **Required reads:** live equations; candidate estimates; N+2 action space.
- **Allowed writes:** `src/echo_action_mask.py`; `src/echo_action_space.py`; `tests/unit/test_echo_deadline_mask.py`; `G1`.
- **Ordered operations:**
  1. Intersect physical candidates with ERT>=0.
  2. empty set => singleton minimum-lateness with tie.
  3. same mask exploration/exploitation/target.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_echo_deadline_mask.py -q
```
- **Acceptance:**
  - feasible set exact.
  - fallback exact.
  - never all-zero on arrival.
  - same mask hash in all selection paths.
- **Stop/rollback:** No leak to HOODIE/baselines.

### ECHO-011 — Implement Equations (47)–(50) pending records and schema-compliant decision logs

- **Dependencies:** ECHO-010, EVAL-001.
- **Required reads:** live equations; EVAL-001 schemas; task lifecycle; action/mask/estimate types.
- **Allowed writes:** `src/echo_pending.py`; `src/echo_types.py`; `src/echo_adapter.py`; `tests/unit/test_echo_pending_records.py`; `G1`.
- **Ordered operations:**
  1. Store source/state/action/mask/candidate estimates/risk/decision slot/deadline/destination.
  2. emit decision log matching frozen schema.
  3. one record/task.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_echo_pending_records.py -q
```
- **Acceptance:**
  - all fields immutable.
  - one record/task.
  - decision-time values not recomputed at resolution.
  - schema valid.
- **Stop/rollback:** Schema change requires reopening EVAL-001.

### ECHO-012 — Implement Equations (51)–(54) size-specific normalized state

- **Dependencies:** ECHO-011.
- **Required reads:** live equations and revision-273 scalability paragraph; EVAL-001 schemas; state/history/status modules.
- **Allowed writes:** `src/echo_state.py`; `src/echo_types.py`; `tests/unit/test_echo_state_contract.py`; `G1`.
- **Ordered operations:**
  1. Build task/queue/workload/residual/load/LSTM/min-ERT/candidate-ERT/mask.
  2. destination blocks and candidate vector scale with N.
  3. fixed order within N.
  4. no-arrival zeros only for task/candidate/mask.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_echo_state_contract.py -q
```
- **Acceptance:**
  - schema/order exact per N.
  - N-specific dimensions tested for 10/15/20/25/30.
  - no 30-node padding for smaller N.
  - bounded normalization.
  - no-arrival semantics exact.
- **Stop/rollback:** Do not reuse one checkpoint across different N.

### ECHO-013 — Implement Equations (55)–(58) task reward

- **Dependencies:** ECHO-012.
- **Required reads:** live reward equations; pending/outcome events.
- **Allowed writes:** `src/echo_reward.py`; `src/echo_types.py`; `tests/unit/test_echo_reward.py`; `G1`.
- **Ordered operations:**
  1. Compute inclusive system duration, decision risk indicator, realized failure indicator and reward.
  2. emit resolution log schema.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_echo_reward.py -q
```
- **Acceptance:**
  - hand rewards exact.
  - risk/drop distinct.
  - one reward/task.
  - late active and waiting expiry exact.
- **Stop/rollback:** Do not finalize replay here.

### ECHO-014 — Implement Equations (59)–(60) event intervals

- **Dependencies:** ECHO-013.
- **Required reads:** live interval equations; `src/training/event_smdp.py`; pending/reward events.
- **Allowed writes:** `src/training/event_smdp.py`; `tests/unit/test_event_smdp_interval_contract.py`; `G1`.
- **Ordered operations:**
  1. One open interval per source EA.
  2. discount rewards within interval.
  3. close at next actual decision of same EA or T+1.
  4. one non-overlapping transition.
  5. preserve Delta.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_event_smdp_interval_contract.py -q
```
- **Acceptance:**
  - multiple rewards aggregate.
  - other-EA decision does not close.
  - no overlapping task transitions.
  - terminal exact.
  - boundary-before-decision ownership.
- **Stop/rollback:** Existing tests are insufficient without boundary ownership.

### ECHO-015 — Implement Equations (61)–(67) masked DDQL with within-run parameter sharing

- **Dependencies:** ECHO-014.
- **Required reads:** live equations and revision-273 parameter-sharing paragraph; replay/DQN/state/action/mask/interval modules.
- **Allowed writes:** `src/agents/echo_model.py`; `src/agents/echo_agent.py`; `src/agents/echo_parameter_server.py`; `src/agents/replay_buffer.py`; `src/agents/double_dqn.py`; `src/agents/target_network.py`; `tests/unit/test_echo_masked_ddql.py`; `tests/unit/test_echo_parameter_sharing.py`; `G1`.
- **Ordered operations:**
  1. Dueling N+2 outputs for current N.
  2. masked online argmax/target evaluation/gamma^Delta/terminal/optimizer/target copy.
  3. share Q/LSTM parameters among EAs inside one run.
  4. retain source-specific interval accumulators and provenance.
  5. separate checkpoint per N.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_echo_masked_ddql.py tests/unit/test_echo_parameter_sharing.py -q
```
- **Acceptance:**
  - hand target exact.
  - masked action never selected.
  - target no gradient.
  - finite update.
  - all EAs reference shared parameters within run.
  - source-specific interval ownership preserved.
  - checkpoint incompatible across N.
- **Stop/rollback:** Do not create independent ECHO network parameters per EA unless source lock changes.

### ECHO-016 — Implement fresh/stale status and supervised LSTM training

- **Dependencies:** ECHO-015.
- **Required reads:** live LSTM section; `src/echo_load_forecast.py`; `src/echo_status.py`; state/model/training config.
- **Allowed writes:** `src/echo_load_forecast.py`; `src/echo_status.py`; `src/agents/echo_load_lstm.py`; `tests/unit/test_echo_load_lstm.py`; `G1`.
- **Ordered operations:**
  1. Separate forecasting loss/optimizer.
  2. training-only histories.
  3. fresh override.
  4. stale/missing prediction.
  5. shared parameters within run.
  6. deterministic checkpoint.
  7. held-out guard.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_echo_load_lstm.py -q
```
- **Acceptance:**
  - fresh ignores prediction.
  - stale/missing uses it.
  - finite loss/gradients.
  - no held-out IDs.
  - checkpoint reproducible.
  - shared-within-run behavior verified.
- **Stop/rollback:** Do not hide forecast loss inside Q loss.

### ECHO-017 — Implement isolated ECHO-NoLSTM

- **Dependencies:** ECHO-016.
- **Required reads:** live ablation definition; ECHO adapter/status/state/model.
- **Allowed writes:** `src/policies/echo_no_lstm.py`; `src/evaluation/policy_registry.py`; `tests/integration/test_echo_no_lstm_isolation.py`; `G1`.
- **Ordered operations:**
  1. Identical to ECHO except approved load estimate replacement.
  2. same kernel/state ordering/action/mask/reward/learner/budget.
- **Exact command:**
```bash
python3 -m pytest tests/integration/test_echo_no_lstm_isolation.py -q
```
- **Acceptance:**
  - differential trace shows only load-estimation-dependent fields/actions differ.
  - no hidden budget/parameter difference.
- **Stop/rollback:** Not a generic heuristic baseline.

### ECHO-018 — Implement exact Algorithm 1 and 2 chronology

- **Dependencies:** ECHO-017.
- **Required reads:** source-locked 23/12-line algorithms; `src/echo_adapter.py`; `src/training/training_loop.py`; interval logic; neutral hooks.
- **Allowed writes:** `src/echo_adapter.py`; `src/training/training_loop.py`; `tests/integration/test_echo_algorithm_order.py`; `tests/integration/test_echo_boundary_reward_ownership.py`; `G1`.
- **Ordered operations:**
  1. Apply boundary resolutions before new decision closure.
  2. then decisions/scheduling/service/history/learning.
  3. terminal T+1.
  4. inference same physical order without learning/highest masked Q.
- **Exact command:**
```bash
python3 -m pytest tests/integration/test_echo_algorithm_order.py tests/integration/test_echo_boundary_reward_ownership.py -q
```
- **Acceptance:**
  - event trace matches all algorithm lines.
  - reward belongs old interval.
  - no double service.
  - training/inference physical order identical.
- **Stop/rollback:** Formula defects reopen owning ECHO task.

### ECHO-019 — Run deterministic ECHO unit and smoke suite

- **Dependencies:** ECHO-018.
- **Required reads:** all Phase-2 tests; source lock; frozen base.
- **Allowed writes:** `tests/integration/test_echo_hand_trace.py`; `configs/experiments/echo_smoke.yaml`; `scripts/smoke/run_echo_smoke.py`; `artifacts/smoke/echo_v4/run_manifest.json`; `artifacts/smoke/echo_v4/task_log.jsonl`; `artifacts/smoke/echo_v4/decision_log.jsonl`; `artifacts/smoke/echo_v4/episode_metrics.csv`; `artifacts/smoke/echo_v4/checkpoint.pt`; `G1`.
- **Ordered operations:**
  1. Run 2-EA+cloud hand trace and short learning smoke.
  2. cover all routes/contention/masks/ERT/expiry/late active.
  3. checkpoint reload.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_echo_equations_01_08.py tests/unit/test_echo_local_estimate.py tests/unit/test_echo_outbound_estimate.py tests/unit/test_echo_destination_model.py tests/unit/test_echo_load_history.py tests/unit/test_echo_local_queue_ordering.py tests/unit/test_echo_outbound_queue_ordering.py tests/unit/test_echo_canonical_action_space.py tests/unit/test_echo_deadline_mask.py tests/unit/test_echo_pending_records.py tests/unit/test_echo_state_contract.py tests/unit/test_echo_reward.py tests/unit/test_event_smdp_interval_contract.py tests/unit/test_echo_masked_ddql.py tests/unit/test_echo_parameter_sharing.py tests/unit/test_echo_load_lstm.py tests/integration/test_echo_no_lstm_isolation.py tests/integration/test_echo_algorithm_order.py tests/integration/test_echo_boundary_reward_ownership.py tests/integration/test_echo_hand_trace.py -q && python3 scripts/smoke/run_echo_smoke.py --config configs/experiments/echo_smoke.yaml --output artifacts/smoke/echo_v4
```
- **Acceptance:**
  - all tests pass.
  - manual trace exact.
  - finite metrics.
  - all routes.
  - no masked action.
  - accounting exact.
  - reload deterministic.
- **Stop/rollback:** Failures reopen owner; no runtime patches here.

### ECHO-020 — Produce equation coverage and paired pilot gate

- **Dependencies:** ECHO-019.
- **Required reads:** source audit; all Phase-2 evidence; frozen base; smokes; EVAL-001 schemas.
- **Allowed writes:** `scripts/audit/build_echo_coverage.py`; `artifacts/audits/echo_equation_coverage.md`; `artifacts/audits/echo_equation_coverage.json`; `configs/experiments/echo_pilot.yaml`; `scripts/pilot/run_echo_pilot.py`; `artifacts/pilot/echo_v4/run_manifest.json`; `artifacts/pilot/echo_v4/task_log.jsonl`; `artifacts/pilot/echo_v4/decision_log.jsonl`; `artifacts/pilot/echo_v4/episode_metrics.csv`; `G1`.
- **Ordered operations:**
  1. Map each equation/algorithm line to symbol/test/evidence.
  2. run paired ECHO/HOODIE/NoLSTM pilot.
  3. check route/mask/reward/replay/accounting/stability and N-specific architecture.
- **Exact command:**
```bash
python3 scripts/audit/build_echo_coverage.py --source-audit artifacts/audits/echo_live_revision_audit.md --output artifacts/audits/echo_equation_coverage.json && python3 scripts/pilot/run_echo_pilot.py --config configs/experiments/echo_pilot.yaml --output artifacts/pilot/echo_v4
```
- **Acceptance:**
  - 69/69 code+test coverage.
  - no unresolved S0/S1.
  - paired hashes equal.
  - finite pilot.
  - no superiority claim.
- **Stop/rollback:** Any uncovered row blocks evaluation.

### EVAL-001 — Freeze logging, evaluation, and 15-panel schemas before ECHO logging

- **Dependencies:** SRC-001, BASE-004.
- **Required reads:** `research/ECHO_evaluation_spec.md`; source lock; immutable trace schema.
- **Allowed writes:** `experiments/manifest.yaml`; `experiments/figure_manifest.yaml`; `experiments/schemas/run_manifest.schema.json`; `experiments/schemas/task_log.schema.json`; `experiments/schemas/decision_log.schema.json`; `experiments/schemas/resolution_event.schema.json`; `experiments/schemas/checkpoint_manifest.schema.json`; `experiments/schemas/episode_metrics.schema.json`; `experiments/schemas/seed_metrics.schema.json`; `experiments/schemas/panel_values.schema.json`; `experiments/schemas/artifact_manifest.schema.json`; `src/evaluation/config.py`; `tests/unit/test_evaluation_manifests.py`; `G1`.
- **Ordered operations:**
  1. Encode all 15 panels, methods, N-specific checkpoints, exact fields for action/ERT/mask/pending/reward/Delta, seeds, held-out protocol, metrics/CI/paths.
  2. protect held-out data.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_evaluation_manifests.py -q
```
- **Acceptance:**
  - 15 unique panels.
  - no placeholders.
  - Figure 6 timeout 2s.
  - Figure 7 c/f swept.
  - Figure 8 exact.
  - schemas validate.
  - N+2 and checkpoint-per-N represented.
- **Stop/rollback:** Unresolved retraining/checkpoint rule blocks task.

### EVAL-002 — Generate immutable paired trace bank

- **Dependencies:** ECHO-020, EVAL-001.
- **Required reads:** immutable trace protocol; evaluation manifest.
- **Allowed writes:** `scripts/evaluation/build_trace_bank.py`; `tests/integration/test_trace_bank.py`; `artifacts/evaluation/trace_bank/index.json`; `G1`; `G4`.
- **Ordered operations:**
  1. Generate every seed/scenario once.
  2. canonical JSON and SHA.
  3. read-only consumption.
- **Exact command:**
```bash
python3 -m pytest tests/integration/test_trace_bank.py -q && python3 scripts/evaluation/build_trace_bank.py --manifest experiments/manifest.yaml --output artifacts/evaluation/trace_bank
```
- **Acceptance:**
  - expected count.
  - stable hashes.
  - all methods load same bytes.
  - arrival/drain valid.
- **Stop/rollback:** Never overwrite trace ID with different bytes.

### EVAL-003 — Freeze config, topology, and checkpoint lineage

- **Dependencies:** EVAL-002.
- **Required reads:** trace bank; frozen base; pilot checkpoints; manifests.
- **Allowed writes:** `scripts/evaluation/build_lineage_manifest.py`; `artifacts/evaluation/lineage/index.json`; `tests/unit/test_lineage_manifest.py`; `G1`.
- **Ordered operations:**
  1. Map every run to config/topology/trace/method/code/checkpoint/source/environment hashes.
  2. enforce checkpoint N compatibility and within-run sharing metadata.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_lineage_manifest.py -q && python3 scripts/evaluation/build_lineage_manifest.py --manifest experiments/manifest.yaml --output artifacts/evaluation/lineage
```
- **Acceptance:**
  - no missing hash.
  - unique resumable run IDs.
  - checkpoint method/N/scenario compatible.
- **Stop/rollback:** No mutable latest-checkpoint references.

### EVAL-004 — Validate all method adapters on common inputs

- **Dependencies:** EVAL-003.
- **Required reads:** policy registry; shared kernel; lineage; trace bank.
- **Allowed writes:** `tests/integration/test_all_method_common_inputs.py`; `artifacts/evaluation/adapter_validation/summary.json`; `G1`.
- **Ordered operations:**
  1. Run one deterministic trace for all methods.
  2. compare input hashes/accounting.
  3. prove method-specific behavior only.
- **Exact command:**
```bash
python3 -m pytest tests/integration/test_all_method_common_inputs.py -q
```
- **Acceptance:**
  - identical inputs.
  - no heuristic training.
  - no ECHO import in HOODIE/heuristics.
  - accounting exact.
- **Stop/rollback:** Runtime fix reopens owning task.

### EVAL-005 — Measure throughput and freeze shard budget

- **Dependencies:** EVAL-004.
- **Required reads:** validated adapters; manifest; available compute.
- **Allowed writes:** `scripts/evaluation/benchmark_throughput.py`; `artifacts/evaluation/compute_budget.json`; `artifacts/evaluation/compute_budget.md`; `experiments/shard_plan.yaml`; `G1`.
- **Ordered operations:**
  1. Benchmark representative jobs.
  2. estimate total resources.
  3. define shard/checkpoint/resume/rerun rules.
- **Exact command:**
```bash
python3 scripts/evaluation/benchmark_throughput.py --manifest experiments/manifest.yaml --output artifacts/evaluation/compute_budget.json --shards experiments/shard_plan.yaml
```
- **Acceptance:**
  - measured estimate.
  - full matrix feasible or explicitly blocked.
  - no full job launched.
- **Stop/rollback:** Infeasible budget requires approved matrix change.

### EVAL-006 — Run Figure-5 validation sweeps

- **Dependencies:** EVAL-005.
- **Required reads:** Figure-5 manifest; trace bank; shard plan.
- **Allowed writes:** `configs/experiments/figure5_sweep.yaml`; `scripts/evaluation/run_figure5_sweep.py`; `artifacts/evaluation/figure5/sweep_manifest.json`; `artifacts/evaluation/figure5/results.csv`; `G1`; `G5`.
- **Ordered operations:**
  1. Run LR and gamma points with validation-only selection.
  2. preserve seeds/logs/checkpoints.
  3. separate N checkpoints where applicable.
- **Exact command:**
```bash
python3 scripts/evaluation/run_figure5_sweep.py --config configs/experiments/figure5_sweep.yaml --output artifacts/evaluation/figure5
```
- **Acceptance:**
  - all points complete/resumable.
  - no held-out selection.
  - finite metrics.
- **Stop/rollback:** Do not select by final-test performance.

### EVAL-007 — Train equal-budget final method checkpoints

- **Dependencies:** EVAL-006.
- **Required reads:** selected hyperparameters; manifest; shard plan; trace bank.
- **Allowed writes:** `configs/experiments/final_training.yaml`; `scripts/evaluation/run_final_training.py`; `artifacts/checkpoints/final/index.json`; `G1`; `G5`.
- **Ordered operations:**
  1. Train ECHO/HOODIE/NoLSTM with equal budgets and separate seeds/N/scenarios.
  2. heuristics excluded.
  3. immutable completion markers.
- **Exact command:**
```bash
python3 scripts/evaluation/run_final_training.py --config configs/experiments/final_training.yaml --output artifacts/checkpoints/final
```
- **Acceptance:**
  - lineage complete.
  - no budget mismatch.
  - no NaN/Inf.
  - resume reproducible.
  - ECHO parameters shared within run and checkpoints separate by N.
- **Stop/rollback:** Rerun failed shard only from same-hash checkpoint.

### EVAL-008 — Run 10×200 held-out paired evaluation

- **Dependencies:** EVAL-007.
- **Required reads:** final checkpoints; held-out trace bank; evaluation manifest.
- **Allowed writes:** `configs/experiments/heldout_evaluation.yaml`; `scripts/evaluation/run_heldout_evaluation.py`; `G1`; `G5`.
- **Ordered operations:**
  1. For every point/method run 10 fixed seeds × 200 held-out episodes.
  2. same trace per seed/point.
  3. log actions/masks/ERT/outcomes/rewards/Delta/hashes.
  4. no optimizer calls.
- **Exact command:**
```bash
python3 scripts/evaluation/run_heldout_evaluation.py --config configs/experiments/heldout_evaluation.yaml --output artifacts/evaluation/runs
```
- **Acceptance:**
  - full job count.
  - no training call.
  - immutable manifests.
  - schema-valid outputs.
- **Stop/rollback:** Partial shard is not averaged.

### EVAL-009 — Validate generated, completed, and dropped accounting

- **Dependencies:** EVAL-008.
- **Required reads:** EVAL-008 run outputs.
- **Allowed writes:** `scripts/evaluation/audit_accounting.py`; `tests/unit/test_evaluation_accounting.py`; `artifacts/evaluation/audits/accounting.json`; `artifacts/evaluation/audits/accounting.md`; `G1`.
- **Ordered operations:**
  1. Verify generated=successful+dropped, one outcome, no duplicate/missing task, horizon/drain, pooled counts.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_evaluation_accounting.py -q && python3 scripts/evaluation/audit_accounting.py --input artifacts/evaluation/runs --output artifacts/evaluation/audits/accounting.json
```
- **Acceptance:**
  - zero violations.
- **Stop/rollback:** Any violation blocks aggregation and reopens runtime owner.

### EVAL-010 — Validate no masked ECHO action

- **Dependencies:** EVAL-008.
- **Required reads:** EVAL-008 ECHO decision logs.
- **Allowed writes:** `scripts/evaluation/audit_masks.py`; `tests/unit/test_evaluation_mask_audit.py`; `artifacts/evaluation/audits/masks.json`; `artifacts/evaluation/audits/masks.md`; `G1`.
- **Ordered operations:**
  1. Verify selected mask=1, legality, fallback, same decision mask used in exploration/exploitation/target.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_evaluation_mask_audit.py -q && python3 scripts/evaluation/audit_masks.py --input artifacts/evaluation/runs --output artifacts/evaluation/audits/masks.json
```
- **Acceptance:**
  - zero masked/invalid/self/disconnected action.
- **Stop/rollback:** Violation reopens ECHO-009/010/015/018.

### EVAL-011 — Validate trace, config, topology, and checkpoint hashes

- **Dependencies:** EVAL-008.
- **Required reads:** run and lineage manifests.
- **Allowed writes:** `scripts/evaluation/audit_lineage.py`; `tests/unit/test_evaluation_lineage_audit.py`; `artifacts/evaluation/audits/lineage.json`; `artifacts/evaluation/audits/lineage.md`; `G1`.
- **Ordered operations:**
  1. Cross-check all hashes.
  2. verify paired inputs and no held-out training.
  3. verify N-specific checkpoint.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_evaluation_lineage_audit.py -q && python3 scripts/evaluation/audit_lineage.py --lineage artifacts/evaluation/lineage --runs artifacts/evaluation/runs --output artifacts/evaluation/audits/lineage.json
```
- **Acceptance:**
  - zero missing/mismatch.
  - no held-out checkpoint fitting.
  - N compatibility exact.
- **Stop/rollback:** Exclude and rerun mismatched run; never relabel.

### EVAL-012 — Aggregate seed metrics and 95% confidence intervals

- **Dependencies:** EVAL-009, EVAL-010, EVAL-011.
- **Required reads:** three PASS audits; run outputs; figure manifest.
- **Allowed writes:** `src/evaluation/statistics.py`; `scripts/evaluation/aggregate_results.py`; `tests/unit/test_evaluation_statistics.py`; `G1`; `G6`.
- **Ordered operations:**
  1. Task→episode→seed aggregation.
  2. negative delay convention.
  3. pooled drop counts before seed ratio.
  4. seed-level mean/95% CI.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_evaluation_statistics.py -q && python3 scripts/evaluation/aggregate_results.py --manifest experiments/figure_manifest.yaml --input artifacts/evaluation/runs --output artifacts/metrics
```
- **Acceptance:**
  - 10 seed rows per point.
  - CI present.
  - formulas tested.
  - byte-identical regeneration.
- **Stop/rollback:** Do not impute missing seeds.

### FIG-001 — Render Figure 4 topology

- **Dependencies:** BASE-002.
- **Required reads:** frozen topology.
- **Allowed writes:** `scripts/figures/render_figure4.py`; `artifacts/figures/vector/figure4.svg`; `artifacts/figures/vector/figure4.pdf`; `artifacts/figures/png_300dpi/figure4.png`; `artifacts/figures/manifests/figure4.json`; `artifacts/figures/panel_exports/f4.csv`; `G1`.
- **Ordered operations:**
  1. Render actual topology with deterministic coordinates.
- **Exact command:**
```bash
python3 scripts/figures/render_figure4.py --topology configs/authoritative/hoodie_topology.json --output artifacts/figures
```
- **Acceptance:**
  - edge list/hash exact.
  - SVG/PDF/300dpi PNG exist.
  - repeated hashes equal.
- **Stop/rollback:** No hand-drawn correction.

### FIG-002 — Render Figure 5(a–b)

- **Dependencies:** EVAL-006.
- **Required reads:** EVAL-006 outputs.
- **Allowed writes:** `scripts/figures/render_figure5.py`; `artifacts/figures/vector/figure5.svg`; `artifacts/figures/vector/figure5.pdf`; `artifacts/figures/png_300dpi/figure5.png`; `artifacts/figures/manifests/figure5.json`; `artifacts/figures/panel_exports/f5a.csv`; `artifacts/figures/panel_exports/f5b.csv`; `G1`.
- **Ordered operations:**
  1. Plot reward vs LR and gamma from retained CSV with CI.
- **Exact command:**
```bash
python3 scripts/figures/render_figure5.py --input artifacts/evaluation/figure5 --output artifacts/figures
```
- **Acceptance:**
  - 2 panels/all points.
  - values equal CSV.
  - lineage complete.
- **Stop/rollback:** No manual y-values.

### FIG-003 — Render Figure 6(a–e)

- **Dependencies:** EVAL-012.
- **Required reads:** EVAL-012 panel metrics; Figure-6 manifest.
- **Allowed writes:** `scripts/figures/render_figure6.py`; `artifacts/figures/vector/figure6.svg`; `artifacts/figures/vector/figure6.pdf`; `artifacts/figures/png_300dpi/figure6.png`; `artifacts/figures/manifests/figure6.json`; `artifacts/figures/panel_exports/f6a.csv`; `artifacts/figures/panel_exports/f6b.csv`; `artifacts/figures/panel_exports/f6c.csv`; `artifacts/figures/panel_exports/f6d.csv`; `artifacts/figures/panel_exports/f6e.csv`; `G1`.
- **Ordered operations:**
  1. Render exact P/capacity/N/traffic/rate profiles with 2s default timeout and CI.
- **Exact command:**
```bash
python3 scripts/figures/render_figure6.py --input artifacts/metrics --manifest experiments/figure_manifest.yaml --output artifacts/figures
```
- **Acceptance:**
  - 5 panels.
  - definitions exact.
  - each point traces to 10 seeds.
- **Stop/rollback:** No unapproved smoothing/interpolation.

### FIG-004 — Render Figure 7(a–f)

- **Dependencies:** EVAL-012.
- **Required reads:** EVAL-012 metrics; Figure-7 manifest.
- **Allowed writes:** `scripts/figures/render_figure7.py`; `artifacts/figures/vector/figure7.svg`; `artifacts/figures/vector/figure7.pdf`; `artifacts/figures/png_300dpi/figure7.png`; `artifacts/figures/manifests/figure7.json`; `artifacts/figures/panel_exports/f7a.csv`; `artifacts/figures/panel_exports/f7b.csv`; `artifacts/figures/panel_exports/f7c.csv`; `artifacts/figures/panel_exports/f7d.csv`; `artifacts/figures/panel_exports/f7e.csv`; `artifacts/figures/panel_exports/f7f.csv`; `G1`.
- **Ordered operations:**
  1. Render delay a-c and pooled-drop d-f with exact fixed/swept timeout and CI.
- **Exact command:**
```bash
python3 scripts/figures/render_figure7.py --input artifacts/metrics --manifest experiments/figure_manifest.yaml --output artifacts/figures
```
- **Acceptance:**
  - 6 panels.
  - negative-delay and pooled-drop preserved.
  - no timeout contradiction.
- **Stop/rollback:** Do not average episode drop ratios.

### FIG-005 — Render Figure 8

- **Dependencies:** EVAL-012.
- **Required reads:** EVAL-012 ECHO/NoLSTM metrics.
- **Allowed writes:** `scripts/figures/render_figure8.py`; `artifacts/figures/vector/figure8.svg`; `artifacts/figures/vector/figure8.pdf`; `artifacts/figures/png_300dpi/figure8.png`; `artifacts/figures/manifests/figure8.json`; `artifacts/figures/panel_exports/f8.csv`; `G1`.
- **Ordered operations:**
  1. Render N=20,P=.3,timeout1s,episodes0–3000 two-series ablation.
- **Exact command:**
```bash
python3 scripts/figures/render_figure8.py --input artifacts/metrics --manifest experiments/figure_manifest.yaml --output artifacts/figures
```
- **Acceptance:**
  - exact two series.
  - values equal CSV.
  - no hidden smoothing.
  - vector/300dpi.
- **Stop/rollback:** No LSTM superiority claim without statistics.

### FIG-006 — Validate all vector and PNG exports and lineage

- **Dependencies:** FIG-001, FIG-002, FIG-003, FIG-004, FIG-005.
- **Required reads:** all figure artifacts/manifests/panel CSVs.
- **Allowed writes:** `scripts/figures/validate_figure_exports.py`; `tests/unit/test_figure_lineage.py`; `artifacts/figures/figure_lineage_index.json`; `G1`.
- **Ordered operations:**
  1. Verify 15 panels, CSV equality, SVG/PDF, PNG 300dpi, hashes, run IDs, labels/units.
- **Exact command:**
```bash
python3 -m pytest tests/unit/test_figure_lineage.py -q && python3 scripts/figures/validate_figure_exports.py --figures artifacts/figures --output artifacts/figures/figure_lineage_index.json
```
- **Acceptance:**
  - 15/15 valid.
  - no missing lineage.
  - deterministic regeneration.
- **Stop/rollback:** Invalid panel reopens owner.

### REPORT-001 — Write final HOODIE reproduction report

- **Dependencies:** BASE-022, FREEZE-001.
- **Required reads:** freeze manifest; BASE-022 evidence; base tests/smoke.
- **Allowed writes:** `docs/reports/HOODIE_REPRODUCTION_REPORT.md`; `artifacts/reports/hoodie_reproduction_lineage.json`; `G1`.
- **Ordered operations:**
  1. Describe mechanics/evidence/trends/deviations/limitations/frozen SHA.
  2. exclude ECHO results.
- **Exact command:**
```bash
python3 - <<'PY'
from pathlib import Path
p=Path('docs/reports/HOODIE_REPRODUCTION_REPORT.md'); assert p.exists() and 'Lineage' in p.read_text()
PY
```
- **Acceptance:**
  - every claim cites raw/test/freeze evidence.
  - no unsupported exact-match claim.
- **Stop/rollback:** Report cannot compensate for failed reproduction.

### REPORT-002 — Write final ECHO implementation report

- **Dependencies:** ECHO-020.
- **Required reads:** source/coverage audits; pilot; Phase-2 evidence.
- **Allowed writes:** `docs/reports/ECHO_IMPLEMENTATION_REPORT.md`; `artifacts/reports/echo_implementation_lineage.json`; `G1`.
- **Ordered operations:**
  1. Document equation/algorithm map, chronology, N+2 size-specific architecture, within-run parameter sharing, state/mask/reward/SMDP/DDQL/LSTM/isolation/tests/limits.
- **Exact command:**
```bash
python3 - <<'PY'
from pathlib import Path
p=Path('docs/reports/ECHO_IMPLEMENTATION_REPORT.md'); assert p.exists() and 'Equations (1)–(67)' in p.read_text()
PY
```
- **Acceptance:**
  - 69 rows linked.
  - current revisions/frozen base recorded.
  - no historical authority.
  - revision-273 architecture explicit.
- **Stop/rollback:** Uncovered equation blocks report.

### REPORT-003 — Write final evaluation and figure report

- **Dependencies:** EVAL-012, FIG-006.
- **Required reads:** metrics/audits; figure lineage; run manifests.
- **Allowed writes:** `docs/reports/ECHO_EVALUATION_REPORT.md`; `artifacts/reports/evaluation_lineage.json`; `G1`.
- **Ordered operations:**
  1. Document methods/budgets/held-out/statistics/15 panels/invariants/limitations with artifact lineage.
- **Exact command:**
```bash
python3 - <<'PY'
from pathlib import Path
p=Path('docs/reports/ECHO_EVALUATION_REPORT.md'); assert p.exists() and '15 panels' in p.read_text()
PY
```
- **Acceptance:**
  - all numbers have lineage.
  - no missing seed.
  - claims bounded by evidence.
- **Stop/rollback:** Failed audit/figure blocks report.

### CLEAN-002 — Archive superseded artifacts without deletion

- **Dependencies:** REPORT-001, REPORT-002, REPORT-003.
- **Required reads:** three final reports; artifact inventory.
- **Allowed writes:** `scripts/cleanup/archive_superseded_artifacts.py`; `artifacts/archive/archive_manifest.json`; `G1`; `G8`.
- **Ordered operations:**
  1. Archive only inventory entries with archive_eligible=true.
  2. preserve old hash/replacement/reason/timestamp.
  3. no delete.
- **Exact command:**
```bash
python3 scripts/cleanup/archive_superseded_artifacts.py --inventory artifacts/classification/artifact_inventory.json --archive artifacts/archive/superseded --manifest artifacts/archive/archive_manifest.json
```
- **Acceptance:**
  - every archived item mapped to canonical replacement.
  - no authoritative raw/checkpoint removed.
- **Stop/rollback:** Ambiguous item remains and is listed unresolved.

### CLEAN-003 — Remove canonical-path ambiguity without deletion

- **Dependencies:** CLEAN-002.
- **Required reads:** archive manifest; artifact inventory field editable_reference_files; final reports.
- **Allowed writes:** `artifacts/archive/path_redirects.json`; `docs/reports/FINAL_ARTIFACT_PATHS.md`; `G1`.
- **Ordered operations:**
  1. Update only explicit editable_reference_files from inventory.
  2. write redirect map.
  3. verify final reports use canonical paths.
- **Exact command:**
```bash
python3 - <<'PY'
import json
from pathlib import Path
p=Path('artifacts/archive/path_redirects.json'); assert p.exists(); json.loads(p.read_text())
PY
```
- **Acceptance:**
  - one canonical path/type.
  - redirects resolve.
  - no permanent deletion.
- **Stop/rollback:** Any unlisted reference file => PLAN_CHANGE_REQUIRED.

### HANDOFF-001 — Produce final artifact index and exact rerun commands

- **Dependencies:** CLEAN-003.
- **Required reads:** all final manifests/reports/figures/archive maps/tested SHAs.
- **Allowed writes:** `artifacts/FINAL_ARTIFACT_INDEX.md`; `artifacts/FINAL_ARTIFACT_INDEX.json`; `scripts/reproduce_all.sh`; `docs/reports/FINAL_HANDOFF.md`; `G1`.
- **Ordered operations:**
  1. Enumerate all source/config/topology/trace/checkpoint/log/metric/figure/report hashes and environment.
  2. verify-only script checks dependency order/hashes.
- **Exact command:**
```bash
bash scripts/reproduce_all.sh --verify-only
```
- **Acceptance:**
  - all paths/hashes resolve.
  - clean-checkout verify succeeds.
  - no hidden manual step.
  - limitations explicit.
- **Stop/rollback:** Missing artifact/hash blocks handoff.

## 9. Evaluation and figure constants
- Figure 4: actual default 20-EA topology.
- Figure 5(a): learning rates `{1e-9,5e-9,1e-8,1e-7,5e-7,7e-7}`.
- Figure 5(b): gamma `{.2,.4,.6,.8,.99}`.
- Figure 6(a): reward vs P `{.1,.3,.5,.7,.9}`, N `{10,15,20}`.
- Figure 6(b): action counts vs P, N=20.
- Figure 6(c): reward vs EA capacity `{4,5,6,7,8,9}` GHz, N `{10,15,20}`.
- Figure 6(d): reward vs N `{10,15,20,25,30}` under moderate `(1–3 Mbits,P=.5)`, heavy `(2–5,P=.7)`, extreme `(3–7,P=.9)`.
- Figure 6(e): reward vs N under balanced `(R_H=10,R_V=30)`, horizontal-centric `(20,20)`, vertical-centric `(5,40)` Mbps.
- Figure 6 default timeout: 20 slots = 2 seconds.
- Figure 7(a): delay vs P, timeout 10 s.
- Figure 7(b): delay vs capacity `{3,4,5,6,7}` GHz, timeout 10 s.
- Figure 7(c): delay vs timeout `{9.6,9.8,10.0,10.2,10.4}` s.
- Figure 7(d): pooled drop ratio vs P, timeout 2 s.
- Figure 7(e): pooled drop ratio vs capacity, timeout 2 s.
- Figure 7(f): pooled drop ratio vs timeout `{1.6,1.8,2.0,2.2,2.4}` s.
- Figure 8: ECHO vs ECHO-NoLSTM, N=20, P=.3, timeout 1 s, episodes 0–3000.
- comparison methods: ECHO, HOODIE, RO, FLC, VO, HO, BCO, MLEO; ECHO-NoLSTM where specified.
- every point: 10 fixed seeds × 200 held-out paired episodes.
- confidence intervals across seed-level metrics; negative-delay convention; pooled drop counts within seed.
- for each tested N, ECHO uses an independently trained N-specific checkpoint with N+2 action outputs and within-run parameter sharing.

## 10. Exact executor prompt

```text
You are the single-task executor for hadifarajvand/hoodie_sim_v2.
The sole authority is artifacts/reports/ECHO_MASTER_EXECUTION_PLAN.md version ECHO-MEP-v4.2 and artifacts/control/NEXT_TASK.json.
Execute exactly the authorized task ID and attempt. Follow its reads, writes, operations, command, acceptance, evidence, branch, and stop rules literally.
Do not choose another task, edit the plan, merge, modify unlisted files, substitute commands, invent source values, or continue after commit.
On missing authority use BLOCKED_EXTERNAL; on unlisted required file use PLAN_CHANGE_REQUIRED; on changed start SHA use STALE_BRANCH; otherwise produce G1, commit, and stop.
```

## 11. Exact reviewer/controller prompt

```text
You are the independent reviewer/controller for hadifarajvand/hoodie_sim_v2.
Use artifacts/reports/ECHO_MASTER_EXECUTION_PLAN.md version ECHO-MEP-v4.2 and G2/G3 as the sole control authority.
In BOOTSTRAP mode, discover the approved plan commit by the Section 1.1 rule, run the structural preflight, initialize G3, authorize SRC-001 attempt 1, commit control files, print the executor invocation, and stop.
In REVIEW mode, review exactly one task branch: verify ancestry and changed paths, inspect all changes/evidence, rerun the exact command, decide PASS/REWORK/BLOCKED, never repair implementation, merge only on PASS or evidence-only BLOCKED_EXTERNAL, update the plan and G2/G3, authorize exactly one next task, print its executor invocation, and stop.
```

## 12. Structural preflight requirements

- 73 unique registry IDs.
- 73 unique card IDs and exact ID-set equality.
- phase totals 6/23/20/12/12.
- status totals 5/2/66.
- zero missing dependency IDs, self-dependencies, and DAG cycles.
- zero wildcard permissions.
- all READY commands exist or the card creates their executable/test.
- BASE-005 owns pre-freeze ECHO decontamination.
- ECHO-001 cannot modify frozen files.
- ECHO-009/012/015 implement revision-273 N+2, N-specific checkpoints, and within-run sharing.
- ECHO-011 depends on early EVAL-001.
- same-invocation SRC fallback prohibited.
- reviewer/controller prompt present.
- permanent deletion prohibited.

## 13. Initial authorization

After bootstrap, `NEXT_TASK.json` authorizes only `SRC-001`, attempt 1, branch `task/src-001-r1`. `BASE-001` is logically READY but is not executable until the controller explicitly authorizes it. The entire plan then advances one reviewed and merged card at a time through `HANDOFF-001`. Permanent deletion is prohibited.
