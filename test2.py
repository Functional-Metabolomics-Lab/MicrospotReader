import matplotlib.pyplot as plt
import pandas as pd
import pyopenms as oms

from src.microspotreader import *

exp = oms.MSExperiment()
feature_finder = FeatureFinder(exp, r"example_files\example_mzml.mzML")
feature_table = feature_finder.run()
feature_chroms = feature_finder.get_feature_traces()

activity_table = pd.read_csv(r"example_files\activity_table.csv")

peak_detector = ActivityPeakDetector(activity_table)
peak_list = peak_detector.run()

activity_annot = ActivityAnnotator(
    feature_table, feature_chroms, peak_list, activity_table
)
activity_annot.settings = {"rt_correlation": {"window_s": 1, "bias_s": 4}}
peak_list = activity_annot.run()

for peak in peak_list:
    print(peak.get_annotated_featuretable(feature_table))
    fig = peak.plot_feature_overlap(feature_table, feature_chroms, activity_table)
    plt.show()
    plt.close()
