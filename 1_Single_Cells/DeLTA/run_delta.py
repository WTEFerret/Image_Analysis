#title           : run_delta.py
#description     : Runs the DeLTA image analysis pipeline on the images in the 'test_imgs' folder
#                   It expects images in tiff format with the nameing sceam 'PA_%01d_C%02d_T%03d.tif' 
#                   (e.g. PA_0_C00_T000.tif) where the first number indicates the position, the second
#                   the channel (C00) and the third the time-point (T00). The indexing is 0 based.
#author          : Tobias Wechsler
#python_version  : 3.10.12
#===================================================================================================
import delta

delta.config.load_config(presets='2D')


source_folder = "test_imgs"

reader = delta.utilities.xpreader(
    source_folder,
    prototype='PA_%01d_C%02d_T%03d.tif',
    fileorder='pct', 
    filenamesindexing=0
)

print("""Initialized experiment reader:
    - %d positions
    - %d imaging channels
    - %d timepoints"""%(reader.positions, reader.channels, reader.timepoints)
)


ppln = delta.pipeline.Pipeline(reader)

ppln.process()