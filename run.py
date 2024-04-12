from __future__ import annotations

import io
import os
import sys
import tempfile
import zipfile
from collections.abc import MutableSequence
from copy import copy, deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import imageio.v3 as iio
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyopenms as oms
import seaborn as sns
from matplotlib.patches import Patch
from numba import njit
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks, savgol_filter
from scipy.stats import pearsonr
from skimage.color import rgb2gray
from skimage.draw import disk
from skimage.feature import canny, peak_local_max
from skimage.filters import threshold_otsu
from skimage.filters.rank import equalize
from skimage.morphology import (
    binary_dilation,
    binary_opening,
    disk,
    reconstruction,
    remove_small_objects,
    skeletonize,
)
from skimage.transform import (
    hough_circle,
    hough_circle_peaks,
    hough_line,
    hough_line_peaks,
)
from skimage.util import img_as_ubyte, invert

import streamlit as st
import streamlit.web.cli as stcli


def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path


if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("Microspot_Reader.py"),
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())
