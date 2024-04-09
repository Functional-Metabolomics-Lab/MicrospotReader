import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.signal import find_peaks
from skimage.feature import peak_local_max

import src.microspotreader.DataPrep as DataPrep
import src.microspotreader.feature_annotation.Peak as Peak


class ActivityPeakDetector:
    settings: dict = {
        "peak_detection": {
            "automatic_threshold": True,
            "noise_convergence": 0.02,
            "manual_treshold": 0.0,
            "minimum_SNR": 3,
        }
    }

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

    def __init__(self, activity_table: pd.DataFrame) -> None:
        """
        Args:
            activity_table (pd.DataFrame): DataFrame of spotlist containing values for retention time in a column called "RT".
        """
        self.df: pd.DataFrame = activity_table

        self.peak_list: list[Peak.Peak] = None
        self.threshold: float = None

    @property
    def wide_df(self):
        return self.pivot()

    def pivot(self):
        """Pivot activity table from long to wide format for 2d peakdetection

        Returns:
            pd.DataFrame: Pivoted activity table.
        """
        return self.df.pivot_table("spot_intensity", index="row_name", columns="column")

    def get_local_minima(self):
        """Get the indices of local local_minima in the activity chromatogram.

        Returns:
            series: series of indices of local local_minima in the activit chromatogram.
        """
        local_minima, _ = find_peaks(-self.df.spot_intensity.to_numpy())
        return self.df.index[local_minima]

    def get_peaks_2d(self, activity_table_wide: pd.DataFrame, threshold: float = 0.0):
        """performs topological 2d peak detection on the activity table in wide format. This is preferred over 1d peakdetection due to spots with high signals, influencing the intensity of surrounding spots. This would lead to multiple false positive peaks when performing peak detection in one dimension.

        Args:
            activity_table_wide (pd.DataFrame): activity table in wide format
            threshold (float, optional): absolute threshold for peak determination, peaks below the threshold will be discarded. Defaults to 0.0.

        Returns:
            list: list of peaks
        """
        return peak_local_max(
            image=activity_table_wide.to_numpy(),
            min_distance=1,
            exclude_border=False,
            threshold_abs=threshold,
        )

    def get_peakidx_longformat(
        self, peak_list: list, activity_table_wide: pd.DataFrame
    ):
        """For each peak in the peaklist get the corresponding index in the activity table in long format

        Args:
            peak_list (list): list of peaks from 2d peak detection
            activity_table_wide (pd.DataFrame): activity table in wide format

        Returns:
            _type_: _description_
        """
        return [
            self.df.loc[
                (self.df["row_name"] == activity_table_wide.index[p[0]])
                & (self.df["column"] == activity_table_wide.columns[p[1]])
            ].index.item()
            for p in peak_list
        ]

    def get_peak_bounds(self, peak_indexes_long: list, local_minima: list):
        """Get a list of peak bounds for each peak in the given list based on a given list of local minima

        Args:
            peak_indexes_long (list): indices of peaks from the long format table
            local_minima (list): indices of local minima from the long format table

        Returns:
            list[(left_bound,right_bound)]: list of left and right bounds for each peak
        """
        left_bounds = [
            (
                local_minima[local_minima < i][-1]
                if any(local_minima < i)
                else self.df.index[0]
            )
            for i in peak_indexes_long
        ]

        right_bounds = [
            (
                local_minima[local_minima > i][0]
                if any(local_minima > i)
                else self.df.index[-1]
            )
            for i in peak_indexes_long
        ]

        return list(zip(left_bounds, right_bounds))

    def get_baseline_noise(self, convergence_criteria: float = 0.02):
        """
        ## Description
        Finds the standard deviation and mean of the baseline of a chromatogram

        ## Input

        |Parameter|Type|Description|
        |---|---|---|
        |array|Seq, Array|Sequence for which the baseline noise should be determined|
        |convergence_criteria|float|convergence criteria for filtering outliers|

        ## Returns
        mean value of baseline
        standard deviation of baseline
        """
        array = self.df.spot_intensity.copy()
        mn_old = array.mean()
        std_old = array.std()

        rmsd = 10
        # Loop through the algorithm until the rmsd of the standard deviation is below a defined criterium
        while rmsd > convergence_criteria:  #
            # exclude values in the array that are most likely outliers -> ie peaks
            test = array[array < mn_old + 3 * std_old]
            # calculate the new mean and std
            mn_new = test.mean()
            std_new = test.std()
            # caluclate rmsd
            rmsd = np.sqrt(np.mean((std_new - std_old) ** 2))

            mn_old = mn_new
            std_old = std_new

        return mn_old, std_old

    def get_peak_AUCs(self, peak_bounds):
        return [
            np.trapz(self.df.loc[i_start:i_end, "spot_intensity"])
            for i_start, i_end in peak_bounds
        ]

    def create_peak_list(self, peak_idx_long: list, peak_bounds: list):
        start_idx = [pk[0] for pk in peak_bounds]
        end_idx = [pk[1] for pk in peak_bounds]
        rt_maxima = self.df.loc[peak_idx_long, "RT"].values
        rt_start = self.df.loc[start_idx, "RT"].values
        rt_end = self.df.loc[end_idx, "RT"].values
        peak_intensity = self.df.loc[peak_idx_long, "spot_intensity"].values
        peak_AUC = self.get_peak_AUCs(peak_bounds)

        self.peak_list = [
            Peak(i, *data)
            for i, data in enumerate(
                zip(
                    peak_idx_long,
                    start_idx,
                    end_idx,
                    rt_maxima,
                    rt_start,
                    rt_end,
                    peak_intensity,
                    peak_AUC,
                )
            )
        ]
        return self.peak_list

    def run(self):
        if self.settings["peak_detection"]["automatic_threshold"] is False:
            self.threshold = self.settings["peak_detection"]["manual_threshold"]
        else:
            baseline_mean, baseline_std = self.get_baseline_noise(
                self.settings["peak_detection"]["noise_convergence"]
            )
            self.threshold = (
                baseline_mean
                + self.settings["peak_detection"]["minimum_SNR"] * baseline_std
            )

        wide_df = self.wide_df

        peaks_wide = self.get_peaks_2d(wide_df, self.threshold)
        peaks_long = self.get_peakidx_longformat(peaks_wide, wide_df)
        minima_long = self.get_local_minima()
        peak_bounds = self.get_peak_bounds(peaks_long, minima_long)

        peak_list = self.create_peak_list(peaks_long, peak_bounds)

        return peak_list

    def plot_chromatogram(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots()

        DataPrep.plot_chromatogram(self.df, ax=ax)

        ax.scatter(
            [pk.retention_time for pk in self.peak_list],
            [pk.intensity for pk in self.peak_list],
            marker="x",
            c="darkviolet",
        )

        ax.hlines(
            [self.threshold],
            xmin=self.df.RT.min(),
            xmax=self.df.RT.max(),
            linewidth=1,
            colors="gray",
            ls="--",
        )

        for peak in self.peak_list:
            ax.fill_between(
                self.df.RT.loc[peak.start_idx, peak.end_idx],
                self.df.spot_intensity.loc[peak.start_idx, peak.end_idx],
                color="palegreen",
            )

            ax.text(
                peak.retention_time * 1.01,
                peak.intensity * 1.01,
                f"Peak {peak.number}",
                c="k",
                size=7,
            )
        ax.legend(["Chromatogram", "Detected Peaks", "Peak Threshold"])

    def plot_heatmap(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots()

        sns.heatmap(
            data=self.wide_df,
            square=True,
            cmap="viridis",
            linewidths=1,
            ax=ax,
            annot=True,
            annot_kws={"fontsize": 6},
        )

        ax.set(ylabel="Row", xlabel="Column")
        ax.tick_params(axis="y", labelrotation=0)

        # Add location of detected peaks to heatmap
        ax.scatter(
            self.df.loc[[pk.index for pk in self.peak_list], "column"],
            -self.df.loc[[pk.index for pk in self.peak_list], "row"],
            c="r",
            marker="D",
        )
        # Write name of peak to corresponding spot
        for peak in self.peak_list:
            ax.text(
                self.df.loc[peak.index, "column"] + 0.2,
                -self.df.loc[peak.index, "row"] + 0.2,
                f"Peak {peak.number}",
                size=8,
                c="r",
                path_effects=[pe.withStroke(linewidth=1, foreground="white")],
            )
