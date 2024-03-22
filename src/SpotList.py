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
