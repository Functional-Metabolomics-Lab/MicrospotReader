from dataclasses import dataclass, field

import numpy as np
from skimage.draw import disk


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

    def draw(self, image: np.array, value: int, radius: int = 0):
        """Draws the spot at its coordinates in the given image, with an intensity defined by value and a radius defined by radius.

        Args:
            image (np.array): Image that the spot should be drawn in
            value (int): Value that the spot should take in the image
            radius (int, optional): Radius that the spot should be drawn with, if 0 self.radius will be used. Defaults to 0.

        Returns:
            np.array: image containing the drawn spot.
        """
        if radius == 0:
            radius = self.radius

        rr, cc = disk((self.y, self.x), radius=radius)
        try:
            image[rr, cc] = value
        except:
            print(
                f"Spot at Coordinates ({self.x}, {self.y}) could not be drawn: Out of Bounds."
            )
        return image
