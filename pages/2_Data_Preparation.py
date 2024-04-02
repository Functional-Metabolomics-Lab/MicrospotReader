import matplotlib.pyplot as plt
import pandas as pd
from scipy.ndimage import gaussian_filter1d

import src.streamlit.image_analysis as stim
import streamlit as st
from src.microspotreader import *
from src.streamlit.DataStorage import DataStorage
from src.streamlit.general import *

# Sets up basic page layout
page_setup()
with st.sidebar:
    st.session_state["sidebar"]["data_storage"].add_data_interface(
        st.session_state["data_preparation"]["df"], "Prepared Data"
    )
    st.session_state["sidebar"]["data_storage"].display_data()

st.markdown("# Data Merging and Preparation")

# Selection between custom file upload or selection from saved data in the current session
choose_input = st.selectbox(
    "File upload:", ["Use Selection in current Session", "Upload Data"]
)

match choose_input:
    case "Use Selection in current Session":
        datasets = st.session_state["sidebar"]["data_storage"].get_selected_data(
            "Image Data"
        )

        dataset_names = st.session_state["sidebar"]["data_storage"].get_selected_names(
            "Image Data"
        )
        st.dataframe(
            dataset_names,
            column_config={"Name": "Selected Datasets:"},
            use_container_width=True,
            hide_index=True,
        )

    case "Upload Data":
        # List of uploaded files.
        dataset_names = st.file_uploader(
            "Upload all .csv files.",
            "csv",
            accept_multiple_files=True,
        )

        datasets = [SpotList().from_df(pd.read_csv(item)) for item in dataset_names]

if len(datasets) == 0:
    disable_dataprep = True
    row_idx = []
    col_idx = []

else:
    disable_dataprep = False
    spot_list = SpotList().from_list(datasets)
    row_idx, col_idx = spot_list.get_indices()
    st.caption("Merged Dataset:")
    st.dataframe(spot_list.to_df())

with st.form("Data Preparation Settings"):
    c1, c2 = st.columns(2)

    with c1:
        remove_rows = st.multiselect("Remove Rows:", row_idx)

        # Input for the retention time at which spotting was started
        start_time = st.number_input(
            "Start Time [s]",
            value=0.0,
        )

        # Toggle serpentine sorting, if enabled spots are sorted in a serpentine pattern
        sort_serpentine = st.toggle(
            "Serpentine Path",
            key="serpentine",
        )

        st.markdown("####")

        # Button starting the data preparation process.
        dataprep = st.form_submit_button(
            "Start Data Preparation", type="primary", disabled=disable_dataprep
        )

    with c2:
        remove_columns = st.multiselect("Remove Columns:", col_idx)
        # Time each spot was eluted to.
        end_time = st.number_input(
            "End Time [s]",
            value=520.0,
        )

        chromatogram_smoothing = st.toggle("Perform Chromatogram-Smoothing", value=True)

        sigma_smooth = st.number_input("Sigma-Value for gaussian smoothing:", value=1)

if dataprep:
    if len(remove_rows) > 0:
        spot_list.remove_rows(remove_rows)

    if len(remove_columns) > 0:
        spot_list.remove_columns(remove_columns)

    spot_list.sort(serpentine=sort_serpentine)

    df = spot_list.to_df()
    add_retention_time(df, start_time, end_time)

    if chromatogram_smoothing:
        _, df.spot_intensity = baseline_correction(
            df.spot_intensity,
            conv_lvl=0.001,
            window_lvl=100,
            poly_lvl=1,
        )

        df.spot_intensity = gaussian_filter1d(
            input=df.spot_intensity.to_numpy(), sigma=sigma_smooth
        )

    st.session_state["data_preparation"]["df"] = df

if st.session_state["data_preparation"]["df"] is not None:
    df = st.session_state["data_preparation"]["df"]

    t1, t2, t3 = st.tabs(["Merged Data Table", "Heatmap", "Chromatogram"])
    figure_dict = {}

    with t1:
        st.dataframe(df, hide_index=True)

    with t2:
        fig_hm, ax = plt.subplots()
        SpotList().from_df(df).plot_heatmap(ax=ax)
        st.pyplot(fig_hm)
        figure_dict["heatmap"] = fig_hm

    with t3:
        fig_chrom, ax = plt.subplots()
        plot_chromatogram(df, ax)
        st.pyplot(fig_chrom)
        figure_dict["chromatogram"] = fig_chrom

    c1, c2 = st.columns(2)
    with c2:
        # Creates a Zipfile containing all plots as .svg files on this page and makes it ready for download.
        stim.download_figures(figure_dict, "svg")

    with c1:
        # Creates a Zipfile containing all plots as .png files on this page and makes it ready for download.
        stim.download_figures(figure_dict, "png")
