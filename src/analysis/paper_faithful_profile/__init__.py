"""Paper-faithful HOODIE baseline configuration.

This module provides profiles that match the HOODIE paper Table 4 specification exactly.
Do NOT use for stress testing or calibration studies.

Paper values (Table 4):
  - N_EA = 20 agents
  - T = 110 time slots
  - Task size: [2.0, 2.1, ..., 5.0] Mbits (step=0.1)
  - Processing density: 0.297 Gcycles/Mbit
  - Horizontal rate: 30 Mbps
  - Vertical rate: 10 Mbps
  - Arrival probability: 0.5
  - Drop penalty C: 40
  - Slot duration: 0.1 seconds
  - Timeout: 20 slots
"""

__all__ = [
    "build_paper_faithful_profile",
    "PAPER_FAITHFUL_PROFILE_NAME",
]

from .config import PAPER_FAITHFUL_PROFILE_NAME, build_paper_faithful_profile
