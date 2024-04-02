import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


def add_retention_time(df: pd.DataFrame, start_time: float, end_time: float):
    df["RT"] = np.linspace(start_time, end_time, num=len(df))


def baseline_correction(array, conv_lvl=0.001, window_lvl=100, poly_lvl=2):
    """
    ## Description
    Baseline correction of an input array using the savitz golay filter.

    ## Input

    |Parameter|Type|Description|
    |---|---|---|
    |array|Seq, Array|Sequence to be baseline corrected|
    |conv_lvl|float|convergence criteria for the determination of the baseline level||
    |window_lvl|int|Window to be used for the savitzky-golay filter for detection of the baseline level|
    |poly_lvl|int|order of the polynomial used to fit the data for baseline level detection|

    ## Returns
    Tuple of the values for the baseline aswell as the corrected baseline vales
    """
    baseline_level = array.copy()

    if len(baseline_level) < window_lvl:
        window_lvl = len(baseline_level)

    # First time running the algo with a large window size to simply detect the general level of the baseline.
    rmsd_lvl = 10
    while rmsd_lvl > conv_lvl:
        sg_filt = savgol_filter(baseline_level, window_lvl, poly_lvl)
        baseline_new = np.minimum(sg_filt, baseline_level)
        rmsd_lvl = np.sqrt(np.mean((baseline_new - baseline_level) ** 2))
        baseline_level = baseline_new

    return baseline_level, array - baseline_level


def plot_chromatogram(df: pd.DataFrame, ax=None):
    if ax is None:
        fig, ax = plt.subplots()

    df.sort_values("RT", inplace=True)
    ax.plot(df["RT"], df["spot_intensity"], c="darkviolet", linewidth=1)
    ylabel = "Smoothed Spot-Intensity [a.u.]"

    ax.set(
        ylabel=ylabel,
        xlabel="Retention Time [s]",
        xlim=[df["RT"].min(), df["RT"].max()],
    )
