# Feature Specification: 001-hoodie-reproduction

**Feature Branch**: `001-hoodie-reproduction`  
**Created**: 2026-04-21  
**Status**: Draft  
**Input**: User description: "Create a new feature specification: 001-hoodie-reproduction."

## Objective

Reproduce the HOODIE paper as a shared, fair-comparison simulator for hybrid task offloading in a
delay-aware Cloud-Edge Continuum.

## System Scope

The feature covers a discrete-time Cloud-Edge Continuum task-offloading environment with deadlines,
queues, and distributed agent decisions. The simulator must support both baseline policies and the
HOODIE method under the same workload, topology, and evaluation rules.

The scope includes task arrival, queueing, offloading, execution completion, deadline expiration,
reward timing, and comparison outputs needed to assess average delay and drop ratio under shared
evaluation traces or paired-comparison workload control.

## Required Entities

- **Task**: A non-divisible workload instance with arrival time, size, processing density, timeout,
  destination, waiting state, completion state, and drop state.
- **EdgeAgent**: A decentralized edge node that receives local tasks and can also host tasks offloaded
  from other agents.
- **CloudNode**: The cloud destination available for vertical offloading and task execution.
- **PrivateQueue**: The FIFO queue for tasks selected for local computation at an edge agent.
- **PublicQueue**: The FIFO queue for tasks hosted by a computing node for tasks offloaded from other
  edge agents.
- **OffloadingQueue**: The FIFO queue holding tasks after the policy has already selected the action
  and resolved the destination, while the task waits for transmission or service before offload
  completion.
- **TopologyGraph**: The connectivity representation that determines legal horizontal and vertical
  offloading destinations.
- **Environment**: The shared simulation environment governing task arrivals, queue evolution,
  execution timing, deadlines, and transitions.
- **Policy**: A decision-making entity used by both baselines and HOODIE for action selection.
- **Evaluation Module**: The shared comparison layer that computes and reports metrics from common
  traces and common simulator outcomes.

## Required Behaviors

- Per-slot arrival handling.
- Slot-based task arrivals.
- Task attribute generation.
- Legal action masking from topology.
- Queue admission timing.
- Queue service timing.
- Public queue routing by source agent.
- Local computation.
- Horizontal offloading.
- Vertical offloading.
- Queue waiting and completion behavior.
- Deadline/drop semantics.
- Timeout expiration and task drop.
- Delayed reward emission timing.
- Delayed reward timing.
- Trace-based evaluation replay behavior.
- Shared evaluation traces or paired-comparison workload control.

## Required Baselines

- RO.
- FLC.
- HO.
- VO.
- MLEO.
- BCO.

## Required HOODIE Components

- Distributed agent decision-making.
- LSTM-based history input.
- Dueling DQN.
- Double DQN.
- Replay memory.
- Target network logic.

## Required Outputs

- Average delay.
- Drop ratio.
- Convergence traces.
- Validation comparison outputs.
- Sweep-ready experiment outputs.

## Out-of-Scope Items

- Implementation details.
- Library or framework selection.
- Code organization.
- Training procedure specifics not stated in the paper.
- Any baseline or HOODIE behavior not required for fair comparison or not supported by the paper.
- Any extension to new objectives beyond delay and drop ratio unless explicitly stated in the paper.

## Unknowns and Paper Gaps

### Critical Unknowns

- Exact reward formula and any reward scaling not explicitly recoverable from the paper.
- Exact evaluation trace bank contents or workload seed set.
- Exact topology size, node counts, and scenario configurations for each reported experiment.

### Calibration Unknowns

- Exact parameter values for all scenario settings unless explicitly recovered from the paper tables or
  figures.
- Exact training hyperparameters unless explicitly stated in the paper.
- Exact task-generation distributions beyond the paper text available in the current project resources.

### Lower-Risk Unknowns

- Any paper details that are not recoverable from the original PDF and are only weakly suggested by the
  OCR text.

## Acceptance Criteria

- The simulator represents a discrete-time Cloud-Edge Continuum task-offloading environment with
  deadlines, queues, and distributed agent decisions.
- A shared environment interface is used across baselines and HOODIE.
- The same environment and evaluation rules are used for all baselines and for HOODIE.
- A shared evaluation module computes all comparison metrics.
- The required entities are represented in the feature scope.
- The required behaviors are present in the feature scope.
- The required baselines are included in the comparison scope.
- The required HOODIE components are included in the reproduction scope.
- The required outputs are produced for comparison and validation.
- Paired or fixed-trace fairness support is available for comparison runs.
- Fair comparison remains possible under the constitution’s Baseline Fairness Rule.
- Any missing or unrecoverable paper detail is recorded in Unknowns and Paper Gaps rather than
  invented.
- Unknown paper details are recorded rather than silently assumed.
- Evaluation can be reproduced from saved seeds or trace-bank identifiers.

## Resource Inputs

- **Source of truth**: `resources/papers/hoodie/original/HOODIE_paper.pdf`
- **Supporting references**: `resources/papers/hoodie/ocr/merged.md`
- **Supporting references**: `resources/papers/hoodie/ocr/merged.txt`
- **Non-authoritative implementation references**: `resources/references/simulators/PureEdgeSim/`
- **Non-authoritative implementation references**: `resources/references/simulators/EdgeSimPy/`
- **Non-authoritative implementation references**: `resources/references/simulators/simpy-main/`
