import matplotlib.pyplot as plt
import pandas as pd
import pyopenms as oms

from src.microspotreader import *

exp = oms.MSExperiment()

feature_finder = FeatureFinder(
    exp=exp, filename_mzml=r"example_files/example_mzml.mzML"
)

print(feature_finder.run())

print(feature_finder.get_feature_traces())
