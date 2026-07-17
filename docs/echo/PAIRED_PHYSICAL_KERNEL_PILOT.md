# Paired physical-kernel pilot

This pilot is a bounded integration gate between the source-locked ECHO
controls and a transparent two-EA-plus-cloud slot kernel. It is not the final
HOODIE Dueling Double-DQN campaign.

It verifies:

- identical paired traces for HOODIE, ECHO, and ECHO-disabled;
- semantic equality of HOODIE and ECHO-disabled task ledgers;
- private and outbound source queues;
- non-preemptive source service;
- next-slot destination admission after transmission;
- source-indexed FIFO destination queues;
- equal destination-capacity sharing without same-slot redistribution;
- completion-before-drop ordering at the deadline slot;
- task conservation;
- ERT route filtering, minimum-lateness fallback, and source scheduling;
- ERT absent from the learned observation contract;
- seed-level aggregation and paired ECHO–HOODIE differences.

Run from a clean checkout:

```bash
bash scripts/echo/run_paired_kernel_pilot.sh \
  /absolute/path/outside/repository/echo-paired-kernel-pilot
```

Every output is labelled `PAIRED PILOT — NOT PAPER EVIDENCE`. The results are
not valid manuscript Figures 5–8 because the pilot uses an identical,
deterministic Q-value proxy rather than trained HOODIE/ECHO checkpoints.
