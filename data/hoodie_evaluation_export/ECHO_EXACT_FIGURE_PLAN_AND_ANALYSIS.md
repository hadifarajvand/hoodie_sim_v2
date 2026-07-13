# Exact ECHO replication of the HOODIE evaluation figures

## Final structure

The ECHO article should reproduce the base evaluation **structurally**, using five numbered figures and fifteen panels:

1. **Figure 3** - topology (one panel; base Figure 7).
2. **Figure 4(a-b)** - learning-rate and discount-factor convergence (two panels; base Figure 8).
3. **Figure 5(a-e)** - behavior and scalability (five panels; base Figure 9).
4. **Figure 6(a-f)** - comparison against HOODIE and six baselines (six panels; base Figure 10).
5. **Figure 7** - LSTM inclusion ablation (one panel; base Figure 11).

The previous six-standalone-figure plan is not an exact replication and should be replaced by this structure.

## Where ECHO can legitimately beat HOODIE

### Primary targets: Figure 6(d-f)

These three drop-ratio panels directly test ECHO's novelty. ECHO should be designed and trained to produce values **below** the digitized HOODIE curve:

- **6(d), arrival load:** strongest expected separation at P=0.7 and P=0.9.
- **6(e), CPU capacity:** strongest expected separation at 3-5 GHz.
- **6(f), timeout:** strongest expected separation at 1.6-2.0 seconds.

### Secondary targets: Figure 6(a-c)

Average delay may improve, particularly at high load and limited CPU, but it is not guaranteed. ERT may protect urgent tasks while delaying non-urgent successful tasks. Consequently, delay must be interpreted together with drop ratio.

### Not valid as direct superiority claims

- Figures 4 and 5 use accumulated reward. Since ECHO changes the reward function, its raw reward scale is not directly comparable with HOODIE's reward scale.
- Figure 5(b) is an action-distribution diagnostic; there is no universally superior number of local, horizontal, or vertical actions.
- Figure 3 is setup only.
- Figure 7 proves the value of LSTM inside ECHO. Direct ECHO-versus-HOODIE superiority is established in Figure 6.

## Data accuracy

The PDF contains vector plots but not the authors' original result files. The exported CSVs are vector-digitized approximations. The topology edge list and adjacency matrix are reconstructed exactly from the vector graph; plotted measurements are approximate and should be replaced by simulator-generated values once the HOODIE code is reproduced.
