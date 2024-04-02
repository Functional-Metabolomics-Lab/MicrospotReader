from __future__ import annotations

from typing import TYPE_CHECKING

import src.microspotreader.spot_classes.Spot as Spot

if TYPE_CHECKING:
    import src.microspotreader.grid_classes.Grid as Grid
    import src.microspotreader.spot_classes.SpotList as SpotList


class SpotCorrector:
    settings = {
        "general": {"spot_radius_backfill": 0},
        "from_grid": {"distance_threshold_px": 10},
    }

    def __init__(self, spot_list: SpotList.SpotList) -> None:
        self.spot_list = spot_list

    def get_settings(self):
        return self.settings.copy()

    def change_settings_dict(self, settings: dict):
        assert type(settings) is dict, "Use a dictionary to change settings."

        for key, value in settings.items():
            if type(value) is dict:
                for k, v in value.items():
                    self.settings[key][k] = v
            else:
                self.settings[key] = value

    def remove_false_positives_from_grid(
        self, grid: Grid.Grid, distance_threshold_px: float, inplace=True
    ):
        """Removes false positive spots by comparing the position of each spot to a grid and removing spots that deviate too much.

        Args:
            grid (Grid): Grid to compare the spots against
            distance_threshold (float): Threshold above which spots are removed
            inplace (bool): changes spotlist in place if true. Defaults to True
        """

        if inplace is True:
            spot_list = self.spot_list
        else:
            spot_list = self.spot_list.copy()

        for spot in spot_list:
            deviation = spot.deviation_from_grid(grid)
            if deviation > distance_threshold_px:
                spot_list.remove(spot)

        return spot_list

    def backfill_from_grid(
        self,
        grid: Grid.Grid,
        distance_threshold_px: float,
        radius: int = 0,
        inplace=True,
    ):
        """Backfills missing spots based on intersections in a grid object.

        Args:
            grid (Grid): Grid to reference for backfilling
            distance_threshold_px (float): Threshold used to determine how far the distance between an intersection and any spot has to be until the intersection is considered to be missing a spot.
            radius (int, optional): radius of the backfilled spot, if 0 the median spot radius of the list is used. Defaults to 0.
            inplace (bool, optional): changes spotlist in place if true. Defaults to True.

        Returns:
            SpotList: Backfilled spotlist object
        """
        if radius == 0:
            radius = self.spot_list.median_radius

        if inplace is True:
            spot_list = self.spot_list
        else:
            spot_list = self.spot_list.copy()

        for intersection in grid.intersections:
            if intersection.check_for_spot(self.spot_list, distance_threshold_px):
                self.spot_list.append(
                    Spot(
                        x=int(intersection.x),
                        y=int(intersection.y),
                        radius=int(radius),
                        note="Backfilled",
                    )
                )
        return spot_list

    def gridbased_spotcorrection(self, grid: Grid.Grid):
        """Performs the whole spot-correction workflow based on a detected Grid in place.

        Args:
            grid (Grid): Grid with which to perform spot-correction

        Returns:
            SpotList: corrected spotlist
        """
        self.remove_false_positives_from_grid(
            grid=grid,
            distance_threshold_px=self.settings["from_grid"]["distance_threshold_px"],
        )
        self.backfill_from_grid(
            grid=grid,
            distance_threshold_px=self.settings["from_grid"]["distance_threshold_px"],
            radius=self.settings["general"]["spot_radius_backfill"],
        )
        return self.spot_list
