# Tools
These tools are used in several workflows and can serve as a starting point for the development of new ones.

#### sort_images_nd2.py
A Python script to convert Nikon microscopy images (.nd2) into individual tiff images sorted into positions and channels. Run the script on the command line, providing the path to a .nd2 file.

#### sort_images_lif.py
A Python script to convert Leica Image Files (.lif) into individual tiff images sorted into positions and channels. Run the script on the command line, providing the path to a .lif file.

#### drift_correction.py (ImageJ)
An ImageJ script to correct drift in time-lapse microscopy images.
https://github.com/fiji/Correct_3D_Drift/blob/master/src/main/resources/scripts/Plugins/Registration/Correct_3D_drift.py

#### batch_unpack_vis.py
An ImageJ script to convert a folder of .vis files to tiff stacks and applies drift correction. 