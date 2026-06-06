# Gap Classification

## 1. Is the current branch content equivalent to the original HOODIE implementation?

Partially yes, but only for the promoted runtime baseline files.

- `main.py`
- `environment/environment.py`
- `utils/__init__.py`
- `hyperparameters/hyperparameters.json`

These files are byte-for-byte identical to the promoted baseline snapshot in Git history.

But the branch overall is **not** a pristine original repo checkout because it also contains:

- `.specify/`
- `artifacts/`
- repository-local audit outputs

## 2. Which files differ from the original HOODIE repo, if any?

I cannot prove external-repository byte identity because `Ilias-Paralikas/HOODIE` is not vendored here for a direct diff.

What I can prove locally:

- The runtime core files above match the promoted baseline snapshot exactly.
- The repository layout differs from the original HOODIE package layout because of the root promotion and audit artifacts.

## 3. Which paper mechanisms are already present?

Present:

- Bernoulli task arrivals
- Task size sampling
- Private queue
- Offloading queue
- Source-specific public queues
- Multi-agent per-server decision makers
- DQN agent with target network and replay memory
- LSTM history input inside the agent
- Cloud object and per-server capacities

## 4. Which mechanisms are present but not auditable enough?

Present but not auditable enough:

- Per-task reward provenance
- Queue completion/drop lifecycle
- Public queue load distribution
- Offload legality semantics
- Validation/evaluation workflow

## 5. Which mechanisms are missing or under-specified?

Missing / under-specified:

- Explicit action-slot vs drain-slot runtime
- Delayed reward collection
- Equal active public-queue CPU sharing
- Figure 7 topology contract as a named artifact
- Historical load matrix export
- 200-episode validation mode
- Figure 8/9/10/11 generation workflow
- A paper-contract baseline registry

## 6. Does public queue CPU sharing follow equal active-queue sharing or priority-weighted sharing?

Priority-weighted sharing.

Evidence:

- `environment/queues.py`, `PublicQueueManager.step()`
- it computes `total_priority = sum(current_task.get_priority())`
- then sets `distributed_computational_capacity = self.computational_capacity / total_priority`

That is not the paper's equal active-queue sharing rule.

## 7. Is reward assignment task-traceable and delayed, or only step-aggregated?

Only step-aggregated.

Evidence:

- `environment/environment.py` returns `rewards` every step
- `main.py` stores those step rewards into agent transitions
- there is no task-level reward-event registry

## 8. Is LSTM operating as a forecast/history pipeline, or only embedded inside DQN input handling?

Only embedded inside DQN input handling.

Evidence:

- `decision_makers/agent.py`
- LSTM history is concatenated into the Q-network input
- no separate forecast trace, load history export, or auditable LSTM pipeline exists

## 9. Is topology/action legality explicitly tied to Figure 7 and the paper’s topology contract?

No.

Evidence:

- `environment/matchmaker.py` maps action indices to `[local_id] + offloading_servers`
- topology is adjacency-based and derived from the connection matrix
- no paper-named topology mode or Figure 7 contract is present

## 10. Are Figure 8/9/10/11 generation workflows present?

No evidence in the runtime path or artifacts.

The smoke run produced only:

- stdout/stderr
- `scheduler.pth`
- basic audit documents

No figure-generation workflow is exercised or exported.

## 11. Are 200 validation episodes supported as a first-class validation mode?

No evidence.

`main.py` supports a generic `--epochs` flag, but there is no dedicated 200-episode validation mode or paper validation harness.

## 12. Are official baselines limited to HOODIE, RO, FLC, VO, HO, BCO, and MLEO?

Not explicitly.

Available runtime test / policy classes are:

- `Agent`
- `AllHorizontal`
- `AllLocal`
- `AllVertical`
- `Random`
- `RoundRobin`
- `RuleBased`
- `SingleAgent`

Only some of those can be interpreted as rough proxies. The official paper baseline set is not explicitly encoded as a verified baseline registry.

