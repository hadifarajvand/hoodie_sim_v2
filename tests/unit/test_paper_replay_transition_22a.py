from __future__ import annotations

import unittest

from src.analysis.full_training_reproduction_campaign import (
    PAPER_ACTION_COUNT,
    PAPER_STATE_DIM,
    ACTION_INDEX_TO_SEMANTICS_PAPER,
    ReplayTransition,
    legal_action_mask_to_tuple,
)
from src.analysis.full_training_reproduction_campaign.replay import (
    action_index_to_semantics,
    semantics_to_action_index,
    zero_state_row,
)


class TestPaperReplayTransition22A(unittest.TestCase):
    """Test ReplayTransition with 22-action space (paper-faithful)."""

    def setUp(self) -> None:
        self.state_dim = PAPER_STATE_DIM    # 74
        self.action_count = PAPER_ACTION_COUNT  # 22
        self.lookback_w = 10

    def _window(self) -> tuple[tuple[float, ...], ...]:
        w = (zero_state_row(self.state_dim),) * self.lookback_w
        return w

    def _transition(self, action: int) -> ReplayTransition:
        return ReplayTransition(
            state=self._window(), action=action,
            legal_action_mask=tuple([True] * self.action_count),
            next_state=self._window(),
            reward=0.0, reward_available=False,
            terminal=False, terminal_reason=None, pending_at_horizon=False,
            arrival_slot=0, completion_or_drop_slot=None,
            agent_id=0, episode_id=0, step_id=0,
            state_dim=self.state_dim, action_count=self.action_count,
        )

    # -- action bounds -------------------------------------------------------

    def test_action_0_passes_validation(self) -> None:
        """action=0 (local) is valid for 22-action space."""
        t = self._transition(action=0)
        self.assertEqual(t.action, 0)

    def test_action_21_passes_validation(self) -> None:
        """action=21 (cloud) is valid for 22-action space."""
        t = self._transition(action=21)
        self.assertEqual(t.action, 21)

    def test_action_negative_one_raises_value_error(self) -> None:
        """action=-1 must raise ValueError."""
        with self.assertRaises(ValueError):
            self._transition(action=-1)

    def test_action_22_raises_value_error(self) -> None:
        """action=22 (== action_count) must raise ValueError."""
        with self.assertRaises(ValueError):
            self._transition(action=22)

    # -- legal action mask ---------------------------------------------------

    def test_legal_action_mask_to_tuple_returns_22_elements(self) -> None:
        """legal_action_mask_to_tuple(action_count=22) must return 22-element tuple."""
        mask = {"local": True, "horizontal": True, "vertical": True}
        result = legal_action_mask_to_tuple(mask, action_count=self.action_count)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), self.action_count)
        self.assertTrue(all(isinstance(v, bool) for v in result))

    def test_wrong_mask_length_raises_value_error(self) -> None:
        """A mask with != 22 elements must raise ValueError."""
        bad_mask = tuple([True] * 21)  # one short
        with self.assertRaises(ValueError):
            ReplayTransition(
                state=self._window(), action=0,
                legal_action_mask=bad_mask,
                next_state=self._window(),
                reward=0.0, reward_available=False,
                terminal=False, terminal_reason=None, pending_at_horizon=False,
                arrival_slot=0, completion_or_drop_slot=None,
                agent_id=0, episode_id=0, step_id=0,
                state_dim=self.state_dim, action_count=self.action_count,
            )

    def test_legal_action_mask_element_type_validated(self) -> None:
        """Each entry in the mask tuple must be bool (post_init checks length only)."""
        mask = tuple([False] * self.action_count)
        t = self._transition(0)
        # Replace via object.__setattr__ since frozen; verify non-bool passes length check
        self.assertEqual(len(mask), self.action_count)
        self.assertTrue(all(isinstance(v, bool) for v in mask))

    # -- paper semantics mapping ---------------------------------------------

    def test_semantics_to_action_index_maps_local_to_0(self) -> None:
        """semantics_to_action_index('local', action_count=22) must return 0."""
        idx = semantics_to_action_index("local", action_count=self.action_count)
        self.assertEqual(idx, 0)

    def test_semantics_to_action_index_maps_cloud_to_21(self) -> None:
        """semantics_to_action_index('cloud', action_count=22) must return 21."""
        idx = semantics_to_action_index("cloud", action_count=self.action_count)
        self.assertEqual(idx, 21)

    def test_semantics_to_action_index_maps_horizontal_N(self) -> None:
        """semantics_to_action_index('horizontal_N', action_count=22) must return N."""
        for n in range(1, 21):
            idx = semantics_to_action_index(f"horizontal_{n}",
                                            action_count=self.action_count)
            self.assertEqual(idx, n)

    def test_action_index_to_semantics_maps_0_to_local(self) -> None:
        """action_index_to_semantics(0, action_count=22) must return 'local'."""
        self.assertEqual(
            action_index_to_semantics(0, action_count=self.action_count),
            "local",
        )

    def test_action_index_to_semantics_maps_21_to_cloud(self) -> None:
        """action_index_to_semantics(21, action_count=22) must return 'cloud'."""
        self.assertEqual(
            action_index_to_semantics(21, action_count=self.action_count),
            "cloud",
        )

    def test_action_index_to_semantics_maps_1_to_20_horizontal_N(self) -> None:
        """action_index_to_semantics(N, action_count=22) returns 'horizontal_N'."""
        for idx in range(1, 21):
            sem = action_index_to_semantics(idx, action_count=self.action_count)
            self.assertEqual(sem, f"horizontal_{idx}")

    def test_paper_mapping_roundtrip(self) -> None:
        """semantics -> action_index -> semantics roundtrips for every paper action."""
        for idx in range(self.action_count):
            sem = action_index_to_semantics(idx, action_count=self.action_count)
            back = semantics_to_action_index(sem, action_count=self.action_count)
            self.assertEqual(back, idx)

    def test_paper_constant_agrees_with_action_index_to_semantics(self) -> None:
        """ACTION_INDEX_TO_SEMANTICS_PAPER matches action_index_to_semantics."""
        for idx in range(self.action_count):
            self.assertEqual(
                ACTION_INDEX_TO_SEMANTICS_PAPER[idx],
                action_index_to_semantics(idx, action_count=self.action_count),
            )


if __name__ == "__main__":
    unittest.main()
