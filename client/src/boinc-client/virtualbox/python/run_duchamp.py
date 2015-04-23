# Python script to run duchamp on a fits file with multiple parameter files
import os
import subprocess
import shutil
import time


input_fits = os.listdir('root/shared/.')[0]
output_folder = input_fits[:-5]
output_directory = '/root/worker/outputs_{0}'.format(output_folder)

def run_duchamp(self):
	fits = self.input_file
	if "fits" in file:
		print 'in if statement'
		shutil.copy(fits, "/root/worker/parameters/input.fits")  # in deployment this will be /root/worker/ etc
		print(os.listdir("/root/worker/parameters"))
		time.sleep(5)
		os.chdir('../parameters')
		print 'We are in parameters, about to run'
		time.sleep(5)
		# test Duchamp on all the parameter files
		counter = 0
		while counter < 177:  # currently hardcoded to the number of parameter files in the machine
			counter += 1
			if counter == 1:
				filename = 'supercube_run' + '_' + str(counter) + '.par'
			if counter < 1000:
				filename = 'supercube_run' + '_00' + str(counter) + '.par'
			if counter < 100:
				filename = 'supercube_run' + '_000' + str(counter) + '.par'
			if counter < 10:
				filename = 'supercube_run' + '_0000' + str(counter) + '.par'
			subprocess.call(['Duchamp', '-p', filename])
		print 'Duchamp is finished'


def move_outputs():
	os.chdir('root/parameters')
	time.sleep(5)
	outputs = os.listdir('.')
	time.sleep(5)
	# if output_folder_name not in output_list:
	os.mkdir(output_directory)
	print 'directory {0} has been made'.format(output_directory)
	for output_file in outputs:
		if "output" in output_file:
			shutil.copy(output_file, output_directory)
			os.remove(output_file)
	print 'Copied all output files'
	time.sleep(5)


def append():
	os.chdir(output_directory)
	file_list = os.listdir('.')  # this will be output_askap16 or something like that
	time.sleep(5)
	print file_list
	print 'Checking number of files'
	time.sleep(5)
	if len(file_list) != 176:  # checks to make sure we have the correct number of output files
		os.chdir('/root')
		print 'In root  directory'
		time.sleep(5)
		print 'Incorrect number of output files, shutting down.'
		time.sleep(5)
		subprocess.call(["rm", "-r", "/root/worker/"])
		subprocess.call(["rm", "-r", "/root/shared/parameters"])
		os.remove('/root/shared/inputs.tar.gz')
		subprocess.call(["shutdown", "-hP", "0"])
	else:
		with open('/root/shared/final_output.txt', 'w') as outfile:  # final_output.txt the file we md5 hash then validate
			for fname in file_list:
				f = open(fname)
				lines = f.readlines()[1:]
				f.close()
				for line in lines:
					outfile.write(line)

# where all the business occurs
run_duchamp()
move_outputs()
append()




