# Script to receieve the important data points from a duchamp output file

import os 
import sys 
import time

directory_list = os.listdir('.')
print directory_list
for output in directory_list:
	print output
	source_files = 0
	if 'duchamp-output' in output:
		source_files += 1 
		output_file = open(output)
		write_file = open("data_collection.csv", 'a')
		write_file.write('ParameterNumber,RA,DEC,freq\n')
		output = output.split('_')[3]
		print output
		output2 = output.split('.')[0]
		print output2
		count = 0
		for line in output_file.readlines():
			if count >= 4:
				line_break = line.split()
				print line_break
				write_file.write(output2 + ',')
				write_file.write(line_break[7] + ',' + line_break[8] +',' + line_break[9]+'\n')
				count+=1
			else:
				count+=1


