#title           : batch_unpack_vis.py
#description     : Takes a folder containing .vis images, converts them to tiff stacks,
#					one per channel and position and applies drift correction.
#					Must be run with the drift_correction.py script in the same folder
#date            : 2022/04/05
#version         : 
#usage           : 
#notes           :
#python_version  : ImageJ

#=======================================================================

import os
import sys
import csv
from ij import IJ, ImagePlus
from ij.io import Opener
from ij.plugin import ChannelSplitter, ImageCalculator, ZProjector, Duplicator
from java.awt import Frame
from ij.gui import YesNoCancelDialog, WaitForUserDialog, GenericDialog, NonBlockingGenericDialog


SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, SCRIPT_PATH)

print(SCRIPT_PATH)

import drift_correction

# set intput and output directory

#@ File (label="Choose the input image:", style="directory") IN_DIR
#@ File (label="Ouput directory:", style="directory") OUT_DIR
#@ Boolean (label="Manually adjust crop region", style=boolean, value=false) adj_crop


def find_edges(img):
	'''
	finds the top, bottom, right and left borders where all
	black bars a cut out in all frames
	'''

	frames = img.getNFrames()
	centerx = int(img.getHeight() /2)
	centery = int(img.getWidth() /2)

	maxleft = 0
	maxtop = 0
	minright = int(img.getHeight())
	minbottom = int(img.getWidth())

	for f in range(1,frames+1):
		img.setPosition(1,1,f)
		ip = img.getProcessor()

		# find left and right limits of the black borders 
		setleft = True
		setright= True

		ic = 0

		if ip.getPixelValue(maxleft,centery)>0.0:
			setleft= False
		if ip.getPixelValue(minright,centery)>0.0:
			setright= False
			
		for i in range(maxleft,minright):
			if ip.getPixelValue(minright-ic,centery) > 0.0 and setright:
				minright -= ic
				setright= False
			ic +=1
		
			if ip.getPixelValue(i,centery) > 0.0 and setleft:
				maxleft = i
				setleft = False

			#if not setleft and not setright:
			#	break

		# find top and bottom limits of the black borders 
		settop = True
		setbottom = True

		ic = 0

		if ip.getPixelValue(centerx, maxtop)>0.0:
			settop= False
		if ip.getPixelValue(centerx,minbottom)>0.0:
			setbottom= False
			
		for i in range(maxtop,minbottom):
			if ip.getPixelValue(centerx,minbottom-ic) > 0.0 and setbottom:
				minbottom -= ic
				setbottom= False
			ic +=1
		
			if ip.getPixelValue(centerx, i) > 0.0 and settop:
				maxtop = i
				settop = False

			#if not settop and not setbottom:
			#	break
	
	IJ.log('MAXLEFT: %d' % maxleft)
	IJ.log('MINRIGHT: %d' % (minright+1-maxleft))
	IJ.log('MAXTOP: %d' % maxtop)
	IJ.log('MINBOTTOM: %d' % (minbottom+1-maxtop))

	return maxleft, minright, maxtop, minbottom


def crop_border(img, maxleft, minright, maxtop, minbottom, adj_crop):
	'''
	selects region and crops it out
	'''
	img.setRoi(maxleft,maxtop,minright+1-maxleft,minbottom+1-maxtop)
	if adj_crop:
		WaitForUserDialog('Adjust crop region','Adjust the crop region if necessary').show()


	IJ.run("Crop")


if __name__ == '__main__':


	out_path = str(OUT_DIR)
	img_path = str(IN_DIR)

	img_files = [f for f in os.listdir(img_path) if f.endswith('vsi')]

	IJ.log('\n-- {0:-<80}'.format('SETUP'))
	IJ.log('    Output dir:{0: >20}'.format(OUT_DIR))

	for f in img_files:
		
		IJ.log('    Input file:{0: >20}'.format(f))


		# list all non-blank images
		img_file = os.path.join(img_path, f)
		img_name = f.replace('.vsi','').replace('Multichannel Time Lapse_','')
		img_dir = os.path.join(out_path, img_name)
		if not os.path.isdir(img_dir):
			os.makedirs(img_dir)
		

		IJ.log('\n-- {0:-<80}'.format(img_file))
		
		# import image and get some info
		img = Opener.openUsingBioFormats(img_file)
		img.show()
		
		IMG_NAME = img.getTitle()
		NUMBER_CHANNELS = img.getNChannels()
		NUMBER_FRAMES = img.getNFrames()
		NUMBER_SLICES = img.getNSlices()
		print(NUMBER_FRAMES, NUMBER_CHANNELS, NUMBER_SLICES)

		
				
		IJ.log('\n-- {0:-<80}'.format('DRIFT CORRECTION'))
		
		# DRIFT CORRECTION
		img_reg = drift_correction.auto_run()
		img.close()


		IJ.log('\n-- {0:-<80}'.format('CROP BORDERS'))

		maxleft, minright, maxtop, minbottom = find_edges(img_reg)

		crop_border(img_reg, maxleft, minright, maxtop, minbottom, adj_crop)
		

		IJ.log('\n-- {0:-<80}'.format('EXPORT'))


		chn_names = ['_phase', '_fluor', '_fluor1', '_fluor2']
		for i in range(NUMBER_CHANNELS):
			cimg = Duplicator().run(img_reg, i+1,i+1,1,1,1,NUMBER_FRAMES)
			IJ.save(cimg, os.path.join(img_dir, img_name + chn_names[i] + '.tif'))
			cimg.close()

		img_reg.changes = False
		img_reg.close()

	print('DONE')
	IJ.log('-----------------------------END-----------------------------')
	