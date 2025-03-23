#title			 : measure_colonies.py
#description	 : Measure the size and position of microcolonies and 
#					add information on fluorescence tags and double layers 
#author			 : Tobias Wechsler
#date			 : 
#version		 : 
#usage			 : 
#notes			 :
#python_version	 : ImageJ
#=======================================================================


import os
from math import sqrt
from datetime import datetime
from ij import IJ, ImagePlus, ImageStack, Menus, ImageListener
from ij.gui import WaitForUserDialog, NonBlockingGenericDialog, ShapeRoi, PolygonRoi
from ij.plugin import Duplicator, ImageCalculator, RoiEnlarger
from ij.measure import ResultsTable
from ij.plugin.frame import RoiManager
from java.awt import Color
from java.awt.event import TextListener, ActionListener
from zipfile import ZipFile
import shutil, copy

#@ File (label="Select the position directory", style="directory") pos_dir

class ButListener(ActionListener):

	def __init__(self, fun):
		self.action = fun
		
		
	def actionPerformed(self, event):
		self.action()
		
class ImgListener(ImageListener):
	
	def __init__(self, fun):
		self.action = fun
			
	def imageUpdated(self, event):
		self.action()
		
	def imageOpened(self, event):
		pass


def get_curFrame():
	'''
	Set currently displayed frame and load corresponding ROIs
	'''
	global CUR_FRAME
	RM = RoiManager.getInstance()
	frame = IMG.getFrame()
	if frame != CUR_FRAME:
		RM.runCommand("Save", os.path.join(ROI_PATH, ROI_FILES[CUR_FRAME-1]))
		CUR_FRAME = frame
		load_roi()


def load_roi():
	'''
	Opens ROIs of the current frame
	'''
	frame = IMG.getFrame()
	RM = RoiManager.getInstance()
	if not RM:
		RM = RoiManager(True)
	RM.reset()
	RM.runCommand("Open", os.path.join(ROI_PATH, ROI_FILES[frame-1]))
	RM.runCommand(IMG,"Show All")


def add_tag():
	'''
	Adds a tag (p) in front of the ROI name of a selected colony, in all time-points
	or removes it, if the lineage is already tagged.
	'''
	RM = RoiManager.getInstance()
	selected_index = RM.getSelectedIndex()

	if selected_index != -1 :
		selected_roi = RM.getRoi(selected_index)
		lin_roi = selected_roi.getName()
		lin_name = lin_roi.split('t')[0]		
		RM.reset()

		for rf in ROI_FILES:
			RM.runCommand("Open", os.path.join(ROI_PATH, rf))
			rois = RM.getRoisAsArray()
			for r in rois:
				if lin_name == r.getName().split('t')[0]:
					if lin_name.startswith('p'):
						r_name = r.getName()
						new_name = r_name[1:]
						r.setName(new_name)
					else:
						r_name = r.getName()
						new_name = 'p' + r_name
						r.setName(new_name)
			RM.reset()
			for r in rois:
				RM.addRoi(r)

			RM.runCommand("Save", os.path.join(ROI_PATH, rf))
			RM.reset()
	else:
		print('No colony selected')

	load_roi()

def add_dlayer():
	'''
	Adds a tag (d) in front of the ROI name of a selected ROI
	as well as all subsequent ROIs of the same colony
	'''
	RM = RoiManager.getInstance()
	selected_index = RM.getSelectedIndex()

	if selected_index != -1 :
		selected_roi = RM.getRoi(selected_index)
		lin_roi = selected_roi.getName()
		lin_name = lin_roi.split('t')[0]		
		RM.reset()

		for rf in ROI_FILES[CUR_FRAME-1:]:
			RM.runCommand("Open", os.path.join(ROI_PATH, rf))
			rois = RM.getRoisAsArray()
			for r in rois:
				r_name = r.getName()
				if lin_name == r.getName().split('t')[0]:
					if r_name.endswith('d'):
						new_name = r_name[:-1]
						r.setName(new_name)
					else:
						new_name = r_name + 'd'
						r.setName(new_name)
			RM.reset()
			for r in rois:
				RM.addRoi(r)

			RM.runCommand("Save", os.path.join(ROI_PATH, rf))
			RM.reset()
	else:
		print('No colony selected')

	load_roi()


def measure():
	'''
	Measures all colonies and saves the results
	'''
	RM = RoiManager.getInstance()
	if not RM:
		RM = RoiManager(True)

	RM.reset()
		
	for rf in ROI_FILES:
		RM.runCommand("Open", os.path.join(ROI_PATH, rf))
		
	RM.runCommand(IMG,"Measure")
	RT = ResultsTable.getResultsTable()
	RT.save(os.path.join(POS_PATH, "Results.csv"))
	


def run():
	'''
	Runs the interactive command launcher
	'''
	load_roi()
	IMG_L = ImgListener(get_curFrame)
	IMG.addImageListener(IMG_L)

	commands = {'Measure':measure,
				'Tag':add_tag,
				'double layer':add_dlayer}


	com_list = list(commands.keys())
	com_list.sort()
				
	gd = NonBlockingGenericDialog('Command Launcher')
	for c in com_list:
		gd.addButton(c, ButListener(commands[c]))

	gd.showDialog()
	IMG.removeImageListener(IMG_L)




if __name__ == '__main__':


	# Setup image and rois
	POS_PATH = pos_dir.getPath()
	BASENAME = os.path.basename(POS_PATH)

	IMG_FILE = os.path.join(POS_PATH, BASENAME + '_phase.tif')
	FLR_FILE = os.path.join(POS_PATH, BASENAME + '_fluor.tif')
	
	ROI_PATH = os.path.join(POS_PATH,'ROI_DONE')
	ROI_FILES = [z for z in os.listdir(ROI_PATH)]

	ROI_FILES.sort()
		
	CUR_FRAME = 1


	# Open channels and combine them
	PHASE = IJ.openImage(IMG_FILE)
	FLR = IJ.openImage(FLR_FILE)

	PHASE.show()
	FLR.show()

	IJ.run(PHASE, "Merge Channels...", 
		"c1={0} c2={1} create".format(PHASE.getTitle(), FLR.getTitle()))

	IMG = IJ.getImage()
	IMG.setDisplayMode(IJ.COLOR)
	IJ.run(IMG, "Grays", "")
	IJ.run(IMG, "Enhance Contrast", "saturated=0.35")

	# Print number of channels, slices and frames
	nc = IMG.getNChannels()
	nf = IMG.getNFrames()
	ns = IMG.getNSlices()
	print(nc, ns, nf)


	# Start ROI Manager
	IJ.run("ROI Manager...", "")
	RM = RoiManager.getInstance()
	if not RM:
		RM = RoiManager(True)
	
	# Run interactive command launcher
	run()

	# Close image
	IMG.close()
	print('END')
