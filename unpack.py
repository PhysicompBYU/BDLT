#! /usr/bin/env python3

# This utility, run either as simply './unpack.py' or
# './unpack infile.xxx output_directory' will open the data file
# and sort out all of the data, filtering and rejecting badly formatted
# entries. It doesn't catch all of the mistakes, but it's a quick and dirty
# way to get the data sorted. The data will be placed into files with the 
# names in the out_files dictionary, which can be designated to be made in
# a different directory, if desired. Let me know if there are any problems 
# or improvements you would like. Sorry this isn't a docstring.

# Made in python 3.4

# Kristian Sims
# kristian.sims@gmail.com
# June 2015

# -----------------------------------------------------------------------------

import sys
import os
from io import IOBase

# Contains all recognized tokens and the names of their respective files.
# These strings will be replaced with file objects as the files are opened.
out_files = {
    'A': 'accelerometer.txt',
    'B': 'barometer.txt',
    'G': 'gyroscope.txt',
    'L': 'light.txt',
    'T': 'temperature.txt',
    'E': 'error.txt',
    'S': 'syslog.txt',
    'V': 'voltage.txt',
}

# Number of columns each type should have
columns = {
    'A': 4,
    'B': 3,
    'G': 4,
    'L': 3,
    'T': 2,
    'E': 0,
    'S': 0,
    'V': 2,
}


# Parse a line, opening files as needed
def parse(the_line):
    global out_files
    token = the_line[0]
    
    # If the token isn't recognized, report and skip
    if token not in out_files:
        if token.isspace():
            print('Found whitespace for token, possibly a \\r')
        else:
            print('Unrecognized token {} in the following line:'.format(token))
            print('    ', the_line)
        return

    # If that file hasn't been opened, open it with the name in out_files
    if type(out_files[token]) is str:
        open_out_file(token)

    if 'i2c error' in the_line:
        print('Warning: the following the_line has been ignored:')
        print('    ', the_line)
        return
    
    if the_line.count(',') is not columns[token] and columns[token] is not 0:
        print('Warning: the following the_line has been ignored;')
        print('    ', the_line)
        return

    # Write the the_line to the file
    formatted_write(the_line[2:], out_files[token])


# Open a file and add it to out_files
def open_out_file(token):
    global out_files
    global directory_name
    
    if directory_name is not None:
        out_file_name = os.path.join(directory_name, out_files[token])
    else:
        out_file_name = out_files[token]
        
    try:
        print('Opening file {}...'.format(out_file_name))
        out_files[token] = open(out_file_name, 'w')
    except IOError:
        print('Could not access or open file {}.'.format(out_file_name))
        sys.exit("Could not open output file")
        
        
# Write a line to a file
def formatted_write(the_line, file):
    file.write(the_line.replace(',', '\t'))


def close_out_files():
    global out_files
    for value in out_files.values():
        if isinstance(value, IOBase):
            print('Closing file {}...'.format(value.__name__))
            value.close()
            

# Main program
if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        in_file_name = sys.argv[1]
    else:
        in_file_name = 'DATA.CSV'
        
    if len(sys.argv) == 3:
        directory_name = sys.argv[2]
        if not os.path.isdir(directory_name):
            print('{} is not a valid directory.'.format(directory_name))
            print('Usage is "./unpack infile.xxx output_directory".')
            sys.exit("Could not access output directory")
    else:
        directory_name = None
                
    if len(sys.argv) > 3:
        print('Too many arguments.')
        print('Usage is "./unpack infile.xxx output_directory".')
        sys.exit("Invalid argument count")
        
    try:
        print('Opening file {}...'.format(in_file_name))
        data = open(in_file_name, 'r')
    except IOError:
        print('File {} not found.'.format(in_file_name))
        print('Usage is "./unpack infile.xxx output_directory".')
        sys.exit("No valid input file")
        
    for line in data:
        if 'Z' in line:
            break
        parse(line)
    
    print('Cleaning up: closing file {}...'.format(in_file_name))
    data.close()
    close_out_files()
