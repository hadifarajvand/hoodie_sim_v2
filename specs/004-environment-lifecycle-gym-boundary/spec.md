# Feature Specification: 004-environment-lifecycle-gym-boundary

**Feature Branch**: `004-environment-lifecycle-gym-boundary`
**Created**: 2026-04-30
**Status**: Draft
**Input**: User description: "Create a new Spec Kit feature specification named `004-environment-lifecycle-gym-boundary`.

This feature must complete the environment lifecycle and expose a clean Gymnasium-style reset/step boundary for the existing HOODIE simulator without adding a Gymnasium dependency unless it is already approved.

Context:

The repository already has a broad reproduction specification in `specs/001-hoodie-reproduction/`. That spec remains the master reproduction scope. The repository also has training-related specs in `specs/002-torchrl-hoodie-training/` and `specs/003-torchrl-hoodie-training/`, but those are not the current priority. Training must not advance until the environment lifecycle is stable, deterministic, and baseline-compatible.

The current implementation already contains environment, policies, evaluation, agents, training, configs, and tests. The next feature must focus only on the environment boundary and lifecycle. Do not rewrite unrelated modules.

Goal:

Complete the existing slot-based environment lifecycle so that one deterministic episode can run through task generation or trace loading, observation construction, legal action masking, policy action selection, queue admission, offloading progression, public queue admission, execution progression, completion/drop handling, delayed reward emission, and metric updates.

Expose this through a minimal Gymnasium-style adapter with:

```python
reset(seed: int | None = None) -> tuple[observation, info]
step(action) -> tuple[observation, reward, terminated, truncated, info]
```

Do not import or require `gymnasium` unless it is already declared as an approved dependency. If Gymnasium is not approved, implement a local compatibility adapter that follows the same reset/step semantics.

Functional requirements:

* The environment must support deterministic reset with seed.
* Same seed plus same policy must produce the same episode trace.
* The adapter must wrap the existing simulator core instead of replacing it.
* The environment must preserve delayed reward semantics: reward is emitted only when a task completes or drops, never at decision time.
* The environment must support all existing baseline policies through the same environment semantics: FLC, VO, HO, RO, BCO, and MLEO.
* The environment must preserve legal action masking from topology.
* The environment must support local execution, horizontal offload, and vertical cloud offload.
* The environment must update metrics through the shared evaluation path where applicable.
* The environment must produce enough debug trace information to reconstruct task lifecycle events.
* The feature must not add neural-network code.
* The feature must not add ns-3, ns-3-gym, or any network simulator dependency.
* The feature must not alter metric formulas, reward semantics, or baseline fairness.

Production and constitution constraints:

* Follow `.specify/memory/constitution.md` v1.3.0.
* No dependency changes are allowed.
* No virtual environment changes are allowed.
* No source-wide refactors are allowed.
* No broad file moves are allowed.
* Any missing paper detail must be documented in assumptions before implementation depends on it.
* Any public interface change must document affected callers and migration path.
* Any config change must include validation behavior or a documented validation gap.
* All generated artifacts must follow the artifact lifecycle rules.
* The feature is not done until the Definition of Done Rule is satisfied.

Out of scope:

* Training improvements.
* TorchRL integration.
* DQN architecture changes.
* LSTM model changes.
* ns-3-gym integration.
* Paper-result reproduction claims.
* Performance optimization beyond avoiding obviously bad complexity.
* Replacing the simulator with EdgeSimPy, SimPy, ns-3, or any external framework.

Required tests:

* reset(seed) determinism
* same seed plus same baseline policy produces same trace
* single-step environment transition
* full episode with at least one baseline policy
* local queue admission
* horizontal offload path
* vertical cloud offload path
* public queue admission after offload
* action legality under topology
* delayed reward emitted only after completion/drop
* metric update consistency
* no dependency changes

Required documentation updates:

* Update paper-to-code mapping for any new environment behavior.
* Update assumptions only if new assumptions are introduced.
* Update quickstart or usage notes only if the environment adapter adds a new official command or entry point.

Acceptance criteria:

* A deterministic baseline episode can run through the adapter.
* The same seed and policy produce the same trace.
* Rewards are not emitted at decision time.
* All baselines can use the same environment boundary or have a documented migration task.
* Existing tests pass.
* New environment-boundary tests pass.
* No dependencies are changed.
* No neural-network code is added.
* No ns-3-gym integration is introduced.
* Any remaining gaps are documented explicitly instead of hidden."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deterministic Environment Boundary (Priority: P1)

As a reproduction maintainer, I want to reset and step the HOODIE environment through a clean
boundary so that one episode can be replayed deterministically for evaluation and baseline
comparison.

**Why this priority**: This is the blocking capability for environment stability and fair baseline
comparison.

**Independent Test**: Reset the environment with the same seed and run the same baseline policy
twice; the trace, terminal outcomes, and rewards should match.

**Acceptance Scenarios**:

1. **Given** the same seed and policy, **When** the environment is reset and stepped through one
   episode, **Then** the resulting trace is identical across runs.
2. **Given** a new seed, **When** the environment is reset, **Then** the generated or loaded episode
   trace differs in a deterministic, reproducible way.

### User Story 2 - Shared Lifecycle Semantics (Priority: P1)

As a baseline user, I want the environment to apply the same lifecycle rules for task arrival,
queueing, offloading, execution, terminal resolution, delayed reward, and metric updates so that
all baselines are evaluated under the same simulator semantics.

**Why this priority**: The reproduction is only valid if the same lifecycle rules govern every
baseline and the HOODIE path.

**Independent Test**: Run a single episode with a baseline policy that exercises local execution and
offloading; verify queue admission, offload progression, public-queue admission, terminal outcome,
reward timing, and metrics.

**Acceptance Scenarios**:

1. **Given** a task that is legal for local execution, **When** the policy chooses local action,
   **Then** the task enters the local queue, completes or drops later, and reward appears only at
   the terminal event.
2. **Given** a task that is legal for horizontal or vertical offload, **When** the policy chooses
   that offload action, **Then** the task enters the offloading path, later joins the correct
   destination queue, and is finalized under the same reward timing rules.

### User Story 3 - Topology-Constrained Action Selection (Priority: P2)

As a policy consumer, I want topology-aware legal action masking so that the policy only selects
actions that are valid for the current task and source node.

**Why this priority**: Baseline fairness depends on identical legality rules and observable inputs.

**Independent Test**: Present a task on a topology with limited connectivity and verify the legal
action mask matches the available destinations.

**Acceptance Scenarios**:

1. **Given** a topology that allows only local execution and one offload target, **When** the
   environment presents a task, **Then** the legal action mask exposes only those allowed choices.
2. **Given** a topology that disallows a destination, **When** the policy asks for that action,
   **Then** the environment rejects or remaps it according to the shared policy contract and
   documented rules.

### User Story 4 - Gymnasium-Style Adapter Boundary (Priority: P2)

As a developer of baseline and evaluation workflows, I want a minimal reset/step adapter around the
simulator so that the environment can be used through a clean episode interface without adding a
new dependency.

**Why this priority**: The adapter is the simplest common entry point for the environment lifecycle.

**Independent Test**: Call `reset(seed)` and `step(action)` on the adapter and confirm that the
returned tuple matches the expected structure and that the adapter does not own simulator state
mutation.

**Acceptance Scenarios**:

1. **Given** an adapter reset with a seed, **When** a step is executed, **Then** the adapter
   returns observation, reward, termination flags, and info in a stable structure.
2. **Given** no approved Gymnasium dependency, **When** the adapter is used, **Then** the project
   still runs using a local compatibility boundary.

### Edge Cases

- What happens when there are no tasks available for a slot?
- How does the environment behave when a policy requests an illegal offload action?
- What happens when a task completes after the decision slot but before the next slot boundary?
- How are dropped tasks represented in delayed reward and metrics?
- What happens when a trace is loaded instead of generated?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The environment MUST support deterministic reset and replay when seeded.
- **FR-002**: The same seed and same policy MUST produce the same episode trace.
- **FR-003**: The environment MUST expose a clean reset/step boundary around the existing slot
  simulator.
- **FR-004**: The environment MUST preserve delayed reward semantics so rewards are emitted only
  on completion or drop.
- **FR-005**: The environment MUST preserve topology-based legal action masking.
- **FR-006**: The environment MUST support local execution, horizontal offload, and vertical cloud
  offload under the shared environment semantics.
- **FR-007**: The environment MUST support all existing baseline policies under the same boundary
  and lifecycle rules.
- **FR-008**: The environment MUST produce trace data sufficient to reconstruct task lifecycle
  events.
- **FR-009**: The environment MUST update shared metrics through the existing evaluation path when
  applicable.
- **FR-010**: The feature MUST NOT add neural-network code, ns-3, ns-3-gym, or other new simulator
  dependencies.
- **FR-011**: The feature MUST NOT change metric formulas, reward semantics, or baseline fairness.
- **FR-012**: The adapter MUST NOT require a new Gymnasium dependency unless one is already approved.

### Key Entities *(include if feature involves data)*

- **Task**: A unit of work with arrival, queue, terminal, and reward state.
- **Environment Boundary**: The reset/step interface that presents one episode at a time.
- **Policy**: A baseline or HOODIE decision-maker that receives observations and action legality
  information.
- **Trace**: The deterministic or loaded episode sequence used for replay and comparison.
- **Topology**: The connectivity rule set that determines legal action availability.
- **Metrics**: Shared episode outcomes such as delay and drop ratio.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The same seed and baseline policy produce identical episode traces in repeated runs.
- **SC-002**: Users can run at least one baseline policy through a full episode using the shared
  environment boundary without changing simulator semantics.
- **SC-003**: Reward is emitted only at terminal completion or drop events in 100% of observed
  lifecycle tests.
- **SC-004**: Topology-constrained action masks match the available legal actions for all tested
  cases.
- **SC-005**: The environment boundary remains usable without adding an unapproved dependency.
- **SC-006**: Task lifecycle traces remain sufficient to reconstruct arrival, queueing, offloading,
  execution, terminal outcome, reward timing, and metrics for at least one full episode.

## Assumptions

- The existing HOODIE simulator core remains the source of truth for lifecycle semantics.
- A local compatibility adapter is acceptable if Gymnasium is not already an approved dependency.
- Existing baseline policies are the comparison set for this feature.
- The shared evaluation path is the authority for metric updates when the environment reaches a
  terminal event.
- No new paper-backed reward formula is introduced; the feature preserves the existing reward
  semantics.

