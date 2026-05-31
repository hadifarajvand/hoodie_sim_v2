from __future__ import annotations

import unittest

from src.analysis.topology_timeout_reward_fidelity.model import (
    Feature070Blocker,
    NeighborLegalityEvidence,
    RewardEquationEvidence,
    TerminalRewardEvidence,
    TimeoutDropRuleEvidence,
    TimeoutDropAccountingEvidence,
    TopologyEvidenceReport,
)
from src.environment.paper_timeout import build_timeout_contract
from src.environment.reward_timing import reward_for_terminal_task
from src.environment.task import Task


class TopologyTimeoutRewardFidelityModelTests(unittest.TestCase):
    def test_topology_evidence_report_schema_and_blocker_state(self) -> None:
        blocker = Feature070Blocker(
            category="topology",
            severity="blocking",
            description="Structured adjacency is missing.",
            evidence_source="specs/070-topology-timeout-reward-fidelity/contracts/feature-070-fidelity-report-schema.md",
            next_action="Recover a structured neighbor graph artifact.",
        )
        report = TopologyEvidenceReport(
            source_agent_id="1",
            edge_agent_ids=("1", "2", "3"),
            cloud_id="cloud",
            adjacency_matrix_source="specs/070-topology-timeout-reward-fidelity/evidence/figure-7-topology-extraction.md",
            neighbor_map={"1": ("2", "3"), "2": ("1",), "3": ("1",)},
            cloud_reachability=False,
            evidence_status="verified_manual_paper_extraction",
            provenance="manual paper extraction from specs/070-topology-timeout-reward-fidelity/evidence/figure-7-topology-extraction.md",
            blockers=(blocker,),
        )

        payload = report.to_dict()
        self.assertEqual(payload["source_agent_id"], "1")
        self.assertEqual(payload["edge_agent_ids"], ["1", "2", "3"])
        self.assertEqual(payload["adjacency_matrix_source"], "specs/070-topology-timeout-reward-fidelity/evidence/figure-7-topology-extraction.md")
        self.assertFalse(payload["cloud_reachability"])
        self.assertEqual(payload["evidence_status"], "verified_manual_paper_extraction")
        self.assertEqual(payload["provenance"], "manual paper extraction from specs/070-topology-timeout-reward-fidelity/evidence/figure-7-topology-extraction.md")
        self.assertEqual(payload["blockers"][0]["category"], "topology")

    def test_feature_070_fidelity_report_rejects_passed_with_with_blockers_status(self) -> None:
        from src.analysis.topology_timeout_reward_fidelity.model import Feature070FidelityReport
        from src.analysis.topology_timeout_reward_fidelity.report import (
            _feature_068r_regression_evidence,
            _feature_069_regression_evidence,
            _neighbor_legality_evidence,
            _reward_equation_evidence,
            _timeout_drop_accounting_evidence,
            _timeout_drop_rule_evidence,
            _topology_evidence,
        )

        with self.assertRaises(ValueError) as ctx:
            Feature070FidelityReport(
                feature_name="Feature 070 - Topology, Timeout/Drop, and Reward Fidelity",
                status="mechanism_fidelity_readiness_with_blockers",
                passed=True,
                changed_files=("specs/070-topology-timeout-reward-fidelity/tasks.md",),
                topology_evidence=_topology_evidence(),
                neighbor_legality_evidence=_neighbor_legality_evidence(),
                timeout_drop_rule_evidence=_timeout_drop_rule_evidence(),
                timeout_drop_accounting_evidence=_timeout_drop_accounting_evidence(),
                reward_equation_evidence=_reward_equation_evidence(),
                terminal_reward_evidence=TerminalRewardEvidence(
                    task_id="task-1",
                    selected_action="A2",
                    terminal_status="completed",
                    terminal_slot=3,
                    reward_slot=4,
                    reward_value=1.0,
                    reward_equation_id="reward-eq-1",
                    timing_valid=True,
                ),
                blockers=(),
                feature_068r_regression_status=_feature_068r_regression_evidence(),
                feature_069_regression_status=_feature_069_regression_evidence(),
                paper_claim_boundary="boundary",
                recommended_next_feature="next",
            )

        self.assertIn("with_blockers", str(ctx.exception))

    def test_neighbor_legality_requires_topology_and_mask_and_no_self_destination(self) -> None:
        legal = NeighborLegalityEvidence(
            source_agent_id="A1",
            destination_agent_id="A2",
            is_neighbor=True,
            is_self_destination=False,
            legal_under_topology=True,
            legal_under_action_mask=True,
            final_legal=True,
        )
        self.assertTrue(legal.to_dict()["final_legal"])

        self_destination = NeighborLegalityEvidence(
            source_agent_id="A1",
            destination_agent_id="A1",
            is_neighbor=True,
            is_self_destination=True,
            legal_under_topology=True,
            legal_under_action_mask=True,
            final_legal=False,
        )
        self.assertFalse(self_destination.final_legal)
        self.assertTrue(self_destination.is_self_destination)

        mask_only = NeighborLegalityEvidence(
            source_agent_id="A1",
            destination_agent_id="A3",
            is_neighbor=True,
            is_self_destination=False,
            legal_under_topology=False,
            legal_under_action_mask=True,
            final_legal=False,
        )
        self.assertFalse(mask_only.final_legal)
        self.assertFalse(mask_only.legal_under_topology)
        self.assertTrue(mask_only.legal_under_action_mask)

    def test_timeout_drop_accounting_schema_and_terminal_requirements(self) -> None:
        rule = TimeoutDropRuleEvidence(
            rule_text=(
                "absolute_deadline_slot = t + phi_n(t) - 1; success requires psi_n^priv(t) < t + phi_n(t) - 1 "
                "or psi_n,k^pub(t') < t + phi_n(t) - 1; otherwise the task is thrown"
            ),
            source_reference=(
                "docs/paper_notes/runtime_model_evidence.md; "
                "artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.md; "
                "src/environment/paper_timeout.py"
            ),
            timeout_relation="deadline_slot = arrival_slot + timeout_phi - 1",
            strict_success_condition="psi_n^priv(t) < t + phi_n(t) - 1 or psi_n,k^pub(t') < t + phi_n(t) - 1",
            drop_condition="completion_slot is None or completion_slot >= deadline_slot",
            provenance="runtime_model_evidence.md and the paper mechanism registry recover the strict paper rule",
            paper_semantics_status="paper_backed_recovered_with_runtime_compatibility_divergence",
            runtime_compatibility_divergence="completion_slot == deadline_slot is accepted by the runtime helper but rejected by the paper's strict success condition",
            searched_sources=(
                "docs/paper_notes/runtime_model_evidence.md",
                "artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.md",
                "docs/paper_notes/paper_to_code_mapping.md",
                "src/environment/paper_timeout.py",
                "src/environment/deadline_rules.py",
                "src/environment/environment.py",
            ),
        )
        completed = TimeoutDropAccountingEvidence(
            task_id="task-1",
            arrival_slot=1,
            timeout_length=4,
            absolute_deadline_slot=5,
            completion_slot=3,
            terminal_slot=3,
            terminal_status="completed",
            drop_reason=None,
            paper_semantics_status="paper_backed_recovered_with_runtime_compatibility_divergence",
            runtime_compatibility_divergence="completion_slot == deadline_slot is accepted by the runtime helper but rejected by the paper's strict success condition",
            rule_evidence=rule,
        )
        self.assertEqual(completed.to_dict()["terminal_status"], "completed")
        self.assertIsNone(completed.drop_reason)
        self.assertEqual(completed.to_dict()["rule_evidence"]["timeout_relation"], "deadline_slot = arrival_slot + timeout_phi - 1")
        self.assertIn("strict_success_condition", completed.to_dict()["rule_evidence"])

        dropped = TimeoutDropAccountingEvidence(
            task_id="task-2",
            arrival_slot=1,
            timeout_length=4,
            absolute_deadline_slot=5,
            completion_slot=None,
            terminal_slot=5,
            terminal_status="dropped",
            drop_reason="deadline_exceeded",
            paper_semantics_status="paper_backed_recovered_with_runtime_compatibility_divergence",
            runtime_compatibility_divergence="completion_slot == deadline_slot is accepted by the runtime helper but rejected by the paper's strict success condition",
            rule_evidence=rule,
        )
        self.assertEqual(dropped.terminal_status, "dropped")
        self.assertIsNone(dropped.completion_slot)
        self.assertEqual(dropped.drop_reason, "deadline_exceeded")
        self.assertEqual(dropped.rule_evidence.rule_text, rule.rule_text)

        paper_contract = build_timeout_contract(arrival_slot=1, timeout_phi=4, completion_slot=4)
        self.assertTrue(paper_contract.dropped_due_to_timeout)
        self.assertEqual(paper_contract.deadline_slot, 4)

        compatibility_contract = build_timeout_contract(arrival_slot=1, timeout_phi=4, completion_slot=4, mode="compatibility")
        self.assertFalse(compatibility_contract.dropped_due_to_timeout)
        self.assertEqual(compatibility_contract.deadline_slot, 4)
        self.assertIn(">= deadline_slot", rule.drop_condition)

    def test_reward_equation_and_terminal_reward_schema_and_timing(self) -> None:
        equation = RewardEquationEvidence(
            equation_id="reward-eq-1",
            equation_text=(
                "Eq. (20): r_n(t+1) = NaN if x_n(t) = 0; r_n(t+1) = -Phi_n(t) if successfully processed; "
                "r_n(t+1) = -C otherwise. Eq. (21): Phi_n(t) = Phi_n^priv(t) when d_n^(1)=1 and "
                "Phi_n(t) = Phi_n^pub(t) when d_n^(1)=0. Eq. (22): Phi_n^priv(t) = psi_n^priv(t) - t + 1. "
                "Eq. (23): Phi_n^pub(t) = sum_{k in N \\ {n}} sum_{t'=t}^T d_{n,k}^{(2)}(t) * "
                "(psi_{n,k}^pub(t') - t + 1)"
            ),
            equation_20_text="r_n(t+1) = NaN if x_n(t)=0; r_n(t+1) = -Phi_n(t) if successfully processed before timeout; r_n(t+1) = -C otherwise (task thrown)",
            equation_21_text="Phi_n(t) = Phi_n^priv(t) if d_n^(1)=1; Phi_n(t) = Phi_n^pub(t) if d_n^(1)=0",
            equation_22_text="Phi_n^priv(t) = psi_n^priv(t) - t + 1",
            equation_23_text="Phi_n^pub(t) = sum over k in N \\ {n} of sum over t' = t..T d_{n,k}^{(2)}(t) * (psi_{n,k}^pub(t') - t + 1)",
            source_reference="resources/papers/hoodie/ocr/merged.tex; docs/paper_notes/reward_evidence.md",
            terms=("x_n(t)", "Phi_n(t)", "Phi_n^priv(t)", "Phi_n^pub(t)", "psi_n^priv(t)", "psi_{n,k}^pub(t')", "d_n^(1)", "d_{n,k}^{(2)}", "C"),
            recovered_status="paper_backed_recovered",
            assumption_status="paper_backed",
            provenance="resources/papers/hoodie/ocr/merged.tex and reward_evidence.md recover Eq. (20)-(23) directly",
            runtime_compatibility_divergence="src/environment/reward_timing.py still uses completion_slot - arrival_slot for completed tasks, which is an off-by-one compatibility divergence from Phi_n^priv(t)",
            searched_sources=(
                "docs/paper_notes/reward_evidence.md",
                "artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.md",
                "docs/paper_notes/paper_to_code_mapping.md",
                "src/environment/reward_timing.py",
                "src/analysis/reward_equation_terminal_reward_contract/report.py",
            ),
            blockers=(),
        )
        self.assertEqual(equation.recovered_status, "paper_backed_recovered")
        self.assertEqual(
            equation.terms,
            ("x_n(t)", "Phi_n(t)", "Phi_n^priv(t)", "Phi_n^pub(t)", "psi_n^priv(t)", "psi_{n,k}^pub(t')", "d_n^(1)", "d_{n,k}^{(2)}", "C"),
        )
        self.assertIn("Eq. (20)", equation.equation_text)
        self.assertIn("Eq. (23)", equation.equation_text)
        self.assertIn("reward_evidence.md", equation.provenance)
        self.assertIn("completion_slot - arrival_slot", equation.runtime_compatibility_divergence)

        task = Task(
            task_id=1,
            source_agent_id=1,
            arrival_slot=10,
            size=1.0,
            processing_density=1.0,
            timeout_length=4,
            absolute_deadline_slot=13,
            completion_slot=13,
            terminal_outcome="completed",
            reward_emitted=True,
        )
        self.assertEqual(reward_for_terminal_task(task), -4.0)
        self.assertEqual(reward_for_terminal_task(task, mode="compatibility"), -3.0)

        terminal = TerminalRewardEvidence(
            task_id="task-1",
            selected_action="A2",
            terminal_status="completed",
            terminal_slot=3,
            reward_slot=4,
            reward_value=1.0,
            reward_equation_id="reward-eq-1",
            timing_valid=True,
        )
        self.assertGreaterEqual(terminal.reward_slot, terminal.terminal_slot)
        self.assertTrue(terminal.timing_valid)
        self.assertEqual(terminal.reward_equation_id, "reward-eq-1")

        blocked = RewardEquationEvidence(
            equation_id="reward-eq-2",
            equation_text="blocked",
            equation_20_text="blocked",
            equation_21_text="blocked",
            equation_22_text="blocked",
            equation_23_text="blocked",
            source_reference="specs/070-topology-timeout-reward-fidelity/research.md",
            terms=(),
            recovered_status="blocked",
            assumption_status="assumption_backed",
            provenance="reward equation exact Phi_n(t) form remains unresolved",
            searched_sources=("docs/paper_notes/reward_evidence.md",),
            blockers=(Feature070Blocker(
                category="reward",
                severity="blocking",
                description="Exact reward equation remains unresolved.",
                evidence_source="specs/070-topology-timeout-reward-fidelity/research.md",
                next_action="Recover the exact equation from paper evidence.",
            ),),
        )
        self.assertEqual(blocked.recovered_status, "blocked")
        self.assertEqual(blocked.assumption_status, "assumption_backed")


if __name__ == "__main__":
    unittest.main()
