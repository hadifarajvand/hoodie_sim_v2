# HOODIE Smoke Run Gap Analysis

## Run Result

- Branch: `100-hoodie-paper-base`
- Exit code: `1`
- Result: failed
- Failure mode: import error before simulator startup

The repository entrypoint failed immediately because `utils/__init__.py` imports `matplotlib.pyplot`, and the active Python environment does not have `matplotlib` installed.

## Evidence Generated

- `artifacts/runtime-audit-smoke/2026-06-05-223708/run_command.txt`
- `artifacts/runtime-audit-smoke/2026-06-05-223708/run_stdout.txt`
- `artifacts/runtime-audit-smoke/2026-06-05-223708/run_stderr.txt`
- `artifacts/runtime-audit-smoke/2026-06-05-223708/exit_code.txt`
- `artifacts/runtime-audit-smoke/2026-06-05-223708/run_manifest.json`
- `artifacts/runtime-audit-smoke/2026-06-05-223708/gap_analysis.json`

No `log_folder` output directory was created because the run never reached the point where the simulator could start.

## 1. Repository Transfer Status

This branch still looks like the legacy HOODIE implementation, not the paper-faithful runtime core rebuild target.

- The top-level code is organized around `environment/`, `decision_makers/`, `hyperparameters/`, and `utils/`.
- There is no dedicated `src/analysis/hoodie_paper_faithful_runtime/` package visible in the executed path.
- The structure reflects the original simulator stack, not the new phase-090 runtime contract.

## 2. Runtime Lifecycle

The runtime lifecycle is incomplete relative to the paper target.

- `environment/environment.py` derives `episode_time_end` from `episode_time + max(timeout_delay_maxs)`, which is not the requested explicit action-slot plus drain-slot structure.
- There is no explicit 100-action-slot phase followed by a drain phase.
- Completion and drop are only implicit in queue/task methods; there is no standalone lifecycle trace or delayed collection registry.

## 3. Topology and Action Legality

The current code uses adjacency-based action mapping, but not the paper contract.

- `environment/matchmaker.py` maps action indices to `[local_id] + offloading_servers`.
- That makes horizontal offloading legality adjacency-based in the legacy sense.
- The code does not clearly model the cloud as a distinct action-matrix node the way the 090-A contract requires.

## 4. Queues

The queue stack exists, but it is the legacy approximation, not the paper-faithful model.

- `environment/queues.py` provides `ProcessingQueue`, `OffloadingQueue`, and `PublicQueueManager`.
- Public CPU sharing is priority-weighted, not equal split across active queues.
- Timeout and drop handling exist, but status is not separated cleanly into queue exit slot versus final completion/drop outcome.
- Public queue behavior is aggregated per server, not explicitly source-specific with the requested diagnostics.

## 5. Reward Model

Reward handling is immediate and implicit.

- `Environment.step()` returns rewards every step.
- Reward provenance is not preserved in a delayed task-event registry.
- `tasks_dropped` is inferred from reward sign and magnitude rather than counted explicitly.

## 6. Task Generation

Task generation is partially aligned.

- `environment/task_generator.py` does implement Bernoulli arrivals.
- Generated task fields include size, timeout, priority, computational density, and drop penalty.
- The agent-visible state is much thinner than the paper target and does not expose the requested task record / arrival diagnostics model.

## 7. State Model and LSTM

This is a legacy DQN/LSTM agent design, not an auditable forecasting pipeline.

- `decision_makers/agent.py` contains the LSTM inside the Q-network policy.
- The state vector is assembled from task size, waiting times, and public queue lengths.
- There is no exported historical load matrix artifact.

## 8. Training Pipeline

Training machinery exists, but it does not justify paper-faithful Figure 8/9/10/11 claims.

- DQN, target network updates, replay memory, and epsilon decay are present in `decision_makers/agent.py`.
- That is training code, not proof of paper-level fidelity.
- The smoke run never reached this stage because the import failed first.

## 9. Official Baselines

The repository exposes multiple decision makers, but the paper baseline mapping is not validated.

- Available classes: `Agent`, `AllHorizontal`, `AllLocal`, `AllVertical`, `Random`, `RoundRobin`, `RuleBased`, `SingleAgent`.
- These are only rough proxies unless they are explicitly mapped and validated against the paper.
- HOODIE, RO, FLC, VO, HO, BCO, and MLEO are not explicitly proven by this run.

## 10. Validation and Figures

No figure-faithful claim is allowed from this smoke run.

- There is no successful execution evidence for a 200-episode validation harness.
- There is no figure-data export evidence in the smoke run.
- Figure 8, Figure 9, Figure 10, and Figure 11 readiness is not supported.

## Conclusion

- What ran successfully or failed: the current HOODIE entrypoint failed immediately on import because `matplotlib` is missing from the active Python environment.
- What evidence was generated: command capture, stdout/stderr capture, exit code, manifest, and gap-analysis artifacts under `artifacts/runtime-audit-smoke/2026-06-05-223708/`.
- What is currently paper-aligned: Bernoulli arrivals, queue-based runtime structure, adjacency-based action legality, and legacy DQN/LSTM machinery exist.
- What is still missing: explicit slot/drain runtime, delayed reward collection, traceable task lifecycle, equal active public-queue sharing, and auditable historical load exports.
- Recommended next implementation phase: fix environment reproducibility, then implement the paper-faithful runtime core before making any training or figure claims.
