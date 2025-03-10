#  Created by Sam Champer, 2020.
#  Modified by Yuan Allegretti, 2022
#  Modified by Weitang Sun, 2022
#  A product of the Messer Lab, http://messerlab.org/slim/

#  Sam Champer, Ben Haller and Philipp Messer, the authors of this code, hereby
#  place the code in this file into the public domain without restriction.
#  If you use this code, please credit SLiM-Extras and provide a link to
#  the SLiM-Extras repository at https://github.com/MesserLab/SLiM-Extras.
#  Thank you.

# This is an example of how to use Python as a driver for SLiM.
# Output is formated as a part, but just printed to stdout by default.

# In order to reconfigure this file for your research project, the
# run_slim() and configure_slim_command_line() functions do not need to be modified.
# Changes you would likely want to make are to the argument parser in main(),
# in order to pass your desired variables to SLiM, and to the parse_slim()
# function, where you could do your desired operations on the output of SLiM.

from argparse import ArgumentParser
import subprocess
import numpy
import numpy as np
import pathlib
import time
import os
import sys
import pandas as pd


local=True

def main(position,number):
    position=position+'/'
    f=open(position+str(number)+'_raw_slim_result.txt',"r")
    datas=f.read()
    result=parse_slim2(datas)
    parsed_result = ", ".join([str(x) for x in result[0] + result[1]])
    
    f.close()
    f=open(position+str(number)+'.part',"w")
    f.write(parsed_result)
    f.write('\n')
    f.close()


def parse_slim2(slim_string):
    slim_string=slim_string.split("---")
    initialize=slim_string[0].split("\n")
    # input or parameters

    # output for every generations

    generations=[]
    populations = [[],[],[],[],[]]
    #genotypes = [[] for i in range(10)]

    #genes = [[],[],[],[]]
    mos_malaria = [[],[],[],[]]
    human_malaria = [[],[],[],[]]
    #potential_chase = [[],[],[]]
    #chase=[[],[],[]]
    # the result of simulation
    #chasing = 0
    malaria = 0
    #suppression = 0
    #chasing_start=1000
    #chasing_end = 10000
    #simulation_end = 0
    parameter_namelist=[]
    parameter_valuelist=[]
    result="NO_RESULT"
    for line in initialize:
        if line.startswith("PARAMS::"):
            for para in line[8:-1].split(";"):
                para_name,para_value=para.split(":")
                parameter_namelist.append(para_name)
                parameter_valuelist.append(para_value)


    for gen in slim_string[1:]:
        lines=gen.split("\n")
        #print("\n")
        new=False
        for line in lines:
            if line.startswith("ALL_SPECIES_DISTINCT"):
                result = line
            elif  line.startswith("MALARIA_ELIMINATED"):
                malaria=1
                result = line
            elif line.startswith("TIME_LIMIT_EXCEEDED"):
                result=line
            #print(line)
            l=line.split(" ")

            if l[0]=="GENERATIONS:":
                generations.append(int(l[1]))
                new=True
            if l[0]=="POPULATIONS:":
                populations[0].append(int(l[1]))
                populations[1].append(int(l[2]))
                populations[2].append(int(l[3]))
                populations[3].append(int(l[4]))
                populations[4].append(int(l[5]))
            if l[0] == "MOSQUITO_MALARIA:":
                mos_malaria[0].append(int(l[1]))
                mos_malaria[1].append(int(l[2]))
                mos_malaria[2].append(int(l[3]))
                mos_malaria[3].append(int(l[4]))
            if l[0] == "HUMAN:":
                human_malaria[0].append(int(l[1]))
                human_malaria[1].append(int(l[2]))
                human_malaria[2].append(int(l[3]))
                human_malaria[3].append(int(l[4]))
                new=False


    simulation_end = generations[-1]
    title = ["GENERATIONS", "POPULATIONS", "MOSQUITO_MALARIA", "HUMAN"]
    POPULATIONS = ["NUM_ALL", "NUM_A", "NUM_ADULT_FEMALE", "NUM_FERTILE_FEMALE","NUM_ADULTS"]
    MOS_MALARIA=["healthy","carrier1","carrier2","patient"]
    HUMAN_MALARIA = ["healthy","carrier", "patient","resistant"]
    datas=(generations,populations,mos_malaria,human_malaria)
    heads =("GENERATIONS",POPULATIONS,MOS_MALARIA,HUMAN_MALARIA)
    parameters=(parameter_namelist,parameter_valuelist)

    #calculate the prevalence of malaria in the last 50 weeks
    df = pd.DataFrame(human_malaria)
    last_50_weeks = df.iloc[:,-50:]
    total_population = last_50_weeks.sum().sum()
    total_infected = last_50_weeks.iloc[2,:].sum()
    average_prevalence = total_infected / total_population


    resultlist =[malaria,average_prevalence,populations[3][-1],populations[4][-1],populations[2][-1],mos_malaria[0][-1],mos_malaria[1][-1],mos_malaria[2][-1],mos_malaria[3][-1],human_malaria[0][-1],human_malaria[1][-1],human_malaria[2][-1],human_malaria[3][-1], simulation_end]
    return (resultlist, parameter_valuelist)



if __name__ == "__main__":
    #number = [2,3,4,5,6,7,8,9,10,11,12,13]
    number = [1]
    position = "Nondrive"
    for n in number:
            main(position,n)
    
