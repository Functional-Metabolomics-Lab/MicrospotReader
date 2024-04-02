from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

import src.streamlit.image_analysis as stim
import streamlit as st
from src.microspotreader import *
from src.streamlit.general import *

# Sets up basic page layout
page_setup()

# TODO: Add saving to session

st.markdown("# Image Analysis")

# Choose how to upload image
choose_image_upload = st.selectbox(
    "File upload:",
    [
        "Upload Image",
        "Example Part 1 (Spot-Idx: A1-L11, Ctrl: Col 1)",
        "Example Part 2 (Spot-Idx: A12-L22, Ctrl: Col 22)",
    ],
    on_change=stim.set_analysis_false,
)

# get the filepath as a path object of the image
match choose_image_upload:
    case "Upload Image":
        image_path = st.file_uploader(
            "Upload Image", ["png", "jpg", "tif"], on_change=stim.set_analysis_false
        )

    case "Example Part 1 (Spot-Idx: A1-L11, Ctrl: Col 1)":
        image_path = Path(r"example_files/part1_a1-l11.tif")

    case "Example Part 2 (Spot-Idx: A12-L22, Ctrl: Col 22)":
        image_path = Path(r"example_files/part2_a12-l22.tif")

    case _:
        raise Exception("No proper image upload option was chosen")

# Show the Settings Menu once a file_path has been chosen
if image_path:
    st.markdown("## Image to be analyzed")
    image_container = st.container()

    col1, col2 = st.columns(2)

    # Displays the available Settings
    with col1:
        st.markdown("⚙️ ***Settings***")

        # Set the indexing for the first spot: Required for the calculation of grid parameters.
        first_spot = st.text_input(
            "Index of First Spot", placeholder="A1", on_change=stim.set_analysis_false
        )

    with col2:
        # Toggle the inversion of the grayscale image.
        invert_image_colors = st.toggle(
            "Invert grayscale Image",
            value=True,
            on_change=stim.set_analysis_false,
        )

        # Set the indexing for the last spot: Required for the calculation of grid parameters.
        last_spot = st.text_input(
            "Index of Last Spot", placeholder="L20", on_change=stim.set_analysis_false
        )

    stim.check_spot_settings(first_spot, last_spot)

    with image_container:
        stim.load_image(image_path, invert_image_colors)
        stim.display_loaded_image()

    with st.form("Settings", border=False):

        with st.expander("**Spot detection**", expanded=True):
            stim.spot_detection_settings()

        with st.expander("**Spot correction**", expanded=True):
            stim.spot_correction_settings()

        with st.expander("**Halo detection**", expanded=False):
            stim.halo_detection_settings()

        with st.expander("❗ Advanced Settings", expanded=False):
            stim.advanced_settings()

        if st.form_submit_button(
            "Start Analysis!",
            type="primary",
            disabled=st.session_state["image_analysis"]["disable_start"],
            use_container_width=True,
        ):
            stim.run_analysis(first_spot, last_spot)
            st.session_state["image_analysis"]["analysis"] = True

if st.session_state["image_analysis"]["analysis"]:
    st.markdown("## Results")
    tab1, tab2, tab3, tab4 = st.tabs(["Image", "Table", "Heatmap", "Grid"])

    spot_list = st.session_state["image_analysis"]["results"]["spot_list"].copy()

    with tab2:
        df = st.session_state["image_analysis"]["results"]["spot_list"].to_df()
        df_new = st.data_editor(
            df,
            disabled=[name for name in df.columns if name != "halo_radius"],
        )

        if st.button("Update Dataset", type="primary"):
            stim.update_spotlist(df_new)

    figuredict = {}
    with tab1:
        fig_img, ax = plt.subplots()
        st.session_state["image_analysis"]["results"]["spot_list"].plot_image(
            st.session_state["image_analysis"]["image"], ax=ax
        )
        st.pyplot(fig_img)
        figuredict["img_results"] = fig_img

    with tab3:
        fig_hm, ax = plt.subplots()
        st.session_state["image_analysis"]["results"]["spot_list"].plot_heatmap(ax=ax)
        st.pyplot(fig_hm)
        figuredict["heatmap"] = fig_hm

    with tab4:
        fig_grid, ax = plt.subplots()
        st.session_state["image_analysis"]["results"]["grid"].plot_image(
            st.session_state["image_analysis"]["image"], ax=ax
        )
        st.pyplot(fig_grid)
        figuredict["detected_grid"] = fig_grid

    c1, c2 = st.columns(2)
    with c2:
        # Creates a Zipfile containing all plots as .svg files on this page and makes it ready for download.
        stim.download_figures(figuredict, "svg")

    with c1:
        # Creates a Zipfile containing all plots as .png files on this page and makes it ready for download.
        stim.download_figures(figuredict, "png")
