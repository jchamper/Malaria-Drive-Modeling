# Generates a slurm text file to run an 
# ####x#### array of SLiM simulations at PKU high computing cluster in parallel.

#  Created by Sam Champer, 2020.
#  Modified by Yuan Hu Allegretti, 2022
#  A product of the Messer Lab, http://messerlab.org/slim/

#  Sam Champer, Ben Haller and Philipp Messer, the authors of this code, hereby
#  place the code in this file into the public domain without restriction.
#  If you use this code, please credit SLiM-Extras and provide a link to
#  the SLiM-Extras repository at https://github.com/MesserLab/SLiM-Extras.
#  Thank you.

#load libraries
#For making array
from scipy.stats import qmc

###YHA note: PKU cluster has 40 cpus

# Genearte a shell script to run a large array of SLiM simulations at PKU cluster in parallel.
'''
    malaria_takein_rate 0.2, 0.05-0.27 (human to mosquito)
    malaria_sensitive 0.2,0.2-0.9 (mosquito to human)

    DISTANCE 0.1, 0.033-0.165
    LOW_DENSITY_GROWTH_RATE 10, 2-18
    REMATE_CHANCE 0.05, 0-1
    want_to_bite_rate 0.5, 0.25-1
    animal_bite_rate 0.5, 0-1 

    less_seasonal_amplitude 0.8, 0-0.8 #should not exceed 0.8
    cure_week 16, 10-30
    immunity 15, 0-20
    
'''


###################################################
# Draw sample points with Latin Hypercube Sampling#
###################################################

#make a sample space
sampler = qmc.LatinHypercube(d=10)
#sample = sampler.random(n=10000) 
sample = sampler.random(n=8000)

#adjust the lower/upperbound
l_bounds = [0.05, 0.2, 0.033, 2, 0, 0.25, 0, 0, 10, 0] #write the lower bound of 10 parameters here
u_bounds = [0.27, 0.9, 0.165, 18, 1, 1, 1, 0.8, 30, 20] #write the upper bound of 10 parameters here

##############################
#Samples from Parameter Space#
##############################
sample_scaled = qmc.scale(sample, l_bounds, u_bounds)


#################
# Make Commands #
#################

#want to make lines that says 
# "python 220808_mosquito_competition_slim_driver.py -dis {} -remate {} -oldcomp {} -intcomp {} -growth {} -dc {} -sfm {} -erc {} -grcbeta {} -r1 {}"
# get the value for each argument from above array

print_header = False
#run_number = 1
#max_simultaneous_procs = 40
#print("#!/bin/bash\n#SBATCH -p cn-long\n#SBATCH --qos=jchampercnl\n#SBATCH -A jchamper_g1\n#SBATCH -c 1\nmkdir -p py_data")
for i in range(len(sample_scaled)):
        #YHAnote: changed the model driver into 220808_mosquito_competition_slim_driver.py
        print(f"python NonDrive_range_driver.py -malaria_takein_rate {sample_scaled[i,0]:.4f} -malaria_sensitive {sample_scaled[i,1]:.3f} -distance {sample_scaled[i,2]:.4f} -ldgr {sample_scaled[i,3]:.0f} -remate_chance {sample_scaled[i,4]:.3f} -want_to_bite_rate {sample_scaled[i,5]:.3f} -animal_bite_rate {sample_scaled[i,6]:.3f} -less_seasonal_amplitude {sample_scaled[i,7]:.1f} -cure_week {sample_scaled[i,8]:.0f} -immunity {sample_scaled[i,9]:.0f} {' -header' if print_header else ''}")
        print_header = False
        #if run_number % max_simultaneous_procs == 0:
            # This sets a limit on how many instances of SLiM are allowed to run at once.
            # In terms of CPU utilization - this reduces efficiency, as threads that
            # finish earlier will idle until all others are finished.
            # However, this method saves a lot of memory, which may be more important,
            # depending on the SLiM file you are running.
            #   print("wait")
#run_number += 1

#print("wait\ncd py_data\ncat *.part > large_array_with_python.csv\nrm *.part")
