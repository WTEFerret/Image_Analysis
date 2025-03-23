# Single Cells (Ilastik)

### Scripts
- make_avg_blank.py (FIJI)
- blank_subtraction.py (FIJI)
- drift_correction.py (FIJI)
- image_measurements.py (FIJI)
- process_results.R (R)

### Example
- Single position processed up until step 3.

### Pre-Processing
- Before starting the processing, all images must be converted to individual TIFF-stack per channel (see example). This can be achieved in ImageJ/FIJI or with one of the conversion scripts in Tools.
- Create an average projection images by opening a blank image and run the `make_avg_blank.py` script in FIJI.
-  Subtract an averaged blank from the currently opened image. This is done to correct for the reduction of image brightness toward the periphery compared to the image center (also called vignetting). Open the image you want to correct and run the `blank_subtraction.py` script and select the average blank image file you would like to use.

### Ilastik Segmentation
- To obtain a single cell segmentation you can use the Pixel and Object classification workflows in Ilastik. Detailed instruction can be found in the Ilastik documentation.
	- [Pixel Classification](https://www.ilastik.org/documentation/pixelclassification/pixelclassification)
	- [Object Classification](https://www.ilastik.org/documentation/objects/objects)
- For the subsequent steps you need to export the object identities obtained from Ilastik as a 

### Measurements
- To obtain the measurements run the `image_measurments.py` script in FIJI
- First you will be prompted to select a directory containing the images of a single position (e.g. the Example directory) and the number of channels
- In a next step, you have to select the files corresponding to the different channels and object identities
- The Script will create individual images for each time-point and background subtracted versions of all fluorescent channels
- In the end a Results.csv file will be created containing the measurements
- The `process_results.R` script can then be used to cluster cells into colonies and calculate the distance of a cell to the edge of its colony. 