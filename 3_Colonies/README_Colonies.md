# README Colonies

This workflow can be used to analyse colonies (mixed or mono) growing on plates. Upon starting the script, you will be prompted to select a LIF-file as input. You can further select the option to only export the field of views containing a colony, skipping every second field of view, and if you want to segment the colonies or measure the entire field of view.

The selection of field of views containing colonies is based on the histogram of an Image. Since colonies are darker than the background, the histogram of an image with a colony has a bigger peak in the lower values. This works in most cases. If your plate is set up symmetrically, you can also choose to skip every second position.

The segmentation of colonies works by finding the sharp changes in intensity in the image, applying a Gaussian blur (sigma = 40 pixels), edge detection and an automatic threshold (default). This can sometimes be inaccurate, especially when there are other darker elements in the image. Since the Gaussian blur usually increases the size of the resulting ROI, it is automatically shrunk by 40 pixels to closer fit the original outline of the colony. When using the colony segmentation, it is also recommended to only select the fields of view containing colonies.

Since the LIF-files can be big, the script works through the images in blocks of 32 images at a time to save memory. To set this up, you must provide the number of plates you imaged.

### Script
- unpack_and_measure.py (FIJI)

### Example images
- 240320_T6SS_Pilot_19h_Mcherry.lif and 240320_T6SS_Pilot_19h_Mcherry.lifext (5 imaged plates)

### Usage
1. Run the script in Fiji/ImageJ, select your input file and options
2. The script unpacks the individual field of view (tiles) and measures the fluorescence in the second channel. You can also adapt the script to measure multiple channels
3. The results table gets displayed on screen and also saved in the output directory as a csv-file.
4. The output directory also contains all the individual fields of view and a zip file containing the corresponding ROI, if the colony segmentation option was ticked.
5. By opening the image and corresponding ROI file you can check the quality of the segmentation.

### Results
The Results.csv file contains the following columns:

- **Label:** Name of the measured image. If the colony segmentation option is ticked, it also contains the name of the ROI or 'NoSegmentation' if the automatic segmentation was not successful and the whole image was measured instead.
- **Area:** Size of the measured ROI
- **Mean:** Mean fluorescence 
- **Max:** Maximum fluorescence
- **Min:** Minimum fluorescence
- **X, Y:** X and Y coordinats of the ROI
- **Round:** Roundness of the ROI, closer to 1 is more circular
- **IntDen:** Integrated fluorescence intensity (**Mean** * **Area**)

