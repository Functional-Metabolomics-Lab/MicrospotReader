import numpy as np
import pandas as pd
from numba import njit
from scipy.stats import pearsonr

import src.microspotreader.feature_annotation.Peak as Peak


class ActivityAnnotator:
    settings: dict = {"rt_correlation": {"window_s": 2, "bias_s": 0}}

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

    def __init__(
        self,
        feature_table: pd.DataFrame,
        feature_chroms: dict[str, pd.DataFrame],
        peak_list: list[Peak.Peak],
        activity_table: pd.DataFrame,
    ) -> None:
        self.feature_table = feature_table
        self.feature_chroms = feature_chroms
        self.peak_list = peak_list
        self.activity_table = activity_table

    def correlate_by_retentiontime(self, window: float, bias: float):
        """Adds indices of features correlated to all peaks in the peaklist by retention time.

        Args:
            window (float): window size in seconds that is correlated to activity peaks
            bias (float): bias in seconds that is applied to the retention time of the activity peak before correlation
        """
        for peak in self.peak_list:
            peak.correlated_feature_ids = self.feature_table.loc[
                window
                >= np.abs(self.feature_table["RT"] - (peak.retention_time + bias))
            ].index.values

    def get_overlapping_bounds(self, peak: Peak.Peak, feature: pd.Series):
        """Get bounds for the activity and feature peak of the same timewindow.

        Args:
            peak (Peak.Peak): peak object from the peaklist
            feature (pd.Series): feature from the feature table

        Returns:
            activity bounds, feature bounds: retention times for the start and end of both peaks where the size of the window matches.
        """
        time_premax = min(
            peak.start_RT - peak.retention_time, feature.RTstart - feature.RT
        )
        time_postmax = min(
            peak.retention_time - peak.end_RT, feature.RT - feature.RTend
        )

        activity_bounds = (
            peak.retention_time - time_premax,
            peak.retention_time + time_postmax,
        )
        feature_bounds = (feature.RT - time_premax, feature.RT + time_postmax)
        return activity_bounds, feature_bounds

    @staticmethod
    @njit
    def sampling_frequency(retention_time_array: np.array):
        return len(retention_time_array) / (
            np.max(retention_time_array) - np.min(retention_time_array)
        )

    def get_number_of_datapoints(
        self, sequence_1, sequence_2, bounds: tuple[float, float]
    ):
        sampling_freq = max(
            self.sampling_frequency(sequence_1), self.sampling_frequency(sequence_2)
        )
        return int(np.abs(bounds[1] - bounds[0]) * sampling_freq)

    @staticmethod
    @njit
    def get_interp_chromatogram(
        bounds: tuple[float, float],
        number_datapoints: int,
        retention_times: np.array,
        intensities: np.array,
    ):
        x_interp = np.linspace(*bounds, number_datapoints).astype(np.float64)
        y_interp = np.interp(
            x_interp,
            retention_times,
            intensities,
        )
        y_interp *= 1 / y_interp.max()
        return x_interp, y_interp

    def get_matching_chromatograms(self, peak: Peak.Peak, feature_id: str):
        activity_bounds, feature_bounds = self.get_overlapping_bounds(
            peak, self.feature_table.loc[feature_id]
        )

        number_datapoints = self.get_number_of_datapoints(
            self.activity_table.RT.to_numpy(),
            self.feature_chroms[feature_id].rt.to_numpy(),
            activity_bounds,
        )
        activity_chrom = self.get_interp_chromatogram(
            activity_bounds,
            number_datapoints,
            self.activity_table.RT.to_numpy(),
            self.activity_table.spot_intensity.to_numpy(),
        )
        feature_chrom = self.get_interp_chromatogram(
            feature_bounds,
            number_datapoints,
            self.feature_chroms[feature_id].rt.to_numpy(),
            self.feature_chroms[feature_id].int.to_numpy(),
        )

        return activity_chrom, feature_chrom

    def pearson_correlation(self, sequence_1, sequence_2):
        return pearsonr(sequence_1, sequence_2).statistic

    def correlate_by_shape(self):
        for peak in self.peak_list:
            for feature_id in peak.correlated_feature_ids:
                activity_chrom, feature_chrom = self.get_matching_chromatograms(
                    peak, feature_id
                )
                peak.correlation_coeff_features.append(
                    self.pearson_correlation(activity_chrom[1], feature_chrom[1])
                )

    def run(self):
        self.correlate_by_retentiontime(
            window=self.settings["rt_correlation"]["window_s"],
            bias=self.settings["rt_correlation"]["bias_s"],
        )
        self.correlate_by_shape()
        return self.peak_list
