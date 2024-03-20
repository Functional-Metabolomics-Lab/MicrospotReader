from collections.abc import MutableSequence

from Spot import *


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
