# Implementation Plan: Feature 084 HOODIE Paper Baseline and Formula Fidelity Audit

## Branch

`084-hoodie-paper-baseline-fidelity-audit`

Base branch: `083-hoodie-paper-baseline-fidelity`

Base SHA at creation: `2db359dfb3948bc0dce7d973a17869e7b9eefbf8`

## Problem Statement

Feature 083 is useful but not final. It incorrectly includes `MQO` as a paper baseline. The HOODIE paper baseline is `MLEO` — Minimum Latency Estimation Offloader. Because baseline identity affects policy implementation, artifact labels, ranking tables, and paper-fidelity claims, Feature 083 must not be merged as final fidelity until this is repaired.

## Plan

### Phase 1 — Baseline Identity Repair

1. Search all repository files for:
   - `MQO`
   - `Minimum Queue Offloader`
   - `ORIGINAL_HOODIE_BASELINE`
   - `HOODIE_PROPOSED`
2. Replace active `MQO` policy identity with `MLEO`.
3. Replace "Minimum Queue Offloader" semantics with "Minimum Latency Estimation Offloader".
4. Ensure `ORIGINAL_HOODIE_BASELINE` and `HOODIE_PROPOSED` are not active paper-fidelity policy IDs.
5. Keep `HOODIE` as the sole proposed method.

### Phase 2 — MLEO Semantics Repair

1. Implement or verify MLEO as a latency-estimation policy, not a queue-length-only policy.
2. MLEO must choose the destination with minimum estimated end-to-end completion latency under the current simulation state.
3. Its estimate must consider available implemented latency components, including local execution, offloading transmission, queueing, remote execution, and cloud/public path timing when available.
4. If a paper component is unavailable in code, document the approximation explicitly in `formula-mapping-matrix.md`.

### Phase 3 — Formula and Simulation Audit

1. Extract formula/model/algorithm/figure obligations from `resources/papers/hoodie/ocr/merged.txt` and the HOODIE PDF.
2. Map each obligation to code locations in:
   - `src/analysis/hoodie_proposed_method/`
   - `src/analysis/hoodie_runtime_evaluation_runner/`
   - relevant tests
   - generated artifacts
3. Assign status:
   - `exact`
   - `approximate`
   - `missing`
   - `wrong`
   - `out_of_scope`
4. Add required fixes for every `approximate`, `missing`, or `wrong` row.

### Phase 4 — Artifact Regeneration

1. Regenerate deterministic evaluation artifacts with active policies:
   - `HOODIE`
   - `RO`
   - `FLC`
   - `VO`
   - `HO`
   - `BCO`
   - `MLEO`
2. Ensure aggregate tables and rankings no longer contain `MQO`.
3. Ensure report status does not overclaim full paper reproduction unless training and empirical figure reproduction are actually complete.

### Phase 5 — Tests and Gates

1. Add tests proving `MQO` is absent from active output.
2. Add tests proving `MLEO` is present and policy-distinct.
3. Add tests proving `HOODIE` is policy-distinct from every baseline.
4. Add a validation gate that fails if `ORIGINAL_HOODIE_BASELINE`, `HOODIE_PROPOSED`, or active `MQO` appear in paper-fidelity artifacts.

## Codex Implementation Prompt

```text
You are working in repository `/Users/hadi/Documents/GitHub/hoodie_sim_v2` on branch `084-hoodie-paper-baseline-fidelity-audit`.

Goal: Repair Feature 083's HOODIE paper baseline fidelity defect and implement the Feature 084 audit Spec Kit.

Critical context:
- HOODIE is the paper's proposed method.
- Do NOT introduce the user's thesis method, DCQ, deadline-aware queue redesign, or any new proposed method.
- There must NOT be both `HOODIE_PROPOSED` and `ORIGINAL_HOODIE_BASELINE` as paper methods.
- `ORIGINAL_HOODIE_BASELINE` must not appear as an active method/policy/artifact row.
- Feature 083 incorrectly used `MQO` / Minimum Queue Offloader.
- The HOODIE paper baseline is `MLEO` / Minimum Latency Estimation Offloader.

Required changes:

1. Baseline identity repair:
   - Search the whole repo for `MQO`, `Minimum Queue Offloader`, `ORIGINAL_HOODIE_BASELINE`, and `HOODIE_PROPOSED`.
   - Replace active `MQO` with `MLEO` everywhere in code, tests, generated report labels, rankings, configs, and Spec Kit paper-fidelity artifacts.
   - Replace "Minimum Queue Offloader" with "Minimum Latency Estimation Offloader".
   - Remove `MQO` from active policy registries and report rows.
   - Historical mentions of MQO are allowed only in Feature 084 documentation as a defect note.

2. Implement/repair MLEO policy semantics:
   - MLEO must choose the candidate action/destination with the minimum estimated end-to-end task completion latency.
   - It must not be a pure minimum-queue-length policy.
   - Use existing simulation timing components wherever available: local execution, vertical offload transmission, horizontal offload transmission, private/offloading/public queue timing, remote execution, and cloud path timing.
   - If some paper component is not modeled in the runtime evaluator, add explicit approximation metadata rather than silently pretending exact fidelity.

3. Formula mapping matrix:
   - Create or update `specs/084-hoodie-paper-baseline-fidelity-audit/formula-mapping-matrix.md`.
   - Include columns: Paper Item, Meaning, Expected Simulation Logic, Current Code Location, Status, Required Fix, Evidence.
   - Cover at minimum: task completion delay, task drop ratio, reward/cost model, local execution delay, vertical offloading delay, horizontal offloading delay, private queue timing, offloading queue timing, public queue timing, DQN interface, Double-DQN target rule, Dueling-DQN interface, LSTM recovery interface, replay memory, epsilon-greedy schedule, inference epsilon zero, baseline policies, evaluation rankings, paper figures/results.
   - Mark status as one of: exact, approximate, missing, wrong, out_of_scope.

4. Runtime artifacts:
   - Regenerate deterministic evaluation artifacts so active policies are exactly: HOODIE, RO, FLC, VO, HO, BCO, MLEO.
   - Ensure no active artifact contains MQO.
   - Ensure rankings use MLEO instead of MQO.
   - Ensure report readiness does not claim full empirical paper reproduction unless trained DRL/LSTM and paper figure reproduction are actually present.

5. Tests/gates:
   - Add tests that fail if active outputs contain MQO, Minimum Queue Offloader, ORIGINAL_HOODIE_BASELINE, or HOODIE_PROPOSED.
   - Add tests that require MLEO in policy registry and generated aggregate outputs.
   - Add tests that verify MLEO is not identical to RO, FLC, VO, HO, BCO, or HOODIE on the deterministic benchmark scenario unless a documented tie exists.
   - Add tests that formula mapping matrix exists and contains non-empty statuses and required-fix fields for approximate/missing/wrong entries.

6. Documentation updates:
   - Update Feature 084 Spec Kit files, especially `tasks.md`, `formula-mapping-matrix.md`, `contracts/validation-rules.md`, and `quickstart.md`.
   - Add a clear note that PR #24 / Feature 083 is blocked from final merge until this repair is implemented.

Validation commands to run:
- `python -m pytest`
- Any existing deterministic runtime evaluation command used by Feature 083.
- Grep checks:
  - active artifacts must not contain `MQO`
  - active artifacts must not contain `Minimum Queue Offloader`
  - active artifacts must not contain `ORIGINAL_HOODIE_BASELINE`
  - active artifacts must not contain `HOODIE_PROPOSED`
  - active artifacts must contain `MLEO`

Commit all changes with message:
`Implement Feature 084 HOODIE baseline and formula fidelity audit`

Final response must include:
- branch name
- final commit SHA
- summary of repaired files
- test commands and results
- regenerated artifact paths
- remaining fidelity gaps, if any
```
