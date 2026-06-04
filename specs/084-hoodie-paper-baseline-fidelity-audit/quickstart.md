# Quickstart: Feature 084

## Pull the Branch

```bash
git fetch origin
git checkout 084-hoodie-paper-baseline-fidelity-audit
git pull --ff-only origin 084-hoodie-paper-baseline-fidelity-audit
```

## Inspect the Blocking Defect

```bash
git grep -n "MQO\|Minimum Queue Offloader\|ORIGINAL_HOODIE_BASELINE\|HOODIE_PROPOSED"
```

Active paper-fidelity outputs must not contain these strings after implementation, except `MQO` inside Feature 084 documentation as a historical defect note.

## Required Implementation Prompt for Codex

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

## Validation After Codex

```bash
python -m pytest
git grep -n "MQO\|Minimum Queue Offloader\|ORIGINAL_HOODIE_BASELINE\|HOODIE_PROPOSED" -- . ':!specs/084-hoodie-paper-baseline-fidelity-audit'
git grep -n "MLEO"
```

The first grep should return no active code/artifact hits outside Feature 084 historical documentation.
