# Script to receieve the important data points from a duchamp output file

import os
import sys
import time

directory_list = os.listdir('.')
print directory_list
write_file = open("data_collection.csv", 'a')
write_file.write('ParameterNumber,RA,DEC,freq,w_50,w_20 w_FREQ,F_int,F_tot,F_peak,Nvoxel,Nchan,Nspatpix\n')
for output in directory_list:
    print output
    source_files = 0
    if 'output' in output:
        source_files += 1
        output_file = open(output)
        output = output.split('_')[3]  # returns parameter number
        print output
        param_number = output.split('.')[0]
        print param_number
        count = 0 # counts the first 4 lines, which are duchamp output formatting
        for line in output_file.readlines():
            if count >= 4:
                line_break = line.split()
                print line_break
                write_file = open("data_collection.csv", 'a')
                write_file.write(param_number + ',')
                line = '{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}\n'.format(line_break[7], line_break[8],
                                                                                    line_break[9], line_break[15],
                                                                                    line_break[16], line_break[17],
                                                                                    line_break[18], line_break[19],
                                                                                    line_break[20], line_break[27],
                                                                                    line_break[28], line_break[29])
                write_file.write(line)
            else:
                count += 1

write_file.close()