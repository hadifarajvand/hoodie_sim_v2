"""
Deterministic random seed setup for reproducibility.
"""
import os
import random
from typing import Optional

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None  # type: ignore

try:
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore


def set_seed(seed: int = 42) -> None:
    """
    Set random seeds for reproducibility across Python's random, NumPy, and PyTorch.

    Parameters
    ----------
    seed : int, default 42
        Seed value to use.
    """
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    if np is not None:
        np.random.seed(seed)
    if torch is not None:
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        # Additional settings for deterministic behavior (may impact performance)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def get_seed_from_env(default: int = 42) -> int:
    """
    Retrieve seed from environment variable `HOODIE_SEED`, falling back to default.

    Returns
    -------
    int
        Seed value.
    """
    try:
        return int(os.environ.get("HOODIE_SEED", str(default)))
    except ValueError:
        return default


def auto_seed() -> None:
    """
    Automatically configure seed from environment (or default).
    Convenience function to call at start of scripts.
    """
    seed = get_seed_from_env()
    set_seed(seed)


if __name__ == "__main__":
    # Example usage
    print("Setting seed to 123")
    set_seed(123)
    print("Random sample:", random.random())
    if np is not None:
        print("NumPy sample:", np.random.rand())
    if torch is not None:
        print("Torch sample:", torch.rand(1).item())