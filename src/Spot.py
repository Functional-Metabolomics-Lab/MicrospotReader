from dataclasses import dataclass, field

import numpy as np


@dataclass
class Spot:
    intensity: float = np.nan
    x: float = np.nan
    y: float = np.nan
    radius: int = np.nan
    halo_radius: int = np.nan
    row: int = np.nan
    row_name: str = field(default_factory=lambda: str())
    col: int = np.nan
    note: str = field(default_factory=lambda: str())
    type: str = field(default_factory=lambda: str())
