from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import src.microspotreader.GridLine as GridLine
    import src.microspotreader.GridPoint as GridPoint


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
