from dataclasses import dataclass

import numpy as np


@dataclass
class GridPoint:
    x: float
    y: float
    distance_to_spot_px: float = np.inf
