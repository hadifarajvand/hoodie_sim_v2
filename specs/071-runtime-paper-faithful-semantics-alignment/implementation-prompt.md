# Feature 071 Implementation Prompt

Use this prompt to implement Feature 071 from the prepared Spec Kit. Do not open a PR and do not merge.

```text
Implement Feature 071 — Runtime Paper-Faithful Semantics Alignment.

Repository:
hadifarajvand/hoodie_sim_v2

Local path:
/Users/hadi/Documents/GitHub/hoodie_sim_v2

Branch:
071-runtime-paper-faithful-semantics-alignment

Workflow rules:
- Do not open a PR.
- Do not merge.
- Commit and push only.
- Use src/.venvmac/bin/python for validation.
- Do not use system python3.
- Do not edit dependencies or lock files.
- Do not generate campaign artifacts.
- Do not touch Feature 072+ files.

Phase 0 — Sync and gate:

Fetch origin.
Checkout branch:
071-runtime-paper-faithful-semantics-alignment

Fast-forward to origin/071-runtime-paper-faithful-semantics-alignment if the working tree is clean.
Verify clean tree before editing.

Read these Feature 071 Spec Kit files first:
- specs/071-runtime-paper-faithful-semantics-alignment/spec.md
- specs/071-runtime-paper-faithful-semantics-alignment/plan.md
- specs/071-runtime-paper-faithful-semantics-alignment/research.md
- specs/071-runtime-paper-faithful-semantics-alignment/data-model.md
- specs/071-runtime-paper-faithful-semantics-alignment/tasks.md
- specs/071-runtime-paper-faithful-semantics-alignment/quickstart.md
- specs/071-runtime-paper-faithful-semantics-alignment/checklists/requirements.md
- specs/071-runtime-paper-faithful-semantics-alignment/contracts/runtime-paper-faithful-semantics-report-schema.md

Also read Feature 070 evidence:
- src/analysis/topology_timeout_reward_fidelity/report.py
- src/analysis/topology_timeout_reward_fidelity/model.py
- tests/unit/test_topology_timeout_reward_fidelity_report.py
- specs/070-topology-timeout-reward-fidelity/evidence/figure-7-topology-extraction.md

Verify Feature 070 behavior before editing:
- build_feature_070_report().passed is True
- status is blocker_resolution_readiness_with_runtime_divergence
- blockers length is 0
- runtime compatibility divergence remains visible
- no full paper reproduction claim is made

If Feature 070 verification fails, stop and report. Do not implement Feature 071 on a broken base.

Phase 1 — Tests first:

Create tests before runtime implementation.

Unit tests must be under:
- tests/unit/test_runtime_paper_faithful_semantics_alignment_deadline.py
- tests/unit/test_runtime_paper_faithful_semantics_alignment_reward.py
- tests/unit/test_runtime_paper_faithful_semantics_alignment_report.py
- tests/unit/test_runtime_paper_faithful_semantics_alignment_scope_guard.py

Integration test must be under:
- tests/integration/test_runtime_paper_faithful_semantics_alignment_report.py

Required test coverage:

1. Deadline strictness:
- compute absolute_deadline_slot = arrival_slot + phi - 1.
- in paper mode, completion before deadline succeeds.
- in paper mode, completion equal to deadline fails.
- in compatibility mode, completion equal to deadline may succeed only when explicitly requested.

2. Terminal state consistency:
- completed tasks cannot have drop_reason.
- dropped tasks require terminal_slot and drop_reason.
- pending tasks cannot emit reward.

3. Reward Eq. (20):
- inactive task x_n(t)=0 returns explicit no-reward/NaN sentinel.
- successful task reward equals -Phi.
- dropped/thrown task reward equals -C.

4. Reward Eq. (21)-(23):
- Phi_n selects private Phi when d_n^(1)=1.
- Phi_n selects public Phi when d_n^(1)=0.
- Phi_priv = psi_priv - t + 1.
- Phi_pub aggregates only selected d_{n,k}^{(2)} terms.
- Non-selected public terms do not contribute.

5. Runtime modes:
- paper mode is Feature 071 default.
- compatibility mode is explicit and separate.

6. Report:
- Feature071Report contains deadline evidence, terminal-state evidence, reward runtime evidence, compatibility evidence, Feature 068R/069/070 regression evidence, claim boundary, and recommended next feature.
- report.passed is True only when all Feature 071 gates pass.
- report does not claim full paper reproduction.

Phase 2 — Runtime implementation:

Implement the smallest changes needed.

Allowed runtime files:
- src/environment/paper_timeout.py
- src/environment/deadline_rules.py
- src/environment/reward_timing.py
- src/environment/runtime_model.py only if terminal-state integration requires it; justify in the report if changed.

Expected paper_timeout.py behavior:
- expose compute_absolute_deadline(arrival_slot, phi)
- expose is_success_before_deadline(completion_slot, arrival_slot, phi, mode="paper")
- expose terminal_status_from_completion(completion_slot, arrival_slot, phi, completion_kind="private", mode="paper")
- paper mode: success only if completion_slot < arrival_slot + phi - 1
- compatibility mode: preserve equality-at-deadline behavior explicitly

Expected deadline_rules.py behavior:
- delegate to paper_timeout.py or exactly match it
- do not keep contradictory duplicate deadline logic

Expected reward_timing.py behavior:
- expose phi_private(psi_priv, t)
- expose phi_public(selected_terms, t)
- expose select_phi(d1_local, phi_priv, phi_pub)
- expose reward_from_terminal_state(x_active, terminal_status, phi_value, drop_penalty)
- expose reward_slot_for_terminal(terminal_slot)
- success reward = -Phi
- drop reward = -C
- inactive task behavior is explicit and tested
- reward emission requires terminal evidence

Phase 3 — Feature 071 analysis/report package:

Create package:
- src/analysis/runtime_paper_faithful_semantics_alignment/__init__.py
- src/analysis/runtime_paper_faithful_semantics_alignment/__main__.py
- src/analysis/runtime_paper_faithful_semantics_alignment/config.py
- src/analysis/runtime_paper_faithful_semantics_alignment/model.py
- src/analysis/runtime_paper_faithful_semantics_alignment/report.py
- src/analysis/runtime_paper_faithful_semantics_alignment/runner.py

Required functions:
- build_feature_071_report()
- render_feature_071_report(report)
- write_feature_071_report(output_dir)
- validate_scope(paths=None)

Report must prove:
- paper-mode deadline strictness aligned
- compatibility mode explicit
- terminal-state accounting consistent
- reward Eq. (20)-(23) executable
- Feature 068R/069/070 regressions preserved
- full paper reproduction is not claimed
- Feature 072 is the next end-to-end golden trace step

Phase 4 — Update task ledger:

Update only:
- specs/071-runtime-paper-faithful-semantics-alignment/tasks.md

Mark tasks complete only when corresponding tests and implementation exist.

Phase 5 — Scope guard:

Feature 071 final diff may include only:
- specs/071-runtime-paper-faithful-semantics-alignment/**
- src/analysis/runtime_paper_faithful_semantics_alignment/**
- src/environment/paper_timeout.py
- src/environment/deadline_rules.py
- src/environment/reward_timing.py
- src/environment/runtime_model.py only if justified
- tests/unit/test_runtime_paper_faithful_semantics_alignment_*.py
- tests/integration/test_runtime_paper_faithful_semantics_alignment_*.py

Forbidden:
- src/training/**
- src/agents/**
- artifacts/**
- resources/**
- dependency files
- lock files
- generated campaign outputs
- Feature 072+ paths
- PR creation
- merge

Phase 6 — Validation:

Run:

src/.venvmac/bin/python -m unittest tests.unit.test_policy_registry tests.unit.test_baseline_policy_fidelity tests.unit.test_mleo_policy tests.integration.test_baseline_policy_fidelity_flow

src/.venvmac/bin/python -m unittest tests.unit.test_full_hoodie_mechanism_fidelity_batch_report tests.unit.test_full_hoodie_mechanism_fidelity_batch_scope_guard tests.integration.test_full_hoodie_mechanism_fidelity_batch_report

src/.venvmac/bin/python -m unittest tests.unit.test_topology_timeout_reward_fidelity_report tests.unit.test_topology_timeout_reward_fidelity_models tests.unit.test_topology_timeout_reward_fidelity_scope_guard tests.integration.test_topology_timeout_reward_fidelity_report

src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_runtime_paper_faithful_semantics_alignment_*.py'

src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_runtime_paper_faithful_semantics_alignment_*.py'

git diff --check

Run Feature 071 scope validator.

Do not claim full-suite green unless full-suite actually passes.

Phase 7 — Commit and push only:

Commit message:
feat: implement feature 071 runtime paper faithful semantics

Push branch:
071-runtime-paper-faithful-semantics-alignment

Do not open a PR.
Do not merge.

Final report must include:
- branch name
- changed files
- exact runtime files changed
- exact Spec Kit files created/updated
- validation commands and results
- Feature 068R regression result
- Feature 069 regression result
- Feature 070 regression result
- Feature 071 result
- paper-mode deadline behavior
- compatibility-mode behavior
- reward Eq. (20)-(23) implementation evidence
- terminal-state accounting evidence
- local SHA
- remote SHA
- SHA equality result
- clean tree proof
- remote scope proof
- explicit statement that no PR was opened
- explicit statement that no merge was performed
- explicit statement that no full paper reproduction claim is made
- open risks
```
