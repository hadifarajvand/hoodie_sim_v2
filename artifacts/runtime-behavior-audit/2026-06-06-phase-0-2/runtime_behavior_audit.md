# Runtime Behavior Audit

## Summary

The repository executed successfully under the `.venvmac` environment after installing the missing runtime packages, but the current behavior is a legacy HOODIE simulator stack, not a paper-faithful runtime core.

The smoke run completed one epoch and wrote `scheduler.pth` into the requested log folder. The execution evidence is real, but it only proves the existing simulator can run, not that it matches the HOODIE paper contract.

## Smoke Artifact Review

### Command

```bash
source .venvmac/bin/activate && python main.py --epochs 1 --log_folder artifacts/runtime-audit-smoke/2026-06-06-071900/log_folder
```

### Exit Status

- `exit_code.txt`: `0`

### Stdout

The runtime printed:

- repeated `weights folder not found` messages while trying to load agent checkpoints
- the full hyperparameter block from `hyperparameters/hyperparameters.json`
- `Epoch 0 Accumulated rewards: -5.883334159851074`

### Stderr

Matplotlib warned that:

- `/Users/hadi/.matplotlib` is not writable
- it created a temporary cache directory
- fontconfig cache directories were not writable

This was noisy, but not fatal.

### Manifest / Report

The smoke manifest states:

- branch: `100-hoodie-paper-base`
- baseline / latest commit: `dfa6be1cf12931ad6238c38ee8397649bbaec4cb`
- Python environment: `.venvmac`
- exit code: `0`
- log folder created: yes

The report correctly records the run as smoke evidence only, not paper-faithful validation.

### `scheduler.pth`

Only metadata was inspected.

- File exists: yes
- Size: `41 bytes`
- mtime: `2026-06-06 07:19:33`
- Type: a small PyTorch-related serialized artifact; `file` identifies it as a relocatable/small-model binary, consistent with a tiny pickled object rather than a trained model checkpoint

## Runtime Flow Trace

`main.py` does the following:

1. Parses `--log_folder`, `--hyperparameters_file`, `--epochs`, and `--validate`.
2. Creates the log folder.
3. Loads `hyperparameters/hyperparameters.json`.
4. Builds an `Environment` with 20 servers and all per-server resource / traffic / timeout settings.
5. Selects an LR scheduler and serializes it to `scheduler.pth`.
6. Selects a decision-maker class from:
   - `Agent`
   - `AllHorizontal`
   - `AllLocal`
   - `AllVertical`
   - `Random`
   - `RoundRobin`
   - `RuleBased`
   - `SingleAgent`
7. Instantiates one decision maker per server.
8. Runs the episode loop:
   - `env.reset()`
   - per-step action selection for every server
   - `env.step(actions)`
   - transition storage into each agent
   - epoch reward accumulation
9. Calls `decision_maker.learn()` and `reset_lstm_history()` at the end of the epoch when not validating.

## Simulation Model Inspection

### A. Task Model

Tasks are represented by `environment/task.py`:

- size
- arrival time
- timeout delay
- priority
- computational density
- drop penalty
- origin server id
- target server id

Yes:

- task size is modeled
- deadline/timeout is modeled
- processing density is modeled
- queue time is implicitly modeled through queue state
- service time is implicit through per-step processing

No:

- explicit CPU cycles are not directly modeled as a first-class state variable
- energy is not modeled
- task/job lifecycle is not traced as a separate audit object

Vehicles generate tasks via `TaskGenerator.step()`.

An arrival process exists:

- Bernoulli arrival with `np.random.rand() > task_arrive_probability`

### B. Network / Topology Model

The model has:

- servers
- one cloud object
- a connection matrix
- per-server outbound and inbound connectivity

There is no explicit RSU abstraction in the runtime path.

Communication delay / bandwidth:

- offloading capacity is encoded as a scalar per edge in the connection matrix
- transmission delay is approximated through queue/service progression, not a separately auditable link-delay model

Offloading decisions exist:

- action `0` means local execution
- other actions map to reachable offload destinations through the matchmaker

### C. Queueing Model

Explicit queues exist:

- private processing queue
- offloading queue
- public queue manager with one public queue per supporting source

Queue discipline:

- FIFO-like queue container via Python `queue.Queue`
- timeout dropping in `TaskQueue.get_first_non_empty_element()`
- public queue processing with priority-weighted CPU split

Not present:

- EDF
- LSTF
- a paper-faithful private/offload/public queue decomposition
- explicit queue waiting-time exports for evaluation

Waiting time is measured:

- `ProcessingQueue.waiting_time`
- `OffloadingQueue.waiting_time`

### D. Resource Model

Resources are modeled as scalar capacities:

- `private_cpu_capacities`
- `public_cpu_capacities`
- `cloud_computational_capacity`

Processing exists for:

- local/private execution
- offloading transmission
- public execution

But the model is not the paper target:

- resource allocation is not explicitly per-slot equal sharing among active queues
- processing capacity is not exposed as a paper-contract resource allocation trace

### E. RL / Decision Model

Current algorithm:

- DQN with target network and replay memory
- optional LSTM history in the network input
- epsilon-greedy exploration
- per-server agent instances, so this is multi-agent in deployment but not necessarily coordinated multi-agent learning

State space:

- task feature(s)
- local waiting times
- public queue lengths
- LSTM history for the agent

Action space:

- discrete mapping over local and reachable offloading targets

Reward function:

- step reward aggregated from task completions and drops
- scaled by `max_reward`
- negated before being returned from the environment

This means the action controls scheduling/offloading, but the reward signal is immediate and step-aggregated rather than delayed and traceable per task.

### F. Metrics and Logging

Logged outputs during smoke run:

- hyperparameter dump to stdout
- accumulated epoch reward
- `scheduler.pth` in the log folder

Not logged in the smoke artifacts:

- latency
- waiting time
- service time
- drop ratio
- deadline violation rate
- energy
- throughput
- queue length traces
- per-task reward traces

## HOODIE Gap Matrix

See `runtime_gap_matrix.csv` for the full matrix. Key takeaways:

- task generation exists but is not paper-faithful
- topology exists but is legacy-adjacency-based
- queueing exists but uses different sharing semantics
- reward is immediate, not delayed
- training machinery exists, but it is not proof of paper readiness
- reproducibility exists at the config level, but not at the paper-validation level

## Unsafe Assumptions

Do not assume:

1. The current action space already represents HOODIE offloading.
2. `scheduler.pth` is meaningful model evidence for the paper.
3. A successful smoke run implies paper-faithful behavior.
4. `requirements.txt` completeness means runtime completeness.
5. The current reward scalar is equivalent to the paper's task-level delayed reward.
6. The public queue sharing logic already matches the paper's equal active-queue CPU split.
7. The LSTM is an auditable forecast/history pipeline. It is model memory inside the DQN.
8. The current codebase has figure-ready validation artifacts for Figures 8/9/10/11.

## Recommended Phase 0.3

Phase 0.3 should define the paper-faithful simulator target before implementation:

- entities
  - task
  - vehicle / edge agent
  - edge server
  - cloud
  - queue objects
  - reward event
  - state snapshot

- state variables
  - task size
  - remaining workload
  - arrival slot
  - deadline
  - private wait
  - offload wait
  - public queue occupancy
  - active queue counts
  - historical load window

- action variables
  - local
  - horizontal offload
  - vertical offload
  - cloud offload

- reward terms
  - completion delay penalty
  - timeout penalty
  - delayed collection semantics

- queue model
  - private queue
  - offloading queue
  - source-specific public queues
  - explicit CPU sharing rules

- metrics
  - arrivals
  - completions
  - drops
  - delay
  - queue utilization
  - active queue counts
  - reward collection trace

- config format
  - topology mode
  - slot counts
  - CPU capacities
  - task distribution parameters
  - deterministic seed
  - forecast mode

- minimal tests
  - slot split
  - Bernoulli arrivals
  - private/offload/public queue semantics
  - delayed reward collection
  - artifact generation

## Conclusion

- What ran successfully or failed: the smoke run succeeded after installing the missing packages into `.venvmac`.
- What evidence was generated: command capture, stdout/stderr, exit code, manifest, report, and `scheduler.pth` from the log folder.
- What is currently paper-aligned: Bernoulli task arrivals, queue-based processing, adjacency-based offloading legality, and a DQN/LSTM training stack exist.
- What is still missing: paper-faithful slot/drain runtime, delayed task-level reward collection, explicit lifecycle tracing, equal active public-queue sharing, and audit-grade validation artifacts.
- Recommended next implementation phase: define Phase 0.3 target architecture/spec for a paper-faithful simulator before coding the runtime rebuild.
