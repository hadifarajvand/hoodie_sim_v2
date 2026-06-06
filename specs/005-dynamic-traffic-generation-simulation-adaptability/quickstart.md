# Quickstart: Dynamic Traffic Generation & Simulation Adaptability

## 1. Pick a paper-backed traffic preset

Use one of the approved presets:

- `paper_default`
- `moderate`
- `heavy`
- `extreme`

Each preset provides the paper-backed agent count, horizon, arrival probability, slot duration, timeout, task-size range, and processing density.

## 2. Generate a deterministic trace from a seed

```python
from pathlib import Path

from src.environment.traffic_config import TrafficScenarioPreset
from src.environment.traffic_generator import TrafficGenerator

config = TrafficScenarioPreset.paper_default()
traffic_trace = TrafficGenerator.generate(config=config, seed=42)
summary = traffic_trace.summary

print(summary.scenario_name)
print(summary.observed_arrival_probability)
print(summary.arrivals_per_slot)
```

The same `config` + `seed` pair must always produce the same trace and summary.

## 3. Hand the generated workload to the existing environment boundary

Persist the generated trace using the same `tasks` payload shape that `TraceSource.load()` already consumes, then load it through the existing `TraceSource` boundary and call `HoodieGymEnvironment.reset(seed)`.

```python
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.trace_source import TraceSource

trace_root = Path("outputs/traffic")
trace_root.mkdir(parents=True, exist_ok=True)
traffic_trace.write_json(trace_root / f"{traffic_trace.trace_id}.json")

env = HoodieGymEnvironment(
    episode_length=config.episode_length,
    trace_source=TraceSource.from_trace_bank(traffic_trace.trace_id, root_path=trace_root),
)

observation, info = env.reset(seed=None)
```

`HoodieGymEnvironment` still owns the lifecycle. The traffic layer only feeds the trace.

## 4. Run the episode with the existing `step(action)` loop

Use the existing environment loop and keep `reset(seed)` / `step(action)` as the only lifecycle entry points.

```python
while True:
    current_task = env.current_task
    action = None if current_task is None else policy.choose_action(...)
    observation, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        break
```

## 5. Inspect traffic observability

Use the traffic summary to inspect configured load, observed load, and arrival distribution over the full trace or a rolling window. This is observability only; it does not change the simulator model.

## No dependency change required

This feature does not require installing Gymnasium, ns-3, ns-3-gym, or any new package. It uses the repository’s existing Python stack and standard-library RNG only.
