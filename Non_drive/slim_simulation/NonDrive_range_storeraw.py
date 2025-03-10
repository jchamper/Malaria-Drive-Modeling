#  Created by Sam Champer, 2020.
#  Modified by Yuan Allegretti, 2022
#  Modified by Weitang Sun, 2022
#  A product of the Messer Lab, http://messerlab.org/slim/

#  Sam Champer, Ben Haller and Philipp Messer, the authors of this code, hereby
#  place the code in this file into the public domain without restriction.
#  If you use this code, please credit SLiM-Extras and provide a link to
#  the SLiM-Extras repository at https://github.com/MesserLab/SLiM-Extras.
#  Thank you.

# This file runs slim file and saves the raw data into txt file in designated path, and also saves the filename information as deesignated.
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



def storeraw(string):
    '''
        position = 'rawdata'
        number = 1
        path = pathlib.Path(position + "/"+str(number) + "_raw_slim_result.txt")
        if not path.exists():
            os.makedirs(path)
            path = pathlib.Path(position+"/"+str(number) + "_raw_slim_result.txt")

        while path.exists():
            number += 1
            path = pathlib.Path(position + "/" +str(number) + "_raw_slim_result.txt")
        file = open(position+"/"+str(number) + "_raw_slim_result.txt", "w")
        file.write(string)
        file.close()

        return position, str(number)
    '''
    position = 'NonDrive'
    number = 1
    while True:
        path = pathlib.Path(position, f"{number}_raw_slim_result.txt")
        if not path.exists():
            break
        number += 1
    file = open(path, "w")
    file.write(string)
    file.close()

    return position,str(number)




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
                         help='the rate of population increase and decrease, ranges 0.5-1')
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

# Next, assemble the command line arguments in the way we want to for SLiM:
    clargs = configure_slim_command_line(args_dict)
# Run the file with the desired arguments.
    slim_result = run_slim(clargs)
    storeraw(slim_result)

# Parse and analyze the result.
    #readdata(position,number)
    #generate_result(position,number)


if __name__ == "__main__":
    main()