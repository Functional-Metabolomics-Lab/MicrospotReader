from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import src.microspotreader.spot_classes.SpotList as SpotList


@dataclass
class GridPoint:
    x: float
    y: float
    distance_to_spot_px: float = np.inf

    def check_for_spot(self, spot_list: SpotList.SpotList, threshold_px: float):
        """Checks if any spot in a spotlist is closer to the gridpoint than the threshold.

        Args:
            spot_list (SpotList): Spotlist to check.
            threshold_px (float): distance threshold in pixels

        Returns:
            bool: True if a spot closer than the threshold exists, false otherwise
        """
        self.distance_to_spot_px = np.min(
            [spot.distance_to_gridpoint(self) for spot in spot_list]
        )
        return self.distance_to_spot_px >= threshold_px
