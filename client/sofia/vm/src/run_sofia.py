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
import logger
import subprocess

file_system = {
    'worker': '/root/shared/worker',
    'shared': '/root/shared/',
    'inputs': '/root/shared/inputs',
    'outputs': '/root/shared/outputs',
    'completed_marker': '/root/completed',
    'log_file': '/root/shared/log/Log.txt'
}

completed_file_name = 'output.tar.gz'
sofia_output_start = 'sofia_output_'
sofia_output_end = '_cat.ascii'

sofia_input_start = 'supercube_run_'
sofia_input_end = '_sofia.par'


logger.basicConfig(filename=file_system['log_file'], level=logger.INFO)


def get_complete_file_numbers():
    return [
        int(f[len(sofia_output_start):-len(sofia_output_end)])
        for f in os.listdir(file_system['outputs'])
        if f.startswith(sofia_output_start)
    ]


def get_input_file_numbers():
    return [
        int(f[len(sofia_input_start):-len(sofia_input_end)])
        for f in os.listdir(file_system['inputs'])
        if f.startswith(sofia_input_start)
    ]


def run_sofia(input_file):
    logger.info('Running sofia for {0}...'.format(input_file))
    start = time.time()
    result = subprocess.call(['sofia_pipeline.py', input_file])
    if result == 1:
        logger.info("An error occured: code {0}".format(result))
    end = time.time()
    logger.info('Took {0}s'.format((end - start)))
    pass


def combine_outputs():
    pass


def create_shutdown_trigger():
    pass


if __name__ == "__main__":
    # Get list of output files
    completed_file_numbers = set(get_complete_file_numbers())
    # Get list of input files
    input_file_numbers = get_input_file_numbers()

    # Determine which files need to be processed
    fmt = sofia_input_start + '{0}' + sofia_input_end
    inputs_to_do = [
        fmt.format(f)
        for f in input_file_numbers
        if f not in completed_file_numbers
    ]

    # Process each file
    for item in inputs_to_do:
        run_sofia(item)

    # Combine output files in to one
    combine_outputs()
    # Create shutdown trigger
    create_shutdown_trigger()