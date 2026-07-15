# HOODIE Supported Execution Surface

Canonical supported surface contains only code needed to reproduce original HOODIE behavior and publication artifacts:

- `src/hoodie/`
- canonical simulation, topology, queue, physical, and domain modules under `src/`
- real DDQN learner and LSTM forecasting code
- delayed reward and transition ownership logic
- distributed learner code
- six baseline policies: FLC, RO, HO, VO, BCO, MLEO
- paired evaluation
- experiment runner and campaign orchestration for Figures 8–11
- dataset generation, reporting, rendering, and reproducibility verification

Outside supported surface:

- historical analysis batches not called by canonical CLI or campaign runner
- ECHO-era analysis modules
- legacy paper_default / terminal_exposure / scope-guard batches
- old main...HEAD gate tests
- archived history under `tests_historical/`

Historical code may remain in repository for provenance, but it is not part of publication-critical supported execution.
