# Tasks: Feature 090 HOODIE Paper-Faithful Simulation Rebuild

## Reference and Mapping

- [ ] T001 Read every file under `docs/hoodie/paper_simulation_reference/`.
- [ ] T002 Create mechanism-to-code mapping.
- [ ] T003 Identify reuse vs replacement areas in current codebase.
- [ ] T004 Add scope guard: no thesis method, no DCQ, no output-sync tuning.

## Runtime

- [ ] T010 Implement 110-slot episode runtime.
- [ ] T011 Implement 100 action slots plus 10 drain slots.
- [ ] T012 Implement Bernoulli arrivals per EA per action slot.
- [ ] T013 Implement task registry and pending lifecycle.
- [ ] T014 Implement task-size sampling and processing density.
- [ ] T015 Implement timeout in slots and seconds.
- [ ] T016 Emit runtime arrival/completion/drop diagnostics.

## Queues

- [ ] T020 Implement private queue waiting formula.
- [ ] T021 Implement private service and exit status.
- [ ] T022 Implement offloading queue waiting formula.
- [ ] T023 Implement horizontal and vertical transmission.
- [ ] T024 Implement offloading exit status.
- [ ] T025 Insert successful offloads into destination public queues.
- [ ] T026 Implement source-specific public queues.
- [ ] T027 Compute active public queue sets each slot.
- [ ] T028 Divide public CPU across active public queues.
- [ ] T029 Record public completion/drop status.

## State and Reward

- [ ] T030 Implement historical load matrix `L(t)`.
- [ ] T031 Implement public queue footprint vector.
- [ ] T032 Implement state snapshot records.
- [ ] T033 Implement delayed reward collection.
- [ ] T034 Link reward events to original state/action.
- [ ] T035 Emit state/reward validation report.

## Policies

- [ ] T040 Declare HOODIE mode: trained/substitute/interface-only.
- [ ] T041 Implement/verify RO.
- [ ] T042 Implement/verify FLC.
- [ ] T043 Implement/verify VO.
- [ ] T044 Implement/verify HO.
- [ ] T045 Implement/verify BCO.
- [ ] T046 Implement/verify MLEO total latency estimation.
- [ ] T047 Emit policy distinctness diagnostics.

## Training Boundary

- [ ] T050 Decide whether full training is implemented now.
- [ ] T051 If not, keep Figure 8/11 gated.
- [ ] T052 If training exists, emit training traces and epsilon/loss diagnostics.
- [ ] T053 If LSTM ablation exists, emit with/without LSTM traces.

## Figure 9

- [ ] T060 Generate Figure 9a from HOODIE validation.
- [ ] T061 Generate Figure 9b preserving probability groups.
- [ ] T062 Generate Figure 9c with CPU sweep.
- [ ] T063 Generate Figure 9d with N and traffic scenario sweep.
- [ ] T064 Generate Figure 9e with N and data-rate sweep.
- [ ] T065 Mark Figure 9 paper-faithful, partial, or gated.

## Figure 10

- [ ] T070 Generate 10a with P sweep and timeout 10 sec.
- [ ] T071 Generate 10b with CPU sweep and timeout 10 sec.
- [ ] T072 Generate 10c with timeout sweep 9.6-10.4 sec.
- [ ] T073 Generate 10d with P sweep and timeout 2 sec.
- [ ] T074 Generate 10e with CPU sweep and timeout 2 sec.
- [ ] T075 Generate 10f with timeout sweep 1.6-2.4 sec.
- [ ] T076 Validate independent policy runs.
- [ ] T077 Validate non-degenerate denominators.

## Reports

- [ ] T080 Generate mechanism coverage.
- [ ] T081 Generate runtime validation report.
- [ ] T082 Generate queue dynamics validation.
- [ ] T083 Generate state/reward validation.
- [ ] T084 Generate policy distinctness report.
- [ ] T085 Generate metric diagnostics.
- [ ] T086 Generate figure readiness report.
- [ ] T087 Generate final Feature 090 report.

## Validation

- [ ] T090 Run `git diff --check`.
- [ ] T091 Run existing Feature 089 tests for regression.
- [ ] T092 Run new Feature 090 unit tests.
- [ ] T093 Run new Feature 090 integration tests.
- [ ] T094 Run artifact generation.
- [ ] T095 Run artifact validation.
