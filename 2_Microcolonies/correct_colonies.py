#title			 : colony_seg_correction.py
#description	 : Manually correct colony segmentations
#author			 : Tobias Wechsler
#date			 : 2022/03/30
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
		RM.runCommand("Save", os.path.join(TEMP_PATH, ROI_FILES[CUR_FRAME-1]))
		CUR_FRAME = frame
		load_roi()

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
	
def split_roi():
	'''
	Splits an ROI along the currecnt selection
	'''
	RM = RoiManager.getInstance()
	keep_div = IMG.getRoi()
	divider = ShapeRoi(IMG.getRoi())
	temp_rois = RM.getRoisAsArray()
	selected_index = -1
	max_overlap = 0
	for i, roi in enumerate(temp_rois):
		overlap, ratio, jacc = overlap_rois(divider,roi)
		if overlap > max_overlap:
			max_overlap = overlap
			selected_index = i
	
	frame = IMG.getFrame()
	
	if selected_index != -1:
		split_roi = ShapeRoi(RM.getRoi(selected_index))
		keep_rois = []
		for i, r in enumerate(temp_rois):
			if i != selected_index:
				keep_rois.append(r)

		RM.reset()
		divider2 = divider.and(split_roi)
		new_rois = split_roi.xor(divider2)
		RM.addRoi(new_rois)
		
		RM.select(0)
		RM.runCommand(IMG, "Split")
		RM.runCommand(IMG, "Delete")

		for i, roi in enumerate(keep_rois):
			RM.addRoi(roi)
		
		frame = IMG.getFrame()
		IMG.setPosition(1,1,frame+1)
		get_curFrame()
		keep_div.setPosition(1,1,frame+1)
		IMG.setRoi(keep_div)
		
	else:
		print('selection has no overlap with any ROI')


def addto_roi():
	'''
	Extend a ROI by a overlapping selection
	'''
	
	RM = RoiManager.getInstance()
	add = ShapeRoi(IMG.getRoi())
	temp_rois = RM.getRoisAsArray()
	selected_index = -1
	max_overlap = 0
	for i, roi in enumerate(temp_rois):
		overlap, ratio, jacc = overlap_rois(add,roi)
		if overlap > max_overlap:
			max_overlap = overlap
			selected_index = i
	
	frame = IMG.getFrame()
	
	if selected_index != -1:
		edit_roi = ShapeRoi(RM.getRoi(selected_index))
		keep_rois = []
		for i, r in enumerate(temp_rois):
			if i != selected_index:
				keep_rois.append(r)

		RM.reset()
		new_roi = edit_roi.or(add)
		RM.addRoi(new_roi)
		
		for i, roi in enumerate(keep_rois):
			RM.addRoi(roi)
		IJ.run(IMG, "Select None", "")
	else:
		print('selection has no overlap with any ROI')


def subto_roi():
	'''
	Subtracts a selected ROI from a overlaping ROI
	'''
	RM = RoiManager.getInstance()

	add = ShapeRoi(RM.getSelectedRoisAsArray()[0])
	temp_rois = RM.getRoisAsArray()
	selected_index = -1
	max_overlap = 0
	for i, roi in enumerate(temp_rois):
		overlap, ratio, jacc = overlap_rois(add,roi)
		if overlap > max_overlap and jacc != 1:
			max_overlap = overlap
			selected_index = i
	
	frame = IMG.getFrame()
	
	if selected_index != -1:
		edit_roi = ShapeRoi(RM.getRoi(selected_index))
		keep_rois = []
		for i, r in enumerate(temp_rois):
			if i != selected_index:
				keep_rois.append(r)

		RM.reset()
		new_roi = edit_roi.not(add)
		RM.addRoi(new_roi)
		
		for i, roi in enumerate(keep_rois):
			RM.addRoi(roi)
		
	else:
		print('selection has no overlap with any ROI')

def clone_tonext():
	'''
	Copies the Selected ROI to the next frame
	'''
	RM = RoiManager.getInstance()
	selected_index = RM.getSelectedIndex()
	frame = IMG.getFrame()
	if selected_index != -1:
		selected_roi = RM.getRoi(selected_index)
		IMG.setPosition(1,1,frame+1)
		get_curFrame()
		RM.addRoi(selected_roi)
		RM.setPosition(frame+1)


def merge_rois():
	'''
	Combines to separate ROIs
	'''
	
	RM = RoiManager.getInstance()
	frame = IMG.getFrame()
	rois = RM.getRoisAsArray()
	selected =  RM.getSelectedRoisAsArray()
	print(len(selected))
	
	if len(selected) > 1:
		print('merge rois...')
		sel_names = [r.getName() for r in selected]
		rois_keep = []
		for r in rois:
			if r.getName() not in sel_names:
				rois_keep.append(r)

		print(len(rois_keep))

		RM.reset()
		merged = ShapeRoi(selected[0])
		for r in selected[1:]:
			merged = merged.or(ShapeRoi(r))

		RM.addRoi(merged)
		print(len(rois_keep))
		for roi in rois_keep:
			RM.addRoi(roi)
	
	else:
		print('select at least 2 ROIs')

def load_roi():
	'''
	Opens ROIs of the current frame
	'''
	frame = IMG.getFrame()
	RM = RoiManager.getInstance()
	if not RM:
		RM = RoiManager(True)
	RM.reset()
	RM.runCommand("Open", os.path.join(TEMP_PATH, ROI_FILES[frame-1]))
	RM.runCommand(IMG,"Show All")
	
def track_rois():
	'''
	Tracks Colonies over time
	'''
	IMG.setPosition(1,1, 1)
	get_curFrame()
	RM = RoiManager.getInstance()
	cur_rois = RM.getRoisAsArray()
	RM.reset()
	for i, roi in enumerate(cur_rois):
		roi.setName('{0:02}t{1:03}'.format(i, 1))
		print(roi.getName())
		RM.addRoi(roi)
	
	RM.setPosition(1)
	RM.runCommand('Save', os.path.join(TEMP_PATH, ROI_FILES[0]))
	
	IMG.setPosition(1,1, 2)
	get_curFrame()
	frame = IMG.getFrame()
	cframe = frame
	while cframe <= nf:
		print(cframe)
		IMG.setPosition(1,1,cframe)
		get_curFrame()
		match_previous()
		cframe += 1
	

def match_previous():
	'''
	Matches ROIs of the current frame to the previous frame for tracking
	'''
	RM = RoiManager.getInstance()
	frame = IMG.getFrame()
	cur_rois = RM.getRoisAsArray()
	RM.reset()

	RM.runCommand("Open", os.path.join(TEMP_PATH, ROI_FILES[frame-2]))
	old_rois = RM.getRoisAsArray()
	RM.reset()
	
	checked = []
	checked_index = []
	
	for i, oroi in enumerate(old_rois):
		match_index = -1
		max_overlap = 0
		lin_id = oroi.getName().split('t')[0]
		for j, nroi in enumerate(cur_rois):
			overlap, ratio, jacc = overlap_rois(nroi,oroi)
			if jacc > max_overlap:
				max_overlap = jacc
				match_index = j
				match_ratio = ratio
					
		if match_index != -1:
			if match_index not in checked_index:
						
				if ratio < 0.0:
					checked_index.append(match_index)
					match_roi = oroi
					match_roi.setName('{0}t{1:03}'.format(lin_id,frame))
					checked.append(match_roi)
				else:
					checked_index.append(match_index)
					match_roi = cur_rois[match_index]
					match_roi.setName('{0}t{1:03}'.format(lin_id,frame))
					checked.append(match_roi)
					
	for roi in checked:
		RM.addRoi(roi)
		
	RM.runCommand('Save', os.path.join(TEMP_PATH, ROI_FILES[frame-1]))


def save_all():
	'''
	Saves a copy of the edited ROIs to a folder with a timestamp
	'''
	RM = RoiManager.getInstance()
	RM.runCommand("Save", os.path.join(TEMP_PATH, ROI_FILES[CUR_FRAME-1]))
	time = datetime.now().strftime('%Y%m%dT%H-%M-%S')
	SAVE_DIR = TEMP_PATH.replace('ROI_CHECK', 'ROI_' + time )
	os.makedirs(SAVE_DIR)

	for f in ROI_FILES:
		shutil.copy(os.path.join(TEMP_PATH, f), os.path.join(SAVE_DIR, f))
	print('saved...')

def run():
	'''
	Displays the Command Launcher dialog
	'''
	load_roi()
	IMG_L = ImgListener(get_curFrame)
	IMG.addImageListener(IMG_L)

	commands = {'Extend':addto_roi,
				'Sub':subto_roi,
				'Clone':clone_tonext,
				'Split':split_roi,
				'Merge':merge_rois,
				'Track':track_rois,
				'Save':save_all}


	com_list = list(commands.keys())
	com_list.sort()
				
	gd = NonBlockingGenericDialog('Command Launcher')
	for c in com_list:
		gd.addButton(c, ButListener(commands[c]))

	gd.showDialog()
	IMG.removeImageListener(IMG_L)


if __name__ == '__main__':

	# setup image and rois
	POS_PATH = pos_dir.getPath()
	BASENAME = os.path.basename(POS_PATH)

	IMG_FILE = os.path.join(POS_PATH, BASENAME + '_phase.tif')
	FLR_FILE = os.path.join(POS_PATH, BASENAME + '_fluor.tif')
	
	ROI_PATH = os.path.join(POS_PATH,'ROI')
	ROI_FILES = [z for z in os.listdir(ROI_PATH)]

	TEMP_PATH = os.path.join(POS_PATH,'ROI_CHECK')
	if not os.path.isdir(TEMP_PATH):
		os.makedirs(TEMP_PATH)

	ROI_FILES.sort()
	print(ROI_PATH)
	for f in ROI_FILES:
		shutil.copy(os.path.join(ROI_PATH, f), os.path.join(TEMP_PATH, f))
		
	CUR_FRAME = 1

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

	nc = IMG.getNChannels()
	nf = IMG.getNFrames()
	ns = IMG.getNSlices()
	print(nc, ns, nf)
	
	IJ.run("ROI Manager...", "")
	RM = RoiManager.getInstance()
	if not RM:
		RM = RoiManager(True)

	IMG.show()
	
	run()
	
	DONE_DIR = TEMP_PATH.replace('ROI_CHECK', 'ROI_DONE' )
	
	if not os.path.isdir(DONE_DIR):
		os.makedirs(DONE_DIR)

	for f in ROI_FILES:
		shutil.copy(os.path.join(TEMP_PATH, f), os.path.join(	DONE_DIR, f))
	
	IMG.close()
	print('END')
