#!/bin/bash
#SBATCH -t 10:00:00
#SBATCH -N 1
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=christoph.kruger@yahoo.com


#Create input/output directory on scratch
mkdir "$TMPDIR"/output
mkdir "$TMPDIR"/input
mkdir "$TMPDIR"/input/meta_data
mkdir "$TMPDIR"/input/"$1"

#copy input folder into input directory
cp -r "$1/Split Data/Batch $SLURM_ARRAY_TASK_ID" "$TMPDIR"/input/"$1"
cp HPC_stata_data.py "$TMPDIR/input/$1/Batch $SLURM_ARRAY_TASK_ID"
cp "Meta_Data_Stata.csv" "$TMPDIR"/input/meta_data
cp "Meta Data Treaty Decisions.csv" "$TMPDIR"/input/meta_data


#load python
module load 2021
module load Python/3.9.5-GCCcore-10.3.0

#run script
python "$TMPDIR/input/$1/Batch $SLURM_ARRAY_TASK_ID/HPC_stata_data.py" $SLURM_ARRAY_TASK_ID $1 

#Copy output directory from scratch to home
cp -r "$TMPDIR"/output $HOME