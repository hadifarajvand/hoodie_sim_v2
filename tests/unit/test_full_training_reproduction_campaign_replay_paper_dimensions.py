from __future__ import annotations

from unittest.mock import patch
import torch
import unittest

from src.analysis.full_training_reproduction_campaign import CampaignConfig
from src.analysis.full_training_reproduction_campaign.replay import (
    PAPER_ACTION_COUNT,
    PAPER_STATE_DIM,
    ReplayTransition,
    build_state_window,
    legal_action_mask_to_tuple,
    zero_state_row,
)
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer


def _paper_window() -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(float(index * 10 + col) for col in range(PAPER_STATE_DIM)) for index in range(10))


PAPER_MASK_22 = tuple(True if i in {0, 6, 11, 16, 21} else False for i in range(PAPER_ACTION_COUNT))


class PaperReplayStateVectorTests(unittest.TestCase):
    def test_zero_state_row_uses_74_dimensions(self) -> None:
        row = zero_state_row(state_dim=PAPER_STATE_DIM)
        self.assertEqual(len(row), PAPER_STATE_DIM)
        self.assertTrue(all(v == 0.0 for v in row))

    def test_zero_state_row_defaults_to_3_dimensions(self) -> None:
        row = zero_state_row()
        self.assertEqual(len(row), 3)
        self.assertTrue(all(v == 0.0 for v in row))

    def test_build_state_window_uses_74_dimensions_when_configured(self) -> None:
        history = [tuple(float(i) for i in range(PAPER_STATE_DIM)) for _ in range(5)]
        window = build_state_window(history, state_dim=PAPER_STATE_DIM)
        self.assertEqual(len(window), 10)
        for row in window:
            self.assertEqual(len(row), PAPER_STATE_DIM)


class PaperLegalActionMaskTests(unittest.TestCase):
    def test_paper_legal_action_mask_is_22(self) -> None:
        mask = legal_action_mask_to_tuple({"legal_action_mask": [True] * PAPER_ACTION_COUNT}, action_count=PAPER_ACTION_COUNT)
        self.assertEqual(len(mask), PAPER_ACTION_COUNT)

    def test_legacy_legal_action_mask_is_3(self) -> None:
        mask = legal_action_mask_to_tuple({"local": True, "horizontal": True, "vertical": True})
        self.assertEqual(len(mask), 3)

    def test_paper_mask_defaults_to_false_when_missing(self) -> None:
        mask = legal_action_mask_to_tuple({}, action_count=PAPER_ACTION_COUNT)
        self.assertEqual(len(mask), PAPER_ACTION_COUNT)
        self.assertTrue(all(not m for m in mask))


class ReplayTransitionPaperDimensionTests(unittest.TestCase):
    def test_accepts_10x74_state_window_and_22_action_mask(self) -> None:
        transition = ReplayTransition(
            state=_paper_window(),
            action=0,
            legal_action_mask=PAPER_MASK_22,
            next_state=_paper_window(),
            reward=0.0,
            reward_available=False,
            terminal=False,
            terminal_reason=None,
            pending_at_horizon=False,
            arrival_slot=0,
            completion_or_drop_slot=None,
            agent_id=1,
            episode_id=7,
            step_id=3,
            state_dim=PAPER_STATE_DIM,
            action_count=PAPER_ACTION_COUNT,
        )
        self.assertEqual(len(transition.state), 10)
        self.assertEqual(len(transition.state[0]), PAPER_STATE_DIM)
        self.assertEqual(len(transition.legal_action_mask), PAPER_ACTION_COUNT)

    def test_rejects_wrong_state_dimension(self) -> None:
        with self.assertRaises(ValueError):
            ReplayTransition(
                state=_paper_window(),
                action=0,
                legal_action_mask=PAPER_MASK_22,
                next_state=_paper_window(),
                reward=0.0,
                reward_available=False,
                terminal=False,
                terminal_reason=None,
                pending_at_horizon=False,
                arrival_slot=0,
                completion_or_drop_slot=None,
                agent_id=1,
                episode_id=7,
                step_id=3,
                state_dim=73,
                action_count=PAPER_ACTION_COUNT,
            )

    def test_rejects_wrong_mask_length(self) -> None:
        with self.assertRaises(ValueError):
            ReplayTransition(
                state=_paper_window(),
                action=0,
                legal_action_mask=(True, True, True),
                next_state=_paper_window(),
                reward=0.0,
                reward_available=False,
                terminal=False,
                terminal_reason=None,
                pending_at_horizon=False,
                arrival_slot=0,
                completion_or_drop_slot=None,
                agent_id=1,
                episode_id=7,
                step_id=3,
                state_dim=PAPER_STATE_DIM,
                action_count=PAPER_ACTION_COUNT,
            )

    def test_rejects_out_of_range_action(self) -> None:
        with self.assertRaises(ValueError):
            ReplayTransition(
                state=_paper_window(),
                action=22,
                legal_action_mask=PAPER_MASK_22,
                next_state=_paper_window(),
                reward=0.0,
                reward_available=False,
                terminal=False,
                terminal_reason=None,
                pending_at_horizon=False,
                arrival_slot=0,
                completion_or_drop_slot=None,
                agent_id=1,
                episode_id=7,
                step_id=3,
                state_dim=PAPER_STATE_DIM,
                action_count=PAPER_ACTION_COUNT,
            )

    def test_rejects_negative_action(self) -> None:
        with self.assertRaises(ValueError):
            ReplayTransition(
                state=_paper_window(),
                action=-1,
                legal_action_mask=PAPER_MASK_22,
                next_state=_paper_window(),
                reward=0.0,
                reward_available=False,
                terminal=False,
                terminal_reason=None,
                pending_at_horizon=False,
                arrival_slot=0,
                completion_or_drop_slot=None,
                agent_id=1,
                episode_id=7,
                step_id=3,
                state_dim=PAPER_STATE_DIM,
                action_count=PAPER_ACTION_COUNT,
            )


class DDQNTrainerPaperInitialHistoryTests(unittest.TestCase):
    @patch("src.analysis.full_training_reproduction_campaign.trainer.build_online_network")
    @patch("src.analysis.full_training_reproduction_campaign.trainer.build_target_network")
    def test_initial_history_uses_74_dimensional_rows_when_configured(self, mock_build_target, mock_build_online) -> None:
        mock_build_online.return_value = torch.nn.Linear(PAPER_STATE_DIM, PAPER_ACTION_COUNT)
        mock_build_target.return_value = torch.nn.Linear(PAPER_STATE_DIM, PAPER_ACTION_COUNT)
        config = CampaignConfig(state_dim=PAPER_STATE_DIM, action_count=PAPER_ACTION_COUNT)
        trainer = DDQNTrainer(config)
        history = trainer._initial_history(episode_length=20)
        self.assertEqual(len(history), config.lookback_w)
        for row in history:
            self.assertEqual(len(row), PAPER_STATE_DIM)
            self.assertTrue(all(v == 0.0 for v in row))

    def test_initial_history_uses_3_dimensional_rows_by_default(self) -> None:
        config = CampaignConfig()
        trainer = DDQNTrainer(config)
        history = trainer._initial_history(episode_length=20)
        self.assertEqual(len(history), config.lookback_w)
        for row in history:
            self.assertEqual(len(row), 3)
            self.assertTrue(all(v == 0.0 for v in row))


class PaperActionIndexSemanticsTests(unittest.TestCase):
    def test_paper_faithful_action_index_zero_is_local(self) -> None:
        from src.analysis.full_training_reproduction_campaign.replay import ACTION_INDEX_TO_SEMANTICS_PAPER
        self.assertEqual(ACTION_INDEX_TO_SEMANTICS_PAPER[0], "local")

    def test_paper_faithful_action_index_21_is_cloud(self) -> None:
        from src.analysis.full_training_reproduction_campaign.replay import ACTION_INDEX_TO_SEMANTICS_PAPER
        self.assertEqual(ACTION_INDEX_TO_SEMANTICS_PAPER[21], "cloud")

    def test_paper_faithful_action_count_is_22(self) -> None:
        from src.analysis.full_training_reproduction_campaign.replay import ACTION_INDEX_TO_SEMANTICS_PAPER
        self.assertEqual(len(ACTION_INDEX_TO_SEMANTICS_PAPER), 22)

    def test_paper_faithful_has_horizontal_edge_indices(self) -> None:
        from src.analysis.full_training_reproduction_campaign.replay import ACTION_INDEX_TO_SEMANTICS_PAPER
        for i in range(1, 21):
            self.assertIn(i, ACTION_INDEX_TO_SEMANTICS_PAPER)
            self.assertTrue(ACTION_INDEX_TO_SEMANTICS_PAPER[i].startswith("horizontal_"))


if __name__ == "__main__":
    unittest.main()
