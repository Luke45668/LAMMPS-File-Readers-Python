# -*- coding: utf-8 -*-
"""
This file will read log.lammps files and output a numpy array containing each thermo column. 
"""

import os
import mmap
import re 
import numba
import time
import numpy as np
import matplotlib.pyplot as plt

#keep code DRY(dont repeat yourself)
# string below for test run
# simulation_file="fix_wall_simulations"
# filename="timestep_0.0001"
# realisation_name = "log.fix_induced_wall_test_no_min_eratexz_1_ts_00001_dump_every_10"
# thermo_var_1 = "c_p0[4] " 
# thermo_var_2 = "Xz "
# thermo_var_3 = "KinEng "
# Path_2_log = "/Volumes/Backup Plus/PhD_/Rouse Model simulations/Using LAMMPS imac/"
#thermo_vars = "c_p0[4] Xz KinEng"

def log2numpy(Path_2_log,simulation_file,filename,realisation_name,thermo_vars):
    


# Finding the logfile 

 os.system('cd ~')
 os.chdir(Path_2_log + simulation_file+"/" +filename)
       

# Searching for thermo output start and end line

 Thermo_data_start_line= ("Step " + thermo_vars)
 Thermo_data_end_line = ("Loop time")
 warning_start = "\\nWARNING:"
 warning_end = "(../fix_srd.cpp:2492)\\n"
# convert string to bytes for faster searching 
 Thermo_data_start_line_bytes=bytes(Thermo_data_start_line,'utf-8')
 Thermo_data_end_line_bytes =bytes(Thermo_data_end_line,'utf-8')

# find begining of data run 
 with open(realisation_name) as f:
    read_data = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) 
    if read_data.find(Thermo_data_start_line_bytes) != -1:
        print('true')
        thermo_byte_start=read_data.find(Thermo_data_start_line_bytes)
    else:
        print('could not find thermo variables')
    

# find end of run         

    if read_data.find(Thermo_data_end_line_bytes) != -1:
        print('true')
        thermo_byte_end =read_data.find(Thermo_data_end_line_bytes)
    else:
        print('could not find end of run')
    

# Splicing out the data and closing the file
   # read_data = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ ) 
    read_data.seek(thermo_byte_start) 
    size_of_data =thermo_byte_end-thermo_byte_start
    log_array_bytes=read_data.read(thermo_byte_end)
    log_array_bytes_trim=log_array_bytes[0:size_of_data]
    read_data.close()
       
# comparison    
#    log_string_before_warning_removal =  str(log_array_bytes_trim)
# Convert byte array to string
    log_string= str(log_array_bytes_trim)
#Count SRD warnings   
    warn_count  = log_string.count(warning_start) 
    #if warn_count == 0:
    # could skip to string split line from here
    
    
# Removing non-data parts 
 # need to re structure the loop to find the first warning idicies then delete it, then find the neext etc etc 
 
    i_0 = list(range(0,warn_count-1))
   # size_i_0=len(i_0)
    warning_start = "WARNING:"
    warning_end = "(../fix_srd.cpp:2492)"
   # warn_offset=len(warning_start)
    warn2_offset= len(warning_end)
   # length_final_warning = len("(../thermo.cpp:422)")
 
    pattern_warn = re.compile(r"nWARNING:") # separates pattern into a variable, allows us to reuse for multiple searches
    pattern_warn_end =re.compile(r"(../fix_srd.cpp:2492)")
    pattern_final_warn =re.compile(r"(../thermo.cpp:422)")
    for i in i_0:
     warning_start_search= pattern_warn.search(log_string)
     warning_end_search= pattern_warn_end.search(log_string)   
     if warning_start_search == None:
         if warning_end_search== None:
             break
     #print(warning_start_search)
     #print(warning_end_search)
 
     warning_start_index=warning_start_search.span(0)[0]
     warning_end_index = warning_end_search.span(0)[0]+ warn2_offset
     if warning_start_index==None:
         if warning_end_index ==None:
             break
     log_string=log_string[:warning_start_index]+log_string[warning_end_index:]

#remove final warning 
    warning_start_search= pattern_warn.search(log_string)
    final_warning_search = pattern_final_warn.search(log_string)
    print(final_warning_search)
    warning_start_index=warning_start_search.span(0)[0]-1  # FIX THIS LINE TO REMOVE WHOLE FINALWARN 
    warning_end_index = final_warning_search.span(0)[1]+1 #+ length_final_warning    
    log_string=log_string[:warning_start_index]+log_string[warning_end_index:]


# use regex again for final check 
    check_warn = pattern_warn.search(log_string)
    check_warn_end = pattern_warn_end.search(log_string)
    check_warn_end_final = pattern_final_warn.search(log_string)


    if check_warn ==None:
       if check_warn_end ==None:
          if check_warn_end_final==None:
            
             print("All Warning messages removed, proceed.")
          else:
            
             print("Data still contains warning messages.")
    
            
# Converting to array and removing '\n'
# getting rid of the spacing '\n'

# Splitting the string into a string array 
    log_string_array_raw = log_string.split()

    log_string_array = [ i for i in log_string_array_raw if i!='\\n' ] # Potentially not the fastest way as we loop through the whole list

    thermo_vars = thermo_vars.split()
    log_string_array = log_string_array[:-1]
    log_string_array = log_string_array[4:]
    log_float_array = [0.00]*len(log_string_array)
    #t_0 =time.time()
    for i in range(len(log_string_array)):
     log_float_array[i] = float(log_string_array[i])
    # print(log_string_array.pop())
    #t=time.time()
    #print(t-t_0)

# Creating numpy array of the data

    log_file = np.array(log_float_array, dtype=np.float64)
    dim_log_file =np.shape(log_file)[0]
    col_log_file = len(thermo_vars)+1
    new_dim_log_file = int(np.divide(dim_log_file,col_log_file))
    log_file = np.reshape(log_file,(new_dim_log_file,col_log_file))
    
 return log_file


















