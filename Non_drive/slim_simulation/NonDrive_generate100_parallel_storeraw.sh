#!/bin/bash
#SBATCH -J storeraw1000
#SBATCH -p cn-long
#SBATCH -N 1
#SBATCH -o storeraw1000_%j.out
#SBATCH -e storeraw1000_%j.err
#SBATCH --no-requeue
#SBATCH -A jchamper_g1
#SBATCH --qos=jchampercnl
#SBATCH -c 1
#SBATCH -a 1-100
#SBATCH --ntasks=20

pkurun  sleep 1

SCRIPT_LOCATION=/lustre2/jchamper_pkuhpc/yuanha/HMM


a=$((${SLURM_ARRAY_TASK_ID} ))
prog=`sed -n "${a}p" ${SCRIPT_LOCATION}/NonDrive_paramset_storeraw.txt`


for j in {1..5}
do
pkurun  sleep 1
$prog &
done
wait
