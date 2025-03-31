#!/bin/sh

## reporting
#SBATCH --open-mode=append
# enable logging to a log directory to print intermediate output and any potential errors that occur 
#SBATCH --error=logs/%A_%a.err 
#SBATCH --output=logs/%A_%a.out
# change the following lines to have one pound sign instead of two
# if you want to receive notices about jobs
##SBATCH --mail-type=BEGIN,END,FAIL,REQUEUE,TIME_LIMIT_80
##SBATCH --mail-user=username@hawaii.edu

#SBATCH --cpus-per-task=1
#SBATCH --mem=8G


#SBATCH --job-name=NM_CA
#SBATCH --partition=shared
#SBATCH --time 00:05:00
#SBATCH --array=0

cd
module load lang/Anaconda3
module load lang/Python 
conda activate cm_data
cd
cd /home/ehartley/_Coding_Workshop

python example.py Data output_high 5 7 --states NM CA