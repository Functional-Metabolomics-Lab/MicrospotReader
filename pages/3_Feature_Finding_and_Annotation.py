import io

import matplotlib.pyplot as plt
import pandas as pd
import pyopenms as oms

import src.streamlit.image_analysis as stim
import streamlit as st
from src.microspotreader import *
from src.streamlit.general import *

# Sets up basic page layout
page_setup()
with st.sidebar:
    st.session_state["sidebar"]["data_storage"].display_data()

st.markdown("# Feature Finding and Annotation")

c1, c2 = st.columns(2)

# Uploading of mzML file
with c2:
    choose_mzml = st.selectbox(
        "Upload of .mzML-File:", ["Upload .mzML File", "Example .mzML File"]
    )

    match choose_mzml:
        case "Upload .mzML File":
            mzml_upload = st.file_uploader("Upload .mzML File", "mzML")
            mzml_upload = io.StringIO(mzml_upload.getvalue().decode("utf-8")).read()

        case "Example .mzML File":
            mzml_upload = "example_files/example_mzml.mzML"
            st.markdown("# ")
            st.info("**Example .mzML File**")

# Uploading of activtiy data
with c1:
    # Choose to upload a .csv file or use data saved in the current session.
    choose_input = st.selectbox(
        "Upload of Activity Data:",
        ["Use Selection in current Session", "Upload Activity Data"],
    )

    match choose_input:
        case "Use Selection in current Session":
            dataset = st.session_state["sidebar"]["data_storage"].get_selected_data(
                "Prepared Data"
            )
            dataset_names = st.session_state["sidebar"][
                "data_storage"
            ].get_selected_names("Prepared Data")

            st.markdown("# ")
            st.dataframe(
                dataset_names,
                column_config={"Name": "Selected Datasets:"},
                use_container_width=True,
                hide_index=True,
            )

            if len(dataset) != 1:
                st.warning("Please select **one** merged dataset!")

            else:
                dataset = dataset[0]

        case "Upload Activity Data":
            dataset = st.file_uploader("Upload Activity Data", ["csv", "tsv"])

            if dataset is not None:
                dataset = pd.read_csv(dataset)

enable_analysis = type(dataset) == pd.DataFrame and mzml_upload is not None

with st.form("Settings", border=False):
    c1, c2 = st.columns(2)
    with c1:
        st.session_state["feature_finding"]["settings"]["feature_finder"][
            "mass_trace_detection"
        ]["mass_error_ppm"] = st.number_input(
            "Mass Error for feature detection *[in ppm]*:", value=10.0
        )

        st.session_state["feature_finding"]["settings"]["feature_finder"][
            "elution_peak_detection"
        ]["min_fwhm_s"] = st.number_input(
            "Min. fwhm of peaks during feature detection *[in s]*:", value=1.0
        )

        st.session_state["feature_finding"]["settings"]["activity_annotator"][
            "rt_correlation"
        ]["window_s"] = st.number_input("Retention Time tolerance *[in s]*:", value=1)

        st.session_state["feature_finding"]["settings"]["activity_detector"][
            "peak_detection"
        ]["automatic_threshold"] = st.toggle(
            "Automatic peak threshold determination for activity Data.", value=True
        )

        st.markdown("####")

        # Initiaize analysis:
        analysis = st.form_submit_button(
            "Start Feature Detection and Annotation",
            disabled=not enable_analysis,
            type="primary",
            use_container_width=True,
        )

    with c2:
        st.session_state["feature_finding"]["settings"]["feature_finder"][
            "mass_trace_detection"
        ]["noise_threshold"] = st.number_input(
            "Noise Threshold for feature detection:", value=1e5
        )

        st.session_state["feature_finding"]["settings"]["feature_finder"][
            "elution_peak_detection"
        ]["max_fwhm_s"] = st.number_input(
            "Max. fwhm of peaks during feature detection *[in s]*:", value=60.0
        )

        st.session_state["feature_finding"]["settings"]["activity_annotator"][
            "rt_correlation"
        ]["bias_s"] = st.number_input("Retention Time offset *[in s]*:", value=4)

        st.session_state["feature_finding"]["settings"]["activity_detector"][
            "peak_detection"
        ]["manual_threshold"] = st.number_input(
            "Manual Threshold activity data peak detection", value=0.02, format="%f"
        )

if analysis:
    exp = oms.MSExperiment()
    feature_finder = FeatureFinder(exp, mzml_upload)
    feature_finder.change_settings_dict(
        st.session_state["feature_finding"]["settings"]["feature_finder"]
    )
    feature_table = feature_finder.run()
    feature_chroms = feature_finder.get_feature_traces()

    peak_detector = ActivityPeakDetector(dataset)
    peak_detector.change_settings_dict(
        st.session_state["feature_finding"]["settings"]["activity_detector"]
    )
    peak_list = peak_detector.run()

    activity_annot = ActivityAnnotator(
        feature_table, feature_chroms, peak_list, dataset
    )
    activity_annot.change_settings_dict(
        st.session_state["feature_finding"]["settings"]["activity_annotator"]
    )
    peak_list = activity_annot.run()

    st.session_state["feature_finding"]["results"] = {
        "feature_finder": feature_finder,
        "peak_detector": peak_detector,
        "activity_annotator": activity_annot,
    }

if st.session_state["feature_finding"]["results"] is not None:
    peak_list = st.session_state["feature_finding"]["results"][
        "activity_annotator"
    ].peak_list
    feature_table = st.session_state["feature_finding"]["results"][
        "feature_finder"
    ].get_feature_table()
    activity_table = st.session_state["feature_finding"]["results"][
        "activity_annotator"
    ].activity_table
    feature_chroms = st.session_state["feature_finding"]["results"][
        "feature_finder"
    ].get_feature_traces()
    consensus_map = st.session_state["feature_finding"]["results"][
        "feature_finder"
    ].consensus_map
    mzml_file = st.session_state["feature_finding"]["results"][
        "feature_finder"
    ].filename
    oms_exp = st.session_state["feature_finding"]["results"]["feature_finder"].exp

    figure_dict = {}

    st.markdown("## Results")
    container = st.container()
    t1, t2 = st.tabs(["Activity peak data", "Annotated Feature Tables"])

    with t1:
        st.dataframe(
            st.session_state["feature_finding"]["results"][
                "peak_detector"
            ].get_peak_df(),
            use_container_width=True,
        )

        fig_chrom, ax = plt.subplots()
        st.session_state["feature_finding"]["results"][
            "peak_detector"
        ].plot_chromatogram(ax=ax)
        st.pyplot(fig_chrom)
        figure_dict["Chromatogram"] = fig_chrom

        fig_heatmap, ax = plt.subplots()
        st.session_state["feature_finding"]["results"]["peak_detector"].plot_heatmap(
            ax=ax
        )
        st.pyplot(fig_heatmap)
        figure_dict["Heatmap"] = fig_heatmap

    with t2:
        for peak in peak_list:
            st.markdown(f"### Peak {peak.number}")

            st.dataframe(
                peak.get_annotated_featuretable(feature_table).sort_values(
                    f"correlation_peak{peak.number}", ascending=False
                ),
                use_container_width=True,
            )

            if len(peak.correlated_feature_ids) > 0:
                fig = peak.plot_feature_overlap(
                    feature_table, feature_chroms, activity_table
                )
                st.pyplot(fig)
                figure_dict[f"Overlay_peak{peak.number}"] = fig

    c1, c2 = st.columns(2)
    with c2:
        # Creates a Zipfile containing all plots as .svg files on this page and makes it ready for download.
        stim.download_figures(figure_dict, "svg")

    with c1:
        # Creates a Zipfile containing all plots as .png files on this page and makes it ready for download.
        stim.download_figures(figure_dict, "png")

    with container:
        stim.download_gnpsmgf(consensus_map, mzml_file, oms_exp)
