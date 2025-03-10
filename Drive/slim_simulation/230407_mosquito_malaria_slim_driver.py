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




def parse_slim2(slim_string):
    slim_string=slim_string.split("---")
    initialize=slim_string[0].split("\n")
    # input or parameters

    # output for every generations

    generations=[]
    populations = [[],[],[],[],[]]
    genotypes = [[] for i in range(10)]

    genes = [[],[],[],[]]
    mos_malaria = [[],[],[],[]]
    human_malaria = [[],[],[],[]]
    potential_chase = [[],[],[]]
    chase=[[],[],[]]
    # the result of simulation
    chasing = 0
    malaria = 0
    suppression = 0
    chasing_start=1000
    chasing_end = 10000
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
                suppression = 1
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
            if l[0]=="GENES:":
                genes[0].append(int(l[1]))
                genes[1].append(int(l[2]))
                genes[2].append(int(l[3]))
                genes[3].append(int(l[4]))
            if l[0]=="GENOTYPES:":
                for i in range(10):
                    genotypes[i].append(int(l[i+1]))
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
            if l[0]=="POTENTIAL_CHASE::":
                potential_chase[0].append(int(l[1]))
                potential_chase[1].append(int(l[2]))
                potential_chase[2].append(float(l[3]))
            if l[0]=="WT_ALLELES::":
                chase[0].append(int(l[1]))
                chase[1].append(float(l[2]))
                chase[2].append(float(l[3]))
                new=False
        if new:
            chase[0].append(0)
            chase[1].append(0)
            chase[2].append(0)

    simulation_end = generations[-1]
    title = ["GENERATIONS", "POPULATIONS", "GENOTYPES", "GENES", "MOSQUITO_MALARIA", "HUMAN", "POTENTIAL_CHASE","CHASE"]
    POPULATIONS = ["NUM_ALL", "NUM_A", "NUM_ADULT_FEMALE", "NUM_FERTILE_FEMALE","NUM_ADULTS"]
    GENOTYPES = ["wtwt", "wtdr", "wtr1", "wtr2", "drdr", "drr1", "drr2", "r1r1", "r1r2", "r2r2"]
    GENES=["wt","dr","r1","r2"]
    MOS_MALARIA=["healthy","carrier1","carrier2","patient"]
    HUMAN_MALARIA = ["healthy","carrier", "patient","resistant"]
    POTENTIAL_CHASE=["GENERATIONS","NUM_FERTILE_FEMALE","THRESHOLD"]
    CHASE=["wt","nondrive_greens_coeff","all_greens_coeff"]
    datas=(generations,populations,genotypes,genes,mos_malaria,human_malaria,potential_chase,chase)
    heads =("GENERATIONS",POPULATIONS,GENOTYPES,GENES,MOS_MALARIA,HUMAN_MALARIA,POTENTIAL_CHASE,CHASE)
    parameters=(parameter_namelist,parameter_valuelist)

    greens_coeff=chase[1]
    wt=genes[0]
    capacity=potential_chase[2]
    num_wt=[]
    num_wt.append(wt[0]/capacity[0])
    num_wt.append(wt[1] / capacity[0])
    num_wt.append(wt[2] / capacity[0])
    for i in range(len(greens_coeff)-3):
        num_wt.append(wt[i+3]/capacity[i]/2)

    lenth=len(num_wt)
    xminlist=[]
    greescoeffmaxlist=[]
    xlist=[]
    for i in range(lenth):
        if i>4 and i<lenth-4:
            if num_wt[i]<0.8 and num_wt[i]<num_wt[i-1] and num_wt[i]<num_wt[i+1] and num_wt[i]<numpy.average(num_wt[i-3:i]) and num_wt[i]<numpy.average(num_wt[i+1:i+4]):
                xminlist.append(i)
                xlist.append(num_wt[i])
            if greens_coeff[i]>greens_coeff[i-1] and greens_coeff[i]>greens_coeff[i+1] and greens_coeff[i]> numpy.average(greens_coeff[i-3:i]) and greens_coeff[i]> numpy.average(greens_coeff[i+1:i+4]) :
                greescoeffmaxlist.append(i)
    for i in range(len(xminlist)):
        for j in range(len(greescoeffmaxlist)):
            if abs(xminlist[len(xminlist)-i-1]-greescoeffmaxlist[len(greescoeffmaxlist)-1-j])<=3:
                chasing=1
                chasing_start=generations[xminlist[len(xminlist)-i-1]]

    fertile_female_average=0
    avg_pop_during_chase = 0
    drivelost=False
    drivelosttime=generations[-1]
    drive_lost_index=len(generations)
    if result=='ALL_SPECIES_DISTINCT':
        drivelosttime=generations[-1]
    else:
        drive = False
        for i in range(len(generations)):
            if genes[1][i] > 0:
                drive = True
            elif genes[1][i] == 0 and drive:
                drivelosttime= generations[i]
                drive_lost_index = i
                drivelost=True
                drive = False
    if chasing:
        chasing_end = drivelosttime
        chasing_end_index = drive_lost_index
        fertile_female_average=numpy.average(populations[3][chasing_start:chasing_end_index])
        avg_pop_during_chase=numpy.average(populations[1][chasing_start:chasing_end_index])

    if result=="TIME_LIMIT_EXCEEDED":
        if chasing :
            if drivelost:
                result="DRIVE_LOST_AFTER_CHASING"
            else:
                result="LONG_TERM_CHASING"
        elif drivelost:
            result="DRIVE_LOST_WITHOUT_CHASING"
    elif result=="MALARIA_ELIMINATED":
        if chasing :
            if drivelost:
                result="MALARIA_ELIMINATED_DRIVE_LOST_AFTER_CHASING"
            else:
                result="MALARIA_ELIMINATED_LONG_TERM_CHASING"
        elif drivelost:
            result="MALARIA_ELIMINATED_DRIVE_LOST_WITHOUT_CHASING"
    carrier_frequency = 0
    carrier_frequency =  genotypes[1][-1]+genotypes[4][-1]+genotypes[5][-1]+genotypes[6][-1]
    resultlist =[suppression, malaria,populations[3][-1],populations[4][-1],populations[2][-1],genes[0][-1],genes[1][-1],genes[2][-1],genes[3][-1],carrier_frequency,mos_malaria[0][-1],mos_malaria[1][-1],mos_malaria[2][-1],mos_malaria[3][-1],human_malaria[0][-1],human_malaria[1][-1],human_malaria[2][-1],human_malaria[3][-1],chasing,chasing_start,chasing_end,avg_pop_during_chase,fertile_female_average, simulation_end]
    return (resultlist, parameter_valuelist)

def run_slim(command_line_args):
    """
    Runs SLiM using subprocess.
    Args:
        command_line_args: list; a list of command line arguments.
    return: The entire SLiM output as a string.
    """
    slim = subprocess.Popen(
        command_line_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
        )
    
    # Capture the output and error messages
    out, err = slim.communicate()
        
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
    #clargs = "slim "
    clargs = "D:\\lab\\mingw64\\bin\\slim "
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
    parser.add_argument('-src', '--source', default="230407_resource_sam.slim", type=str,help=r"SLiM file to be run.")
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
    parser.add_argument('-malaria_takein_rate', '--MALARIA_TAKEIN_RATE', default=0.11, type=float,
                        help='rate of malaria from human to mosquito')
    parser.add_argument('-malaria_sensitive', '--MALARIA_SENSITIVE', default=0.3, type=float,
                        help='rate of malaria from mosquito to human')
    parser.add_argument('-distance', '--DISTANCE', default=0.11, type=float,
                        help='ability for adult female to move,find food,or mate')
    parser.add_argument('-remate_chance', '--REMATE_CHANCE', default=0.05, type=float,
                        help='Remate chance. 0-1')
    parser.add_argument('-want_to_bite_rate', '--WANT_TO_BITE_RATE', default=0.6, type=float,
                        help='the rate for an adult female to try to find food')
    parser.add_argument('-animal_bite_rate', '--ANIMAL_BITE_RATE', default=1.0, type=float,
                        help='when a mosquito can not find a human in its territory ,this is the chance for it to reproduce')
    parser.add_argument('-dd', '--DD_FITNESS_VALUE', default=1.0, type=float,
                        help='homozygous fitness')
    parser.add_argument('-sfm_f', '--SOMATIC_FITNESS_MULTIPLIER_F', default=0.5, type=float,
                        help='for recessive sterile drive, how dr influence the fecundity fitness')
    parser.add_argument('-grc_beta', '--GRC_BETA', default=0.05, type=float,
                        help='to calculate the germline resistant cut rate')
    parser.add_argument('-dc', '--DRIVE_CONVERSION', default=0.9, type=float,
                        help='the rate of drive to convert wt allele')
    parser.add_argument('-erc_f', '--EMBRYO_RESISTANCE_CUT_RATE_F', default=0.15, type=float,
                        help='female embryo resistance cut rate. 0-1')
    parser.add_argument('-r1', '--R1_OCCURRENCE_RATE', default=0.0, type=float,
                        help='when NHEJ the frequency of functional resistant gene')
    parser.add_argument('-ldgr', '--LOW_DENSITY_GROWTH_RATE', default=6, type=float,
                        help='low density growth rate means if capacity is infinity')
    ##seasonal related
    parser.add_argument('-less_seasonal_amplitude', '--LESS_SEASONAL_AMPLITUDE', default=0.5, type=float,
                         help='the rate of population increase and decrease, ranges 0-1')
    ##human 
    parser.add_argument('-cure_week', '--CURE_WEEK', default=15, type=int,
                         help='the average time for a patient to recover from malaria')
    parser.add_argument('-immunity','--IMMUNITY', default = 5, type = int,
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
        print("suppressed,malaria_eliminated,num_fertile_females,adult_total_numbers, adult_female,\
              wt,dr,r1,r2,carrier_mos_frequency,healthy_mosquito, carrier_mosquito,carrier_mosquito2,patient_mosquito,\
              healthy_human,carrier_human,patient_human,resistant_human,\
              chasing,chasing_start,chasing_end,avg_pop_during_chase,fertile_female_average,simulation_end,\
              malaria_takein_rate,malaria_sensitive,\
              distance,remate_chance,want_to_bite_rate,animal_bite_rate,\
              dd_fitness_value,somatic_fitness_multiplier_f,grc_beta,drive_conversion,erc_f,\
              r1_occurrence_rate,low_density_growth_rate,seasonal_amplitude,cureweek,immunity\
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
    f=open('default_result.txt','w')
    f.write(slim_result)
    f.close()
    f = open('default_result.short','w')
    f.write(parsed_result)
    f.close()

if __name__ == "__main__":
    main()