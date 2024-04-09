import pandas as pd
import pyopenms as oms


class FeatureFinder:
    settings: dict = {
        "mass_trace_detection": {
            "mass_error_ppm": 10,
            "noise_threshold": 1e5,
        },
        "elution_peak_detection": {
            "min_fwhm_s": 1,
            "max_fwhm_s": 60,
        },
        "adduct_detection": {
            "adduct_list": [
                b"H:+:0.4",
                b"Na:+:0.2",
                b"NH4:+:0.2",
                b"H3O1:+:0.1",
                b"CH2O2:+:0.1",
                b"H-2O-1:0:0.2",
            ]
        },
    }

    def __init__(self, exp: oms.MSExperiment, filename_mzml: str) -> None:
        self.exp: oms.MSExperiment = exp
        self.filename = filename_mzml

        self.feature_map = oms.FeatureMap()
        self.consensus_map = None

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

    def load_mzml(self):
        oms.MzMLFile().load(self.filename, self.exp)
        self.exp.sortSpectra(True)
        return self.exp

    def mass_trace_detection(self, mass_error_ppm: float, noise_threshold: float):
        """Mass trace detection using pyopenms, implemented from "https://pyopenms.readthedocs.io/en/latest/user_guide/feature_detection.html"

        Args:
            mass_error_ppm (float): mass error in ppm
            noise_threshold (float): threshold below which peaks are considered noise

        Returns:
            list: list of mass traces
        """
        mass_traces = []
        mtd = oms.MassTraceDetection()
        mtd_params = mtd.getDefaults()
        mtd_params.setValue(
            "mass_error_ppm", float(mass_error_ppm)
        )  # set according to your instrument mass error
        mtd_params.setValue(
            "noise_threshold_int", float(noise_threshold)
        )  # adjust to noise level in your data
        mtd.setParameters(mtd_params)
        mtd.run(self.exp, mass_traces, 0)
        return mass_traces

    def elution_peak_detection(
        self, mass_traces: list, min_fwhm: float, max_fwhm: float
    ):
        """Elution peak detection using pyopenms, implemented from "https://pyopenms.readthedocs.io/en/latest/user_guide/feature_detection.html"

        Args:
            mass_traces (list): mass traces from mass trace detection
            min_fwhm (float): minimum full width at half maximum (in seconds) to be considered a feature
            max_fwhm (float): maximum full width at half maximum (in seconds) to be considered a feature

        Returns:
            list: list of mass traces
        """
        mass_traces_final = []
        epd = oms.ElutionPeakDetection()
        epd_params = epd.getDefaults()
        epd_params.setValue("width_filtering", "fixed")
        epd_params.setValue("min_fwhm", float(min_fwhm))
        epd_params.setValue("max_fwhm", float(max_fwhm))
        epd.setParameters(epd_params)
        epd.detectPeaks(mass_traces, mass_traces_final)

        return mass_traces_final

    def feature_finding(self, mass_traces: list):
        """Feature finding using the featurefindermetabo from pyopenms, implemented from https://pyopenms.readthedocs.io/en/latest/user_guide/feature_detection.html

        Args:
            mass_traces (list): list of mass traces from elution peak detection or mass trace detection

        Returns:
            feature_map,feature chromatograms: featuremap from feature detection and a list of all feature chromatograms.
        """
        feature_map = self.feature_map
        feature_chromatograms = []
        ffm = oms.FeatureFindingMetabo()
        ffm_params = ffm.getDefaults()
        ffm_params.setValue("isotope_filtering_model", "none")
        ffm_params.setValue(
            "remove_single_traces", "true"
        )  # set false to keep features with only one mass trace
        ffm_params.setValue("mz_scoring_by_elements", "false")
        ffm_params.setValue("report_convex_hulls", "true")
        ffm_params.setValue("report_chromatograms", "true")
        ffm.setParameters(ffm_params)
        ffm.run(mass_traces, feature_map, feature_chromatograms)

        feature_map.setPrimaryMSRunPath([self.filename.encode()])

        return feature_map, feature_chromatograms

    def assign_chromatograms(
        self, feature_map: oms.FeatureMap, feature_chromatograms: list
    ):
        """Assigns the chromatpgram of each feature to the metavalues "chrom_rts" and "chrom_intensities" of the feature map

        Args:
            feature_map (oms.FeatureMap): feature map containing features
            feature_chromatograms (list): list of chromatograms of feature. feature ids have to match the ones in the feature map

        Returns:
            oms.FeatureMap: feature map containing the chromatograms as meta values.
        """
        assert feature_map.size() == len(
            feature_chromatograms
        ), "Size of feature map does not match list of chromatograms"

        feature_map_chroms = oms.FeatureMap(feature_map)
        feature_map_chroms.clear(False)

        for feature in feature_map:
            # get the matching monoisotopic chromatogram
            match = [
                c[0]
                for c in feature_chromatograms
                if int(c[0].getName().split("_")[0]) == feature.getUniqueId()
            ][0]
            rts, ints = match.get_peaks()
            feature.setMetaValue("chrom_rts", ",".join(rts.astype(str)))
            feature.setMetaValue("chrom_intensities", ",".join(ints.astype(str)))
            feature_map_chroms.push_back(feature)

        feature_map_chroms.setUniqueIds()

        self.feature_map = feature_map_chroms

        return feature_map_chroms

    def get_feature_traces(self, feature_map: oms.FeatureMap = None):
        """Get a dictionary of dataframes containing the feature traces of each feature in the feature map, can only be used after the assign_chromatograms method has been called.

        Args:
            feature_map (oms.FeatureMap, optional): Feature map to get the traces from, if none use the instances feature map. Defaults to None.

        Returns:
            dict: dictionary of feature traces, key is the feature id and value is a dataframe.
        """
        if feature_map is None:
            feature_map = self.feature_map

        assert (
            len(feature_map[0].getMetaValue("chrom_rts")) > 0
        ), "Please assign chromatograms to the featuremap first!"
        feature_traces = {
            str(f.getUniqueId()): pd.DataFrame(
                {
                    "rt": [float(rt) for rt in f.getMetaValue("chrom_rts").split(",")],
                    "int": [
                        float(intensity)
                        for intensity in f.getMetaValue("chrom_intensities").split(",")
                    ],
                }
            )
            for f in feature_map
        }
        return feature_traces

    def map_ms2_to_features(self):
        """
        ## Description
        Implemented algorithm for mapping ms2 data to features from pyopenms https://pyopenms.readthedocs.io/en/latest/user_guide/untargeted_metabolomics_preprocessing.html

        Maps the ms2 data to features in the featuremap

        ## Input

        |Parameter|Type|Description|
        |---|---|---|
        |exp|MSExperiment|pyOpenMS MSExperiment class with a loaded mzml file|
        |fm|oms.FeatureMap|Featuremap instance from feature finding|
        """

        use_centroid_rt = False
        use_centroid_mz = True
        mapper = oms.IDMapper()
        peptide_ids = []
        protein_ids = []

        mapper.annotate(
            self.feature_map,
            peptide_ids,
            protein_ids,
            use_centroid_rt,
            use_centroid_mz,
            self.exp,
        )

    def adduct_detection(
        self,
        feature_map: oms.MSExperiment = None,
        adduct_list: list[str] = [
            b"H:+:0.4",
            b"Na:+:0.2",
            b"NH4:+:0.2",
            b"H3O1:+:0.1",
            b"CH2O2:+:0.1",
            b"H-2O-1:0:0.2",
        ],
    ):
        """
        ## Description
        Implemented algorithm adduct detection from pyopenms https://pyopenms.readthedocs.io/en/latest/user_guide/adduct_detection.html

        ## Input

        |Parameter|Type|Description|
        |---|---|---|
        |fm|oms.FeatureMap|Featuremap instance from feature finding|
        |adduct_list|list of strings|list of strings containing all expected adducts, rules for the list can be found on the linked website|

        ## Output
        ft -> pd.Dataframe feature table containing information on all features
        groups -> result consensus map: will store grouped features belonging to a charge group, used to save an mgf file
        """
        if feature_map is None:
            feature_map = self.feature_map

        mfd = oms.MetaboliteFeatureDeconvolution()

        params = mfd.getDefaults()
        params.setValue("potential_adducts", adduct_list)
        params.setValue("charge_min", 1, "Minimal possible charge")
        params.setValue("charge_max", 3, "Maximal possible charge")
        params.setValue("charge_span_max", 3)
        params.setValue("retention_max_diff", 3.0)
        params.setValue("retention_max_diff_local", 3.0)
        mfd.setParameters(params)

        feature_map_MFD = oms.FeatureMap()
        groups = oms.ConsensusMap()
        edges = oms.ConsensusMap()
        mfd.compute(feature_map, feature_map_MFD, groups, edges)

        self.feature_map = feature_map_MFD
        self.consensus_map = groups
        return feature_map_MFD, groups

    def get_feature_table(self):
        """Get the feature table from the feature map saved in the instance of this class

        Returns:
            dataframe: feature table of the feature map
        """
        assert self.feature_map is not None, "Perform feature detection first!"

        return self.feature_map.get_df(export_peptide_identifications=False)

    def run(self):
        """Performs the feature finding workflow of this class in its entirety using the settings defined in self.settings.

        Returns:
            dataframe: feature table of the .mzml file
        """
        self.load_mzml()

        mass_traces = self.mass_trace_detection(
            self.settings["mass_trace_detection"]["mass_error_ppm"],
            self.settings["mass_trace_detection"]["noise_threshold"],
        )

        mass_traces_final = self.elution_peak_detection(
            mass_traces,
            self.settings["elution_peak_detection"]["min_fwhm_s"],
            self.settings["elution_peak_detection"]["max_fwhm_s"],
        )

        feature_map, feature_chromatograms = self.feature_finding(mass_traces_final)
        self.assign_chromatograms(feature_map, feature_chromatograms)

        self.map_ms2_to_features()

        self.adduct_detection(
            adduct_list=self.settings["adduct_detection"]["adduct_list"]
        )

        return self.get_feature_table()
