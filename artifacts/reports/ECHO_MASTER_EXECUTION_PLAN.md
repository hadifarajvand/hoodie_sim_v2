# ECHO Master Execution Plan — Closed-Form Agent Runbook

## 1. Document control

| Field | Value |
|---|---|
| Plan version | `ECHO-MEP-v4.0` |
| Plan status | `FINAL CLOSED-FORM RUNBOOK — EXECUTE ONLY DEPENDENCY-READY CARDS` |
| Repository | `hadifarajvand/hoodie_sim_v2` |
| Branch at planning start | `main` |
| Planning-start HEAD | `09b53c9d1d69c136cf794e6f865c8c5ccf2c0994` |
| Planning-start plan blob | `96333720529882db6fd761b7d53e901186225c07` |
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

No tab title is asserted. The connector exposes the document title, tab ID, content heading, modification time, and revisions, but not a tab title.

This file supersedes earlier execution instructions. Older plans and `resources/ECHO_multi_agent_phase_runbook.md` remain historical references only when they agree with this file.

---

## 2. Final implementation decision

This plan is now an executable runbook rather than a descriptive roadmap. It contains:

- one immutable authority hierarchy;
- one deterministic task-selection algorithm;
- one status machine;
- exact dependency IDs for all 73 tasks;
- exact read/write boundaries for every task;
- ordered implementation operations;
- exact commands that either already exist or are created by the task itself;
- acceptance criteria, evidence requirements, rollback boundaries, and stop conditions;
- complete evaluation, figure, reporting, and cleanup requirements.

The coding agent must execute **one task card only**, prove its acceptance criteria, produce the evidence package, commit the task branch, and stop. It must not design additional work, start another card, merge its own branch, or improvise outside the listed file allowlist.

Current execution authorization:

1. `SRC-001` is READY.
2. `BASE-001` is READY.
3. All other incomplete tasks are BLOCKED by the dependencies in the registry.
4. A single executor selects `SRC-001` first. When live-source access is unavailable, it records `BLOCKED_EXTERNAL` and then selects `BASE-001`.
5. Separate executors may run `SRC-001` and `BASE-001` concurrently only on separate branches and only when explicitly launched for those exact IDs.
6. No ECHO implementation may be accepted before `SRC-001` and `FREEZE-001` are VERIFIED COMPLETE.
7. No evaluation, paper figure, or superiority claim may be produced before `ECHO-020` is VERIFIED COMPLETE.

---

## 3. Scientific authority and non-negotiable contracts

### 3.1 Authority order

1. Current live ECHO proposed-method tab at the revisions recorded in Section 1.
2. Original HOODIE paper PDF/OCR for inherited base mechanics and HOODIE learning.
3. `research/ECHO_evaluation_spec.md`, provided it does not conflict with the current live method.
4. Topology authorization and deterministic PNG-export authorization.
5. Repository code/tests as implementation evidence only.
6. Legacy reports, old source snapshots, smoke outputs, checkpoints, and figures as historical evidence only.

A passing test cannot override a paper equation. Existing code cannot define the method. A newer live revision blocks ECHO acceptance until `SRC-001` is repeated.

### 3.2 Current ECHO contract

The source lock must verify Equations (1)–(67), Algorithm 1 with 23 numbered lines, and Algorithm 2 with 12 numbered lines. The implementation must preserve:

- independent Bernoulli arrival opportunity for every EA at every decision slot;
- `d_i = t_i^a + δ_i - 1`;
- one direct route decision at arrival and no second destination decision;
- one local waiting queue and one outbound waiting queue per source, excluding active operations;
- one non-preemptive local CPU and one non-preemptive transmitter per source;
- transmission finishing at the end of slot `t` becoming destination admission at the boundary opening `t+1`;
- source-indexed FIFO destination queues and equal public-CPU sharing among active source queues;
- remaining destination workload in CPU cycles;
- fresh destination load preferred and LSTM used only for stale/missing status;
- deterministic constructive `O(q²)` ERT ordering: smallest nonnegative ERT, otherwise minimum lateness, FIFO/stable ID final tie break;
- 30 padded destination feature blocks and 32 canonical outputs: local, positions 1–30, cloud;
- ECHO reward from Equations (55)–(58);
- Equation (59) as one source-EA discounted interval return between consecutive actual decisions of that EA;
- no overlapping per-task replay transitions;
- event-epoch target discount `γ^Δ_(n,m)`;
- masked Dueling Double-DQL from Equations (61)–(67);
- separate supervised LSTM forecasting objective and no held-out evaluation data used for fitting.

### 3.3 Exact boundary chronology to be protected by tests

At the boundary opening slot `t`:

1. apply service/transmission completions generated at the end of `t-1` and perform destination admissions due at `t`;
2. resolve outcomes and attach their task rewards to the source-EA interval that was already open;
3. obtain fresh status or the stale/missing LSTM estimate;
4. remove expired waiting tasks without preempting active work;
5. observe every same-slot arrival;
6. for each arriving EA, finalize its previous interval before opening the new decision interval;
7. evaluate candidates, mask actions, choose one action, and admit the task;
8. rebuild affected ERT waiting orders and start idle source resources;
9. schedule destination queues;
10. execute exactly one slot of active service;
11. update histories/LSTM and perform learning/target-copy work;
12. at `T+1`, resolve remaining outcomes and terminally close every open interval.

Known current defect: `src/training/training_loop.py` processes decision events before task-resolution events returned for the same boundary. `ECHO-018` must reverse that scientific ownership: boundary resolutions belong to the old interval before the new decision closes it.

---

## 4. Strict executor protocol

### 4.1 Task selection

The agent must:

1. Read this file from the current branch.
2. Record `git rev-parse HEAD` and `git status --short`.
3. Refuse to work when the tree contains unrelated edits.
4. Select exactly one task whose execution status is `READY`.
5. Use the priority order in the registry; do not choose a later READY task while an earlier one is executable.
6. Create branch `task/<lowercase-task-id>` from the recorded HEAD.
7. Execute only the selected task card.
8. Stop after committing the task branch.

### 4.2 File ownership

- Files under `Allowed writes` are the complete edit allowlist.
- Files under `Required reads` are read-only unless also listed under `Allowed writes`.
- When correctness appears to require any unlisted file, stop with `PLAN_CHANGE_REQUIRED`; do not edit it.
- Do not modify this master plan during a task. The independent gate reviewer updates statuses after review.
- Do not permanently delete files. Cleanup tasks may move files only into the declared archive paths.
- Do not alter dependencies, package versions, lockfiles, CI, or formatting configuration unless the card explicitly allows it.

### 4.3 Command validity

A listed command is valid only when:

- the executable/test already exists at task start; or
- the card lists that executable/test under `Allowed writes` and explicitly requires creating it before running the command.

Do not substitute commands. Do not suppress failures. Do not mark tests xfail/skip unless the card explicitly requires a scientifically justified skip.

### 4.4 Status machine

`BLOCKED → READY → IN_PROGRESS → IMPLEMENTED_PENDING_REVIEW → VERIFIED_COMPLETE`

Failure transitions:

- missing authority/access: `BLOCKED_EXTERNAL`;
- failed acceptance or test: `REWORK`;
- required unlisted file: `PLAN_CHANGE_REQUIRED`;
- HEAD changed during execution: `STALE_BRANCH`.

The executor may set only `IN_PROGRESS`, `IMPLEMENTED_PENDING_REVIEW`, `BLOCKED_EXTERNAL`, `REWORK`, `PLAN_CHANGE_REQUIRED`, or `STALE_BRANCH` in its task evidence. Only an independent reviewer may grant `VERIFIED_COMPLETE`.

### 4.5 Mandatory evidence package

Every task creates exactly:

```text
artifacts/task_evidence/<TASK-ID>/
├── report.md
├── status.json
├── commands.txt
├── test_output.txt
├── changed_files.json
├── hashes.json
└── git_diff.patch
```

`report.md` must state authority, start HEAD, branch, exact operations, results, acceptance checklist, unresolved risks, and rollback. `changed_files.json` must equal the actual diff file set. `status.json` must contain one allowed status and the tested commit SHA.

Commit message: `<TASK-ID>: <exact task title>`.

The executor must not push to `main`, merge, delete the branch, or start the next task.

---

## 5. Master task registry — source of truth

Execution status totals at this revision: 5 VERIFIED COMPLETE, 2 READY, 66 BLOCKED. Total 73.

### Phase 0 — source, audit, and control (6)

| ID | Status | Dependencies | Title |
|---|---|---|---|
| SRC-001 | READY | NONE | Lock current live ECHO source and close 69-row audit |
| SRC-002 | VERIFIED COMPLETE | NONE | Maintain HOODIE paper evidence registry |
| AUDIT-001 | VERIFIED COMPLETE | NONE | Maintain current code-path inventory |
| AUDIT-002 | VERIFIED COMPLETE | NONE | Reconcile historical completion claims |
| PLAN-001 | VERIFIED COMPLETE | NONE | Maintain closed-form execution plan |
| CLEAN-001 | VERIFIED COMPLETE | NONE | Classify existing artifacts |

### Phase 1 — faithful base HOODIE (23)

| ID | Status | Dependencies | Title |
|---|---|---|---|
| BASE-001 | READY | PLAN-001, CLEAN-001 | Freeze canonical HOODIE Table-4 configuration |
| BASE-002 | BLOCKED | BASE-001 | Freeze approved topology and scalable topology rule |
| BASE-003 | BLOCKED | BASE-002 | Validate independent per-EA arrivals and 100+10 slots |
| BASE-004 | BLOCKED | BASE-003 | Make paired traces immutable and directly consumable |
| BASE-006 | BLOCKED | BASE-004 | Freeze hand-calculated base slot contract |
| BASE-005 | BLOCKED | BASE-006 | Implement/accept synchronized multi-EA slot engine |
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
| FREEZE-001 | BLOCKED | BASE-022 | Freeze validated physical simulator and HOODIE baseline |

### Phase 2 — ECHO on frozen base (20)

| ID | Status | Dependencies | Title |
|---|---|---|---|
| ECHO-001 | BLOCKED | FREEZE-001, SRC-001 | Isolate ECHO from shared/HOODIE code |
| ECHO-002 | BLOCKED | ECHO-001 | Implement Equations (1)–(8) lifecycle/dispatch |
| ECHO-003 | BLOCKED | ECHO-002 | Implement Equations (9)–(11) local estimate |
| ECHO-004 | BLOCKED | ECHO-003 | Implement Equations (12)–(16) outbound estimate |
| ECHO-005 | BLOCKED | ECHO-004 | Implement Equations (17)–(25) destination model |
| ECHO-006 | BLOCKED | ECHO-005 | Implement Equations (26)–(28) history/LSTM inputs |
| ECHO-007 | BLOCKED | ECHO-006 | Implement Equation (29) local queue ERT ordering |
| ECHO-008 | BLOCKED | ECHO-007 | Implement Equation (30) outbound ERT ordering |
| ECHO-009 | BLOCKED | ECHO-008 | Implement 32-position canonical action space |
| ECHO-010 | BLOCKED | ECHO-009 | Implement Equations (42)–(46) mask/fallback |
| ECHO-011 | BLOCKED | ECHO-010 | Implement Equations (47)–(50) pending records |
| ECHO-012 | BLOCKED | ECHO-011 | Implement Equations (51)–(54) normalized state |
| ECHO-013 | BLOCKED | ECHO-012 | Implement Equations (55)–(58) task reward |
| ECHO-014 | BLOCKED | ECHO-013 | Implement Equations (59)–(60) event intervals |
| ECHO-015 | BLOCKED | ECHO-014 | Implement Equations (61)–(67) masked DDQL |
| ECHO-016 | BLOCKED | ECHO-015 | Implement fresh/stale status and LSTM training |
| ECHO-017 | BLOCKED | ECHO-016 | Implement isolated ECHO-NoLSTM |
| ECHO-018 | BLOCKED | ECHO-017 | Implement exact Algorithm 1/2 chronology |
| ECHO-019 | BLOCKED | ECHO-018 | Run deterministic ECHO unit/smoke suite |
| ECHO-020 | BLOCKED | ECHO-019 | Produce equation coverage and paired pilot gate |

### Phase 3 — authoritative evaluation (12)

| ID | Status | Dependencies | Title |
|---|---|---|---|
| EVAL-001 | BLOCKED | ECHO-020 | Freeze evaluation/figure manifests and schemas |
| EVAL-002 | BLOCKED | EVAL-001 | Generate immutable paired trace bank |
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
| CLEAN-002 | BLOCKED | REPORT-001, REPORT-002, REPORT-003 | Mark stale artifacts superseded and archive copies |
| CLEAN-003 | BLOCKED | CLEAN-002 | Remove canonical-path ambiguity without permanent deletion |
| HANDOFF-001 | BLOCKED | CLEAN-003 | Produce final artifact index and exact rerun commands |

---

## 6. Complete task cards

The following cards are executable specifications. The agent may not replace listed paths with alternatives.

### SRC-001 — Lock current live ECHO source and close 69-row audit

- Required reads: live Google Doc identifiers in Section 1; historical `research/authority/echo/live/*`; `research/ECHO_method_spec.md`; `artifacts/reports/ECHO_MASTER_EXECUTION_PLAN.md`.
- Allowed writes: `research/authority/echo/live/ECHO_PROPOSED_METHOD.md`, `research/authority/echo/live/source_metadata.json`, `research/authority/echo/live/SHA256SUMS`, `artifacts/audits/echo_live_revision_audit.md`, `scripts/authority/verify_echo_source_lock.py`, `tests/unit/test_echo_source_lock.py`, task evidence directory.
- Execute: export the exact proposed-method tab without inventing a tab title; normalize line endings only; record Drive revision 270, connector revision, modified time, document/tab IDs, heading, retrieval method/time; compute raw and normalized SHA-256; enumerate Equations 1–67 plus Algorithms 1/2; verify algorithm line counts 23/12; create 69 audit rows with `MATCH`, `CHANGED`, `ADDED`, `REMOVED`, or `AMBIGUOUS`; map each non-MATCH row to one ECHO task and one test path.
- Command created by this task: `python3 scripts/authority/verify_echo_source_lock.py --snapshot research/authority/echo/live/ECHO_PROPOSED_METHOD.md --metadata research/authority/echo/live/source_metadata.json --checksums research/authority/echo/live/SHA256SUMS --audit artifacts/audits/echo_live_revision_audit.md && python3 -m pytest tests/unit/test_echo_source_lock.py -q`.
- Pass: exact IDs/revisions match Section 1; all 69 rows classified; no missing equation/algorithm; SHA files agree; no unsupported tab title; audit contains task/test consequences.
- Stop/rollback: when live access is unavailable, write only evidence status `BLOCKED_EXTERNAL` and change no authority file; rollback is branch deletion.

### SRC-002 — Maintain HOODIE paper evidence registry

- Required reads: `resources/papers/hoodie/ocr/merged.md`, `resources/papers/hoodie/ocr/merged.txt`, `artifacts/analysis/paper-mechanism-registry/*`, `src/analysis/paper_mechanism_registry.py`.
- Allowed writes when reopened: those registry artifacts, `src/analysis/paper_mechanism_registry.py`, `tests/unit/test_paper_mechanism_registry.py`, `tests/integration/test_paper_mechanism_registry_flow.py`, task evidence.
- Execute: preserve exact page/table/equation provenance; distinguish paper-explicit, derived, approved clarification, and unresolved values.
- Command: `python3 -m pytest tests/unit/test_paper_mechanism_registry.py tests/integration/test_paper_mechanism_registry_flow.py -q`.
- Pass: every base mechanism used by Phase 1 has a source location and no ECHO behavior is attributed to HOODIE.
- Stop/rollback: this card is already VERIFIED COMPLETE; do not execute unless an independent reviewer reopens it.

### AUDIT-001 — Maintain current code-path inventory

- Required reads: `src/`, `tests/`, `src/analysis/hoodie_proposed_fidelity/implementation_scan.py`, existing implementation-scan artifacts.
- Allowed writes when reopened: implementation-scan source/tests/artifacts and task evidence only.
- Execute: enumerate runtime entry points, queue ownership, learner paths, evaluation paths, and generated artifacts; verify every claim by opening source.
- Command: `python3 -m pytest tests/unit/test_hoodie_proposed_fidelity_implementation_scan.py -q`.
- Pass: inventory paths exist at the tested SHA and no completion is inferred from names alone.
- Stop/rollback: already VERIFIED COMPLETE; reopen only after a material repository restructure.

### AUDIT-002 — Reconcile historical completion claims

- Required reads: commit history, `artifacts/reports/*`, `artifacts/test_triage/*`, `artifacts/analysis/hoodie-training-foundation-readiness-audit/*`.
- Allowed writes when reopened: readiness-audit code/tests/artifacts and task evidence only.
- Execute: classify every prior claim as authoritative, potentially reusable, premature, historical, or revert candidate; never infer completion from a commit title.
- Command: `python3 -m pytest tests/unit/test_hoodie_training_foundation_readiness_audit.py -q`.
- Pass: all current implementation areas are assigned to one task card and one acceptance gate.
- Stop/rollback: already VERIFIED COMPLETE; reopen when unaudited implementation commits appear.

### PLAN-001 — Maintain closed-form execution plan

- Required reads: this file and current Git HEAD.
- Allowed writes when reopened: this file and task evidence only.
- Execute: preserve exactly 73 unique task IDs, valid dependencies, acyclic graph, exact status totals, and one detailed card per ID.
- Verification command: `python3 - <<'PY'
import re, pathlib
p=pathlib.Path('artifacts/reports/ECHO_MASTER_EXECUTION_PLAN.md').read_text()
ids=re.findall(r'^### ([A-Z]+-\d{3}) —',p,re.M)
assert len(ids)==73,(len(ids),ids)
assert len(set(ids))==73
print('73 unique task cards')
PY`.
- Pass: registry IDs equal card IDs; every dependency exists; no self-dependency; status total is 73.
- Stop/rollback: already VERIFIED COMPLETE for v4.0; plan changes require a dedicated planning-only commit.

### CLEAN-001 — Classify existing artifacts

- Required reads: `artifacts/`, `research/`, existing artifact indexes and triage files.
- Allowed writes when reopened: artifact classification/index files and task evidence; never source code.
- Execute: label files authoritative, historical, superseded, smoke-only, synthetic, or unresolved; do not delete.
- Command: `python3 - <<'PY'
from pathlib import Path
assert Path('artifacts').exists() and Path('research').exists()
print('artifact roots present')
PY`.
- Pass: no legacy figure/checkpoint/report is cited as final evidence.
- Stop/rollback: already VERIFIED COMPLETE; reopen only after new unclassified artifact families appear.

### BASE-001 — Freeze canonical HOODIE Table-4 configuration

- Required reads: `resources/papers/hoodie/ocr/merged.md`, `resources/papers/hoodie/ocr/merged.txt`, `configs/simulation.yaml`, `configs/runtime_model.yml`, `configs/experiments/exp_small_deterministic.json`, paper registry, topology authorization.
- Allowed writes: `configs/authoritative/hoodie_table4.yaml`, `configs/authoritative/hoodie_table4.schema.json`, `tests/unit/test_hoodie_table4_config.py`, `artifacts/authority/hoodie/table4_manifest.json`, task evidence.
- Execute: encode 20 EAs; 100 decision + 10 drain slots; independent arrivals with default `P=0.5`; task sizes 2.0–5.0 Mbits in 0.1 increments; density `0.297 Gcycles/Mbit`; slot `0.1 s`; timeout 20 slots/2 s; edge 5 GHz and cloud 30 GHz where paper-supported; copy rates and all learning parameters from exact Table-4 rows; classify every value; compare every current config value as match/conflict/smoke-only/assumption-backed/unrelated.
- Command created by task: `python3 -m pytest tests/unit/test_hoodie_table4_config.py -q`.
- Pass: schema validates; every value has unit/source/classification; manifest contains source and file hashes; no unresolved value is promoted; current smoke configs remain non-authoritative.
- Stop/rollback: when a Table-4 value cannot be resolved, keep it `UNRESOLVED`, mark task `REWORK`, and do not guess.

### BASE-002 — Freeze approved topology and scalable rule

- Required reads: `src/environment/topology.py`, `resources/papers/hoodie/recovered/user-approved-assumption-registry.json`, topology authorization, canonical config from BASE-001.
- Allowed writes: `configs/authoritative/hoodie_topology.json`, `tests/unit/test_hoodie_topology_authority.py`, `artifacts/authority/hoodie/topology/*`, task evidence; update `src/environment/topology.py` only when tests expose mismatch.
- Execute: freeze exact 20-EA adjacency; implement/verify `G_N = 5K_(N/5)` only for N divisible by 5; export adjacency CSV, edge list, JSON, SVG, 300-dpi PNG, hashes, metrics; verify deterministic seed/coordinates.
- Command created by task: `python3 -m pytest tests/unit/test_hoodie_topology_authority.py -q`.
- Pass: N=20 topology equals approved anchor; N=10/15/20/25/30 generation is deterministic; no self/disconnected illegal edge; repeated exports hash identically.
- Stop/rollback: never replace the approved adjacency with a visually similar graph.

### BASE-003 — Validate independent per-EA arrivals and 100+10 slots

- Required reads: `src/evaluation/trace_protocol.py`, canonical config/topology, `tests/unit/test_trace_protocol_paper_semantics.py`.
- Allowed writes: `src/evaluation/trace_protocol.py`, `tests/unit/test_trace_protocol_paper_semantics.py`, `tests/unit/test_trace_expected_arrivals.py`, task evidence.
- Execute: verify one Bernoulli draw per EA per decision slot; zero drain arrivals; exact size set/density/deadline; stable ordering `(arrival_slot, source_agent_id, task_id)`; record trace metadata.
- Commands: `python3 -m pytest tests/unit/test_trace_protocol_paper_semantics.py tests/unit/test_trace_expected_arrivals.py -q`.
- Pass: P=0 creates zero tasks; P=1 creates `N×100`; repeated-seed mean for N=20,P=.5 is statistically centered on 1000 with deterministic exact blueprints per seed; slots 100–109 have no arrival.
- Stop/rollback: do not change random-draw order to force a preferred sample count.

### BASE-004 — Make paired traces immutable and directly consumable

- Required reads: `src/evaluation/trace_protocol.py`, `src/environment/trace_source.py`, `src/evaluation/runner.py`, `src/environment/evaluation_gym_adapter.py`.
- Allowed writes: those four files, `tests/unit/test_trace_immutability.py`, `tests/integration/test_paired_trace_identity.py`, task evidence.
- Execute: make blueprint/trace immutable; add canonical serialization and SHA-256; ensure training/evaluation accept supplied trace objects without regeneration; build fresh Task instances per method while preserving byte-identical blueprints.
- Commands: `python3 -m pytest tests/unit/test_trace_immutability.py tests/integration/test_paired_trace_identity.py -q`.
- Pass: mutation raises; same serialized bytes/hash across methods; no runner calls trace generation when supplied trace exists; task runtime mutation does not mutate blueprint.
- Stop/rollback: do not cache mutable Task objects inside the trace bank.

### BASE-006 — Freeze hand-calculated base slot contract

- Required reads: HOODIE evidence registry; `src/environment/gym_adapter.py`, `src/environment/evaluation_gym_adapter.py`, `src/environment/slot_engine.py`, queue files.
- Allowed writes: `docs/contracts/hoodie_slot_contract.md`, `tests/fixtures/hoodie_slot_timelines.json`, `tests/unit/test_hoodie_slot_contract_vectors.py`, task evidence.
- Execute: specify boundary/service order for same-slot arrivals, one-slot/multi-slot local service, outbound wait, transmission completion, next-boundary destination admission, destination processing, waiting expiration, active late completion, and 10 drain slots; calculate expected slots manually.
- Command created by task: `python3 -m pytest tests/unit/test_hoodie_slot_contract_vectors.py -q`.
- Pass: fixture calculations are internally consistent and distinguish boundary slot from end-of-slot completion; no ECHO reward/mask/ERT semantics appear.
- Stop/rollback: this task must not modify runtime code; runtime mismatches are fixed by BASE-005/007–012.

### BASE-005 — Implement/accept synchronized multi-EA slot engine

- Required reads: BASE-006 contract/fixtures; `src/environment/evaluation_gym_adapter.py`, `src/environment/gym_adapter.py`, `src/environment/slot_engine.py`.
- Allowed writes: those three files, `tests/unit/test_hoodie_slot_engine.py`, `tests/integration/test_same_slot_multi_ea.py`, task evidence.
- Execute: process all same-slot arrivals without advancing time; give exactly one decision to each arriving EA; advance the global physical slot exactly once; apply previous-boundary events before new decisions; prohibit drain arrivals.
- Commands: `python3 -m pytest tests/unit/test_hoodie_slot_engine.py tests/integration/test_same_slot_multi_ea.py -q`.
- Pass: K same-slot arrivals produce K decisions and one service advance; completion/admission timestamps match BASE-006 vectors; no global `_current_task` causes skipped agents; supplied trace consumed directly.
- Stop/rollback: do not introduce method-specific ECHO imports into the neutral slot kernel.

### BASE-007 — Implement/accept private FIFO waiting and active separation

- Required reads: `src/environment/private_queue.py`, `src/environment/execution_helper.py`, `src/environment/evaluation_gym_adapter.py`, BASE-006 fixtures.
- Allowed writes: those files, `tests/unit/test_private_queue_lifecycle.py`, existing `tests/unit/test_fifo_ordering.py`, `tests/unit/test_queue_waiting_time.py`, task evidence.
- Execute: queue admission does not start computation; active task is explicit/non-preemptive; waiting FIFO excludes active; only active task consumes CPU; expired waiting tasks removed before service selection; late active result resolved per contract.
- Commands: `python3 -m pytest tests/unit/test_private_queue_lifecycle.py tests/unit/test_fifo_ordering.py tests/unit/test_queue_waiting_time.py -q`.
- Pass: start timestamp set only on first CPU service; active head never reordered/preempted; one-slot inclusive completion exact; no waiting task receives cycles.
- Stop/rollback: ERT ordering is forbidden in HOODIE private queues.

### BASE-008 — Implement/accept one outbound FIFO/transmitter per source

- Required reads: `src/environment/offloading_queue.py`, `src/environment/evaluation_gym_adapter.py`, `src/environment/link_rate_config.py`.
- Allowed writes: those files, `tests/unit/test_single_source_transmitter.py`, `tests/integration/test_outbound_fifo.py`, task evidence.
- Execute: represent one physical transmitter per source; destination may remain task metadata but must not create parallel source transmitters; admission does not set transmission start; active transmission is non-preemptive; waiting order FIFO.
- Commands: `python3 -m pytest tests/unit/test_single_source_transmitter.py tests/integration/test_outbound_fifo.py -q`.
- Pass: two different-destination tasks from one source never overlap transmission; two different sources may transmit simultaneously; head starts only when source transmitter idle.
- Stop/rollback: do not use `(source,destination)` queue identity as a physical resource identity.

### BASE-009 — Preserve one selected destination through transmission

- Required reads: `src/environment/task.py`, `src/environment/environment.py`, `src/environment/gym_adapter.py`, `src/environment/evaluation_gym_adapter.py`.
- Allowed writes: those files, `tests/unit/test_destination_retention.py`, task evidence.
- Execute: store destination at arrival decision; preserve it in outbound queue, completion event, and destination admission; reject any second route choice; ensure local/cloud/horizontal metadata is unambiguous.
- Command: `python3 -m pytest tests/unit/test_destination_retention.py -q`.
- Pass: destination is immutable after admission; every offloaded task reaches exactly the selected queue; action/destination lineage survives serialization/logging.
- Stop/rollback: do not infer destination from current topology after the decision.

### BASE-010 — Enforce next-boundary destination admission

- Required reads: `src/environment/slot_engine.py`, `src/environment/evaluation_gym_adapter.py`, `src/environment/public_queue.py`, BASE-006 vectors.
- Allowed writes: those files, `tests/unit/test_next_boundary_admission.py`, `tests/integration/test_transmission_timeline.py`, task evidence.
- Execute: transmission receiving its final service in slot t completes at end t; stage event; admit at boundary t+1; prohibit destination CPU use in t; handle one- and multi-slot transmissions.
- Commands: `python3 -m pytest tests/unit/test_next_boundary_admission.py tests/integration/test_transmission_timeline.py -q`.
- Pass: exact timestamps match fixture; no same-slot destination processing; one terminal transmission event; no lost staged completion.
- Stop/rollback: do not hide off-by-one behavior behind comments or metadata-only corrections.

### BASE-011 — Implement source-indexed destination FIFO queues

- Required reads: `src/environment/public_queue.py`, `src/environment/gym_adapter.py`, `src/environment/evaluation_gym_adapter.py`.
- Allowed writes: those files, `tests/unit/test_source_indexed_public_queues.py`, task evidence.
- Execute: key each destination queue by `(destination, source)`; FIFO inside each source queue; active head explicit; a task exists in exactly one destination source queue.
- Command: `python3 -m pytest tests/unit/test_source_indexed_public_queues.py -q`.
- Pass: N edge destinations expose N−1 relevant external source queues and cloud exposes N source queues; source queues do not merge; FIFO deterministic.
- Stop/rollback: do not let source-side ERT reorder destination queues.

### BASE-012 — Implement equal public-CPU sharing

- Required reads: `src/environment/execution_helper.py`, `src/environment/runtime_model.py`, `src/environment/evaluation_gym_adapter.py`, `src/environment/public_queue.py`.
- Allowed writes: those files, `tests/unit/test_public_cpu_sharing.py`, `tests/integration/test_destination_capacity_sharing.py`, task evidence.
- Execute: identify active nonempty source queues at a destination; split destination cycles per slot equally; update remaining cycles; complete multiple heads deterministically; recompute shares after boundary changes.
- Commands: `python3 -m pytest tests/unit/test_public_cpu_sharing.py tests/integration/test_destination_capacity_sharing.py -q`.
- Pass: k active source queues each receive capacity/k; total allocated capacity never exceeds destination capacity; no empty queue receives capacity; completion order deterministic.
- Stop/rollback: do not approximate sharing with sequential full-capacity execution.

### BASE-013 — Implement exact HOODIE action semantics

- Required reads: HOODIE evidence registry; `src/policies/action_masking.py`, `src/policies/policy_interface.py`, `src/environment/gym_adapter.py`, topology.
- Allowed writes: those files, `src/agents/hoodie_action_space.py`, `tests/unit/test_hoodie_action_space.py`, task evidence.
- Execute: encode local, each legal horizontal destination, and cloud according to HOODIE; physical mask only; deterministic indexing; no ECHO deadline mask/min-lateness fallback.
- Command: `python3 -m pytest tests/unit/test_hoodie_action_space.py -q`.
- Pass: every connected destination is separately selectable; self/disconnected actions illegal; action IDs stable; no generic “first neighbor” collapse.
- Stop/rollback: do not import `src.echo_action_space` or ECHO ERT/mask modules.

### BASE-014 — Implement exact HOODIE state/history

- Required reads: HOODIE paper registry; `src/agents/paper_state_builder.py`, `src/agents/history_builder.py`, `src/environment/gym_adapter.py`.
- Allowed writes: those files, `configs/authoritative/hoodie_state_schema.json`, `tests/unit/test_hoodie_state_contract.py`, existing paper-state tests, task evidence.
- Execute: encode task-size one-hot, density, private/offload waits, public queue/load features, W=10 history/forecast exactly as paper; fixed ordering/dimension; no ECHO ERT/candidate/mask features.
- Commands: `python3 -m pytest tests/unit/test_hoodie_state_contract.py tests/unit/test_paper_state_builder.py tests/unit/test_paper_state_vector_real.py -q`.
- Pass: shape/order/schema exact; no-arrival handling documented; values derive from current snapshot only; normalization follows paper or is explicitly classified.
- Stop/rollback: do not keep placeholder zero forecasts once BASE-015 begins.

### BASE-015 — Implement real HOODIE LSTM forecast

- Required reads: `src/agents/lstm_dueling_dqn.py`, `src/agents/hoodie_model.py`, `src/agents/neural_net_hoodie_model.py`, history/state schema, HOODIE paper.
- Allowed writes: those files, `src/agents/hoodie_load_forecaster.py`, `tests/unit/test_hoodie_load_forecaster.py`, `tests/agents/test_lstm_dueling_dqn.py`, task evidence.
- Execute: implement W=10 ordered history, model input/output, loss, optimizer, deterministic initialization, checkpoint save/load; connect real forecast to state; separate forecast target from held-out evaluation data.
- Commands: `python3 -m pytest tests/unit/test_hoodie_load_forecaster.py tests/agents/test_lstm_dueling_dqn.py -q`.
- Pass: forecast changes with history; gradients/loss finite; checkpoint round-trip exact; no hard-coded zeros; no test leakage.
- Stop/rollback: when the paper leaves a training detail unresolved, record it and stop rather than borrowing ECHO behavior.

### BASE-016 — Implement one independent HOODIE learner per EA

- Required reads: `src/agents/hoodie_agent.py`, replay/target/model files, `src/training/training_loop.py`.
- Allowed writes: those files, `src/agents/hoodie_agent_manager.py`, `tests/unit/test_per_ea_hoodie_learners.py`, task evidence.
- Execute: instantiate N independent agents with private replay, online network, target network, optimizer, epsilon state, and checkpoint namespace; route each source decision/reward only to its agent.
- Command: `python3 -m pytest tests/unit/test_per_ea_hoodie_learners.py -q`.
- Pass: parameter mutation/replay insertion for EA n does not affect m; exactly N agent states/checkpoints; deterministic seeding per EA.
- Stop/rollback: one shared policy object for all EAs is not acceptable.

### BASE-017 — Implement original HOODIE reward/replay timing

- Required reads: HOODIE registry; `src/environment/reward_timing.py`, `src/training/delayed_reward_training.py`, `src/training/training_loop.py`, `src/agents/replay_buffer.py`.
- Allowed writes: those files, `tests/unit/test_hoodie_reward_replay_timing.py`, task evidence.
- Execute: reproduce paper reward sign, delivery, next-state, terminal behavior, and ordinary base discount; remove ECHO interval return, ERT risk, deadline fallback, and `γ^Δ` unless explicitly paper-supported.
- Command: `python3 -m pytest tests/unit/test_hoodie_reward_replay_timing.py -q`.
- Pass: hand trace yields expected transition; every decision resolves once; replay belongs to correct EA; terminal flush complete; no ECHO-only field required.
- Stop/rollback: current legacy branch is evidence, not authority; unresolved Bellman timing must stop the task.

### BASE-018 — Implement paper-correct HOODIE Dueling Double-DQN

- Required reads: `src/agents/double_dqn.py`, `src/agents/target_network.py`, `src/agents/hoodie_model.py`, `src/agents/neural_net_hoodie_model.py`, `src/agents/torchrl_hoodie_learner.py`, canonical learning config.
- Allowed writes: those files, `tests/unit/test_hoodie_double_dqn_contract.py`, task evidence.
- Execute: real online/target networks, dueling aggregation, Double-DQN selection/evaluation, epsilon schedule, target copy, finite optimizer step, normal base discount; remove heuristic Q paths from authoritative training.
- Commands: `python3 -m pytest tests/unit/test_hoodie_double_dqn_contract.py tests/unit/test_agent_components.py -q`.
- Pass: online chooses and target evaluates; target has no gradient; epsilon endpoints/copy period exact; loss decreases on deterministic batch; checkpoint round-trip.
- Stop/rollback: do not claim a stub/heuristic model is the paper learner.

### BASE-019 — Validate RO/FLC/VO/HO/BCO/MLEO isolation

- Required reads: `src/policies/{ro,flc,vo,ho,bco,mleo}.py`, `src/evaluation/policy_registry.py`, shared simulator.
- Allowed writes: those policy files, policy registry, `tests/integration/test_baseline_method_isolation.py`, `docs/contracts/baseline_definitions.md`, task evidence.
- Execute: define allowed information/action/tie/fallback for each baseline; replace HOODIE alias-to-ADAPTIVE with real HOODIE adapter; ensure heuristics do not train and do not import ECHO modules.
- Command: `python3 -m pytest tests/integration/test_baseline_method_isolation.py -q`.
- Pass: FLC local; VO cloud; HO horizontal or documented physical fallback; RO only physical actions; BCO deterministic cycle; MLEO own latency rule; same traces/accounting.
- Stop/rollback: ECHO mask/ERT/reward imports in baseline code fail the task.

### BASE-020 — Run complete deterministic base invariant suite

- Required reads: all Phase-1 code/tests and BASE-006 fixtures.
- Allowed writes: `tests/integration/test_base_physical_invariants.py`, `tests/integration/test_base_differential_trace.py`, `artifacts/validation/base/*`, task evidence; no runtime code.
- Execute: add end-to-end local/horizontal/cloud traces; simultaneous arrivals; waiting expiration; active late completion; drain; accounting; no multi-location; trace identity; method isolation.
- Command created by task: `python3 -m pytest tests/unit/test_hoodie_table4_config.py tests/unit/test_hoodie_topology_authority.py tests/unit/test_trace_protocol_paper_semantics.py tests/unit/test_trace_immutability.py tests/unit/test_hoodie_slot_contract_vectors.py tests/unit/test_hoodie_slot_engine.py tests/unit/test_private_queue_lifecycle.py tests/unit/test_single_source_transmitter.py tests/unit/test_destination_retention.py tests/unit/test_next_boundary_admission.py tests/unit/test_source_indexed_public_queues.py tests/unit/test_public_cpu_sharing.py tests/unit/test_hoodie_action_space.py tests/unit/test_hoodie_state_contract.py tests/unit/test_hoodie_load_forecaster.py tests/unit/test_per_ea_hoodie_learners.py tests/unit/test_hoodie_reward_replay_timing.py tests/unit/test_hoodie_double_dqn_contract.py tests/integration/test_baseline_method_isolation.py tests/integration/test_base_physical_invariants.py tests/integration/test_base_differential_trace.py -q`.
- Pass: all listed tests pass; generated=completed+dropped; one terminal outcome; no invalid action; no NaN/Inf; no ECHO contamination.
- Stop/rollback: failures reopen the owning task; BASE-020 may not patch runtime code.

### BASE-021 — Run bounded HOODIE runtime/learner smoke

- Required reads: frozen candidate config, Phase-1 code, smoke conventions.
- Allowed writes: `configs/experiments/hoodie_smoke.yaml`, `scripts/smoke/run_hoodie_smoke.py`, `tests/integration/test_hoodie_smoke_runner.py`, `artifacts/smoke/hoodie_v4/*`, task evidence.
- Execute: one fixed seed, bounded episodes/slots, all route types where topology permits, real learner updates, checkpoint save/load, raw task/episode logs.
- Commands: `python3 -m pytest tests/integration/test_hoodie_smoke_runner.py -q && python3 scripts/smoke/run_hoodie_smoke.py --config configs/experiments/hoodie_smoke.yaml --output artifacts/smoke/hoodie_v4`.
- Pass: finite loss/Q/reward; replay grows; target copies; checkpoint reload reproduces inference; accounting exact; smoke labels prevent paper claims.
- Stop/rollback: do not tune hyperparameters from this smoke.

### BASE-022 — Reproduce HOODIE experiment organization/trends

- Required reads: HOODIE paper figure/table registry, frozen candidate base, smoke evidence.
- Allowed writes: `configs/experiments/hoodie_reproduction.yaml`, `scripts/reproduction/run_hoodie_reproduction.py`, `artifacts/reproduction/hoodie/*`, `docs/reports/hoodie_reproduction_evidence.md`, task evidence.
- Execute: reproduce paper experiment organization and trend-level checks using real simulation; preserve raw outputs/config/seeds; compare direction/trend, not fabricated exact pixels.
- Command: `python3 scripts/reproduction/run_hoodie_reproduction.py --config configs/experiments/hoodie_reproduction.yaml --output artifacts/reproduction/hoodie`.
- Pass: every reproduced trend has raw lineage; deviations documented; no hard-coded paper values; base methods consume paired inputs.
- Stop/rollback: a failed trend blocks freeze and must not be described as reproduced.

### FREEZE-001 — Freeze validated physical simulator and HOODIE baseline

- Required reads: all Phase-1 evidence, reproduction report, tested commit.
- Allowed writes: `scripts/release/freeze_hoodie_baseline.py`, `artifacts/releases/hoodie_base_v1/manifest.json`, `artifacts/releases/hoodie_base_v1/SHA256SUMS`, `docs/contracts/hoodie_base_freeze.md`, task evidence.
- Execute: record commit, config/topology/trace schemas, test list/results, checkpoint hashes, public interfaces, forbidden ECHO imports, known limitations; create immutable manifest only after reviewer PASS.
- Command: `python3 scripts/release/freeze_hoodie_baseline.py --manifest artifacts/releases/hoodie_base_v1/manifest.json --checksums artifacts/releases/hoodie_base_v1/SHA256SUMS`.
- Pass: manifest hashes verify; complete Phase-1 suite passes at frozen SHA; no unresolved S0/S1 defect; HOODIE and shared kernel interfaces versioned.
- Stop/rollback: any base code change after freeze invalidates the manifest and reopens affected Phase-1 tasks.

### ECHO-001 — Isolate ECHO from shared/HOODIE code

- Required reads: frozen base contract; `src/environment/gym_adapter.py`, `src/environment/evaluation_gym_adapter.py`, current `src/echo_*`, policy/training paths.
- Allowed writes: `src/environment/method_hooks.py`, `src/echo_adapter.py`, the two adapters, `tests/integration/test_echo_method_isolation.py`, `docs/contracts/echo_isolation_matrix.md`, task evidence.
- Execute: neutral kernel exposes hooks; move ECHO ERT/mask/reward/state/transition behavior behind ECHO adapter; shared kernel and HOODIE import no ECHO modules; preserve frozen base behavior byte-for-byte.
- Command: `python3 -m pytest tests/integration/test_echo_method_isolation.py tests/integration/test_base_physical_invariants.py -q`.
- Pass: dependency scan confirms no ECHO import in frozen base modules; HOODIE regression identical; ECHO adapter can be selected explicitly.
- Stop/rollback: any frozen-base behavioral change requires returning to the owning BASE task and re-freezing.

### ECHO-002 — Implement Equations (1)–(8) lifecycle/dispatch

- Required reads: source snapshot/audit; `src/echo_types.py`, `src/echo_ert.py`, `src/environment/task.py`, ECHO adapter.
- Allowed writes: those files, `tests/unit/test_echo_equations_01_08.py`, task evidence.
- Execute: encode task variables, deadline, route set, one-time direct dispatch, stored destination, success/drop lifecycle, inclusive slot arithmetic.
- Command: `python3 -m pytest tests/unit/test_echo_equations_01_08.py -q`.
- Pass: equation examples and edge cases exact; no second action; deadline off-by-one exact; task state machine has one terminal resolution.
- Stop/rollback: no queue estimator or learner changes in this task.

### ECHO-003 — Implement Equations (9)–(11) local estimate

- Required reads: live equations; `src/echo_ert.py`, private queue/active state.
- Allowed writes: `src/echo_ert.py`, `tests/unit/test_echo_local_estimate.py`, task evidence.
- Execute: compute local service slots, residual active service, predecessor waiting, inclusive completion, ERT/lateness using remaining cycles where required.
- Command: `python3 -m pytest tests/unit/test_echo_local_estimate.py -q`.
- Pass: hand calculations for empty/active/multiple-predecessor queue exact; no deadline truncation; units consistent.
- Stop/rollback: do not reorder queues in this task.

### ECHO-004 — Implement Equations (12)–(16) outbound estimate

- Required reads: live equations; `src/echo_ert.py`, link-rate config, outbound state, next-boundary contract.
- Allowed writes: `src/echo_ert.py`, `tests/unit/test_echo_outbound_estimate.py`, task evidence.
- Execute: source residual/predecessor transmission, horizontal/vertical rate, inclusive transmission slots, explicit next-boundary admission term, completion/ERT/lateness.
- Command: `python3 -m pytest tests/unit/test_echo_outbound_estimate.py -q`.
- Pass: horizontal/cloud examples exact; +1 boundary accounted exactly once; no destination work omitted.
- Stop/rollback: do not approximate destination workload; ECHO-005 owns it.

### ECHO-005 — Implement Equations (17)–(25) destination model

- Required reads: live equations; public queues, runtime capacity, status model.
- Allowed writes: `src/echo_destination_model.py`, `src/echo_ert.py`, `tests/unit/test_echo_destination_model.py`, task evidence.
- Execute: remaining workload in cycles, active source-queue count, hypothetical admission, effective capacity, waiting/processing, destination completion; fresh/estimated load input interface without training LSTM yet.
- Command: `python3 -m pytest tests/unit/test_echo_destination_model.py -q`.
- Pass: units are cycles/cycles-per-slot; active queue count adjustment exact; zero/one/many active queues; no future information.
- Stop/rollback: destination queues remain FIFO and are not reordered here.

### ECHO-006 — Implement Equations (26)–(28) history/LSTM inputs

- Required reads: live equations; `src/environment/runtime_model.py`; current load/history code.
- Allowed writes: `src/echo_load_forecast.py`, `src/echo_status.py`, `tests/unit/test_echo_load_history.py`, task evidence.
- Execute: fixed ordered history, freshness timestamp/status, stale/missing flag, training target record, deterministic zero/bootstrap behavior; no model fitting yet.
- Command: `python3 -m pytest tests/unit/test_echo_load_history.py -q`.
- Pass: W/history order exact; fresh data selected over prediction; stale/missing paths explicit; no evaluation data enters training store.
- Stop/rollback: neural architecture/optimizer belongs to ECHO-016.

### ECHO-007 — Implement Equation (29) local queue ERT ordering

- Required reads: live equation/tie rules; `src/echo_queue_ordering.py`, private queue.
- Allowed writes: `src/echo_queue_ordering.py`, `tests/unit/test_echo_local_queue_ordering.py`, task evidence.
- Execute: freeze active head; construct waiting order position-by-position; choose smallest nonnegative ERT, otherwise minimum lateness; arrival/stable ID final tie; count candidate evaluations.
- Command: `python3 -m pytest tests/unit/test_echo_local_queue_ordering.py -q`.
- Pass: hand queue order exact; all-late fallback exact; active task untouched; evaluations equal q(q+1)/2.
- Stop/rollback: HOODIE FIFO path must remain unchanged.

### ECHO-008 — Implement Equation (30) outbound ERT ordering

- Required reads: live equation; `src/echo_queue_ordering.py`, offloading queue, destination model.
- Allowed writes: `src/echo_queue_ordering.py`, `tests/unit/test_echo_outbound_queue_ordering.py`, task evidence.
- Execute: freeze active transmission; include cumulative source transmission and destination workload/service for provisional positions; same feasible/lateness/tie rules; preserve stored destination.
- Command: `python3 -m pytest tests/unit/test_echo_outbound_queue_ordering.py -q`.
- Pass: mixed destinations and all-late scenarios match hand calculations; one source transmitter invariant; O(q²) count.
- Stop/rollback: do not create one physical queue/transmitter per destination.

### ECHO-009 — Implement 32-position canonical action space

- Required reads: live action/scalability section; `src/echo_action_space.py`, `src/echo_types.py`, topology.
- Allowed writes: those files, `tests/unit/test_echo_canonical_action_space.py`, task evidence.
- Execute: index 0 local, 1–30 horizontal positions, 31 cloud; mask absent/self/disconnected positions physically; separate checkpoint per tested N while tensor shape remains 32.
- Command: `python3 -m pytest tests/unit/test_echo_canonical_action_space.py -q`.
- Pass: exact 32 outputs for N=10/15/20/25/30; mapping stable; padded nodes masked; cloud final.
- Stop/rollback: do not collapse to N+2 runtime-varying tensor dimensions.

### ECHO-010 — Implement Equations (42)–(46) mask/fallback

- Required reads: live mask/effective-set equations; candidate estimates/action space.
- Allowed writes: `src/echo_action_mask.py`, `src/echo_action_space.py`, `tests/unit/test_echo_deadline_mask.py`, task evidence.
- Execute: intersect physical candidates with ERT≥0; if empty choose singleton minimum-lateness candidate with deterministic tie; apply identical mask to exploration, exploitation, and target selection.
- Command: `python3 -m pytest tests/unit/test_echo_deadline_mask.py -q`.
- Pass: feasible set exact; fallback singleton exact; never all-zero on arrival; source/self/disconnected absent; same mask object/hash across selection paths.
- Stop/rollback: no mask behavior may leak into HOODIE/baselines.

### ECHO-011 — Implement Equations (47)–(50) pending records

- Required reads: live equations; task lifecycle, action/mask/estimate types.
- Allowed writes: `src/echo_pending.py`, `src/echo_types.py`, ECHO adapter, `tests/unit/test_echo_pending_records.py`, task evidence.
- Execute: at decision store source, state, action, mask, predicted candidates/risk, decision slot, task ID, destination; attach physical outcome later; prohibit duplicate/open record corruption.
- Command: `python3 -m pytest tests/unit/test_echo_pending_records.py -q`.
- Pass: one record per decision; task identity preserved; resolution does not create transition itself; terminal cleanup complete.
- Stop/rollback: interval construction belongs to ECHO-014.

### ECHO-012 — Implement Equations (51)–(54) normalized state

- Required reads: live state equations; `src/echo_types.py`, candidate/action/history modules, runtime snapshot.
- Allowed writes: `src/echo_state.py`, `configs/authoritative/echo_state_schema.json`, `tests/unit/test_echo_state_contract.py`, task evidence.
- Execute: fixed 30-destination feature blocks plus task/queue/residual/load/LSTM/min-ERT/candidate-ERT/mask features; explicit occupancy; symmetric ERT clipping; fixed normalization bounds; zero task/candidate features on no arrival while queue/load remain live.
- Command: `python3 -m pytest tests/unit/test_echo_state_contract.py -q`.
- Pass: exact dimension/order/schema; bounded finite values; no future leakage; no-arrival distinction; mask/candidate positions align with 32 actions.
- Stop/rollback: unresolved normalization bound blocks completion.

### ECHO-013 — Implement Equations (55)–(58) task reward

- Required reads: live reward equations; task resolution/pending records.
- Allowed writes: `src/echo_reward.py`, ECHO adapter, `tests/unit/test_echo_reward.py`, task evidence.
- Execute: realized system duration, predicted-risk indicator from decision-time estimates, realized-drop indicator, `-duration - λ_R risk - λ_D drop`; reward only at physical resolution.
- Command: `python3 -m pytest tests/unit/test_echo_reward.py -q`.
- Pass: success/risk/drop combinations exact; decision-time risk immutable; no reward before resolution; one reward per task.
- Stop/rollback: do not change HOODIE reward code.

### ECHO-014 — Implement Equations (59)–(60) event intervals

- Required reads: live interval equations; `src/training/event_smdp.py`, pending/reward events.
- Allowed writes: `src/training/event_smdp.py`, `tests/unit/test_event_smdp_interval_contract.py`, task evidence.
- Execute: one open interval per source EA; add each resolving task reward with within-interval discount; close only at next actual decision of same EA or terminal T+1; emit one non-overlapping transition; preserve Δ.
- Command: `python3 -m pytest tests/unit/test_event_smdp_interval_contract.py -q`.
- Pass: multiple rewards aggregate correctly; other-EA decisions do not close interval; no task-level overlapping transition; terminal interval exact; embedded state pair valid.
- Stop/rollback: current tests are insufficient unless they cover boundary-before-decision ownership.

### ECHO-015 — Implement Equations (61)–(67) masked DDQL

- Required reads: live equations; replay buffer, DQN utilities, state/action/mask/interval modules.
- Allowed writes: `src/agents/echo_model.py`, `src/agents/echo_agent.py`, `src/agents/replay_buffer.py`, `src/agents/double_dqn.py`, `src/agents/target_network.py`, `tests/unit/test_echo_masked_ddql.py`, task evidence.
- Execute: dueling value/advantage with 32 outputs; mean advantage; online masked argmax, target evaluation, `γ^Δ`, terminal mask, optimizer, target copy, epsilon exploration only inside mask.
- Command: `python3 -m pytest tests/unit/test_echo_masked_ddql.py -q`.
- Pass: hand target exact; masked high-Q action never selected; target no gradient; finite update; checkpoint round-trip; separate agent/checkpoint per EA/N as specified.
- Stop/rollback: no heuristic Q fallback in authoritative ECHO learner.

### ECHO-016 — Implement fresh/stale status and LSTM training

- Required reads: live LSTM section; `src/echo_load_forecast.py`, `src/echo_status.py`, state/model/training config.
- Allowed writes: those files, `src/agents/echo_load_lstm.py`, `tests/unit/test_echo_load_lstm.py`, task evidence.
- Execute: supervised forecasting loss, separate optimizer/state, training-only histories, freshness threshold, fresh override, stale/missing prediction, deterministic checkpoint, evaluation guard.
- Command: `python3 -m pytest tests/unit/test_echo_load_lstm.py -q`.
- Pass: fresh path ignores prediction; stale/missing uses prediction; loss/gradients finite; no held-out trace IDs in fit data; checkpoint reproducible.
- Stop/rollback: do not jointly hide forecasting loss inside Q loss unless current source explicitly requires it.

### ECHO-017 — Implement isolated ECHO-NoLSTM

- Required reads: live ablation definition; ECHO adapter/status/state/model.
- Allowed writes: `src/policies/echo_no_lstm.py`, `src/evaluation/policy_registry.py`, `tests/integration/test_echo_no_lstm_isolation.py`, task evidence.
- Execute: create ablation identical to ECHO except load estimate replacement defined by source; same physical kernel, state ordering, action/mask, reward, learner, budgets.
- Command: `python3 -m pytest tests/integration/test_echo_no_lstm_isolation.py -q`.
- Pass: differential trace shows only load-estimation fields/actions derived from them differ; no hidden parameter/budget difference.
- Stop/rollback: do not classify it as a generic heuristic baseline.

### ECHO-018 — Implement exact Algorithm 1/2 chronology

- Required reads: source-locked 23/12-line algorithms; `src/environment/evaluation_gym_adapter.py`, `src/training/training_loop.py`, ECHO adapter/interval logic.
- Allowed writes: those files, `tests/integration/test_echo_algorithm_order.py`, `tests/integration/test_echo_boundary_reward_ownership.py`, task evidence.
- Execute: implement boundary chronology in Section 3.3; process resolution events before new decision closure; then decisions; schedule/service; terminal T+1; inference same physical order without learning and uses highest masked Q.
- Commands: `python3 -m pytest tests/integration/test_echo_algorithm_order.py tests/integration/test_echo_boundary_reward_ownership.py -q`.
- Pass: event trace matches every numbered algorithm line; boundary reward belongs to old interval; no same-slot double service; inference/training physical order identical.
- Stop/rollback: this task may not change equation formulas; formula defects reopen owning ECHO task.

### ECHO-019 — Run deterministic ECHO unit/smoke suite

- Required reads: all Phase-2 tests; source lock; frozen base.
- Allowed writes: `tests/integration/test_echo_hand_trace.py`, `configs/experiments/echo_smoke.yaml`, `scripts/smoke/run_echo_smoke.py`, `artifacts/smoke/echo_v4/*`, task evidence; no runtime code.
- Execute: 2-EA+cloud hand trace with local/horizontal/cloud, contention, feasible/late candidates, mask/fallback, ERT reorder, waiting expiration, active late outcome; short finite learning smoke and checkpoint reload.
- Command: `python3 -m pytest tests/unit/test_echo_equations_01_08.py tests/unit/test_echo_local_estimate.py tests/unit/test_echo_outbound_estimate.py tests/unit/test_echo_destination_model.py tests/unit/test_echo_load_history.py tests/unit/test_echo_local_queue_ordering.py tests/unit/test_echo_outbound_queue_ordering.py tests/unit/test_echo_canonical_action_space.py tests/unit/test_echo_deadline_mask.py tests/unit/test_echo_pending_records.py tests/unit/test_echo_state_contract.py tests/unit/test_echo_reward.py tests/unit/test_event_smdp_interval_contract.py tests/unit/test_echo_masked_ddql.py tests/unit/test_echo_load_lstm.py tests/integration/test_echo_no_lstm_isolation.py tests/integration/test_echo_algorithm_order.py tests/integration/test_echo_boundary_reward_ownership.py tests/integration/test_echo_hand_trace.py -q && python3 scripts/smoke/run_echo_smoke.py --config configs/experiments/echo_smoke.yaml --output artifacts/smoke/echo_v4`.
- Pass: all tests pass; hand trace matches manual table; finite metrics; all three routes; no masked action; accounting exact; checkpoint reload deterministic.
- Stop/rollback: failures reopen the owning ECHO task; ECHO-019 cannot patch runtime code.

### ECHO-020 — Produce equation coverage and paired pilot gate

- Required reads: source audit, all Phase-2 evidence, frozen base, ECHO/HOODIE smoke.
- Allowed writes: `scripts/audit/build_echo_coverage.py`, `artifacts/audits/echo_equation_coverage.{md,json}`, `configs/experiments/echo_pilot.yaml`, `scripts/pilot/run_echo_pilot.py`, `artifacts/pilot/echo_v4/*`, task evidence.
- Execute: map each equation/algorithm line to code symbol/test/evidence; run paired ECHO/HOODIE/ECHO-NoLSTM pilot on same traces; check route, mask, reward, replay, accounting, numerical stability.
- Commands: `python3 scripts/audit/build_echo_coverage.py --source-audit artifacts/audits/echo_live_revision_audit.md --output artifacts/audits/echo_equation_coverage.json && python3 scripts/pilot/run_echo_pilot.py --config configs/experiments/echo_pilot.yaml --output artifacts/pilot/echo_v4`.
- Pass: 69/69 coverage rows have code+test; no unresolved S0/S1; paired trace hashes equal; pilot finite; no scientific superiority claim.
- Stop/rollback: any uncovered equation or invariant blocks EVAL-001.

### EVAL-001 — Freeze evaluation/figure manifests and schemas

- Required reads: `research/ECHO_evaluation_spec.md`, source lock, pilot evidence.
- Allowed writes: `experiments/manifest.yaml`, `experiments/figure_manifest.yaml`, `experiments/schemas/{run_manifest,task_log,episode_metrics,seed_metrics,panel_values,artifact_manifest}.schema.json`, `src/evaluation/config.py`, `tests/unit/test_evaluation_manifests.py`, task evidence.
- Execute: encode all 15 panels, exact methods/x/fixed values, training/reuse rule, seeds, 200 held-out episodes, metrics, CI, raw/export paths; protect held-out data.
- Command: `python3 -m pytest tests/unit/test_evaluation_manifests.py -q`.
- Pass: 15 unique panels; no placeholder; Figure 6 timeout 20 slots/2s; Figure 7(c/f) swept; Figure 8 exact; schemas validate.
- Stop/rollback: unresolved retraining/checkpoint rule blocks task rather than being guessed.

### EVAL-002 — Generate immutable paired trace bank

- Required reads: immutable trace protocol, evaluation manifest.
- Allowed writes: `scripts/evaluation/build_trace_bank.py`, `tests/integration/test_trace_bank.py`, `artifacts/evaluation/trace_bank/*`, task evidence.
- Execute: generate every required seed/scenario trace once; canonical JSON/JSONL; SHA manifest; read-only consumption; no regeneration by methods.
- Commands: `python3 -m pytest tests/integration/test_trace_bank.py -q && python3 scripts/evaluation/build_trace_bank.py --manifest experiments/manifest.yaml --output artifacts/evaluation/trace_bank`.
- Pass: expected job/scenario/seed count; hashes stable; all methods load same bytes; drain/arrival semantics valid.
- Stop/rollback: never overwrite an existing trace ID with different bytes.

### EVAL-003 — Freeze config/topology/checkpoint lineage

- Required reads: trace bank, frozen base, ECHO pilot checkpoints, manifests.
- Allowed writes: `scripts/evaluation/build_lineage_manifest.py`, `artifacts/evaluation/lineage/*`, `tests/unit/test_lineage_manifest.py`, task evidence.
- Execute: map each planned run to config hash, topology hash, trace hash, method/code SHA, training checkpoint hash, source revisions, software environment.
- Commands: `python3 -m pytest tests/unit/test_lineage_manifest.py -q && python3 scripts/evaluation/build_lineage_manifest.py --manifest experiments/manifest.yaml --output artifacts/evaluation/lineage`.
- Pass: no missing hash; each run ID unique/resumable; checkpoint N/method/scenario compatible.
- Stop/rollback: no mutable “latest checkpoint” references.

### EVAL-004 — Validate all method adapters on common inputs

- Required reads: policy registry, shared kernel, lineages, trace bank.
- Allowed writes: `tests/integration/test_all_method_common_inputs.py`, `artifacts/evaluation/adapter_validation/*`, task evidence; policy adapters only if validation finds a task-owned defect, otherwise stop/reopen ECHO/BASE task.
- Execute: run one deterministic trace for ECHO, ECHO-NoLSTM, HOODIE, RO, FLC, VO, HO, BCO, MLEO; compare task/config/topology hashes and physical accounting.
- Command: `python3 -m pytest tests/integration/test_all_method_common_inputs.py -q`.
- Pass: identical inputs; method-specific behavior only; no training for heuristics; no ECHO import in HOODIE/heuristics.
- Stop/rollback: runtime fix requires reopening owning implementation task.

### EVAL-005 — Measure throughput and freeze shard budget

- Required reads: validated adapters, manifest, available compute.
- Allowed writes: `scripts/evaluation/benchmark_throughput.py`, `artifacts/evaluation/compute_budget.{json,md}`, `experiments/shard_plan.yaml`, task evidence.
- Execute: benchmark representative training/evaluation jobs; estimate total jobs, CPU/GPU/RAM/storage/wall time; define shard IDs, checkpoint frequency, completion marker, resume/rerun rules.
- Command: `python3 scripts/evaluation/benchmark_throughput.py --manifest experiments/manifest.yaml --output artifacts/evaluation/compute_budget.json --shards experiments/shard_plan.yaml`.
- Pass: estimate based on measured throughput; full matrix feasible or explicitly blocked; no full job launched.
- Stop/rollback: infeasible budget blocks EVAL-006 pending approved matrix reduction.

### EVAL-006 — Run Figure-5 validation sweeps

- Required reads: Figure-5 manifest, trace bank, shard plan.
- Allowed writes: `configs/experiments/figure5_sweep.yaml`, `scripts/evaluation/run_figure5_sweep.py`, `artifacts/evaluation/figure5/*`, task evidence.
- Execute: learning rates `{1e-9,5e-9,1e-8,1e-7,5e-7,7e-7}` and gamma `{.2,.4,.6,.8,.99}` with 5000 training episodes or exact source-locked budget; validation-only selection; preserve all seeds/logs/checkpoints.
- Command: `python3 scripts/evaluation/run_figure5_sweep.py --config configs/experiments/figure5_sweep.yaml --output artifacts/evaluation/figure5`.
- Pass: all points complete/resumable; selection rule applied only to validation; no held-out traces used; finite metrics.
- Stop/rollback: do not choose by final-test performance.

### EVAL-007 — Train equal-budget final method checkpoints

- Required reads: selected hyperparameters, manifest, shard plan, trace bank.
- Allowed writes: `configs/experiments/final_training.yaml`, `scripts/evaluation/run_final_training.py`, `artifacts/checkpoints/final/*`, `artifacts/raw_logs/training/*`, task evidence.
- Execute: train required ECHO/HOODIE/ECHO-NoLSTM checkpoints with equal declared budgets and separate seeds/N/scenarios; heuristics excluded; immutable completion markers.
- Command: `python3 scripts/evaluation/run_final_training.py --config configs/experiments/final_training.yaml --output artifacts/checkpoints/final`.
- Pass: every required checkpoint has config/source/code/trace lineage; no budget mismatch; no NaN/Inf; resume reproduces results.
- Stop/rollback: failed shard reruns only from last verified checkpoint with same hashes.

### EVAL-008 — Run 10×200 held-out paired evaluation

- Required reads: final checkpoints, held-out trace bank, evaluation manifest.
- Allowed writes: `configs/experiments/heldout_evaluation.yaml`, `scripts/evaluation/run_heldout_evaluation.py`, `artifacts/raw_logs/task_level/*`, `artifacts/raw_logs/episode_level/*`, `artifacts/evaluation/run_manifests/*`, task evidence.
- Execute: for every reported point/method, 10 fixed seeds × 200 held-out episodes; same trace per seed/point; log task actions, masks, ERT, outcomes, rewards, Δ, hashes.
- Command: `python3 scripts/evaluation/run_heldout_evaluation.py --config configs/experiments/heldout_evaluation.yaml --output artifacts/raw_logs`.
- Pass: full expected job count; no training/optimizer call; immutable run manifests; all outputs schema-valid.
- Stop/rollback: missing/partial shard is not silently averaged.

### EVAL-009 — Validate generated/completed/dropped accounting

- Required reads: EVAL-008 raw logs/manifests.
- Allowed writes: `scripts/evaluation/audit_accounting.py`, `tests/unit/test_evaluation_accounting.py`, `artifacts/evaluation/audits/accounting.*`, task evidence.
- Execute: generated=successful+dropped; one terminal outcome; no duplicate/missing task; horizon/drain accounting; pooled counts.
- Commands: `python3 -m pytest tests/unit/test_evaluation_accounting.py -q && python3 scripts/evaluation/audit_accounting.py --input artifacts/raw_logs --output artifacts/evaluation/audits/accounting.json`.
- Pass: zero invariant violation across all runs.
- Stop/rollback: any violation blocks aggregation and reopens owning runtime task.

### EVAL-010 — Validate no masked ECHO action

- Required reads: EVAL-008 ECHO logs.
- Allowed writes: `scripts/evaluation/audit_masks.py`, `tests/unit/test_evaluation_mask_audit.py`, `artifacts/evaluation/audits/masks.*`, task evidence.
- Execute: verify selected action mask=1, physical legality, fallback identity, same decision-time mask used for exploration/exploitation/target metadata.
- Commands: `python3 -m pytest tests/unit/test_evaluation_mask_audit.py -q && python3 scripts/evaluation/audit_masks.py --input artifacts/raw_logs/task_level --output artifacts/evaluation/audits/masks.json`.
- Pass: zero masked/invalid/disconnected/self action.
- Stop/rollback: any violation blocks aggregation and reopens ECHO-009/010/015/018.

### EVAL-011 — Validate trace/config/topology/checkpoint hashes

- Required reads: run/lineage manifests and raw logs.
- Allowed writes: `scripts/evaluation/audit_lineage.py`, `tests/unit/test_evaluation_lineage_audit.py`, `artifacts/evaluation/audits/lineage.*`, task evidence.
- Execute: cross-check every row/run against expected trace, config, topology, checkpoint, source, and code hashes; verify paired methods share inputs.
- Commands: `python3 -m pytest tests/unit/test_evaluation_lineage_audit.py -q && python3 scripts/evaluation/audit_lineage.py --lineage artifacts/evaluation/lineage --runs artifacts/evaluation/run_manifests --output artifacts/evaluation/audits/lineage.json`.
- Pass: zero missing/mismatched hash; no test checkpoint trained on held-out trace.
- Stop/rollback: mismatched run is excluded and rerun; never relabel it.

### EVAL-012 — Aggregate seed metrics and 95% CIs

- Required reads: all three PASS audits, raw logs, figure manifest.
- Allowed writes: `src/evaluation/statistics.py`, `scripts/evaluation/aggregate_results.py`, `tests/unit/test_evaluation_statistics.py`, `artifacts/metrics/{seed_level,panel_level,confidence_intervals}/*`, task evidence.
- Execute: task→episode→seed aggregation; negative-delay convention; pooled drop counts before seed ratio; seed-level mean and 95% CI; no episode-level pseudo-replication.
- Commands: `python3 -m pytest tests/unit/test_evaluation_statistics.py -q && python3 scripts/evaluation/aggregate_results.py --manifest experiments/figure_manifest.yaml --input artifacts/raw_logs --output artifacts/metrics`.
- Pass: every panel point has 10 seed rows and CI; formulas unit-tested; results regenerate byte-identically.
- Stop/rollback: do not impute missing seeds or average partial jobs.

### FIG-001 — Render Figure 4 topology

- Required reads: frozen topology artifacts/config.
- Allowed writes: `scripts/figures/render_figure4.py`, `artifacts/figures/vector/figure4.svg`, `artifacts/figures/vector/figure4.pdf`, `artifacts/figures/png_300dpi/figure4.png`, `artifacts/figures/panel_exports/figure4.csv`, manifest/evidence.
- Execute: render actual 20-EA topology using deterministic coordinates; no hand-drawn edges.
- Command: `python3 scripts/figures/render_figure4.py --topology configs/authoritative/hoodie_topology.json --output artifacts/figures`.
- Pass: edge list equals topology hash; SVG/PDF and 300-dpi PNG exist; repeated render hashes equal.
- Stop/rollback: no visual-only correction that changes data.

### FIG-002 — Render Figure 5(a–b)

- Required reads: EVAL-006 raw/aggregated sweep outputs.
- Allowed writes: `scripts/figures/render_figure5.py`, Figure-5 CSV/vector/PNG/manifest files, task evidence.
- Execute: plot average reward vs learning rate and gamma from retained CSV; show seed CI where specified; label exact selected values.
- Command: `python3 scripts/figures/render_figure5.py --input artifacts/evaluation/figure5 --output artifacts/figures`.
- Pass: 2 panels and all configured points; plot values equal CSV; vector + 300-dpi PNG lineage.
- Stop/rollback: no manually entered y-values.

### FIG-003 — Render Figure 6(a–e)

- Required reads: EVAL-012 panel metrics and Figure-6 manifest.
- Allowed writes: `scripts/figures/render_figure6.py`, Figure-6 panel CSV/vector/PNG/manifest files, task evidence.
- Execute: five panels with exact P, capacity, N, traffic, and rate-profile series; default timeout 20 slots/2 s; CIs from seed metrics.
- Command: `python3 scripts/figures/render_figure6.py --input artifacts/metrics --manifest experiments/figure_manifest.yaml --output artifacts/figures`.
- Pass: 5 panels; x/series definitions exact; every plotted point traceable to 10 seed rows.
- Stop/rollback: no smoothing/interpolation unless explicitly in manifest.

### FIG-004 — Render Figure 7(a–f)

- Required reads: EVAL-012 metrics and Figure-7 manifest.
- Allowed writes: `scripts/figures/render_figure7.py`, Figure-7 panel CSV/vector/PNG/manifest files, task evidence.
- Execute: delay panels a–c and pooled-drop panels d–f; exact fixed/swept timeout rules; all comparison methods; seed CIs.
- Command: `python3 scripts/figures/render_figure7.py --input artifacts/metrics --manifest experiments/figure_manifest.yaml --output artifacts/figures`.
- Pass: 6 panels; negative-delay and pooled-drop conventions preserved; no timeout contradiction.
- Stop/rollback: do not mix per-episode average drop ratios with pooled counts.

### FIG-005 — Render Figure 8

- Required reads: EVAL-012 ECHO/ECHO-NoLSTM metrics.
- Allowed writes: `scripts/figures/render_figure8.py`, Figure-8 CSV/vector/PNG/manifest files, task evidence.
- Execute: N=20, P=.3, timeout 1s, episodes 0–3000; selected LR/gamma; seed-level convergence/final delay/stability evidence.
- Command: `python3 scripts/figures/render_figure8.py --input artifacts/metrics --manifest experiments/figure_manifest.yaml --output artifacts/figures`.
- Pass: exact two methods/series; values equal CSV; no hidden smoothing; 300-dpi/vector outputs.
- Stop/rollback: no claim that LSTM is superior unless statistics support it.

### FIG-006 — Validate all vector/PNG exports and lineage

- Required reads: all figure artifacts/manifests/panel CSVs.
- Allowed writes: `scripts/figures/validate_figure_exports.py`, `tests/unit/test_figure_lineage.py`, `artifacts/figures/figure_lineage_index.json`, task evidence.
- Execute: verify 15 panels, CSV→plot equality, SVG/PDF presence, PNG 300 dpi, hashes, source run IDs, labels/units.
- Commands: `python3 -m pytest tests/unit/test_figure_lineage.py -q && python3 scripts/figures/validate_figure_exports.py --figures artifacts/figures --output artifacts/figures/figure_lineage_index.json`.
- Pass: 15/15 panels valid; no missing lineage; deterministic regeneration.
- Stop/rollback: invalid panel reopens its FIG task.

### REPORT-001 — Write final HOODIE reproduction report

- Required reads: freeze manifest, BASE-022 evidence, base tests/smoke.
- Allowed writes: `docs/reports/HOODIE_REPRODUCTION_REPORT.md`, `artifacts/reports/hoodie_reproduction_lineage.json`, task evidence.
- Execute: describe exact base mechanics, evidence, reproduced trends, deviations, limitations, frozen SHA; no ECHO results.
- Command: `python3 - <<'PY'
from pathlib import Path
p=Path('docs/reports/HOODIE_REPRODUCTION_REPORT.md')
assert p.exists() and 'Lineage' in p.read_text()
print('HOODIE report present')
PY`.
- Pass: every claim cites raw/test/freeze evidence; no unsupported exact-match claim.
- Stop/rollback: report cannot compensate for failed base reproduction.

### REPORT-002 — Write final ECHO implementation report

- Required reads: source/coverage audits, ECHO-020 pilot, all Phase-2 evidence.
- Allowed writes: `docs/reports/ECHO_IMPLEMENTATION_REPORT.md`, `artifacts/reports/echo_implementation_lineage.json`, task evidence.
- Execute: equation/algorithm-to-code map, slot chronology, state/mask/reward/interval/DDQL/LSTM, isolation, tests, limitations; no final evaluation superiority claim.
- Command: `python3 - <<'PY'
from pathlib import Path
p=Path('docs/reports/ECHO_IMPLEMENTATION_REPORT.md')
assert p.exists() and 'Equations (1)–(67)' in p.read_text()
print('ECHO report present')
PY`.
- Pass: 69 source rows linked; current revisions and frozen base recorded; no historical source cited as authority.
- Stop/rollback: uncovered equation blocks report completion.

### REPORT-003 — Write final evaluation/figure report

- Required reads: EVAL-012 metrics/audits, FIG-006 lineage, run manifests.
- Allowed writes: `docs/reports/ECHO_EVALUATION_REPORT.md`, `artifacts/reports/evaluation_lineage.json`, task evidence.
- Execute: methods, budgets, held-out protocol, statistics, 15 panels, invariant results, limitations; derive every number from preserved artifacts.
- Command: `python3 - <<'PY'
from pathlib import Path
p=Path('docs/reports/ECHO_EVALUATION_REPORT.md')
assert p.exists() and '15 panels' in p.read_text()
print('evaluation report present')
PY`.
- Pass: all numerical claims have run/CSV/figure lineage; no missing seed; no causal/absolute claim beyond evidence.
- Stop/rollback: failed audit or invalid figure blocks report.

### CLEAN-002 — Mark stale artifacts superseded and archive copies

- Required reads: three final reports/lineage indexes and CLEAN-001 classification.
- Allowed writes: `scripts/cleanup/archive_superseded_artifacts.py`, `artifacts/archive/superseded/*`, `artifacts/archive/archive_manifest.json`, classification/index files, task evidence.
- Execute: copy/move only artifacts proven replaced; preserve original hashes and replacement references; never delete; leave canonical final paths untouched.
- Command: `python3 scripts/cleanup/archive_superseded_artifacts.py --classification artifacts --archive artifacts/archive/superseded --manifest artifacts/archive/archive_manifest.json`.
- Pass: every archived item has old hash, new canonical replacement, reason, timestamp; no authoritative raw log/checkpoint removed.
- Stop/rollback: ambiguous item remains in place and is listed unresolved.

### CLEAN-003 — Remove canonical-path ambiguity without permanent deletion

- Required reads: archive manifest, repository references, final artifact index candidates.
- Allowed writes: import/reference files that point to legacy artifacts, `artifacts/archive/path_redirects.json`, docs/index files, task evidence; no source algorithm changes.
- Execute: update references to canonical files; add redirect map; verify no final report points to legacy figures/runs; keep archived bytes.
- Command: `python3 - <<'PY'
import json
from pathlib import Path
p=Path('artifacts/archive/path_redirects.json')
assert p.exists(); json.loads(p.read_text()); print('redirect map valid')
PY`.
- Pass: one canonical path per artifact type; all redirects resolve; no permanent deletion.
- Stop/rollback: code behavior change is out of scope and requires PLAN_CHANGE_REQUIRED.

### HANDOFF-001 — Produce final artifact index and exact rerun commands

- Required reads: all final manifests/reports/figures/archive maps and tested SHAs.
- Allowed writes: `artifacts/FINAL_ARTIFACT_INDEX.md`, `artifacts/FINAL_ARTIFACT_INDEX.json`, `scripts/reproduce_all.sh`, `docs/reports/FINAL_HANDOFF.md`, task evidence.
- Execute: enumerate source locks, configs, topology, traces, checkpoints, raw logs, metrics, figures, reports, hashes, environment, exact commands; script performs validation/reproduction in dependency order and refuses hash mismatch.
- Command: `bash scripts/reproduce_all.sh --verify-only`.
- Pass: index paths/hashes resolve; verify-only succeeds from clean checkout with declared dependencies; no hidden manual step; final report distinguishes reproduced facts and limitations.
- Stop/rollback: missing artifact/hash blocks handoff; do not omit it.

---

## 7. Evaluation and figure constants

- Figure 4: actual default 20-EA topology.
- Figure 5(a): learning rate `{10^-9, 5×10^-9, 10^-8, 10^-7, 5×10^-7, 7×10^-7}`.
- Figure 5(b): gamma `{0.2, 0.4, 0.6, 0.8, 0.99}`.
- Figure 6(a): reward vs P, P `{.1,.3,.5,.7,.9}`, N `{10,15,20}`.
- Figure 6(b): local/horizontal/cloud action counts vs P, N=20.
- Figure 6(c): reward vs EA capacity `{4,5,6,7,8,9}` GHz, N `{10,15,20}`.
- Figure 6(d): reward vs N `{10,15,20,25,30}`; moderate `(1–3 Mbits,P=.5)`, heavy `(2–5,P=.7)`, extreme `(3–7,P=.9)`.
- Figure 6(e): reward vs N; balanced `(R_H=10,R_V=30)`, horizontal-centric `(20,20)`, vertical-centric `(5,40)` Mbps.
- Figure 6 default timeout: 20 slots = 2 seconds.
- Figure 7(a): delay vs P `{.1,.3,.5,.7,.9}`, timeout 10 s.
- Figure 7(b): delay vs capacity `{3,4,5,6,7}` GHz, timeout 10 s.
- Figure 7(c): delay vs timeout `{9.6,9.8,10.0,10.2,10.4}` s.
- Figure 7(d): pooled drop ratio vs P, timeout 2 s.
- Figure 7(e): pooled drop ratio vs capacity, timeout 2 s.
- Figure 7(f): pooled drop ratio vs timeout `{1.6,1.8,2.0,2.2,2.4}` s.
- Figure 8: ECHO vs ECHO-NoLSTM; N=20, P=.3, timeout 1 s, episodes 0–3000.
- Comparison methods: ECHO, HOODIE, RO, FLC, VO, HO, BCO, MLEO; ECHO-NoLSTM only where specified.
- Every reported point: 10 fixed seeds × 200 held-out paired episodes.
- Confidence intervals are computed across seed-level metrics.
- Average delay preserves the approved negative-delay convention.
- Drop ratio pools task counts within each seed before cross-seed summaries.

---

## 8. Exact autonomous executor prompt

```text
You are the task executor for repository hadifarajvand/hoodie_sim_v2.

The sole execution authority is:
artifacts/reports/ECHO_MASTER_EXECUTION_PLAN.md
version ECHO-MEP-v4.0.

Execute exactly one task card and nothing else.

Protocol:
1. Read the entire plan.
2. Record HEAD and clean working-tree status.
3. Select the earliest READY task. SRC-001 has priority; when live source access is unavailable, record BLOCKED_EXTERNAL and select BASE-001.
4. Create branch task/<lowercase-task-id>.
5. Read only required files and edit only Allowed writes.
6. Perform the ordered operations exactly.
7. Create the mandatory task evidence package.
8. Run the exact listed command without substitution or suppressed failures.
9. Verify every acceptance criterion.
10. Commit with `<TASK-ID>: <exact task title>`.
11. Stop. Do not merge, push to main, edit the master plan, or start another task.

When an unlisted file is required, stop with PLAN_CHANGE_REQUIRED.
When HEAD changes, stop with STALE_BRANCH.
When authority is missing, stop with BLOCKED_EXTERNAL.
Never invent paper values, source text, results, or test evidence.
```

---

## 9. Dashboard and next action

| Metric | Value |
|---|---|
| Task count | 73 |
| Phase totals | 6 / 23 / 20 / 12 / 12 |
| Verified complete | 5 |
| Ready | 2 |
| Blocked | 66 |
| First task | `SRC-001` |
| Fallback first task when external source unavailable | `BASE-001` |
| First ECHO task | `ECHO-001`, only after `SRC-001` + `FREEZE-001` |
| Full evaluation gate | `ECHO-020` |
| Final completion gate | `HANDOFF-001` |
| Permanent deletion allowed | No |
| Direct push/merge by executor | No |

The plan is finalized. The next executor must run `SRC-001` only; when source access is unavailable, it must record the external block and run `BASE-001` only.
