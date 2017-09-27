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
import csv
import time
import logging
import logging.handlers
import subprocess
import gzip
import tarfile
import xml.etree.ElementTree as ET
from threading import Timer

RESULT_COLUMNS = [
    "parameter_number",
    "id",
    "name",
    "x",
    "y",
    "z",
    "x_geo",
    "y_geo",
    "z_geo",
    "rms",
    "rel",
    "x_min",
    "x_max",
    "y_min",
    "y_max",
    "z_min",
    "z_max",
    "n_pix",
    "n_los",
    "n_chan",
    "ra",
    "dec",
    "lon",
    "lat",
    "freq",
    "velo",
    "w20",
    "w50",
    "wm50",
    "f_peak",
    "f_int",
    "f_wm50",
    "ell_maj",
    "ell_min",
    "ell_pa",
    "ell3s_maj",
    "ell3s_min",
    "ell3s_pa",
    "kin_pa",
    "bf_a",
    "bf_b1",
    "bf_b2",
    "bf_c",
    "bf_xe",
    "bf_xp",
    "bf_w",
    "bf_chi2",
    "bf_flag",
    "bf_z",
    "bf_w20",
    "bf_w50",
    "bf_f_peak",
    "bf_f_int"
]

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
sofia_output_end = '_cat.xml'
sofia_output_end_complete_marker = '_cat.xml.complete'

sofia_input_start = 'supercube_run_'
sofia_input_end = '_sofia.par'

process_timeout_seconds = 30 * 60 * 60  # 30 mins

logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)
file_handler = logging.FileHandler(file_system['log_file'])
file_handler.setFormatter(logging.Formatter('%(asctime)-15s:' + logging.BASIC_FORMAT))
logging.getLogger().addHandler(file_handler)


def run_with_timeout(timeout_seconds, *args, **kwargs):
    """
    Runs a subprocess with a timeout (seconds)
    :param timeout_seconds: The timeout in seconds
    :param args: args for Popen
    :param kwargs: kwargs for Popen
    :return:
    """
    def process_kill(ps):
        ps.kill()
        logging.info("Process timeout after {0} seconds".format(timeout_seconds))

    process = subprocess.Popen(*args, **kwargs)

    timer = Timer(timeout_seconds, process_kill, [process])

    try:
        timer.start()
        return process.wait()
    finally:
        timer.cancel()


def save_csv(results, filename):
    """
    Saves a CSV file containing the provided SofiaResults.
    :param results: Results to save.
    :param filename: CSV file to save to.
    :return:
    """
    # First, confirm the headers are all the same
    with_results = [result for result in results if result.has_data]

    # Write out the common header
    # Write out the values for each item in the header
    with open(filename, 'w') as f:
        if len(with_results) == 0:
            # No data at all
            f.write("No sources\n")
        else:
            writer = csv.DictWriter(f, RESULT_COLUMNS, restval="null")

            writer.writeheader()
            for result in results:
                for line in result.data:
                    row = {}
                    for column in RESULT_COLUMNS:
                        if column in line:
                            row[column] = line[column]
                        else:
                            row[column] = "null"
                    row["parameter_number"] = result.parameter_number

                    writer.writerow(row)


class SofiaResult:
    """
    Parses a result from a sofia XML result file
    """

    def __init__(self, parameter_number, data):
        self.parameter_number = parameter_number
        self.raw_data = data
        self.has_data = False
        self.parse_error = None

        self.headings = []  # Each heading from the XML file. In order.
        self.types = []  # Type of data for each heading
        self.data = []  # List of dictionaries, with heading: value pairs.

        self._parse()

    def _parse_xml(self):
        root = ET.fromstring(self.raw_data)
        self._parse_xml_headings(root)
        self._parse_xml_data(root)

    def _parse_xml_headings(self, root):
        table = root.find("RESOURCE").find("TABLE")
        fields = table.findall("FIELD")

        for field in fields:
            name = field.get("name")
            type = field.get("datatype")

            self.headings.append(name)
            self.types.append(type)

    def _parse_xml_data(self, root):
        table = root.find("RESOURCE").find("TABLE").find("DATA").find("TABLEDATA")
        fields = table.findall("TR")

        for field in fields:
            entry = {}
            elements = field.findall("TD")
            for element_idx, element in enumerate(elements):
                entry[self.headings[element_idx]] = element.text
            self.data.append(entry)

    def _parse(self):
        try:
            self._parse_xml()

            self.has_data = True
        except Exception as e:
            self.parse_error = e.message
            return


def get_complete_file_numbers():
    """
    Returns the numbers of all completed files
    :return:
    """
    return {
        int(f[len(sofia_output_start):-len(sofia_output_end_complete_marker)])
        for f in os.listdir(file_system['outputs'])
        if f.startswith(sofia_output_start) and f.endswith(sofia_output_end_complete_marker)
    }


def get_input_file_numbers():
    """
    Returns the numbers of all input files
    :return:
    """
    return [
        int(f[len(sofia_input_start):-len(sofia_input_end)])
        for f in os.listdir(file_system['inputs'])
        if f.startswith(sofia_input_start) and f.endswith(sofia_input_end)
    ]


def run_sofia(inputs):
    """
    Runs sofia on the given list of input files
    :param inputs: List of input files to run
    :return:
    """
    filename = inputs['name']
    number = inputs['number']
    output_filename = os.path.join(
            file_system['outputs'],
            (sofia_output_start + '{0}' + sofia_output_end).format(number)
    )

    logging.info('Running sofia for {0}...'.format(filename))
    out = "{0}.out".format(output_filename)
    err = "{0}.err".format(output_filename)
    complete_marker = "{0}.complete".format(output_filename)
    start = time.time()
    try:
        with open(out, 'a') as stdout, open(err, 'a') as stderr:
            result = run_with_timeout(process_timeout_seconds, ['python', file_system['sofia'], filename], stdout=stdout, stderr=stderr)

        if result == 1:
            logging.info('An application error occurred: code {0}'.format(result))

        # Write a simple marker file to specify that this file has been completed
        with open(complete_marker, 'w') as marker:
            marker.write("Complete")

    except:
        logging.exception('An exception occurred')

    end = time.time()
    logging.info('Took {0}s'.format((end - start)))

    shared_path = os.path.join(file_system['shared'], (sofia_output_start + '{0}' + sofia_output_end).format(number))
    if os.path.exists(shared_path):
        # SoFiA decided to put the file in this directory instead. Move it
        logging.info("SoFiA output file placed in the wrong directory. Moving it...")
        os.rename(shared_path, output_filename)


def combine_outputs():
    """
    Combines all existing sofia output files in to one CSV.
    :return:
    """
    # Compress all results together for returning to the server
    # Skip the '.complete' files.
    outputs = [f for f in os.listdir(file_system['outputs']) if not f.endswith('.complete')]
    results = []

    logging.info("Combining outputs...")

    # Work out which files are results and process them
    for output in outputs:
        if output.endswith(".xml"):
            with open(os.path.join(file_system['outputs'], output), 'r') as f:
                parameter_number = int(output[len(sofia_output_start):-len(sofia_output_end)])
                result = SofiaResult(parameter_number, f.read())
                results.append(result)

    # Save a CSV of the results
    csv_filename = os.path.join(file_system['outputs'], 'data_collection.csv')
    save_csv(results, os.path.join(csv_filename))

    # Return everything in the output folder, as well as the logs.
    with tarfile.open(file_system['outputs_compressed'], 'w:gz') as outputs_compressed:
        for f in outputs:
            outputs_compressed.add(os.path.join(file_system['outputs'], f), f)  # Store in tar as basename only

        outputs_compressed.add(file_system['log_file'], 'Log.txt')
        outputs_compressed.add(csv_filename, 'data_collection.csv')


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
            logging.info("Extracting parameters...")
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

            logging.info("Completed: {0}".format(completed_file_numbers))
            logging.info("Inputs: {0}".format(input_file_numbers))

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

    logging.info("All done.")
