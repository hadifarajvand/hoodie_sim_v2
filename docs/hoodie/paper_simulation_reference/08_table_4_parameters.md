# 08 — Table 4 Parameter Contract

This file defines the paper default simulation parameters that must be used unless a figure-specific sweep overrides them.

| Parameter | Symbol | Paper value | Implementation requirement |
|---|---|---|---|
| Task arrival probability | P | 0.5 | Bernoulli arrival per EA per action slot |
| Horizontal data rate | R_H | 30 Mbps | Used for EA-to-EA transmission |
| Vertical data rate | R_V | 10 Mbps | Used for EA-to-Cloud transmission |
| Task size | eta_n(t) | [2, 2.1, ..., 5] Mbits | Sampled per arriving task unless figure overrides range |
| Processing density | rho_n(t) | 0.297 gigacycles/Mbit | Used in all processing-time calculations |
| Number of EAs | N | 20 | Default system size |
| Edge topology | G | Figure 7 | Must be represented as adjacency or explicitly documented fallback |
| Private EA CPU | f_EA_priv_n | 5 GHz | Used for private queue service |
| Public EA CPU | f_EA_pub_n | 5 GHz | Shared across active public queues |
| Cloud CPU | f_Cloud | 30 GHz | Shared across active Cloud public queues |
| Training episodes | N_E | 5000 | Required for paper-faithful training figures |
| Slots per episode | T | 110 | 100 action + 10 drain |
| Slot duration | Delta | 0.1 sec | Used in all slot/service conversions |
| Task timeout | phi_n | 20 slots = 2 sec | Default unless figure-specific regime overrides |
| Learning rate | alpha_lr | 7e-7 | Best learning rate from paper Figure 8a |
| Discount factor | gamma | 0.99 | Best discount factor from paper Figure 8b |
| Q hidden layers | N_L | 3 × 1024 neurons | Q-network architecture |
| Optimizer | Opt | Adam | Training optimizer |
| Loss | MSE | Eq. 28 | Q-network loss |
| Target update | N_copy | 2000 | Target network copy frequency |
| LSTM lookback | W | 10 steps | Historical load window |
| LSTM hidden | N_L | 1 × 20 cells | LSTM structure |
| Replay memory | N_R | 10000 | Experience replay size |
| Drop penalty | C | 40 | Reward penalty for dropped tasks |
| Batch size | N_B | 64 | Training batch size |

## Figure-Specific Overrides

### Figure 8

Training sweeps override learning rate or discount factor while keeping other Table 4 values.

### Figure 9a

Overrides `P` and `N`.

### Figure 9b

Overrides `P` and records action counts.

### Figure 9c

Overrides CPU capacity from 4 to 9 GHz and uses `N=10,15,20`.

### Figure 9d

Overrides task size and P by traffic scenario:

```text
Moderate: size 1-3 Mbits, P=0.5
Heavy: size 2-5 Mbits, P=0.7
Extreme: size 3-7 Mbits, P=0.9
```

### Figure 9e

Overrides data rates by scenario:

```text
Balanced: R_H=10 Mbps, R_V=30 Mbps
Horizontal-centric: R_H=20 Mbps, R_V=20 Mbps
Vertical-centric: R_H=5 Mbps, R_V=40 Mbps
```

### Figure 10a-c

Delay comparison uses timeout `10 sec`.

### Figure 10d-e

Drop-ratio comparison uses timeout `2 sec`.

### Figure 10f

Timeout sweep uses:

```text
1.6, 1.8, 2.0, 2.2, 2.4 sec
```

### Figure 11

Uses:

```text
N=20
P=0.3
deadline=1 sec
training episodes=3000
with-LSTM and without-LSTM variants
```

## Artifact Requirement

Every generated experiment must emit a configuration manifest containing all parameters, overrides, units, random seed, and whether the run is paper-faithful, partial, or test-mode.
