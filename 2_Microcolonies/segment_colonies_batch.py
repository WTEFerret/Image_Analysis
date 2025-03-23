#title			 : segment_colonies.py
#description	 : Segment micro-colonies based on phase contrast and fluorescence
#author			 : Tobias Wechsler
#date			 : 2023/04/22
#version		 : 
#usage			 : 
#notes			 :
#python_version	 : ImageJ
#=======================================================================


import os
import re
from math import sqrt
from ij import IJ, ImagePlus, ImageStack
from ij.gui import WaitForUserDialog, ShapeRoi
from ij.plugin import Duplicator, ImageCalculator, RoiEnlarger
from ij.measure import ResultsTable
from ij.plugin.frame import RoiManager

# input folder and settings
#@ File (label="phase contrast image", style="directory") main_dir

def mask_phase(img):
	'''
	Segment based on phase contrast image while excluding
	colonies that are already segmented based on fluorescence
	'''
	IJ.run(img, "Subtract Background...", "rolling=40 light")
	IJ.run(img, "Gaussian Blur...", "sigma=10")
	#IJ.run(img, "Invert", "")
	IJ.run(img, "Auto Threshold", "method=Default white")
	
	return img
	
def check_imgname(name, c, t=None):
	ok = False
	ok = 'C={0}'.format(c) in name
	if t:
		ok = 'T={0:03}'.format(t) in name
		
	return ok

def overlap_rois(nroi,oroi):
	'''
	Calculates the number of overlapping pixels between roi1 and roi2
	'''
	
	nsize = float(len(nroi.getContainedPoints()))
	osize = float(len(oroi.getContainedPoints()))
	overlap_roi = ShapeRoi(nroi).and(ShapeRoi(oroi))
	overlap = float(len(overlap_roi.getContainedPoints()))
	if overlap > 0:
		ratio = nsize / osize
		jacc = overlap / (nsize + osize - overlap)

	else:
		ratio = 1
		jacc = 0 

	return overlap, ratio, jacc



if __name__ == '__main__':

    mdir = main_dir.getPath()
    positions = [os.path.join(mdir, d) for d in os.listdir(mdir)]

    
    for pos in positions:
        print(pos)

        # Create output folder
        out_path = pos
        roi_path = os.path.join(out_path, 'ROI')
        if not os.path.isdir(roi_path):
            os.makedirs(roi_path)
    
        basename = os.path.basename(out_path)
        phase_file = os.path.join(pos, basename + '_phase.tif')
        #fluor_file = os.path.join(pos, basename + '_fluor.tif')

        # Open images
        img_p = IJ.openImage(phase_file)
        #img_f = IJ.openImage(fluor_file)

        # Get the number of frames
        nf = img_p.getNFrames()

        for t in range(1,nf+1):
            
            print('time',t)

            # Get phase contrast segmentation of the current frame
            phase = Duplicator().run(img_p, 1,1,1,1,t,t)
            phase = mask_phase(phase)

            IJ.run(phase, "Analyze Particles...", "size=10-Infinity add")
            
            # Save ROIs
            RM = RoiManager.getInstance()
            if not RM:
                RM = RoiManager(False)
                
            cur_rois = RM.getRoisAsArray()
            RM.reset()
            if len(cur_rois) > 0:
            	for r in cur_rois:
            		r.setPosition(1,1,t)
                	RM.addRoi(r)
                RM.runCommand('Save', os.path.join(roi_path, '{0}_T={1:03}.zip'.format('ROI', t)))
                RM.reset()
            else:
                print('no seg')
            
            # Close temporary files
            phase.changes = False
            phase.close()

        img_p.close()

	print('------ END ------')
