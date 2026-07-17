from src.environment.evaluation_gym_adapter import (
    EvaluationHoodieGymEnvironment,
)
from src.hoodie.experiments.runtime_fixes import install_runtime_fixes


def test_slotted_dataclass_reset_uses_explicit_base_call() -> None:
    install_runtime_fixes()
    environment = EvaluationHoodieGymEnvironment(episode_length=3)
    observation, info = environment.reset(seed=7)
    assert isinstance(observation, dict)
    assert isinstance(info, dict)
