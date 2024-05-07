![Logo](../assets/Logo.png)

# MicroSpot-Reader WebApp user guide

***Author:*** *Simon Knoblauch*
## Introduction

The MicroSpot-Reader WebApp is a bioinformatic tool meant to assist researchers in the identification process of bioactive compounds in complex biological samples during Liquid Chromatography Mass Spectrometry (LC-MS) analysis. The tool employs an image processing algorithm to extract bioactivity data from optical biological or biochemical assays performed on LC fractions, particularly utilizing grid-based assay systems such as well plates or microfluidic devices. Subsequently, the tool constructs a bioactivity chromatogram, providing a comprehensive representation of bioactive peaks. This chromatogram is then correlated with features derived from untargeted metabolomics experiments. By integrating the bioactivity information with mass spectrometric data, the tool facilitates the precise correlation of specific m/z-values with bioactive compounds. This synergistic approach aims not only to enhance the accuracy of bioactive compound identification but also provides valuable insights into the molecular basis of bioactivity within complex biological mixtures, thereby advancing our understanding of the functional aspects of metabolomes. An example of an experimental workflow benefiting from this App is shown in Fig. 1.

![Basic Workflow for annotation of LC-MS features with bioactivity-data](../assets/userguide/experimental_workflow.png)
***Figure 1: Basic Workflow for annotation of LC-MS features with bioactivity-data:*** *A complex sample undergoes HPLC separation. Post-column, the eluate is divided between mass spectrometric analysis and fractionation. Feature detection of mass spectrometry data provides information on m/z and retention time of compounds in the eluate. Simultaneously, the fractionation set-up deposits the sample onto a grid-based microfluidic device or well-plate. Optical biological or biochemical assays performed on the fractions then yield activity data, from which an activity chromatogram can be constructed. The activity chromatogram's peaks are then correlated with features from mass spectrometry through careful alignment of retention times and systematic peak-shape correlation.*

### Libraries used

The MicroSpot-Reader WebApp is implemented in Python 3.11 and leverages the Streamlit open-source app framework. All key libraries that have substantially contributed to the codebase are listed along with their version numbers in Tab. 1. An exhaustive list of *all* used packages and libraries can be found in the `environment.yml` file in our [GitHub repository](https://github.com/Functional-Metabolomics-Lab/MicrospotReader).

***Table 1: Python Libraries which contributed substantially to the MicroSpot-Reader WebApp codebase.***
|Library        |Version    |Citation                   
|-              |-          |-       
|Streamlit      | 1.31.1    | [Snowflake Inc.](https://streamlit.io/)
|NumPy          | 1.26.1    | [Harris *et al.*](https://doi.org/10.1038/s41586-020-2649-2)
|pandas         | 2.1.2     | [McKinney *et al.*](https://doi.org/10.25080/Majora-92bf1922-00a), [pandas development team](https://doi.org/10.5281/zenodo.10045529)
|SciPy          | 1.11.3    | [Virtanen *et al.*](https://doi.org/10.1038/s41592-019-0686-2)
|pyOpenMS       | 3.1.0     | [Röst *et al.*](https://doi.org/10.1038/nmeth.3959), [Röst *et al.*](https://doi.org/10.1002/pmic.201300246)
|scikit-image   | 0.22.0    | [Van der Walt *et al.*](https://doi.org/10.7717/peerj.453)
|Matplotlib     | 3.8.0     | [Hunter](https://doi.org/10.1109/MCSE.2007.55)
|Numba          | 0.59.0    | [Lam *et al.*](https://doi.org/10.1145/2833157.2833162)

### General Layout

The Layout of the WebApp is shown in Fig. 2, it comprises three distinct modules: (1) Image Analysis, (2) Data Preparation and Merging and (3) Feature Finding and Annotation.

1. **Image Analysis:**
The Image Analysis page is used to derive activity values for each fraction from an image of the performed activity assay. The output is a table containing information on each fractions index on the microwellplate or microfluidics device.

2. **Data Preparation and Merging:**
The Data Preparation and Merging page constructs an activity chromatogram from image analysis data. Multiple datasets from the same LC-MS run can be merged. This page associates fractions with retention time to generate the chromatogram.

3. **Feature Finding and Annotation:** 
The Feature Finding and Annotation page conducts feature detection on a centroided mzML file of the LC-MS run. The identified features are correlated with peaks in the bioactivity chromatogram via retention time matching and peak shape correlation. This process yields feature tables for each activity peak and a comprehensive LC-MS feature table.

</br>

![General Layout of the WebApp](../assets/userguide/layout.png)
***Figure 2: General Layout of the WebApp:*** *(1) Image Processing page, (2) Data Preparation and Merging page, (3) deprecated .mzML-File Annotation and (5) Display of Datasets stored in the Session.*

In addition to the web app pages, the sidebar provides information on stored session data through a table (5). Each stored dataset is labeled with its *name* and its *type*. The following data types can be stored in the session:

- **Image Data:** Contains saved datasets from image analysis.

- **Prepared Data:** Contains saved datasets from data preparation and merging.

The process for adding data will be explained in later chapters. Please be aware that session data is lost upon closing the app!

### Requirements

The application relies on two essential input files. Firstly, an optical readout of an activity assay in image format (.png, .jpg, or .tif) is necessary for image analysis. The image's color space must be either RGB (colored images) or grayscale (black and white images). The image should display circular wells or spots organized in a grid-based manner, as is the case with standard well-plates. To avoid potential artifacts during analysis, it is recommended to crop the image, focusing only on the relevant wells or spots.

In cases where multiple assays are needed to cover all fractions collected during the LC run, it is advised to either capture one image per assay or split the recorded image into multiple images containing one assay each. This approach ensures that image analysis and normalization can be conducted independently for each assay.

Oversaturation of regions in the image should be prevented, as this could distort peak shapes during subsequent analysis. In later chapters examples will be discussed, where oversaturation may not be problematic, it is however generally advisable to avoid it proactively.

<!-- TODO: Add figure for image examples here -->

The second vital input file is a centroided .mzML file containing information on the performed LC-MS run for feature detection and annotation. The file must contain data from an LC-MS run that can sensibly be correlated with the bioactivity data derived from image analysis. While using an experimental setup as described in Fig. 1 is recommended, alternatively, data from a separate LC-run conducted under identical conditions to the one executed for fraction collection can be used. For precise activity correlation it is important, that the retention times of all compounds in the two runs closely align.

## Walkthrough of the App

As mentioned in the introduction, the WebApp is comprised of three main modules: (1) Image Analysis, (2) Data preparation and merging, and (3) Feature detection and annotation. This walkthrough will explain the general workflow intended for this app using an example dataset. The examples can be found on our [GitHub repository](https://github.com/Functional-Metabolomics-Lab/MicrospotReader) in the `example_files` folder. 

In the folder you will find *two* images in `.tif` format that will be used for **image analysis**. Both of these images contain activity data of reporter gene assays from the *same* fractionation experiment. Two assays had to be performed as the imaging system used to record the images does not allow for the entirety of the microfluidic device to be imaged at once. We will therefore perform image analysis *twice* and in the following step, **data preparation and merging**, we will merge the datasets of both images to construct an activity chromatogram. Additionally the first column of the first image as well as the last column of the second image were used as control-columns to check the background signal of the assay. They were thus not used for fractionation during the LC-run. Before assigning each fraction a retention time, we will have to remove these columns from the dataset. The result of the data preparation step can also be found in the `example_files` folder with the name `activity_table.csv`. Finally we will perform feature detection using the `example_mzml.mzML` file and find possibly bioactive features within the feature table by correlating them to the bioactivity values obtained in the **feature finding and annotation** module.

This chapter will only concern itself with the user workflow of the app and keep technical details to a minimum. The algorithms used in each module as well as all settings will be explained in a separate chapter later.

### Image analysis

In this section we will focus on the *image analysis* module of the MicrospotReader WebApp. As explained above, we will perform image analysis *twice*, once with each picture in the `example_files` folder in our [GitHub repository](https://github.com/Functional-Metabolomics-Lab/MicrospotReader). Each time we will focus on a different aspect of the module. To start image analysis please navigate to the *"Image Analysis"* page by selecting it in the top left corner.

#### Example Part 1: Simple workflow

Once you have navigated to the *"Image Analysis"* page, you will be asked to upload an image using the drag and drop field (2) provided. In this example we will instead be using the provided dropdown menu (1) to select ***"Example Part 1"***. The selected or uploaded image should now be displayed in grayscale using the *viridis* colormap.

![Step 1: Uploading Image](../assets/userguide/image_analysis/step1.png)

Below the displayed image you will find the settings that can be changed for image analysis. Most of the settings are hidden inside expandable menus organized by the step of image analysis that they influence. Depending on the measurement setup used by you, it may be critical to change some of these parameters. In a later chapter we will go through how to change these settings. Since the settings of the WebApp are optimized for our measurement set up, none of the "hidden" settings will have to be changed. 

You are however prompted to enter the indices of the first (1) and last spot (2). We refer to each individual fraction that has been fractionated onto our microfluidic device as a ***spot***. The *"First Spot"* refers to the top-left most spot visible in the image, while the *"Last Spot"* refers to the bottom-right most spot visible in the image. Indices should be provided as `<LETTER><NUMBER>`, where the letter (from A-Z) indicates the *row-index* and the number indicates the *column-index*, similarly to microwellplates. In the case of this example the index of the first spot would be **A1** and the index of the last spot would be **L11**. We can now press the ***"Start Analysis"*** button to initiate analysis.
   
![Step 2: Settings](../assets/userguide/image_analysis/step2.png)

Once analysis has concluded, results will be displayed in 3 tabs below the *"Start Analysis"* button: (1) "Image", (2) "Table" and (3) "Heatmap".

![Step 3: Results](../assets/userguide/image_analysis/step3.png)

*(1) The resulting Image:* The first tab *"Image"* of the *Results-View* shows the analyzed image overlaid with some of the extracted information:

1. All spots detected during initial spot detection (shown in black)
2. All spots backfilled during spot correction (shown in red)
3. The row and column indices of the spots

This view allows you to check for any mistakes made during image analysis, like missing rows or columns, correct detection of all spots and correct row and column indexing as well as providing a nice overview of what the algorithm has detected.

*(2) The Data Table:* The data table is the most important piece of information obtained by image analysis. It contains the indices and activity values for each spot detected by the algorithm. This table is used in the *data preparation and merging* step, at which point each spot will be assigned a retention time based on their indices. This information can then be used to construct a bioactivity chromatogram. By hovering over the table and finding the download button on the top left of the table, you can save the results of this step to your computer.

![Step 4: Saving tabular data](../assets/userguide/image_analysis/step4.png)

The following table provides a comprehensive overview of the data saved in the table provided by the image analysis page:

| Name          | Description
| ---           | ---
| *Unnamed*     |  row-index of the table.
| *row*         |  numeric index of the row a specific spot belongs to.
| *row_name*    |  alphabetic index of the row a specific spot belongs to.
| *column*      |  numeric index of the column a specific spot belongs to.
| *type*        |  type of the spot, currently not in use. 
| *x_coord*     |  x-coordinate of the center of a spot.
| *y_coord*     |  y-coordinate of the center of a spot. Note that for images, the higher the y-value, the lower the spot is in the image.
| *radius*      |  radius of the detected spot in pixels.
| *halo_radius* |  radius of the halo surrounding a particular spot in pixels. If no halo was detected, this field is empty.
| *spot_intensity* |  spot intensity value used for further processing steps. At this stage it displays the raw_int column normalized by the median spot intensity.
| *raw_int*     |  raw intensity of a spot defined as the mean intensity of pixels within the spot.
| *note*        | Shows at which stage a particular spot was detected. Currently either "Initial Detection" if a spot was detected during initial spot detection or "Backfilled" if a spot was backfilled during spot-correction.


*(3) The Heatmap:* The *"Heatmap*" tab, fittingly, displays a heatmap of all spot-intensities found in the image. It provides a visual overview of the results by the image analysis module, that is complementary to the plot shown in the *"Image"* tab. Both plots can be saved with some additional information in `.png` (1) or `.svg` (2) format using the two buttons  provided below the results tabs.

![Step 5: Saving Plots](../assets/userguide/image_analysis/step5.png)

After inspecting and downloading your results, you can save them in the current session. This facilitates data handling, as you do not have to upload the downloaded datatable for each consecutive step. To save your data to the current session, navigate to the sidebar, enter a unique name for your dataset (1) and press the *"Add current Data to Session"* button. The data will then be displayed in the sidebar. All datasets added during the image analysis step will be labeled with the type *"Image Data"*. The name of the set can still be changed after adding it to the session, by double-clicking its name in the "Name" column, choosing a new name and then pressing the *"Apply Changes"* button. If you want to delete a saved dataset, please select it by ticking the box in the "Select" column and then pressing the *"Delete Selection"* button.

![Step 6: Saving to Session](../assets/userguide/image_analysis/step6.png)

After saving your results, you can safely continue with the analysis of other images or with the *"data preparation and merging"* step. In our case we will continue with the analysis of our second example image called *"Example Part 2"* by scrolling the the top of the page and selecting it in the first dropdown menu mentioned.

#### Example Part 2: Halo detection

If we inspect the second image, we will find a section of high bioactivity in the bottom third of the picture indicated by high grayscale values. At this point it may be of importance to mention, that the bioactivity assay performed in this example was a reporter gene assay. The reporter gene used induces a luminescent signal upon cellular stress. Bacteria on spots with a high luminescent signal are therefore likely under higher cellular stress compared to spots with low luminescent signal. This can be correlated with antimicrobial activity of the fraction that was fractionated onto that specific spot. High antimicrobial activity can lead to an inhibition zone around the center of the spot. This leads to antimicrobial halos being visible in the image. Some spots on the example image do show antimicrobial halos, they are characterized by a ring around the the spot with higher luminescent intensities compared to the center. In these cases, the intensity values of the spots do not correlate well with the actual bioactivity of the fraction. This is why, in these cases, we perform an additional step during image analysis called *"Halo Detection"*. During this step, halos and their radii are detected within the image to extract semi-quantitative information from these spots. 

After selecting *"Example Part 2"* we again have to enter the indices of the first and last spot. As we are now dealing with the second half of the microfluidics device, the first index will be **A12** and the last index will be **L22**. Before pressing the *"Start Analysis"* button however, we will now enable the halo detection step in the settings. We do this by navigating to the settings tab called *"Halo detection"* and activating the *"Enable Halo detection"* (1) and *"Scale Halo radii to Spot intensity"* (2) settings. This second setting is important to include information extracted by halo detection in the chromatogram construction step. How this works in detail is explained in the chapter explaining the algorithm. After enabling these two settings you can go ahead and start the analysis.

![Step 7: Enabling Halo detection](../assets/userguide/image_analysis/step7.png)

If we now inspect the results, we can see that not all halos could be detected within the image. Specifically *I20* and *J20* have wrongfully not been assigned a halo radius. This is because the algorithm used for halo detection is not as robust as the spot detection algorithm and therefore is more prone to errors. We can now backfill the missing halo radii through interpolation using the neighboring spots. The simplest method for this is a linear interpolation, where we take the mean of the halo radii of the spots located before and after the current spot. For I20 this would result in a halo radius of 71 and for J20 in a halo radius of 68. We can now manually input these values in the data table for the two corresponding spots (1). By pressing the *"Update Dataset"* (2) button the dataset will then be updated to correctly include the interpolated values. If you now inspect the results tabs again, you will see that both I20 and J20 are labeled with a halo radius.

Similarly if a spot has been wrongfully assigned a halo radius, you can remove the false positive by deleting the corresponding halo radius in the datatable and then pressing the *"Update Dataset"* button.

![Step 8: correcting halos](../assets/userguide/image_analysis/step8.png)

After inspecting your results, you can again add the dataset to the current session and proceed to the next step.

### Data preparation and merging

