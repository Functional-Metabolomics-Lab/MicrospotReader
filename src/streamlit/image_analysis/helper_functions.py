import io
import os
import tempfile
import zipfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pyopenms as oms

import streamlit as st
from src.microspotreader import *


def set_analysis_false():
    st.session_state["image_analysis"]["analysis"] = False


def display_loaded_image():
    # Display the grayscale image using the "viridis" colormap.
    fig, ax = plt.subplots()
    img_plot = ax.imshow(st.session_state["image_analysis"]["image"])
    fig.colorbar(img_plot, shrink=0.5, label="Grayscale-Value")
    ax.axis("off")
    st.pyplot(fig)


def load_image(path, invert):
    img_loader = ImageLoader()
    img_loader.set(invert_image=invert)
    st.session_state["image_analysis"]["image"] = img_loader.prepare_image(path)
    st.toast("Image prepared Successfully!")


def check_spot_settings(first_spot, last_spot):
    if not first_spot or not last_spot:
        st.session_state["image_analysis"]["disable_start"] = True
        st.warning("Please enter Spot Indices!")

    else:
        st.session_state["image_analysis"]["disable_start"] = False


def get_rowindex_list(point1, point2):
    return [chr(i).upper() for i in range(ord(point1[0]), ord(point2[0]) + 1)]


def get_colindex_list(point1, point2):
    return [i for i in range(int(point1[1:]), int(point2[1:]) + 1)]


def get_first_colindex(point):
    return int(point[1:])


def get_first_rowindex(point):
    return ord(point[0].lower()) - ord("a") + 1


def get_spot_nr(point1, point2):
    return len(get_rowindex_list(point1, point2)) * len(
        get_colindex_list(point1, point2)
    )


def temp_figurefiles(figure_dict, suffix, directory):
    pathlist = []
    for figname, figure in figure_dict.items():
        figpath = os.path.join(directory, f"{figname}.{suffix}")
        figure.savefig(figpath, format=suffix, dpi=300)
        pathlist.append(figpath)
    return pathlist


@st.cache_resource
def temp_zipfile(paths):
    with tempfile.NamedTemporaryFile(delete=False) as tempzip:
        with zipfile.ZipFile(tempzip.name, "w") as temp_zip:
            for figurepath in paths:
                temp_zip.write(figurepath, arcname=os.path.basename(figurepath))
    return tempzip


def download_figures(figure_dict: dict, suffix: str = "svg") -> None:
    with tempfile.TemporaryDirectory() as tempdir:
        paths = temp_figurefiles(figure_dict, suffix, tempdir)

        tempzip = temp_zipfile(paths)

        with open(tempzip.name, "rb") as zip_download:
            st.download_button(
                label=f"Download Plots as .{suffix}",
                data=io.BytesIO(zip_download.read()),
                mime=".zip",
                file_name="plots_img-analysis.zip",
                use_container_width=True,
            )
        os.unlink(tempzip.name)


def update_spotlist(df_new):
    spot_list = SpotList().from_df(df_new)

    spot_list.reset_intensities()

    if st.session_state["image_analysis"]["settings"]["toggle_normalization"]:
        spot_list.normalize_by_median()

    if st.session_state["image_analysis"]["settings"]["halo_scaling_toggle"]:
        spot_list.scale_halos_to_intensity(
            st.session_state["image_analysis"]["settings"]["halo_scaling_factor"]
        )
    st.session_state["image_analysis"]["results"]["spot_list"] = spot_list
    st.rerun()


def download_gnpsmgf(
    consensus_map: oms.ConsensusMap, mzmlfilename: str, exp: oms.MSExperiment
):
    filtered_map = oms.ConsensusMap(consensus_map)
    filtered_map.clear(False)
    for feature in consensus_map:
        if feature.getPeptideIdentifications():
            filtered_map.push_back(feature)

    temp = tempfile.NamedTemporaryFile(suffix=".consensusXML", delete=False)
    temp.close()
    oms.ConsensusXMLFile().store(temp.name, filtered_map)

    with tempfile.TemporaryDirectory() as tempdir:
        mgf_name = os.path.join(tempdir, "MS2data.mgf")
        quant_name = os.path.join(tempdir, "FeatureQuantificationTable.txt")
        mzml_name = os.path.join(tempdir, os.path.basename(mzmlfilename))

        oms.MzMLFile().store(mzml_name, exp)

        oms.GNPSMGFFile().store(
            oms.String(temp.name), [mzml_name.encode()], oms.String(mgf_name)
        )
        oms.GNPSQuantificationFile().store(consensus_map, quant_name)

        tempzip = temp_zipfile([mzml_name, mgf_name, quant_name])
    os.unlink(temp.name)

    with open(tempzip.name, "rb") as zip_download:
        st.download_button(
            label=f"Download Files for FBMN",
            data=io.BytesIO(zip_download.read()),
            mime=".zip",
            file_name="fbmn_files.zip",
            use_container_width=True,
            type="primary",
        )
