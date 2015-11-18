# Python script to run duchamp on a fits file with multiple parameter files
import gzip
import os
import shutil
import subprocess
import tarfile
import time

wu_input = None
wu_params = None
num_params = 0
input_files = os.listdir('worker/.')


def main():
    unzip_files()
    run_duchamp()
    output_directory = 'outputs_{0}'.format(wu_input)
    move_outputs(output_directory)
    append()


# This function is called in the worker directory
def unzip_files():
    os.chdir('worker')
    print(os.listdir('.'))
    for wu_file in input_files:
        print wu_file
        if "fits" in wu_file:  # This is a workunit file
            output = subprocess.call(['gunzip', wu_file])
            print output
            print wu_file
            global wu_input
            wu_input = wu_file[:-3]
            # os.system('gunzip {0}'.format(wu_file))

        elif wu_file.endswith("tar.gz"):  # This is a parameter folder
            tar = tarfile.open(wu_file)
            tar.extractall()
            tar.close()
            global wu_params
            wu_params = wu_file[:-7]
            os.remove(wu_file)  # remove the uncompressed file
            os.chdir(wu_params)
            global num_params
            num_params = len(os.listdir('.'))
            os.chdir('../')


def run_duchamp():
    print wu_input
    print wu_params
    shutil.copy(wu_input, "{0}/input.fits".format(wu_params))
    os.chdir(wu_params)
    time.sleep(5)
    print 'We are in parameters, about to run'
    time.sleep(5)
    # test Duchamp on all the parameter files
    counter = 0
    while counter <= num_params:
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


def move_outputs(directory):
    # os.chdir('{0}'.format(wu_params))
    time.sleep(5)
    # we should be in the parameter directory
    outputs = os.listdir('.')
    print outputs
    time.sleep(5)
    os.chdir('../')  # this means we should be in the worker directory
    os.mkdir(directory)
    print 'Directory {0} has been made'.format(directory)
    for output_file in outputs:
        if "output" in output_file:
            shutil.copy(output_file, '../{0}'.format(directory))
            os.remove(output_file)
    print 'Copied all output files'
    time.sleep(5)


def append(directory):
    # we should be in the worker directory
    os.chdir('{0}'.format(directory))
    file_list = os.listdir('.')  # this will be output_askap16 or something like that
    time.sleep(5)
    print file_list
    print 'Checking number of files'
    time.sleep(5)
    if len(file_list) != num_params:  # checks to make sure we have the correct number of output files
        # os.chdir('/root')
        print 'In root  directory'
        time.sleep(5)
        print 'Incorrect number of output files, shutting down.'
        time.sleep(5)
        subprocess.call(["rm", "-r", "/root/worker/*"])
        subprocess.call(["rm", "-r", "/root/shared/*"])
        subprocess.call(["shutdown", "-hP", "0"])
    else:
        with open('../final_output.txt',
                  'w') as outfile:  # final_output.txt the file we md5 hash then validate
            for fname in file_list:
                f = open(fname)
                lines = f.readlines()[1:]
                f.close()
                for line in lines:
                    outfile.write(line)


'''WHERE ALL THE BUSINES OCCURS'''

if __name__ == "__main__": main()
