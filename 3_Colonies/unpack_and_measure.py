#title			 : unpack_and_measure_simple.py
#description	 : unpacks individual images of colonies from lif-files
#author			 : Tobias Wechsler
#date			 : 
#version		 : 
#usage			 : 
#notes			 :
#python_version	 : ImageJ
#=======================================================================

import os
from ij import IJ
from ij.plugin import Duplicator, RoiEnlarger
from ij.plugin.frame import RoiManager
from loci.plugins import BF
from loci.plugins.in import ImporterOptions
from ij.measure import ResultsTable


#@ File (label="Choose .lif file", style="file") in_file
#@ Boolean (label="Skip empty fields of view", style=boolean, value=true) skip_empty
#@ Boolean (label="Skip every second fields of view", style=boolean, value=true) skip_even
#@ Boolean (label="Segment colonies", style=boolean, value=false) seg_cols
#@ Integer (label="Select the number of plates", min=1, max=12, value=5) num_Plts



def has_col(IMG):
	'''
	Check if the current field of view contains a colony
	by checking the histogramm of the image.
	If there is a colony, the histogramm has a bigger peak
	in the lower values, since colonies are dark
	'''
	IJ.run(IMG, "Select None", "")
	phase_img = Duplicator().run(IMG, 1,1,1,1,1,1)
	img_stats = phase_img.getStatistics()
	phase_img.close()
					
	return(sum(img_stats.histogram()[:100]) > 1000000)

def get_main_roi(rois):
	'''
	Returns the largest ROI if there are more than one
	or None if the ROI list is empty
	'''
	if len(rois)== 1:
		return(rois[0])
	elif len(rois) == 0:
		return(None)
	else:
		a_max = 0
		i_max = 0
		for i, r in enumerate(rois):
			area = r.getStatistics().area
			if area > a_max:
				a_max = area
				i_max = i
		return(rois[i])


def seg_frame(phase_img, name):
	'''
	Segment current frame based on the phase contrast image
	'''
	IJ.run(phase_img, "Gaussian Blur...", "sigma=40")
	IJ.run(phase_img, "Find Edges", "")
	IJ.run(phase_img, "Auto Threshold", "method=Default")
	IJ.run(phase_img, "Invert", "")
	IJ.run(phase_img, "Analyze Particles...", "size=5000000-Infinity add")
	RM = RoiManager.getInstance()
	all_rois = RM.getRoisAsArray()
	col_roi = get_main_roi(all_rois)
	
	if not col_roi:
		print(name, 'no segmentation')
		IJ.run(phase_img, "Select All", "")
		roi = phase_img.getRoi()
		roi.setName('NoSegmentation')
		RM.reset()
		return(roi)
	else:
		RM.reset()
		roi = RoiEnlarger().enlarge(col_roi, -40.0)
		roi.setName(name)
		return(roi)

def make_dir(in_file):
	'''
	create a project directory, named after the input file 
	if it doesn't already exist
	'''
	out_dir = in_file.getPath().replace('.lif','')
	if not os.path.isdir(out_dir):
		os.makedirs(out_dir)
	return out_dir

if __name__ == '__main__':

	# Create output directory
	OUT_DIR = make_dir(in_file)
	N_positions = num_Plts * 96
	print(OUT_DIR)


	# Set measurements
	IJ.run("Set Measurements...", "area mean min centroid center shape feret's integrated stack display redirect=None decimal=3")

	# Setup import options
	options = ImporterOptions()
	options.setId(in_file.getPath())
	options.setOpenAllSeries(False)

	# Run in blockes of 32
	block_size = 32
	N_blocks = N_positions / block_size
	block_start = 0
	block_end = block_size

	row_even = 0
	total_count = 0

	for b in range(N_blocks):
		print('block', b)
		for i in range(block_start, block_end):
			options.setSeriesOn(i, False)

		block_start = b * block_size
		block_end = (b + 1) * block_size

		for i in range(block_start, block_end):
			options.setSeriesOn(i, True)

		RM = RoiManager.getInstance()
		if not RM:
			RM = RoiManager(True)

		imp = BF.openImagePlus(options)
		for i in range(len(imp)):

			keep_fov = True

			if skip_even:
				row_even = (total_count // 12) % 2
				keep_fov = total_count % 2 == row_even

			elif skip_empty:
				keep_fov = has_col(imp[i])

			if keep_fov:
				name = imp[i].getTitle().split(' ')[-1].replace('/','_')

				print(name)
				mch_img = Duplicator().run(imp[i], 2,2,1,1,1,1)
				# If you have multiple fluorescence channels that you measure
				# you can dublicate it as follows:
				# gfp_img = Duplicator().run(imp[i], 3,3,1,1,1,1)
				# to measure the additional channel copy the line
				# measuring the mch channel and change the image name
				# e.g. IJ.run(gfp_img, "Measure")



				if seg_cols:
					phase_img = Duplicator().run(imp[i], 1,1,1,1,1,1)
					roi = seg_frame(phase_img, name)
					phase_img.close()
					
					RM.addRoi(roi)
					RM.select(0)
					RM.runCommand(mch_img,"Measure")
					RM.runCommand('Save', os.path.join(OUT_DIR, name + '.zip'))
					RM.reset()
				else:
					IJ.run(mch_img, "Measure", "")
				
				IJ.save(imp[i], os.path.join(OUT_DIR, name + '.tif'))
							
				mch_img.close()
				imp[i].close()
			total_count +=1

	RT = ResultsTable.getResultsTable()
	RT.save(os.path.join(OUT_DIR, "Results.csv"))
		
	print('number of images:', total_count)
	print('done')