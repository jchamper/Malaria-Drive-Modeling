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
    simulation_end = 0
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

    
    resultlist =[malaria, average_prevalence, populations[3][-1],populations[4][-1],populations[2][-1],mos_malaria[0][-1],mos_malaria[1][-1],mos_malaria[2][-1],mos_malaria[3][-1],human_malaria[0][-1],human_malaria[1][-1],human_malaria[2][-1],human_malaria[3][-1],simulation_end]
    return (resultlist, parameter_valuelist)

def run_slim(command_line_args):
    """
    Runs SLiM using subprocess.
    Args:
        command_line_args: list; a list of command line arguments.
    return: The entire SLiM output as a string.
    """
    slim = subprocess.Popen(command_line_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True)
    out, err = slim.communicate()
# For debugging purposes:
# std.out from the subprocess is in slim.communicate()[0]
# std.error from the subprocess is in slim.communicate()[1]
# Errors from the process can be printed with:
    #print(err)
    return out




def configure_slim_command_line(args_dict):
    """
    Sets up a list of command line arguments for running SLiM.
    Args:
        args_dict: a dictionary of arg parser arguments.
    Return
        clargs: A formated list of the arguments.
    """
# We're running SLiM, so the first arg is simple:
    clargs = "slim "
# The filename of the source file must be the last argument:
    source = args_dict.pop("source")
# Add each argument from arg parser to the command line arguemnts for SLiM:
    for arg in args_dict:
        if isinstance(args_dict[arg], bool):
            clargs += f"-d {arg}={'T' if args_dict[arg] else 'F'} "
        else:
            clargs += f"-d {arg}={args_dict[arg]} "
# Add the source file, and return the string split into a list.
    clargs += source
    return clargs.split()



def main():
    """
    1. Configure using argparse.
    2. Generate the command line list to pass to subprocess through the run_slim() function.
    3. Run SLiM.
    4. Process the output of SLiM to extract the information we want.
    5. Print the results.
    """
# Get args from arg parser:
    parser = ArgumentParser()
    parser.add_argument('-src', '--source', default="linear.slim", type=str,help=r"SLiM file to be run.")
    parser.add_argument('-header', '--print_header', action='store_true', default=False,
    help='If this is set, python prints a header for a part file.')

    #each params I want to vary
 #   parser.add_argument('-endtime', '--ENDTIME', default=1000, type=int,
 #                       help='The time to end simulation. Default in slim is 1000')
 #   parser.add_argument('-sim_bound', '--SIM_BOUND', default=1.0, type=float,
 #                       help='The length of the simulation place')
 #   parser.add_argument('-female_age', '--FEMALE_AGE', default=7, type=int,
 #                       help='number of human in this simulation')
 #   parser.add_argument('-strong_seasonal', '--STRONG_SEASONAL', default=False, type=bool,
 #                       help='population(capacity) becomes higher than average in some season')
 #   parser.add_argument('-less_seasonal', '--LESS_SEASONAL', default=True, type=bool,
 #                       help='population(capacity) change with time continuously')
 #   parser.add_argument('-sight', '--SIGHT', default=False, type=bool,
 #                       help="output don't need colors")


    #variable parameters
    parser.add_argument('-malaria_takein_rate', '--MALARIA_TAKEIN_RATE', default=0.2, type=float,
                        help='rate of malaria from human to mosquito')
    parser.add_argument('-malaria_sensitive', '--MALARIA_SENSITIVE', default=0.4, type=float,
                        help='rate of malaria from mosquito to human')
    parser.add_argument('-distance', '--DISTANCE', default=0.1, type=float,
                        help='ability for adult female to move,find food,or mate')
    parser.add_argument('-remate_chance', '--REMATE_CHANCE', default=0.05, type=float,
                        help='Remate chance. 0-1')
    parser.add_argument('-want_to_bite_rate', '--WANT_TO_BITE_RATE', default=0.5, type=float,
                        help='the rate for an adult female to try to find food')
    parser.add_argument('-animal_bite_rate', '--ANIMAL_BITE_RATE', default=0.5, type=float,
                        help='when a mosquito can not find a human in its territory ,this is the chance for it to reproduce')
    parser.add_argument('-ldgr', '--LOW_DENSITY_GROWTH_RATE', default=10, type=float,
                        help='low density growth rate means if capacity is infinity')
    ##seasonal related
    parser.add_argument('-less_seasonal_amplitude', '--LESS_SEASONAL_AMPLITUDE', default=0.8, type=float,
                         help='the rate of population increase and decrease, ranges 0-1')
    ##human 
    parser.add_argument('-cure_week', '--CURE_WEEK', default=16, type=int,
                         help='the average time for a patient to recover from malaria')
    parser.add_argument('-immunity','--IMMUNITY', default = 10, type = int,
                        help='immunity parameter')
    parser.add_argument('-femaledensity', '--ADULT_FEMALES_DENSITY', default=3000, type=int,
                        help='The number of adult female mosquitos at the beginning of simulation')
    parser.add_argument('-human_density', '--HUMAN_DENSITY', default=300, type=int,
                        help='number of human in this simulation')
    parser.add_argument('-simbound', '--SIM_BOUND', default=4, type=int,
                        help='area')
    parser.add_argument('-seasonal', '--SEASONAL', default=True, type=bool,
                        help='area')


    args_dict = vars(parser.parse_args())
# The '-header' argument prints a header for the output. This can
# help generate a nice part by adding this argument to the first SLiM run:
    if args_dict.pop("print_header", None):
        print("malaria_eliminated,malaria_prevalence,num_fertile_females,adult_total_numbers, adult_female,\
              healthy_mosquito, carrier_mosquito,carrier_mosquito2,patient_mosquito,\
              healthy_human,carrier_human,patient_human,resistant_human,\
              simulation_end,\
              malaria_takein_rate,malaria_sensitive,\
              distance,remate_chance,want_to_bite_rate,animal_bite_rate,\
              low_density_growth_rate,seasonal_amplitude,cureweek,immunity,\
              density_num_adult_female,human_density,sim_bound")
# Next, assemble the command line arguments in the way we want to for SLiM:
    clargs = configure_slim_command_line(args_dict)
# Run the file with the desired arguments.
    slim_result = run_slim(clargs)
    parsed_result = parse_slim2(slim_result)
    parsed_result = ", ".join([str(x) for x in parsed_result[0] + parsed_result[1]])
    print(parsed_result)
    #position,number=storeraw(slim_result)
# Parse and analyze the result.
    #readdata(position,number)
    #generate_result(position,number)


if __name__ == "__main__":
    main()