"""
ND2 to TIFF Converter Script

This script is designed to convert Nikon NIS-Elements ND2 files into individual TIFF files.
It processes each series, timepoint, channel, and Z-stack within the ND2 file and saves them as TIFF images.
The output is organized into directories for each series, with separate subdirectories for 
bright-field (C = 0) and fluorescence images (C > 0).

Sample1
	└── Images 
	│		├── Sample1_T00_C00_Z00.tif
	│		├── Sample1_T00_C00_Z01.tif
	│		└── ...
	│
	└── Fluor
			├── Sample1_T00_C01_Z00.tif
			├── Sample1_T00_C02_Z00.tif
			└── ...

Usage:
	python sort_images_nd2.py [path_to_nd2_file]
"""

import os
import argparse
import logging
from nd2reader import ND2Reader
from skimage.io import imsave
import itertools

def create_directory(path):
	"""
	Create directory if it doesn't exist.
	"""
	if not os.path.isdir(path):
		os.makedirs(path)


def get_nd_pname(nd_file, index):

	try:
		name = nd_file.parser._raw_metadata.image_metadata[b'SLxExperiment'][b'uLoopPars'][b'Points'][b''][index][b'dPosName']
		name = name.decode('ascii')
	except:
		name = f'Series_{index:03}'
	
	return(name)


def process_images(file_path):
	"""
	Process and save images from ND2 file.
	"""
	if not file_path.endswith('.nd2'):
		logging.error("The provided file is not an ND2 file.")
		return

	if not os.path.exists(file_path):
		logging.error("The provided file path does not exist.")
		return

	out_dir , _= os.path.splitext(file_path)


	try:
		nd2 = ND2Reader(file_path)
	except Exception as e:
		logging.error(f"Error reading ND2 file: {e}")
		return

	dimensions = {}
	for dimension in nd2.sizes.keys():
		if dimension in ['c','t','v','z']:
			dimensions[dimension] = list(range(nd2.sizes[dimension]))



	keys = list(dimensions)
	positions = {}

	
	for values in itertools.product(*map(dimensions.get, keys)):
		img_name = 'Series'

		paras = dict(zip(keys,values))
		for p in paras.keys():
			img_name += f"_{p.upper()}{paras[p]:02}" 

		img_name += '.tif'
		print(img_name)

		try:
			frame = nd2.get_frame_2D(**dict(zip(keys,values)))
			if 'v' in keys:
				if not paras['v'] in positions.keys():
					positions[paras['v']] = os.path.join(out_dir,get_nd_pname(nd2, paras['v']))
					fluor_dir = os.path.join(positions[paras['v']], 'Fluor')
					img_dir = os.path.join(positions[paras['v']], 'Images')
					create_directory(fluor_dir)
					create_directory(img_dir)
			else:
				positions[0] = os.path.join(out_dir,get_nd_pname(nd2, 0))
				fluor_dir = os.path.join(positions[0], 'Fluor')
				img_dir = os.path.join(positions[0], 'Images')
				create_directory(fluor_dir)
				create_directory(img_dir)

			if paras['c'] == 0:
				if 'v' in keys:
					imsave(os.path.join(positions[paras['v']], 'Images', img_name), frame, check_contrast=False)
				else:
					imsave(os.path.join(positions[0], 'Images', img_name), frame, check_contrast=False)

			else:
				if 'v' in keys:
					imsave(os.path.join(positions[paras['v']], 'Fluor', img_name), frame, check_contrast=False)
				else:
					imsave(os.path.join(positions[0], 'Fluor', img_name), frame, check_contrast=False)

			logging.info(f"Saved {img_name} to {out_dir}")
		except:
			logging.warn(f"index out of range {img_name}")


def run():
	"""
	Run the script with command line arguments.
	"""
	logging.basicConfig(level=logging.INFO)
	parser = argparse.ArgumentParser(description="Convert ND2 file into individual tiff files")
	parser.add_argument("file_path", help="Path to ND2 file")
	args = parser.parse_args()
	process_images(args.file_path)
	
if __name__ == "__main__":
	run()
