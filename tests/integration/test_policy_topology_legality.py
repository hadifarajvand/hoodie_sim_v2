from __future__ import annotations

import unittest

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.task import Task
from src.environment.topology import TopologyGraph
from src.environment.trace_source import TraceSource
from src.policies import (
    BalancedCooperationOffloadingPolicy,
    FullLocalComputingPolicy,
    HorizontalOffloadingPolicy,
    MinimumLatencyEstimateOffloadingPolicy,
    PolicyContext,
    RandomOffloadingPolicy,
    VerticalOffloadingPolicy,
)


class PolicyTopologyLegalityTests(unittest.TestCase):
    """Integration test: all 6 baseline policies must respect topology-constrained legal action masks.

    The legal_action_mask is produced by HoodieGymEnvironment.legal_action_mask()
    and reflects the topology graph. Policies MUST only return actions that are
    marked True in this mask. This test verifies that invariant holds for every
    node in a known topology under repeated sampling (to catch probabilistic
    violations).
    """

    def setUp(self) -> None:
        # Topology: a 4-node graph where node 4 is isolated (no horizontal neighbors).
        #
        #   1 ←→ 2 ←→ 3     4 (isolated)
        #
        #   horizontal reachability:
        #     1 → {2}          (True)
        #     2 → {1, 3}       (True)
        #     3 → {2}          (True)
        #     4 → {}           (False — no legal horizontal destinations)
        self.topology = TopologyGraph(
            node_ids=("1", "2", "3", "4"),
            legal_adjacency={
                "1": ("2",),
                "2": ("1", "3"),
                "3": ("2",),
                "4": (),
            },
        )

        # Seed all stochastic policies deterministically so the test is
        # reproducible.
        self.policies: dict[str, object] = {
            "FLC": FullLocalComputingPolicy(),
            "RO": RandomOffloadingPolicy(seed=42),
            "HO": HorizontalOffloadingPolicy(),
            "VO": VerticalOffloadingPolicy(),
            "BCO": BalancedCooperationOffloadingPolicy(),
            "MLEO": MinimumLatencyEstimateOffloadingPolicy(),
        }

        # A single environment instance that we reuse across all sub-tests.
        # The env is reset per test method but the topology is fixed.
        self.env = HoodieGymEnvironment(
            episode_length=10,
            topology=self.topology,
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            compute_config=ComputeConfig(cpu_capacity_per_slot_agent=1.0),
            trace_source=TraceSource.from_seed("topology-legality-test"),
            policy_name="test",
        )
        self.env.reset(seed=42)

    def _task_at(self, source_agent_id: int, task_id: int = 1) -> Task:
        """Create a minimal realistic task at the given source node."""
        return Task(
            task_id=task_id,
            source_agent_id=source_agent_id,
            arrival_slot=0,
            size=10.0,
            processing_density=2.0,
            timeout_length=5,
            absolute_deadline_slot=5,
            cycles_required=20.0,
            cycles_remaining=20.0,
        )

    # ------------------------------------------------------------------
    # Per-policy test methods — each verifies topology legality
    # ------------------------------------------------------------------

    def test_flc_respects_topology_mask(self) -> None:
        self._assert_policy_legal_across_all_nodes("FLC", 100)

    def test_ro_respects_topology_mask(self) -> None:
        self._assert_policy_legal_across_all_nodes("RO", 100)

    def test_ho_respects_topology_mask(self) -> None:
        self._assert_policy_legal_across_all_nodes("HO", 100)

    def test_vo_respects_topology_mask(self) -> None:
        self._assert_policy_legal_across_all_nodes("VO", 100)

    def test_bco_respects_topology_mask(self) -> None:
        self._assert_policy_legal_across_all_nodes("BCO", 100)

    def test_mleo_respects_topology_mask(self) -> None:
        self._assert_policy_legal_across_all_nodes("MLEO", 100)

    # ------------------------------------------------------------------
    # Combined test — all 6 policies in a single loop
    # ------------------------------------------------------------------

    def test_all_six_baseline_policies_respect_topology_mask(self) -> None:
        """Run every policy against every node with repeated sampling."""
        violations: list[str] = []
        for name, policy in self.policies.items():
            for source_node in ("1", "2", "3", "4"):
                violations.extend(
                    self._sample_policy(name, policy, source_node, 50)
                )
        self.assertEqual(
            violations,
            [],
            f"Topology legality violations detected ({len(violations)}):\n"
            + "\n".join(violations),
        )

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _assert_policy_legal_across_all_nodes(
        self, name: str, samples: int
    ) -> None:
        """Assert that *name* returns only legal actions at every node."""
        policy = self.policies[name]
        violations: list[str] = []
        for source_node in ("1", "2", "3", "4"):
            violations.extend(
                self._sample_policy(name, policy, source_node, samples)
            )
        self.assertEqual(
            violations,
            [],
            f"{name}: topology legality violations ({len(violations)}):\n"
            + "\n".join(violations),
        )

    def _sample_policy(
        self,
        name: str,
        policy: object,
        source_node: str,
        samples: int,
    ) -> list[str]:
        """Run *policy* for *samples* iterations at *source_node*.

        Returns a list of violation messages (empty = all legal).
        """
        violations: list[str] = []
        task = self._task_at(int(source_node))
        legal_action_mask = self.env.legal_action_mask(task)
        observation = self.env.observe_flat(task)

        for _ in range(samples):
            context = PolicyContext(
                observation=observation,
                legal_action_mask=legal_action_mask,
                trace_history=("topology-legality-test",),
            )
            action = policy.choose_action(context)  # type: ignore[union-attr]

            if not legal_action_mask.get(action, False):
                violations.append(
                    f"  {name} @ node {source_node}: "
                    f"returned '{action}' not in mask {legal_action_mask}"
                )

        return violations


if __name__ == "__main__":
    unittest.main()
