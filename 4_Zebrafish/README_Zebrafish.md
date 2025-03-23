# Zebrafish

This workflow is used to segment the otic vesical of Zebrafish and measure the state of co infections within it, based on fluorescence. The README_setup file provides details on the installation and usage of the necessary software. More details can also be found in the paper and the accompanying protocols.

- [A new protocol for multispecies bacterial infections in zebrafish and their monitoring through automated image analysis](https://www.biorxiv.org/content/10.1101/2024.01.15.575759v2.supplementary-material)

### Scripts
- __sort_images_nd2.py:__ this script is designed to convert Nikon NIS-Elements ND2 files into individual TIFF files. It processes each series, timepoint, channel, and Z-stack within the ND2 file and saves them as TIFF images. The output is organized into directories for each series, with separate subdirectories for bright-field (C = 0) and fluorescence images (C > 0).
- __segmentation.sh:__ Starts a Docker container to run the segmentation model. A path to the folder containing the 'Images' and 'Fluor' folders, created with the previous script, needs to be provided.
- __segmentation.ps1:__ Segmentation script for use on Windows
- __check_measure.py:__ FIJI script to check the quality of the segmentation and measure features in the otic vesical
- __co_localization.R:__ R script to analyze the results from the __check_measure.py__ script

### Example
- The example consists of two imaged zebrafish after the pre-processing step

---

### Pre-Processing

The `sort_images_nd2.py` script converts Nikon Image Files (.nd2) into the correct format. 
Run it with the following command in the terminal:
```
python sort_images_nd2.py path/to/your/nd2file
```
### Otic Vesicle Segmentation

 The segmentation model runs in a Docker container. Therefore make sure that the Docker engine is running. Execute the segmentation script by running the following and providing the path to one of the imaged positions (created in the previous step):

```
./segmentation.sh path/to/position/folder
```
### Segmentation Validation and Measurements

Run the `check_measure.py` FIJI script and select the folder of the fish you want to check. All segmentations will be displayed on the image and listed in the ROI Manager. Go through the slices and delete bad segmentations in the ROI Manager and klikh `OK` to continue. The measurements are saved automatically and an image showing the area occupied by bacteria is created. The results from multiple fish can also be plotted with the `co_localization.R` script.