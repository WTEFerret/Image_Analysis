#title           : make_avg_blank.py
#description     : Creates average projection images for each channel of a multichannel image stack and 
#					saves them as separate TIFF files
#author          : Tobias Wechsler
#usage           : Open the image stack in ImageJ, run the script and select an output directory
#=======================================================================================================================

# Import modules
import os
from ij import IJ
from ij.plugin import ChannelSplitter
from ij.plugin import ZProjector


# Setting up an input for the user to choose a target directory for output files
#@ File (label="Choose a target directory", style="directory") out_dir
OUT_DIR = str(out_dir)

# Getting the current image opened in ImageJ
img = IJ.getImage()

# Retrieving the number of channels, frames, and slices in the image
nc = img.getNChannels()
nf = img.getNFrames()
ns = img.getNSlices()

# Hide the current image window
img.hide()

# Initialize the ZProjector
PJ = ZProjector()
PJ.setMethod(ZProjector.AVG_METHOD)


# Split the image into its separate color channels
channels = ChannelSplitter.split(img)
for i, c in enumerate(channels):

	# Make ZProjection of the current channel (c)
	PJ.setImage(c)
	PJ.doProjection()
	projection = PJ.getProjection()
	
	# Copy attributes from the original image to the projection
	projection.copyAttributes(img)

	# Save the projection as a TIFF file in the specified output directory
	IJ.saveAs(projection, 'Tiff', os.path.join(OUT_DIR, 'BLANK_C=' + str(i+1) +'.tif'))
	c.close()

img.show()	
print('end')