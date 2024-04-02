from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

if TYPE_CHECKING:
    import src.microspotreader.grid_classes.GridLine as GridLine
    import src.microspotreader.grid_classes.GridPoint as GridPoint


class Grid:
    def __init__(
        self,
        horizontal_lines: list[GridLine.GridLine],
        vertical_lines: list[GridLine.GridLine],
        intersections: list[GridPoint.GridPoint],
    ) -> None:
        self.horizontal_lines = horizontal_lines
        self.vertical_lines = vertical_lines
        self.intersections = intersections

    def plot_image(self, image, ax=None):
        if ax is None:
            fig, ax = plt.subplots()

        ax.imshow(image)
        for item in self.horizontal_lines:
            ax.axline((0, item.y_intersect), slope=item.slope, c="r")

        for item in self.vertical_lines:
            ax.axline((0, item.y_intersect), slope=item.slope, c="r")

        ax.set(ylim=[image.shape[0], 0], xlim=[0, image.shape[1]])
        ax.axis("off")

    def plot_lines(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots()

        for item in self.horizontal_lines:
            ax.axline((0, item.y_intersect), slope=item.slope, c="r")

        for item in self.vertical_lines:
            ax.axline((0, item.y_intersect), slope=item.slope, c="r")

    def plot_intersections(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots()

        x_coords = [point.x for point in self.intersections]
        y_coords = [point.y for point in self.intersections]

        ax.scatter(x_coords, y_coords, marker="x", color="k")
