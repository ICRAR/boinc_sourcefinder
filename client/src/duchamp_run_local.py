# Inputs: input folder, parameter folder, output folder
# Outputs: output folder contains output file for each input.
import argparse, os, time, threading, tarfile, subprocess, errno


def make_path(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def parse_args():
    parser = argparse.ArgumentParser(description='Run duchamp on the provided set of inputs, using the provided set of parameters')
    parser.add_argument('input_folder', type=str, nargs=1)
    parser.add_argument('parameter_folder', type=str, nargs=1)
    parser.add_argument('output_folder', type=str, default='.')
    parser.add_argument('--threads', type=int, default=4)

    return vars(parser.parse_args())

fits_files = []
fits_files_lock = None
param_files = []


def worker(thread_name, input_folder, param_folder, output_folder):

    while True:
        fits_files_lock.acquire()

        if len(fits_files) == 0:
            fits_files_lock.release()
            break

        fits_file = fits_files.pop()
        fits_files_lock.release()

        input_file = os.path.join(input_folder, fits_file)
        print '{0}: Input: {1}'.format(thread_name, input_file)

        unzipped = os.path.join(output_folder, fits_file[:-3])
        print '{0}: Unzipping to: {1}'.format(thread_name, unzipped)

        with open(unzipped, 'w+') as f:
            subprocess.call(['gunzip', '-c', input_file], stdout=f)

        renamed = os.path.join(output_folder, 'input.fits')
        os.rename(unzipped, renamed)
        print '{0} renamed {1} to {2}'.format(thread_name, unzipped, renamed)

        fits_output_path = os.path.join(output_folder, input_file[:-8])
        make_path(fits_output_path)
        print '{0} Making output path... {1}'.format(thread_name, fits_output_path)

        for param in param_files:
            param_abs = os.path.join(param_folder, param)
            print '{0}: Running duchamp on {1} with parameters {2}'.format(thread_name, fits_file, param)
            start = time.time()
            with open(os.devnull, 'w') as f:
                subprocess.call(['Duchamp', '-p', param_abs], cwd=output_folder, stdout=f, stderr=f)
            end = time.time()
            print '{0}: Took {1} ms'.format(thread_name, (end - start) * 1000)

            duchamp_output = 'duchamp-output_{0}'.format(param)
            os.rename(os.path.join(output_folder, duchamp_output), os.path.join(fits_output_path, duchamp_output))

        os.remove(renamed)

    print '{0} done!'.format(thread_name)


def main():
    args = parse_args()

    # Find all input files in input directory (list)
    # Make a folder for each worker thread (named worker_0 -> worker_x)
    # Fire up worker threads
        # Get mutex lock on input files list
        # Get top most input file from list
        # Remove top most input file from list
        # Free mutex lock on input files list
        # Decompress file in to the worker directory
            # For each parameter file in the parameter folder
                # Run Duchamp subprocess for each parameter file the fits file (duchamp -p param_file)
    # Wait for all worker threads
    # Copy all output files from the worker directories in to the output folder.
    print 'Input: {0}'.format(args['input_folder'][0])
    print 'Parameters: {0}'.format(args['parameter_folder'][0])
    print 'Output: {0}'.format(args['output_folder'])
    time.sleep(5)

    global fits_files, fits_files_lock, param_files
    fits_files = [f for f in os.listdir(args['input_folder'][0]) if f.endswith('.fits.gz')]
    fits_files_lock = threading.Lock()
    param_files = [f for f in os.listdir(args['parameter_folder'][0]) if f.endswith('.par')]
    num_workers = args['threads']

    print 'Number of fits files {0}'.format(len(fits_files))
    print 'Number of parameter files {0}'.format(len(param_files))
    print 'Worker Threads {0}'.format(num_workers)

    threads = []
    for i in range(0, num_workers):
        out_folder = 'worker_{0}'.format(i)
        make_path(os.path.join(args['output_folder'], out_folder))
        thread = threading.Thread(target=worker, name=out_folder,
                                  args=[out_folder,
                                        args['input_folder'][0],
                                        args['parameter_folder'][0],
                                        os.path.join(args['output_folder'], out_folder)]
                                  )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    main()