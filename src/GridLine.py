from dataclasses import dataclass

import numpy as np

from .GridPoint import GridPoint


@dataclass
class GridLine:
    """Class to represent a line in a grid."""

    distance: float
    angle: float

    @property
    def slope(self):
        """Calculates the slope of the line

        Returns:
            float: Slope of the line.
        """
        return np.tan(self.angle + np.pi / 2)

    @property
    def y_intersect(self):
        """Calculates the y-value of the line at x=0.

        Returns:
            float: y-value at x=0
        """
        x0, y0 = self.distance * np.array([np.cos(self.angle), np.sin(self.angle)])
        return y0 - self.slope * x0

    def calculate_intersection(self, line):
        """Calculates the intersection Between two lines and returns the coordinates as a gridpoint.

        Args:
            line (GridLine): Gridline of which the intersection with this line should be calculated with

        Returns:
            GridPoint: Intersection coordinates as a GridPoit object.
        """
        x = (line.y_intersect - self.y_intersect) / (self.slope - line.slope)
        y = self.slope * x + self.y_intersect

        return GridPoint(x, y)
