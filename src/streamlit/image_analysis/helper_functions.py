import io
import os
import tempfile
import zipfile

import matplotlib.pyplot as plt

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
