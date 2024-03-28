from .GridLine import GridLine
from .GridPoint import GridPoint


class Grid:
    def __init__(
        self,
        horizontal_lines: list[GridLine],
        vertical_lines: list[GridLine],
        intersections: list[GridPoint],
    ) -> None:
        self.horizontal_lines = horizontal_lines
        self.vertical_lines = vertical_lines
        self.intersections = intersections
