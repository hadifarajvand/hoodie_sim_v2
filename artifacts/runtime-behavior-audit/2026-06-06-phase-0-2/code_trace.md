# Code Trace

## `main.py`

- Lines 1-9 import the environment, decision makers, LR scheduler, NumPy, argparse, torch, os, json, and pickle.
- Lines 10-21 parse CLI args and load `hyperparameters/hyperparameters.json`.
- Lines 23-48 construct the `Environment` with all model parameters from JSON.
- Lines 51-63 create `scheduler.pth` and pickle the LR schedule function into it.
- Lines 67-77 select the decision-maker class from the config.
- Lines 82-126 instantiate one decision maker per server.
- Lines 133-160 execute the epoch loop:
  - `env.reset()`
  - per-step action selection
  - `env.step(actions)`
  - transition storage when not validating
  - `decision_maker.learn()` after each epoch

## `environment/environment.py`

- Lines 35-39 define the environment state and episode horizon.
- Lines 41-71 construct task generators, servers, matchmakers, and cloud.
- Lines 74-83 derive feature dimensions and scaling constants.
- Lines 84-111 reset state and sample one task per server before the first observation.
- Lines 127-166 build the observation:
  - task features
  - local waiting times
  - per-server public queue lengths
  - active queue counts
- Lines 176-221 execute one environment step:
  - collect current arrivals
  - map discrete actions through the matchmaker
  - step cloud and server queues
  - send transmitted tasks into target public queues
  - generate `rewards`, `tasks_arrived`, and `tasks_dropped`

## `environment/queues.py`

- Lines 5-52 implement the generic queue base, queue length tracking, and timeout dropping.
- Lines 54-81 implement private processing with waiting-time accumulation.
- Lines 85-117 implement offloading with waiting-time accumulation and transmission.
- Lines 119-126 implement public queue processing.
- Lines 129-192 implement `PublicQueueManager`:
  - one public queue per supporting source server
  - active queue counting
  - priority-weighted CPU split
  - drop and processing reward aggregation

## `environment/task.py`

- Lines 3-26 define task fields: size, arrival time, timeout, priority, computational density, drop penalty, origin, and target.
- Lines 28-71 define task lifecycle:
  - `drop_task`
  - `finish_task`
  - `process`
  - `public_process`
  - `transmit`
- Lines 73-124 expose task getters and feature extraction.

## `environment/task_generator.py`

- Lines 6-39 configure per-server arrival probability and variable distributions.
- Lines 41-49 implement Bernoulli task generation over `episode_time`.
- Lines 51-62 create task instances with sampled task attributes.

## `environment/server.py`

- Lines 17-28 create private, offloading, and public queue managers.
- Lines 43-58 route an action either to local processing or to offloading.
- Lines 53-58 combine private and offloading rewards with foreign public rewards.
- Lines 60-82 expose server features, action count, and offload topology.

## `environment/cloud.py`

- Lines 5-38 create the cloud public queue manager and expose queue features / active queues.

## `environment/matchmaker.py`

- Lines 2-13 map discrete action indices to `[local_id] + offloading_servers`.

## `decision_makers/agent.py`

- Lines 19-81 define the DQN network.
- Lines 84-163 set up per-agent replay buffers, LSTM history, target network, optimizer, and epsilon schedule.
- Lines 165-201 store transitions and choose actions.
- Lines 223-298 implement Double-DQN style learning with replay memory and target updates.

## `decision_makers/dummies.py`

- Provides runtime test policies / baselines:
  - `AllLocal`
  - `AllVertical`
  - `AllHorizontal`
  - `Random`
  - `SingleAgent`
  - `RoundRobin`

## `decision_makers/rule_based.py`

- Implements a heuristic that compares local and offloaded completion estimates using current waiting times and public queue loads.

## `utils/__init__.py`

- Provides shared helpers:
  - `merge_dicts`
  - `dict_to_array`
  - `remove_diagonal_and_reshape`
  - `Variabledistributor`
  - `visualize_2d_array`
  - `sum_dicts_in_positions`
- Imports `matplotlib.pyplot`, which caused the smoke-run environment dependency failure before the package was installed.

## Smoke Artifacts

- `run_command.txt` records the exact command.
- `run_stdout.txt` shows configuration dump and one-epoch accumulated reward.
- `run_stderr.txt` shows matplotlib cache warnings, not a fatal error.
- `exit_code.txt` confirms the run exited cleanly with `0`.
- `run_manifest.json` and `run_report.md` summarize the smoke run.
- `log_folder/scheduler.pth` was written as a pickled learning-rate schedule function.
