#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia
#    Copyright by UWA (in the framework of the ICRAR)
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#

# Python script to run SoFiA on a fits file with multiple parameter files
import os
import time
import logging
import logging.handlers
import subprocess
import gzip
import tarfile

file_system = {
    'sofia': '/root/SoFiA/sofia_pipeline.py',
    'shared': '/root/shared/',
    'inputs': '/root/shared/inputs',

    'input_fits': '/root/shared/input.fits.gz',
    'input_fits_decompressed': '/root/shared/input.fits',
    'input_parameters': '/root/shared/parameters.tar.gz',

    'outputs': '/root/shared/outputs',
    'outputs_compressed': '/root/shared/outputs.tar.gz',

    'log_file': '/root/shared/Log.txt'
}

completed_file_name = 'output.tar.gz'
sofia_output_start = 'sofia_output_'
sofia_output_end = '_cat.ascii'

sofia_input_start = 'supercube_run_'
sofia_input_end = '_sofia.par'

logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)
file_handler = logging.FileHandler(file_system['log_file'])
file_handler.setFormatter(logging.Formatter('%(asctime)-15s:' + logging.BASIC_FORMAT))
logging.getLogger().addHandler(file_handler)


def get_complete_file_numbers():
    return {
        int(f[len(sofia_output_start):-len(sofia_output_end)])
        for f in os.listdir(file_system['outputs'])
        if f.startswith(sofia_output_start)
    }


def get_input_file_numbers():
    return [
        int(f[len(sofia_input_start):-len(sofia_input_end)])
        for f in os.listdir(file_system['inputs'])
        if f.startswith(sofia_input_start)
    ]


def run_sofia(inputs):
    filename = inputs['name']
    number = inputs['number']
    output_filename = os.path.join(
            file_system['outputs'],
            (sofia_output_start + '{0}' + sofia_output_end).format(number)
    )

    logging.info('Running sofia for {0}...'.format(filename))
    start = time.time()
    try:
        result = subprocess.call(['python', file_system['sofia'], filename])
        if result == 1:
            logging.info('An application error occurred: code {0}'.format(result))
    except:
        logging.exception('An exception occurred')

    end = time.time()
    logging.info('Took {0}s'.format((end - start)))

    # Now, to ensure the program has an output file for this specific parameter,
    # check if SoFiA generated an output file. If not, generate a fake one ourselves.
    if not os.path.exists(output_filename):
        with open(output_filename, 'w') as f:
            f.write("!!! No sources found for {0}".format(filename))


def combine_outputs():
    # Compress all results together for returning to the server
    outputs = os.listdir(file_system['outputs'])

    with tarfile.open(file_system['outputs_compressed'], 'w:gz') as outputs_compressed:
        for f in outputs:
            outputs_compressed.add(os.path.join(file_system['outputs'], f), f)  # Store in tar as basename only

        outputs_compressed.add(file_system['log_file'], 'Log.txt')


def unzip_if_needed():
    """
    The parameter files should be stored in /root/shared/.
    They should be unzipped and moved to /root/shared/inputs/.
    The input.fits file should be decompressed and left in /root/shared
    :return:
    """
    # Assume that if there are files in /root/shared/inputs that we've decompressed the parameter files correctly
    parameter_files = os.listdir(file_system['inputs'])
    if len(parameter_files) == 0:
        # Parameter files need to be unzipped
        with tarfile.open(file_system['input_parameters'], 'r') as parameters:
            logging.info("Extracing parameters...")
            parameters.extractall(file_system['inputs'])
    else:
        logging.info("Parameter files exist.")

    # Simply check for the existence of input.fits
    if not os.path.exists(file_system['input_fits_decompressed']):
        # input.fits.gz needs to be decompressed
        with gzip.open(file_system['input_fits'], 'r') as input_fits:
            with open(file_system['input_fits_decompressed'], 'w') as input_fits_decompressed:
                logging.info("Extracting input file...")
                input_fits_decompressed.write(input_fits.read())
    else:
        logging.info("Input file exists.")


if __name__ == "__main__":
    try_count = 10

    while try_count:
        try:
            # Unzip the input files if needed
            unzip_if_needed()

            # Get list of output files
            completed_file_numbers = get_complete_file_numbers()
            # Get list of input files
            input_file_numbers = get_input_file_numbers()

            # Determine which files need to be processed
            fmt = sofia_input_start + '{0}' + sofia_input_end
            inputs_to_do = [
                {"name": fmt.format(f), "number": f}
                for f in input_file_numbers
                if f not in completed_file_numbers
            ]

            logging.info("Files to run: {0}".format([f["name"] for f in inputs_to_do]))

            # Process each file
            for item in inputs_to_do:
                item['name'] = os.path.join(file_system['inputs'], item['name'])
                run_sofia(item)

            # Combine output files in to one
            combine_outputs()
            break
        except:
            logging.exception("Exception in main")
            try_count -= 1

    if try_count == 0:
        logging.info("{0} exceptions encountered. Exiting...".format(try_count))
        combine_outputs()  # Just dump the Log.txt file and exit
