import streamlit as st
from src.streamlit.DataStorage import DataStorage


def initialize_session_states():
    session_states = {
        "sidebar": {"data_storage": DataStorage()},
        "image_analysis": {
            "settings": {
                "spot_detector": {
                    "edge_detection": {
                        "sigma": 10,
                        "low_threshold": 0.001,
                        "high_threshold": 0.001,
                    },
                    "circle_detection": {
                        "min_distance_px_x": 70,
                        "min_distance_px_y": 70,
                        "smallest_radius_px": 20,
                        "largest_radius_px": 30,
                        "detection_threshold": 0.3,
                    },
                },
                "grid_detector": {
                    "line_detection": {
                        "maximum_tilt": 5,
                        "minimum_distance_px": 80,
                        "threshold": 0.2,
                    },
                    "spot_mask": {"spot_radius": 5},
                },
                "spot_corrector": {
                    "general": {"spot_radius_backfill": 0},
                    "from_grid": {"distance_threshold_px": 10},
                },
                "halo_detector": {
                    "preprocessing": {
                        "disk_radius_opening": 5,
                        "minimum_object_size_px": 800,
                        "disk_radius_dilation": 10,
                    },
                    "circle_detection": {
                        "min_distance_px_x": 70,
                        "min_distance_px_y": 70,
                        "smallest_radius_px": 40,
                        "largest_radius_px": 100,
                        "detection_threshold": 0.2,
                    },
                    "halo_assignment": {"distance_threshold_px": 15},
                },
                "halo_detection_toggle": False,
                "halo_scaling_toggle": False,
                "halo_scaling_factor": 0.04,
                "get_intensity_spotradius": 0,
                "toggle_normalization": True,
            },
            "results": {"spot_list": None, "grid": None},
            "analysis": False,
            "image": None,
            "disable_start": True,
        },
        "data_preparation": {"df": None},
        "feature_finding": {
            "settings": {
                "feature_finder": {
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
                },
                "activity_detector": {
                    "peak_detection": {
                        "automatic_threshold": True,
                        "noise_convergence": 0.02,
                        "manual_threshold": 0.0,
                        "minimum_SNR": 3,
                    }
                },
                "activity_annotator": {"rt_correlation": {"window_s": 2, "bias_s": 0}},
            },
            "results": None,
        },
    }

    for name, state in session_states.items():
        if name not in st.session_state:
            st.session_state[name] = state


def page_setup():
    # Sets title and site icon
    st.set_page_config(
        page_title="Microspot Reader",
        page_icon="assets/Icon.png",
        initial_sidebar_state="auto",
        menu_items={
            "About": """
                    - Interested in contributing? Check out our [GitHub personal page](https://github.com/sknesiron).
                    - For more about our work, visit our [lab's GitHub page](https://github.com/Functional-Metabolomics-Lab).
                    - Follow us on [Twitter](https://twitter.com/Functional-Metabolomics-Lab) for the latest updates.

                    Made by Simon B. Knoblauch
                    """,
            "Report a Bug": "https://github.com/Functional-Metabolomics-Lab/MicrospotReader/issues/new",
        },
    )
    # Initializes all required session states
    initialize_session_states()
