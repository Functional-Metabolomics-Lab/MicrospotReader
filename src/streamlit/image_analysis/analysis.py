import streamlit as st
from src.microspotreader import *
from src.streamlit.image_analysis.helper_functions import (
    get_first_colindex,
    get_first_rowindex,
    get_spot_nr,
)


def run_analysis(first_spot, last_spot):

    # Spot Detection
    spot_detector = SpotDetector(st.session_state["image_analysis"]["image"])
    spot_detector.change_settings_dict(
        st.session_state["image_analysis"]["settings"]["spot_detector"]
    )
    spot_list = spot_detector.initial_detection(get_spot_nr(first_spot, last_spot))

    # Grid detection for spot correction
    grid_detector = GridDetector(st.session_state["image_analysis"]["image"], spot_list)
    grid_detector.change_settings_dict(
        st.session_state["image_analysis"]["settings"]["grid_detector"]
    )
    grid = grid_detector.detect_grid()

    # Spot correction
    spot_corrector = SpotCorrector(spot_list)
    spot_corrector.change_settings_dict(
        st.session_state["image_analysis"]["settings"]["spot_corrector"]
    )
    spot_list = spot_corrector.gridbased_spotcorrection(grid)

    # Indexing of spots
    SpotIndexer(spot_list).assign_indexes(
        row_idx_start=get_first_rowindex(first_spot),
        col_idx_start=get_first_rowindex(first_spot),
    )
    spot_list.sort(serpentine=False)
    # Intensity determination of spots.
    spot_list.get_spot_intensities(
        image=st.session_state["image_analysis"]["image"],
        radius=st.session_state["image_analysis"]["settings"][
            "get_intensity_spotradius"
        ],
    )

    # Normalize by median if chosen
    if st.session_state["image_analysis"]["settings"]["toggle_normalization"]:
        spot_list.normalize_by_median()

    # Halo detection
    if st.session_state["image_analysis"]["settings"]["halo_detection_toggle"]:
        halo_detector = HaloDetector(st.session_state["image_analysis"]["image"])

        halo_detector.change_settings_dict(
            st.session_state["image_analysis"]["settings"]["halo_detector"]
        )

        halo_detector.perform_halo_detection()
        halo_detector.assign_halos_to_spots(spot_list)

    # scaling halos to spot intensities.
    if st.session_state["image_analysis"]["settings"]["halo_scaling_toggle"]:
        spot_list.scale_halos_to_intensity(
            st.session_state["image_analysis"]["settings"]["halo_scaling_factor"]
        )

    st.session_state["image_analysis"]["results"]["spot_list"] = spot_list
    st.session_state["image_analysis"]["results"]["grid"] = grid
