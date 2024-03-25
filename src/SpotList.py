from collections.abc import MutableSequence
from copy import deepcopy

import numpy as np

from .Grid import Grid
from .GridPoint import GridPoint
from .Spot import Spot
from .SpotList import SpotList


class SpotList(MutableSequence):
    def __init__(self, *args):
        self._list: list[Spot] = list(args)

    def __getitem__(self, index):
        return self._list[index]

    def __setitem__(self, index, value):
        self._list[index] = value

    def __delitem__(self, index):
        del self._list[index]

    def __len__(self):
        return len(self._list)

    def insert(self, index, value):
        self._list.insert(index, value)

    def __str__(self):
        return str(self._list)

    def __repr__(self):
        return repr(self._list)

    @property
    def mean_radius(self):
        """Calculates the mean radius in pixels for the list of spots.

        Returns:
            float: Mean spot radius.
        """
        return np.mean([spot.radius for spot in self._list])

    @property
    def median_radius(self):
        """Calculates the median radius in pixels for the list of spots.

        Returns:
            float: Median spot radius.
        """
        return np.median([spot.radius for spot in self._list])

    def copy(self):
        return deepcopy(self)

    def find_topleft_bycoords(self):
        """
        ## Description

        Finds the top-left spot in the list by coordinates of the spots.

        ## Output

        spot-object
        """
        return sorted(self._list, key=lambda s: s.x + s.y)[0]

    def find_topright_bycoords(self):
        """
        ## Description

        Finds the top-right spot in the list by coordinates of the spots.

        ## Output

        spot-object
        """
        return sorted(self._list, key=lambda s: s.x - s.y)[-1]

    def sort(self, serpentine: bool = True, reverse: bool = True):
        """Sorts the spot list by index so that a retention time can be assigned to each spot.

        Args:
            serpentine (bool, optional): If true, sorts in a serpentine manner, where odd rows are sorted ascendingly and even rows are sorted descendingly. If false, sort all rows ascendingly. Defaults to True.
            reverse (bool, optional): Changes the sort direction. Defaults to True.
        """

        # Check if all spots have an index.
        assert (
            len(
                [
                    spot
                    for spot in self._list
                    if spot.row is np.nan and spot.col is np.nan
                ]
            )
            == 0
        ), "Not all spots have been assigned an index, cannot sort list!"

        if serpentine:
            self._list.sort(
                reverse=reverse,
                key=lambda x: x.row * 1000  # row gets a higher value for the sort
                + (x.row % 2)
                * x.col  # If row is odd, add the column value -> sorts row ascendingly
                - ((x.row + 1) % 2)
                * x.col,  # If row is even, subtract the column value -> sorts row descendingly
            )
        else:
            self._list.sort(reverse=reverse, key=lambda x: x.row * 1000 + x.col)
