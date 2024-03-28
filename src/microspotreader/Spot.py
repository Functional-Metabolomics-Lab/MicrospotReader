from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np
from skimage.draw import disk

if TYPE_CHECKING:
    import src.microspotreader.Grid as Grid
    import src.microspotreader.GridPoint as GridPoint


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

    def distance_to_gridpoint(self, gridpoint: GridPoint.GridPoint):
        """Calculates the euclidean distance between the spot and a grid-point.

        Args:
            gridpoint (GridPoint): Point in a Grid object

        Returns:
            float: Euclidean distance between spot and gridpoint
        """
        return np.linalg.norm(
            np.array((self.x, self.y)) - np.array((gridpoint.x, gridpoint.y))
        )

    def deviation_from_grid(self, grid: Grid.Grid):
        """Calculates the minmimum distance of a spot from an intersection in a grid

        Args:
            grid (Grid): Grid to check deviation from

        Returns:
            float: minimum distance of spot from an intersection in a grid
        """
        return np.min(
            [self.distance_to_gridpoint(point) for point in grid.intersections]
        )

    def add_index(
        self,
        row_idx: int,
        col_idx: int,
        row_name_dictionary: dict = {
            i: "abcdefghijklmnopqrstuvwxyz"[i - 1] for i in range(1, 27)
        },
    ):
        """Adds index values to the spot

        Args:
            row_idx (int): row index of the spot
            col_idx (int): column index of the spot
            row_name_dictionary (dictionary, optional): dictionary to add a row name to the spot. Defaults to {i:"abcdefghijklmnopqrstuvwxyz"[i - 1] for i in range(1,27)}.
        """

        self.row = row_idx
        self.col = col_idx

        self.row_name = row_name_dictionary[row_idx]

    def get_intensity(self, img: np.array, rad: int = None) -> None:
        """
        ## Description

        Determines the average pixel-intensity of a spot in an image.

        ## Input

        |Parameter|Type|Description|
        |---|---|---|
        |img|np.array|Image to extract spot-intensity from|
        |rad|int|radius to be used for intensity determination, if None or 0: use the radius determined by spot-detection|

        ## Output

        Avgerage intensity of pixels in spot.
        """
        if rad == None or rad == 0:
            radius = self.radius
        else:
            radius = rad

        try:
            # Indices of all pixels part of the current spot
            rr, cc = disk((self.y, self.x), radius)
            # Mean intensity of all pixels within the spot
            self.int = img[rr, cc].sum() / len(rr)
            return self.int

        except:
            print(
                f"Spot at Coordinates ({self.x}, {self.y}) could not be evaluated: (Partly) Out of Bounds."
            )
