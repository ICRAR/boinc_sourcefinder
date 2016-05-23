# Python script to run duchamp on a fits file with multiple parameter files
import os
from os.path import join
import shutil
import subprocess
import tarfile
import time
import logging
import hashlib

file_system = {
    'worker': '/root/shared/worker',
    'shared': '/root/shared/',
    'outputs': '/root/shared/outputs',
    'completed_marker': '/root/completed',
    'log_file': '/root/shared/log/Log.txt'
}

# We now write logs to a log file that is visible for the client (helps a lot with debugging)
logging.basicConfig(filename=file_system['log_file'], level=logging.INFO)

# **Some utilities here are from the server, but the client acts as a standalone file so it doesn't have access to the
#   server's utilities file**

# Utilities---------------------------------------------------

class DirStack:
    """
    DirStack is a simple helper class that allows the user to push directories on to the stack then
    pop them off later. If you want to change the working directory of the program, use stack.push() then
    os.chdir(dir).
    Later, to restore the previous directory, use stack.pop()
    """

    def __init__(self):
        self.stack = []

    def push(self):
        self.stack.append(os.getcwd())

    def pop(self):
        os.chdir(self.stack.pop())


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


@static_vars(folder=None)
def parameter_folder():
    """
    Search for the parameter folder and return the absolute path to it.
    :return: Absolute path to the parameter folder
    """

    if parameter_folder.folder is not None: # Our static has already been set, so return it
        return parameter_folder.folder

    # Parameter folder should be in the worker directory

    files = os.listdir(file_system['worker'])

    for f in files:
        if f.startswith('parameter_files'):
            parameter_folder.folder = f
            return f

    return None

@static_vars(folder=None)
def input_file():
    """
    Search for the input file and return an absolute path to it
    :return: Absolute path to the input file
    """

    # Input file should be in the worker/parameter_files directory

    # First, does the parameter folder exist?

    params = parameter_folder()

    if not params:
        return None
    else:

        if input_file.folder is not None: # Our static has already been set, so return it
            return input_file.folder

        files = os.listdir(params)

        for f in files:
            if f.startswith('input.fits'):
                input_file.folder = f
                return f

        return None



def parameter_number(f):
    """
    Gets the parameter number from a parameter file.
    :param f: The file to obtain the number from
    :return: The parameter number of that file
    """

    # File name is like supercube_run_00001.par

    dot = f.find('.')
    last_ = f.rfind('_') + 1  # Need +1 to ignore the underscore

    # Substring from the last underscore in the name to the dot (this should be the number)

    return int(f[last_:dot])


def write_complete_marker():
    """
    Creates a file to notify the external bash script running us that we've completed successfully.
    :return: nil
    """
    with open(file_system['completed_marker'], 'w') as f:
        f.write('Done')

# Utilities end---------------------------------------------------

def check_files_unzipped():
    """
    Have the files we use for running duchamp already been unzipped?
    This should include an input.fits file and a folder of parameters.

    Note - this does not confirm whether all parameter files in the parameter files zip folder exist, just whether
    the parameter files folder has been created.

    :return: True,True if both are found, True,False if input is found, but not parameters, False,True if parameters
    are found, but not input, False,False if neither are found.
    """

    # Look in worker director, is there input.fits and parameter_files_X in there?

    worker_list = os.listdir(file_system['worker'])
    input_found = False
    parameters_found = False

    for f in worker_list:

        if f.endswith('input.fits'):
            # We have the input file.
            input_found = True

        if f.startswith('parameter_files'):
            # We have the parameter files
            parameters_found = True

    return input_found, parameters_found


def last_completed():
    """
    Search through the parameter_files_(run_ID) folder and find the latest (highest number) for any duchamp output files that exist
    :return: number of the last processed parameter file.
    """

    # Number of files that start with duchamp-output
    return len([f for f in os.listdir(join(file_system['worker'], parameter_folder())) if f.startswith('duchamp-output')])


def main():

    good = False

    try:
        logging.info('Staring...')

        # Decompress all of the files needed to run duchamp.
        # If already decompressed, does nothing.
        unzip_files()

        # Runs duchamp on the decompressed files.

        while not good:
            run_duchamp(remaining_files())

            # Moves all of the output files in to the output directory
            move_outputs(file_system['outputs'])

            # When this returns true, we're good to go past this
            good = check_and_build_output(file_system['outputs'])

        write_complete_marker()  # This tells the bash script that we actually finished and it should finish too

        logging.info('All done!')
    except:
        logging.exception('An exception occurred when trying to run')


# This function assumes we're in the worker directory
def unzip_files():
    """
    Decompresses all of the files required to run duchamp. This includes the parameters directory and the input file.
    :return:
    """

    dirstack = DirStack()
    inputs, params = check_files_unzipped()

    if inputs and params:
        logging.info('No need to unzip anything')
        return  # We have everything already in place.

    # Input files, by default, are put in the shared directory.
    input_files = os.listdir(file_system['shared'])

    logging.info("Unzipping files...")
    logging.info(input_files)

    for wu_file in input_files:
        if "fits" in wu_file and not inputs:  # This is a workunit file

            logging.info("Decompressing input fits file...")
            # Copy the file in to the worker directory
            shutil.copy(join(file_system['shared'], wu_file), file_system['worker'])

            dirstack.push()

            os.chdir(file_system['worker'])
            subprocess.call(['gunzip', wu_file])

            dirstack.pop()

            # Rename the file to 'input.fits'.
            new_filename = join(file_system['worker'], 'input.fits')

            logging.info("Renaming input fits file from {0} to {1}".format(wu_file[:-3], new_filename))

            shutil.move(wu_file[:-3], new_filename)

        elif wu_file.endswith("tar.gz") and not params:  # This is a parameter folder

            logging.info("Decompressing parameter files...")

            # Copy the file in to the worker directory
            shutil.copy(join(file_system['shared'], wu_file), file_system['worker'])

            dirstack.push()

            # Extract the tar file in to worker, creating the parameter_files_(run_id) folder
            os.chdir(file_system['worker'])
            tar = tarfile.open(wu_file)
            tar.extractall()
            tar.close()
            os.remove(wu_file)

            dirstack.pop()

    # worker directory now consists of two files - uncompressed 'input.fits' file, and a directory that has the name 'parameter_files_(run_id)'

    # The params folder has just been built, so we need to move the input.fits file in there now
    if not params:
        logging.info("Coping input.fits over to {0}".format(parameter_folder()))
        shutil.copy(join(file_system['worker'], 'input.fits'), parameter_folder())


    # Once this function has finished, the directory structure of the program should look like this:

    # worker -> input.fits
    # worker -> parameter_files_(run_id)
    # worker -> parameter_files_(run_id) -> input.fits
    # worker -> parameter_files_(run_id) -> multiple.par files

def remaining_files():
    """
    Gets a list of the remaining files that duchamp has to run
    :return: list of filenames for the remaining files that duchamp must run.
    """

    # Get a list of all of the files we can run. The ones that end in .par and start with supercube
    files_to_run = [f for f in os.listdir(parameter_folder()) if f.endswith('.par') and f.startswith('supercube')]

    # Look for complete files in the outputs and the parameters directory.
    files_done = [f for f in os.listdir(file_system['outputs']) if f.endswith('.par') and f.startswith('duchamp')]
    files_done.extend([f for f in os.listdir(parameter_folder()) if f.endswith('.par') and f.startswith('duchamp')])

    # remove duplicates
    files_done = set(files_done)
    # logging.info("Files done: {0}".format(sorted(files_done)))

    still_to_go = []
    if len(files_to_run) != len(files_done):
        # Which ones did we miss?

        for input in files_to_run:
            found = False
            for output in files_done:

                # Found a match, it's not this one.
                if parameter_number(input) == parameter_number(output):
                    found = True
                    break  # Break here if we find a match

            if not found: # Not found, add to the still to go list
                still_to_go.append(input)

    # logging.info("Still to go: {0}".format(still_to_go))

    # Sort everything by its parameter number
    still_to_go.sort(key=lambda param_n: parameter_number(param_n))

    logging.info('Remaining files: {0}'.format(len(still_to_go)))

    return still_to_go


def run_duchamp(files_to_run):
    """
    Runs duchamp sequentially on the given files.

    :param files_to_run: List of filenames to run on
    :return:
    """

    dirstack = DirStack()
    # If we called unzip_files() we can be sure that everything has been laid out for this function to work.
    logging.info('Running duchamp...')

    dirstack.push()
    os.chdir(parameter_folder())

    for run in files_to_run:

        logging.info('Running duchamp for {0}...'.format(run))
        start = time.time()
        subprocess.call(['Duchamp', '-p', run])
        end = time.time()

        logging.info('Took {0} ms'.format((end - start) * 1000))

    dirstack.pop()

    logging.info('Duchamp is finished')


def move_outputs(directory):
    """
    This is to move all of the duchamp outputs from the parameter folder to our output directory.
    :param directory: Where to move the outputs to.
    :return:
    """
    outputs = os.listdir(parameter_folder())

    # logging.info('Directory {0} has been made'.format(directory))

    for output_file in outputs:
        if "output" in output_file:
            shutil.copy('{0}/{1}'.format(parameter_folder(), output_file), directory)
            os.remove('{0}/{1}'.format(parameter_folder(), output_file))

    logging.info('Copied all duchamp-output files')


def check_and_build_output(directory):
    """
    Checks whether there are any files remaining to be processed.
    If there are, returns false.
    If there aren't, builds the output CSV and returns true,

    :param directory: the directory to check for outputs
    :return:
    """

    # Check to ensure the number of output files we have matches the number of input files
    remaining = len(remaining_files())
    if remaining > 0:
        logging.error('Missed {0} parameter files somehow'.format(remaining))
        return False  # Tell the rest of the program to try again.

    build_output_csv(directory)

    return True


def build_output_csv(directory):
    """
    Builds an output CSV based on the data found in the provided directory.

    :param directory: The directory to look in.
    :return:
    """
    dirstack = DirStack()

    dirstack.push()

    os.chdir(directory)

    directory_list = os.listdir(directory)

    write_file = open("{0}/data_collection.csv".format(directory), 'a')
    write_file.write('ParameterNumber,RA,DEC,freq,w_50,w_20,w_FREQ,F_int,F_tot,F_peak,Nvoxel,Nchan,Nspatpix\n')
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
            count = 0  # counts the first 4 lines, which are duchamp output formatting
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

    # MD5 hash
    write_file = open("{0}/data_collection.csv".format(directory), 'r')
    m = hashlib.md5()

    m.update(write_file.read())
    hash = m.digest()

    with open("{0}/hash.md5".format(directory), 'w') as f:
        f.write(hash)

    dirstack.pop()

'''WHERE ALL THE BUSINESS OCCURS''' # business has two s' on the end

if __name__ == "__main__": main()
