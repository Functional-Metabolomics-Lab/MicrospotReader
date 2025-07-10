![image](assets/Logo.png)

# MicroSpot Reader

Web-App for the detection of bioactive features in an untargeted metabolomics experiment with concomitant bioactivity determination. 

## Web-App

The Web-App is based on streamlit and can be accessed online via the following link:

[![Open Website!](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://microspotreader.gnps2.org/)

### Local Installation:

MicrospotReader can be installed on Windows and Linux. For installation on Linux please download the `linux` branch of this repository.

1. Clone this repository
2. Open Windows Terminal and go to the main folder of the repository:

`cd <filepath>`

1. Create and activate a new conda environment:

`conda env create -f environment.yml`

`conda activate microspotreader`

4. Start the App by running `run.py`

## User Guide

A user guide for the WebApp is provided in the `userguide`-folder. It contains a walkthrough of each module of the app, a description of the algorithms used and an explanation of all possible settings as well as advice on how to set them.

## Jupyter Notebooks

Additionally, this Repository contains Jupyter Notebooks in the `notebooks`-folder if you do not wish to use the Web-App:

- `1_image_analysis.ipynb`: Detection and analysis of MicroSpots as well as antimicrobial halos within an image. Determination of bioactivity.

- `2_data_preparation.ipynb`: Concatenation of Spot-Lists of the same LC-MS run and correlation of MicroSpots with a retention time.

- `3_feature_finding.ipynb`: Feature detection and annotation with activity data from .csv file prepared with previous steps and a .mzML file.
