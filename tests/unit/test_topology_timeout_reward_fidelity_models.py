from __future__ import annotations

import unittest

from src.analysis.topology_timeout_reward_fidelity.model import (
    Feature070Blocker,
    NeighborLegalityEvidence,
    RewardEquationEvidence,
    TerminalRewardEvidence,
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
        )
        self.assertEqual(completed.to_dict()["terminal_status"], "completed")
        self.assertIsNone(completed.drop_reason)

        dropped = TimeoutDropAccountingEvidence(
            task_id="task-2",
            arrival_slot=1,
            timeout_length=4,
            absolute_deadline_slot=5,
            completion_slot=None,
            terminal_slot=5,
            terminal_status="dropped",
            drop_reason="deadline_exceeded",
            paper_semantics_status="blocked",
        )
        self.assertEqual(dropped.terminal_status, "dropped")
        self.assertIsNone(dropped.completion_slot)
        self.assertEqual(dropped.drop_reason, "deadline_exceeded")

    def test_reward_equation_and_terminal_reward_schema_and_timing(self) -> None:
        equation = RewardEquationEvidence(
            equation_id="reward-eq-1",
            equation_text="R_t = terminal_reward - wait_penalty",
            source_reference="specs/070-topology-timeout-reward-fidelity/research.md",
            terms=("terminal_reward", "wait_penalty"),
            recovered_status="recovered",
            assumption_status="verified",
            blockers=(),
        )
        self.assertEqual(equation.recovered_status, "recovered")
        self.assertEqual(equation.terms, ("terminal_reward", "wait_penalty"))
        self.assertIn("R_t", equation.equation_text)

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
