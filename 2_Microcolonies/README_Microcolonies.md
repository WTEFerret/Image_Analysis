# 2. Microcolonies


This workflow can be used to follow micro-colonies growing on agarose pads. It segments the micro-colonies as a whole, tracks them over time and provides tools to correct the segmentation and tracking. 

### Scripts
- batch_unpack_vis.py (FIJI)
- drift_correction.py (FIJI)
- segment_colonies_batch.py (FIJI)
- colony_seg_correction.py (FIJI)
- measure_colonies.py (FIJI)
- collect_results.R (R)

### Example
- The Example consists of one imaged position, processed up until step 3. 

### 1. Pre-Processing
The images can be converted to individual tiff images with the `batch_unpack_vis.py` script or by importing the file into FIJI and exporting them as tiff images. The images have to be exported as individual TIFF-stacks for each channel, with the phase contrast stack ending in `_phase.tif` and the fluorescence stack in `_fluor.tif` respectively. 
In a first step, we corrected drift between time-points. We aligned the different frames using a script that can be found on [GitHub](https://github.com/fiji/Correct_3D_Drift). 

#### Usage
- The drift correction is already integrated in the `batch_unpack_vis.py` script, but in order for it to work the `drift_correction.py` script must be in the same directory as the `batch_unpack_vis.py` script. 
- After starting the script in FIJI select the parent directory containing all your VSI-files.
- The script creates a new directory with subdirectories for each position.  

### 2. Threshold Segmentation
The next step was to segment individual colonies based on the phase contrast images. The image background was subtracted using the rolling ball algorithm in FIJI (radius = 40 pixels, ca. 4 µm) to correct for uneven illumination and increase the contrast between background and colonies. To smooth over gaps in between cells of a colony, we applied a Gaussian filter (sigma = 10 pixels, ca. 1 µm). We used the default automatic threshold function to create a segmentation mask and subsequently regions of interest (ROI).
This step can be performed with `segment_colonies_batch.py` script.

#### Usage
- To run the segmentation on all positions run the `segment_colonies_batch.py` script in FIJI and select the parent directory containing all subdirectories of the the individual positions
- A ROI folder gets created within each position directory.
- The ROIs are stored as zip files for each time-point

### 3. Correct Segmentation and Tacking
 In a next step, we manually corrected our segmentation. The manual correction consisted of separating merging colonies based on fluorescence images, in the case of mixed position, or by eye for colonies of the same strain and combining colonies that merge early in the time-lapse. We further excluded colonies that partially grew out of the field of view, and corrected or discarded colonies with inaccurate segmentations. Colonies were tracked over time, based on their overlap with the segmentation of the previous time-point. We discarded colonies that had no overlap with any colonies from the previous time-point. The colony_seg_correction.py script can help you perform these steps.

#### Usage
After starting the script in FIJI, select the folder of the position you want to correct. 
You can add or delete ROIs in the ROI Manager.
In addition, you can use the Command launcher to perform the following actions.

- __Extend:__ Extend a ROI with an overlapping manual selection.
- __Clone:__ Copy the currently selected ROI to the next frame.
- __Merge:__ Combine two selected ROI to one.
- __Split:__ Draw a selection over a ROI and split it along the selection.
- __Save:__ Save the corrected ROIs in a folder with a time-stamp.
- __Track:__ Track colonies over time. Note that all colonies not present in any time points will be removed in subsequent time points.

While correcting the ROIs, they are stored in a new folder (ROI_CHECK) and will be moved to another upon completion of the correction (ROI_DONE). If you want to change the already corrected further ROIs you can move the zip files from the ROI_DONE folder into the original ROI folder. 

> [!note]
> If the ROIs are not shown in the image, you have to select `More >> Options` in the ROI Manager 
> and untick the box `Associate "Show ALL" ROIs with slices`. 
> Here, you can also choose to 'Use ROI names as labels' to display the actual ROI names on the image.

### 4. Measurements
We measured the area (in number of pixels), roundness, aspect ratio and fluorescence for all the colonies in each time-point. In addition, we recorded the time when colonies started to grow in double layers and also manually measured the size of the second layers at the last time-point.

#### Usage
- Run the `measure_colonies.py` script in FIJI and select the position directory you want to measure
- You can tag a colony as fluorescent by selecting it at any time-point and pressing `tag` in the command launcher. This adds a `p` in front of the ROI name
- You can indicate the start of a second layer by selecting the colony at the time-point where the second layer starts and press `layer` in the command launcher.
- To measure the double layer in the last time-point you can manually add a ROI
- The `collect_results.R` can be used to combine the results of the different positions.