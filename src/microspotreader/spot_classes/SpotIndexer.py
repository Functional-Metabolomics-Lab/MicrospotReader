from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

import src.microspotreader.spot_classes.SpotList as SpotList

if TYPE_CHECKING:
    import src.microspotreader.spot_classes.Spot as Spot


class SpotIndexer:
    def __init__(self, spot_list: SpotList.SpotList) -> None:
        self.list = spot_list

    def dist_from_row(
        self, spot: Spot.Spot, left_spot: Spot.Spot, right_spot: Spot.Spot
    ):
        """Calculates the distance of a spot to a row (line) defined by its left and rightmost spots

        Args:
            spot (Spot): Spot to calculate the distance for
            left_spot (Spot): left most spot in the row
            right_spot (Spot): Right most spot in the row

        Returns:
            float: distance of the given spot to a line
        """
        return np.linalg.norm(
            np.cross(
                np.subtract(
                    np.array((spot.x, spot.y)), np.array((left_spot.x, left_spot.y))
                ),
                np.subtract(
                    np.array((right_spot.x, right_spot.y)),
                    np.array((left_spot.x, left_spot.y)),
                ),
            )
            / np.linalg.norm(
                np.subtract(
                    np.array((right_spot.x, right_spot.y)),
                    np.array((left_spot.x, left_spot.y)),
                )
            )
        )

    def assign_indexes(
        self,
        row_idx_start: int = 1,
        col_idx_start: int = 1,
        maximum_cycle_nr: int = 1000,
    ):
        """assigns Indexes for spots in the given spotlist.

        Args:
            row_idx_start (int, optional): starting numerical row index. Defaults to 1.
            col_idx_start (int, optional): starting numerical column index. Defaults to 1.
            maximum_cycle_nr (int, optional): throws an error if index assignment exeeds the specified numer of cycles. Defaults to 1000.
        """
        working_list = self.list.copy()

        current_row_idx = row_idx_start
        while len(working_list) > 0:
            # The current top left and top right spots define the upmost row still in the working list
            topleft = working_list.find_topleft_bycoords()
            topright = working_list.find_topright_bycoords()

            # Add all spots to the current row if their radius is larger than the distance to the row.
            current_row = [
                spot
                for spot in self.list
                if self.dist_from_row(spot, topleft, topright) <= spot.radius
            ]
            col_idx_end = col_idx_start + len(current_row)
            current_row.sort(key=lambda s: s.x)  # Sort row by x-coordinate

            # Add the proper indexes to each spot in the current row.
            for spot, column_index in zip(
                current_row, range(col_idx_start, col_idx_end)
            ):
                spot.add_index(current_row_idx, column_index)

            # remove current row from working list.
            working_list = SpotList.SpotList(
                *[spot for spot in working_list if spot not in current_row]
            )

            current_row_idx += 1

            assert (
                current_row_idx < maximum_cycle_nr + row_idx_start
            ), "Exceeded maximum cycle number while finding spot indexes."
