#title           : blank_subtraction.py
#description     : Subtract an averaged blank from the currently opened image
#author          : Tobias Wechsler
#usage           : Open the image stack in ImageJ, run the script and select the blank image and the corresponding channel
#=======================================================================================================================

# Import modules
from ij import IJ
from ij.plugin import ImageCalculator

# Setting up inputs for the user to choose the average blank image and specify a channel
#@ File (label="Choose the average blank image", style="file") blank_file
#@ Integer (label="set channel", min=1, max=10, value=2) ch_num


BLANK_FILE = str(blank_file)
CH_NUM = int(ch_num)

# Initialize the Image Calculator
IC = ImageCalculator()

# Open the specified blank image
blank_img = IJ.openImage(BLANK_FILE)

# Get the currently active image in ImageJ
img = IJ.getImage()

# Retrieve the number of channels and frames in the image
nc = img.getNChannels()
nf = img.getNFrames()

# Iterate through each frame and subtract the blank
for i in range(1,nf+1):
	img.setPosition(CH_NUM,1,i)
	IC.run("Subtract", img, blank_img)

print('end')