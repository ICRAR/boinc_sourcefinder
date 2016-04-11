# Python script to run duchamp on a fits file with multiple parameter files
import os
import shutil
import subprocess
import tarfile
# import time
import cPickle as p

wu_input = None
wu_params = None
num_params = 0
input_files = os.listdir('worker/.')
progress_file_name = '/root/progress'
complete_marker = '/root/completed'


def progress_file_exists():
    return os.path.isfile(progress_file_name)


def read_progress_file():

    global wu_input, wu_params, num_params

    with open(progress_file_name) as f:
        progress = p.load(f)
        wu_input = p.load(f)
        wu_params = p.load(f)
        num_params = p.load(f)

    return progress


def write_progress_file(progress):
    with open(progress_file_name, 'w') as f:
        p.dump(progress, f, p.HIGHEST_PROTOCOL)
        p.dump(wu_input, f, p.HIGHEST_PROTOCOL)
        p.dump(wu_params, f, p.HIGHEST_PROTOCOL)
        p.dump(num_params, f, p.HIGHEST_PROTOCOL)


def write_complete_marker():
    with open(complete_marker, 'w') as f:
        f.write('Done')


def main():
    # We do work in this directory
    print 'Staring...'
    os.chdir('worker')

    # Don't keep unzipping
    progress_point = 0
    if not progress_file_exists():
        print 'Unzipping files'
        unzip_files()
        write_progress_file(0)  # Write to say we've unzipped the files
    else:
        print 'Resuming from previous point'
        progress_point = read_progress_file()

    run_duchamp(progress_point)

    output_directory = 'outputs'
    move_outputs(output_directory)
    append(output_directory)
    write_complete_marker()  # This tells the bash script that we actually finished and it should finish too


# This function assumes we're in the worker directory
def unzip_files():
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
            os.remove(wu_file)
            # directory now consists of two files - uncompressed 'input.fits' file, and a directory that has the name 'parameter_files_(run_id)'
    new_dir_list = os.listdir('.')
    for new_dir_name in new_dir_list:
        if "parameter" in new_dir_name:
            global wu_params
            wu_params = new_dir_name
            #os.remove(wu_params)  # remove the uncompressed file
            os.chdir(wu_params)
            global num_params
            print(os.listdir('.'))
            #time.sleep(3)
            num_params = len(os.listdir('.'))
            os.chdir('../')


def run_duchamp(progress_point):
    print wu_input
    print wu_params
    print os.getcwd()
    shutil.copy(wu_input, "{0}/input.fits".format(wu_params))
    os.chdir(wu_params)
    #time.sleep(5)
    print 'We are in parameters, about to run'
    #time.sleep(5)
    # test Duchamp on all the parameter files

    counter = progress_point
    print 'Last completed {0}'.format(counter)
    while counter <= num_params:
        counter += 1
        # this one is pointless
        #if counter == 1:
        #    filename = 'supercube_run' + '_' + str(counter) + '.par'
        if counter < 10:
            filename = 'supercube_run' + '_0000' + str(counter) + '.par'
        elif counter < 100:
            filename = 'supercube_run' + '_000' + str(counter) + '.par'
        elif counter < 1000:
            filename = 'supercube_run' + '_00' + str(counter) + '.par'
        elif counter < 10000: # Added just to be complete
            filename = 'supercube_run' + '_0' + str(counter) + '.par'
        else:
            filename = 'supercube_run' + '_' + str(counter) + '.par'

        print 'Running duchamp for {0}...'.format(counter)
        # subprocess.call(['Duchamp', '-p', filename])
        os.system("Duchamp -p {0} > /dev/null".format(filename))
        # We just completed something, write the progress file
        write_progress_file(counter)
    print 'Duchamp is finished'


def move_outputs(directory):
    # directory is the duchamp-output directory
    #time.sleep(5)
    # we should be in the parameter directory
    outputs = os.listdir('.')
    print outputs
    #time.sleep(5)
    os.chdir('../')  # this means we should be in the worker directory
    os.mkdir(directory)
    print 'Directory {0} has been made'.format(directory)
    for output_file in outputs:
        if "output" in output_file:
            shutil.copy('{0}/{1}'.format(wu_params, output_file), directory)
            os.remove('{0}/{1}'.format(wu_params, output_file))
    print 'Copied all duchamp-output files'
    #time.sleep(5)


def append(directory):
    # we should be in the worker directory
    os.chdir('{0}'.format(directory))  # moves us to duchamp-output directory
    file_list = os.listdir('.')  # this will be output_askap16 or something like that
    #time.sleep(5)
    print file_list
    print 'Checking number of files'
    #time.sleep(5)
    if len(file_list) != num_params:  # checks to make sure we have the correct number of duchamp-output files
        # os.chdir('/root')
        print 'In root  directory'
        #time.sleep(5)
        print 'Incorrect number of output files, shutting down.'
        #time.sleep(5)
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

            # make run file
            run_file = open("run_file.txt", 'w+')
            wu_run = wu_params.split('_')[2]
            run_file.write(wu_run)
            run_file.close()


'''WHERE ALL THE BUSINESS OCCURS''' # business has two s' on the end

if __name__ == "__main__": main()
