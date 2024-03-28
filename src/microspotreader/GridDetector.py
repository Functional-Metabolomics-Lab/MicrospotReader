from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from skimage.transform import hough_line, hough_line_peaks

import src.microspotreader.Grid as Grid
import src.microspotreader.GridLine as GridLine

if TYPE_CHECKING:
    import src.microspotreader.SpotList as SpotList


class GridDetector:
    settings = {
        "line_detection": {
            "maximum_tilt": 5,
            "minimum_distance_px": 80,
            "threshold": 0.2,
        },
        "spot_mask": {"spot_radius": 5},
    }

    def __init__(self, image: np.array, spot_list: SpotList.SpotList) -> None:
        self.spot_list = spot_list
        self.image = image

    def create_spot_mask(self, spot_radius: int = 5) -> np.array:
        """Creates a mask with the dimensions of the image in GridDetector that contains drawn disks of a specified radius at each spots position.

        Args:
            spot_radius (int, optional): Radius of the disk that should be drawn. Defaults to 5.

        Returns:
            np.array: Mask containing drawn disks for each spot in the detectors spotlist.
        """
        self.spot_mask = np.zeros(self.image.shape)
        for spot in self.spot_list:
            spot.draw(self.spot_mask, 255, spot_radius)

        return self.spot_mask

    def sort_lines_by_alignment(
        self, grid_lines: list[GridLine.GridLine]
    ) -> tuple[list[GridLine.GridLine], list[GridLine.GridLine]]:
        """Sorts a list of gridlines into lists of horizontal and vertical lines.

        Args:
            grid_lines (list[GridLine]): List of gridlines to be sorted

        Returns:
            tuple[list[GridLine], list[GridLine]]: List of horizontal lines, list of vertical lines
        """

        horizontal_lines = [
            line
            for line in grid_lines
            if np.abs(np.rad2deg(line.angle))
            <= self.settings["line_detection"]["maximum_tilt"]
        ]

        vertical_lines = [
            line
            for line in grid_lines
            if np.abs(np.rad2deg(line.angle))
            >= 90 - self.settings["line_detection"]["maximum_tilt"]
        ]
        return horizontal_lines, vertical_lines

    def detect_gridlines(self, spot_mask: np.array) -> list[GridLine.GridLine]:
        """Detects lines in the spot-mask.

        Args:
            spot_mask (array): Spotmask obtained by the create_spot_mask method.

        Returns:
            list: List of gridlines detected in the spot mask
        """

        hough_transform, ang, dist = hough_line(spot_mask)

        # Set the intensites of all lines with unwanted angles to 0.
        hough_transform[
            :,
            np.r_[
                self.settings["line_detection"]["maximum_tilt"] : 89
                - self.settings["line_detection"]["maximum_tilt"],
                91
                + self.settings["line_detection"]["maximum_tilt"] : 180
                - self.settings["line_detection"]["maximum_tilt"],
            ],
        ] = 0

        _, angle, distance = hough_line_peaks(
            hspace=hough_transform,
            angles=ang,
            dists=dist,
            min_distance=self.settings["line_detection"]["minimum_distance_px"],
            threshold=self.settings["line_detection"]["threshold"]
            * hough_transform.max(),
        )

        grid_lines = [
            GridLine.GridLine(distance=d, angle=a) for a, d in zip(angle, distance)
        ]

        return grid_lines

    def construct_grid(self, grid_lines: list[GridLine.GridLine]) -> Grid.Grid:
        """Constructs a Grid-object from Gridlines

        Args:
            grid_lines (list[GridLine]): list of gridlines to construct a grid from

        Returns:
            Grid: constructed grid object
        """
        horizontal_lines, vertical_lines = self.sort_lines_by_alignment(
            grid_lines=grid_lines
        )

        intersections = []
        for hor_line in horizontal_lines:
            for vert_line in vertical_lines:
                intersections.append(hor_line.calculate_intersection(vert_line))

        return Grid(
            horizontal_lines=horizontal_lines,
            vertical_lines=vertical_lines,
            intersections=intersections,
        )

    def detect_grid(self):
        """Runs through the entire grid detection workflow.

        Returns:
            Grid: detected Grid
        """
        spot_mask = self.create_spot_mask(self.settings["spot_mask"]["spot_radius"])
        grid_lines = self.detect_gridlines(spot_mask=spot_mask)
        grid = self.construct_grid(grid_lines=grid_lines)

        return grid
