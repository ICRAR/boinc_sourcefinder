# Inputs: input folder, parameter folder, output folder
# Outputs: output folder contains output file for each input.
import argparse, os, time, threading, tarfile, subprocess


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


def worker(output_folder):

    while True:
        fits_files_lock.acquire()

        if len(fits_files) == 0:
            fits_files_lock.release()
            break

        fits_file = fits_files.pop()
        fits_files_lock.release()

        tar = tarfile.open(fits_file)
        tar.extractall(output_folder)
        tar.close()

        fits_file = [f for f in os.listdir(output_folder) if f.endswith('.fits')][0]
        os.rename(fits_file, 'input.fits')
        for param in param_files:
            print 'Running duchamp on {0}'.format(param)
            start = time.time()
            subprocess.call(['Duchamp', '-p', param])
            end = time.time()
            print 'Took {0} ms'.format((end - start) * 1000)

        os.remove(fits_file)

    print '{0} done!'.format(output_folder)


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

    threads = []
    for i in range(0, num_workers):
        out_folder = 'worker_{0}'.format(i)
        os.mkdir(os.path.join(args['output_folder'], out_folder))
        thread = threading.Thread(target=worker, name=out_folder, args=[out_folder])
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    main()