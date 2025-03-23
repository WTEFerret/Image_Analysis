import delta
import pandas as pd
import os
from PIL import Image

# Load all data
res_path = 'Position000000.pkl'
data = delta.pipeline.Position(None, None,None)
data.load(res_path)

# Get data of first position 
roi = data.rois[0]


# Set center of each cell based on pole positions
for cell in roi.lineage.cells:
	cell['x'] = []
	cell['y'] = []
	for i, frame in enumerate(cell['frames']):
		p1 = cell['new_pole'][i]
		p2 = cell['old_pole'][i]

		c = (p1 + p2) / 2.0
		cell['x'].append(c[0])
		cell['y'].append(c[1])


# Calculate the integrated Density (can also be combined with the previous step)
for cell in roi.lineage.cells:
	cell['IntDen'] = []
	for i, frame in enumerate(cell['frames']):
		a = cell['area'][i]
		f = cell['fluo1'][i]

		intDen = a * f
		cell['IntDen'].append(intDen)


   
# Make pandas data frame
cells_df = pd.concat([pd.DataFrame(cell) for cell in roi.lineage.cells], sort=False)
cells_df.to_csv('results.csv')



# Save segmentation as tiff images
if not os.path.isdir('segmentation'):
	os.makedirs('segmentation')
for i,label in enumerate(roi.label_stack):
	img = Image.fromarray(label)
	img.save(os.path.join('segmentation', f'frame_{i+1:02}.tif'))
