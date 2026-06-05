# 05 — Training, Inference, and Validation Contract

## 1. Paper Training Is Real DRL Training

### Paper says

HOODIE is trained with a distributed DRL process. It is not only a deterministic offloading rule.

The paper uses:

- DQN;
- Double-DQN;
- Dueling-DQN;
- LSTM;
- replay memory;
- target network;
- epsilon-greedy exploration;
- Adam optimizer;
- MSE loss.

### Implementation requirement

The repository must distinguish clearly between:

- `trained_hoodie_policy`: a policy produced by actual training;
- `deterministic_hoodie_substitute`: useful for current simulator behavior but not paper-faithful;
- `interface_only`: model boundary exists but no trained policy exists.

### Validation evidence

Reports must state training mode before any Figure 8/9/10/11 claim.

### Failure symptom if missing

If a deterministic rule is treated as trained HOODIE, Figure 9/10 policy behavior will not match the paper mechanism.

## 2. Training Parameters

### Paper says

Default training parameters include:

```text
training episodes N_E = 5000
slots per episode T = 110
replay memory N_R = 10000
batch size N_B = 64
target update N_copy = 2000
learning rate alpha_lr = 7e-7
discount gamma = 0.99
Q hidden layers = 3 × 1024
optimizer = Adam
loss = MSE
LSTM lookback W = 10
LSTM hidden = 1 × 20 cells
```

### Implementation requirement

Training configuration must be stored in artifacts. If a smaller test mode is used, it must be labeled as a test mode and must not support paper reproduction claims.

### Validation evidence

Artifacts must include:

- number of training episodes;
- slots per episode;
- replay memory size;
- batch size;
- target update frequency;
- learning rate;
- discount factor;
- epsilon schedule;
- LSTM mode.

## 3. Training Episode Flow

### Paper says

Training proceeds by repeated episodes. Within each episode:

1. initialize state;
2. iterate over slots;
3. generate Bernoulli arrivals;
4. select action using epsilon-greedy;
5. advance environment;
6. collect delayed rewards from tasks completed or dropped at current slot;
7. store experience tuple;
8. sample batch from replay memory;
9. compute Double-DQN target;
10. update Q-network;
11. periodically copy weights to target network;
12. decay epsilon during first half of training;
13. run exploitation-only during second half.

### Implementation requirement

The training loop must not be reduced to static action selection if Figure 8/9/10 paper-faithful claims are expected.

### Validation evidence

Artifacts must include:

- reward trace by episode;
- epsilon trace;
- replay memory usage;
- update count;
- target copy count;
- loss trace if available.

## 4. Epsilon Schedule

### Paper says

Epsilon starts at 1. It decreases linearly to zero during the first half of training. It remains zero for the second half.

### Implementation requirement

The schedule must be explicitly recorded and tested.

### Failure symptom if missing

If exploration/exploitation is not implemented, training convergence curves cannot be paper-faithful.

## 5. Inference Mode

### Paper says

During inference/validation:

- the trained Q-model is deployed;
- epsilon is zero;
- no training update is performed;
- task actions are selected greedily from Q-values.

### Implementation requirement

Validation must run in inference mode. It must not update policy weights or use exploratory actions unless explicitly evaluating a non-paper test mode.

## 6. Validation Episodes

### Paper says

Figures 9 and 10 use:

```text
200 validation episodes
```

### Implementation requirement

Figure 9 and Figure 10 generation must run validation episodes and must preserve episode-level denominators. A single deterministic scenario is not sufficient.

### Validation evidence

Artifacts must include:

- validation episode count;
- total arrived tasks;
- completed tasks;
- dropped tasks;
- per-policy counts;
- per-sweep counts;
- random seeds.

### Failure symptom if missing

Sparse traces, one-task runs, zero completions, all-policy ties, and 100% drop saturation are signs that validation is not paper-scale or queue logic is broken.
