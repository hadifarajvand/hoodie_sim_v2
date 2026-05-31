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
            rule_text="drop if completion_slot is None or completion_slot > deadline_slot; deadline_slot = arrival_slot + timeout_phi - 1",
            source_reference="docs/paper_notes/runtime_model_evidence.md; src/environment/paper_timeout.py",
            timeout_relation="deadline_slot = arrival_slot + timeout_phi - 1",
            drop_condition="completion_slot is None or completion_slot > deadline_slot",
            provenance="paper_timeout.py encodes the deadline relation recovered from runtime_model_evidence.md",
            paper_semantics_status="source_backed_rule_with_unresolved_terminal_grace_behavior",
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
            paper_semantics_status="verified",
            rule_evidence=rule,
        )
        self.assertEqual(completed.to_dict()["terminal_status"], "completed")
        self.assertIsNone(completed.drop_reason)
        self.assertEqual(completed.to_dict()["rule_evidence"]["timeout_relation"], "deadline_slot = arrival_slot + timeout_phi - 1")

        dropped = TimeoutDropAccountingEvidence(
            task_id="task-2",
            arrival_slot=1,
            timeout_length=4,
            absolute_deadline_slot=5,
            completion_slot=None,
            terminal_slot=5,
            terminal_status="dropped",
            drop_reason="deadline_exceeded",
            paper_semantics_status="blocked_by_unresolved_terminal_grace_behavior",
            rule_evidence=rule,
        )
        self.assertEqual(dropped.terminal_status, "dropped")
        self.assertIsNone(dropped.completion_slot)
        self.assertEqual(dropped.drop_reason, "deadline_exceeded")
        self.assertEqual(dropped.rule_evidence.rule_text, rule.rule_text)

    def test_reward_equation_and_terminal_reward_schema_and_timing(self) -> None:
        equation = RewardEquationEvidence(
            equation_id="reward-eq-1",
            equation_text="r_n(t+1) = -Phi_n(t) for successful processing; -C for dropped tasks; reward omitted when no task arrived",
            source_reference="docs/paper_notes/reward_evidence.md; src/environment/reward_timing.py",
            terms=("Phi_n(t)", "C", "NaN/omitted when no task arrived"),
            recovered_status="source_backed_partial",
            assumption_status="phi_n_t_remains_approximation_backed",
            provenance="reward_evidence.md recovers the paper's success and drop reward structure",
            searched_sources=(
                "docs/paper_notes/reward_evidence.md",
                "artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.md",
                "docs/paper_notes/paper_to_code_mapping.md",
                "src/environment/reward_timing.py",
                "src/analysis/reward_equation_terminal_reward_contract/report.py",
            ),
            blockers=(),
        )
        self.assertEqual(equation.recovered_status, "source_backed_partial")
        self.assertEqual(equation.terms, ("Phi_n(t)", "C", "NaN/omitted when no task arrived"))
        self.assertIn("-Phi_n(t)", equation.equation_text)
        self.assertIn("reward_evidence.md", equation.provenance)

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
