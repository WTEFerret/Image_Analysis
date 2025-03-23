#!/bin/bash

### Comment lines start with ## or #+space
### Slurm option lines start with #SBATCH

### Here are the SBATCH parameters that you should always consider:
#SBATCH --time=0-01:00:00   ## days-hours:minutes:seconds
#SBATCH --mem 7GB         ## 3GB ram (hardware ratio is < 4GB/core)
#SBATCH --ntasks=1          ## Not strictly necessary because default is 1
#SBATCH --cpus-per-task=1   ## Use greater than 1 for parallelized jobs
#SBATCH --gpus=1
#SBATCH --array=0-4

### Here are other SBATCH parameters that you may benefit from using, currently commented out:
###SBATCH --job-name=hello1 ## job name
###SBATCH --output=job.out  ## standard out file

## The following creates a list of all directories in 'inputdir'
posArr=($(ls -d test_positions/*/))

## The array of the input directory can use the TASK_ID as an index
## to set the input direcory for each job
echo 'started at:' $(date)
module load gpu
module load mamba
source activate delta_env
python ./run_dlt.py ${posArr[$SLURM_ARRAY_TASK_ID]}
echo 'finished at:' $(date)