# Paper to Code Mapping

## Environment and traffic

- Paper arrival process / Algorithm 1 -> `src/environment/traffic_generator.py`
- Paper traffic presets / Table 4 -> `src/environment/traffic_config.py`
- Traffic observability / load summaries -> `src/environment/traffic_observer.py`
- Environment lifecycle boundary -> `src/environment/gym_adapter.py`

## Compute and execution

- Task compute budget from size × processing density -> `src/environment/task.py`, `src/environment/execution_helper.py`
- Per-slot capacity settings -> `src/environment/compute_config.py`
- Slot-based compute decrement -> `src/environment/execution_helper.py`
- Terminal resolution after compute exhaustion -> `src/environment/gym_adapter.py`, `src/environment/reward_timing.py`
- Delayed reward emission after terminal resolution -> `src/environment/reward_timing.py`, `src/environment/gym_adapter.py`

## Evaluation and traceability

- Trace compatibility -> `src/evaluation/trace_protocol.py`, `src/environment/trace_source.py`
- Paper-backed metrics and evaluation summaries -> `src/evaluation/metrics.py`, `src/evaluation/runner.py`

## Adaptive policy and offloading decisions

- Adaptive decision inputs -> `src/policies/adaptive_context.py`
- Conservative adaptive baseline -> `src/policies/adaptive_offloading.py`
- Observed traffic summary input -> `src/environment/traffic_observer.py`
- Compute / execution estimates from feature 006 -> `src/environment/task.py`, `src/evaluation/trace_protocol.py`, `src/environment/gym_adapter.py`

## Paper-backed evaluation matrix

- Evaluation matrix configuration -> `src/evaluation/matrix_config.py`
- Approved policy lookup -> `src/evaluation/policy_registry.py`
- Approved scenario lookup -> `src/evaluation/scenario_registry.py`
- Serial matrix orchestration -> `src/evaluation/matrix_runner.py`
- Matrix run records and aggregate summaries -> `src/evaluation/matrix_runner.py`, `src/evaluation/metrics.py`
