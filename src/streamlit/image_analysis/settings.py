import streamlit as st


def spot_detection_settings():
    col1, col2 = st.columns(2)
    with col1:
        st.session_state["image_analysis"]["settings"]["spot_detector"][
            "circle_detection"
        ]["smallest_radius_px"] = st.number_input(
            "Smallest tested radius *[in pixels]*:",
            value=20,
            step=1,
            min_value=1,
        )

        st.session_state["image_analysis"]["settings"]["spot_detector"][
            "circle_detection"
        ]["min_distance_px_x"] = st.number_input(
            "Minimum x-distance between spots *[in pixels]*:",
            value=70,
            step=1,
            min_value=0,
        )

    with col2:
        st.session_state["image_analysis"]["settings"]["spot_detector"][
            "circle_detection"
        ]["largest_radius_px"] = st.number_input(
            "Largest tested radius *[in pixels]*:",
            value=30,
            step=1,
            min_value=1,
        )

        st.session_state["image_analysis"]["settings"]["spot_detector"][
            "circle_detection"
        ]["min_distance_px_y"] = st.number_input(
            "Minimum y-distance between spots *[in pixels]*:",
            value=70,
            step=1,
            min_value=0,
        )


def spot_correction_settings():
    c1, c2 = st.columns(2)
    with c1:
        st.session_state["image_analysis"]["settings"]["grid_detector"][
            "line_detection"
        ]["minimum_distance_px"] = st.number_input(
            "Minimum distance between grid-points *[in pixels]*:",
            value=80,
            step=1,
            min_value=0,
        )

    with c2:
        st.session_state["image_analysis"]["settings"]["spot_corrector"]["from_grid"][
            "distance_threshold_px"
        ] = st.number_input(
            "Max. spot-distance from grid-points *[in pixels]*:",
            value=10,
            min_value=1,
            step=1,
        )


def halo_detection_settings():
    # Enables or disables the detection of Halos
    st.session_state["image_analysis"]["settings"]["halo_detection_toggle"] = st.toggle(
        "Enable Halo detection", value=False
    )

    c1, c2 = st.columns(2)
    with c1:
        st.session_state["image_analysis"]["settings"]["halo_detector"][
            "circle_detection"
        ]["smallest_radius_px"] = st.number_input(
            "Smallest tested radius *[in pixels]*:",
            value=40,
            step=1,
            min_value=1,
        )

        st.session_state["image_analysis"]["settings"]["halo_detector"][
            "circle_detection"
        ]["min_distance_px_x"] = st.number_input(
            "Minimum x-distance between halos *[in pixels]*:",
            value=70,
            step=1,
            min_value=0,
        )

        st.session_state["image_analysis"]["settings"]["halo_scaling_toggle"] = (
            st.toggle("Scale Halo radii to Spot intensity", value=False)
        )

    with c2:
        st.session_state["image_analysis"]["settings"]["halo_detector"][
            "circle_detection"
        ]["largest_radius_px"] = st.number_input(
            "Largest tested radius *[in pixels]*:",
            value=100,
            step=1,
            min_value=1,
        )

        st.session_state["image_analysis"]["settings"]["halo_detector"][
            "circle_detection"
        ]["min_distance_px_y"] = st.number_input(
            "Minimum y-distance between halos *[in pixels]*:",
            value=70,
            step=1,
            min_value=0,
        )

        st.session_state["image_analysis"]["settings"]["halo_scaling_factor"] = (
            st.number_input(
                "Scaling Factor:",
                value=0.04,
                min_value=0.0,
            )
        )


def advanced_settings():
    st.markdown("__Initial Spot-Detection__")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state["image_analysis"]["settings"]["spot_detector"][
            "edge_detection"
        ]["sigma"] = st.number_input(
            "Sigma-value for gaussian blur:",
            min_value=1,
            max_value=20,
            step=1,
            value=10,
        )

        st.session_state["image_analysis"]["settings"]["spot_detector"][
            "edge_detection"
        ]["low_threshold"] = st.number_input(
            "Edge-detection low threshold:",
            value=0.001,
            min_value=0.000000,
            format="%f",
        )

    with c2:
        st.session_state["image_analysis"]["settings"]["spot_detector"][
            "circle_detection"
        ]["detection_threshold"] = st.number_input(
            "Spot-detection threshold:",
            value=0.3,
            min_value=0.0,
            format="%f",
        )

        st.session_state["image_analysis"]["settings"]["spot_detector"][
            "edge_detection"
        ]["high_threshold"] = st.number_input(
            "Edge-detection high threshold:",
            value=0.001,
            min_value=0.000000,
            format="%f",
        )

    st.divider()

    st.markdown("__Grid-Detection__")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state["image_analysis"]["settings"]["grid_detector"][
            "line_detection"
        ]["maximum_tilt"] = st.number_input(
            "Maximum tilt of grid *[in degrees]*:", value=5, step=1, min_value=0
        )

    with c2:
        st.session_state["image_analysis"]["settings"]["grid_detector"][
            "line_detection"
        ]["threshold"] = st.number_input(
            "Threshold for line-detection:", value=0.2, min_value=0.0
        )

    st.divider()

    st.markdown("__Spot Correction and Intensity Evaluation__")

    st.session_state["image_analysis"]["settings"]["toggle_normalization"] = st.toggle(
        "Normalize Spot Intensities by median value", value=True
    )

    st.session_state["image_analysis"]["settings"]["get_intensity_spotradius"] = (
        st.number_input(
            "Disk-Radius for spot-intensity calculation *[in pixels]*:",
            value=0,
            min_value=0,
            step=1,
        )
    )

    st.divider()

    st.markdown("__Halo-Detection__")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state["image_analysis"]["settings"]["halo_detector"][
            "circle_detection"
        ]["detection_threshold"] = st.number_input(
            "Halo-detection threshold:",
            value=0.2,
            min_value=0.0,
        )

        st.session_state["image_analysis"]["settings"]["halo_detector"][
            "preprocessing"
        ]["disk_radius_dilation"] = st.number_input(
            "Disk radius for morphological dilation *[in pixels]*:",
            value=10,
        )

    with c2:
        st.session_state["image_analysis"]["settings"]["halo_detector"][
            "preprocessing"
        ]["minimum_object_size_px"] = st.number_input(
            "Minimum Object Size *[in pixels]*:",
            value=800,
            min_value=0,
            step=1,
        )
