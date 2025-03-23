# Single cells (DeLTA)

### Scripts
-  convert_nd2.py (Python)
-  run_delta.py (Python)
-  SLURM_job_submission.sh (bash)
-  SLURM_array_job_submission.ch (bash)
-  run_delta_array_job.py (Python)
-  analyse_delta_results.py (Python)
-  tree_plot.R (R)
-  process_results.R (R)
-  compare_tracking_results.py (Python)

### Example
- The example consists of a short time-lapse movie with two channels (phase contrast and fluorescence)

### Pre-Processing
For the subsequent steps, images must be converted into individual TIFF files, separated by time-step as well as channels.  The images must be named according to the following pattern `Name_[position number]_C[channel number]_T[time-point].tif` . The `convert_nd2.py` script can be used to automatically convert Nikon Image Files (.nd2) into the correct format.
__Usage__:
```
python convert_nd2.py path/to/ND2/file.nd2
```

### Segmentation and Tracking
The segmentation and tracking of individual cells is done by the [DeLTA2.0 pipeline](https://gitlab.com/delta-microscopy/delta). Detailed instructions on installation and usage can be found in the [documentation](https://delta.readthedocs.io/en/latest/). The `run_delta.py` script is a short example on how to run the pipeline.
The pipeline can also be run in [Google Colab](https://colab.research.google.com/drive/1UL9oXmcJFRBAm0BMQy_DMKg4VHYGgtxZ?usp=sharing) for testing or on [ScienceCluster](https://docs.s3it.uzh.ch/cluster/overview/) for faster speeds. The provided `SLURM` scripts can be used to submit jobs on ScienceCluster. More detailed instructions can be found in the `README_SC_DeLTA_setup.md` file and the  [ScienceCluster documentation](https://docs.s3it.uzh.ch/cluster/overview/).

### Analysis  and Measurements

__analyse_delta_results.py__: Convert cell data from DeLTAs .pkl file into CSV format and calculates additional metrics.

__tree_plot.R__: Used to plot a lineage tree based on the tracking data from DeLTA

__compare_tracking_results.py__: Can be used to check how accurate DeLTA tracks individual cells and divisions by comparing it to manually tracked positions. A more detailed description of the analysis can be found in the `README_test_DeLTA_tracking.md` file.

Further analysis steps can also be found in the supplement of the related paper [__Space and epigenetic inheritance determine inter-individual differences in siderophore gene expression in bacterial colonies__](https://figshare.com/articles/dataset/Space_and_epigenetic_inheritance_determine_inter-individual_differences_in_siderophore_gene_expression_in_bacterial_colonies/25391614)