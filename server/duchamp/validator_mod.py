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

"""
Validator implementation for Duchamp
"""

import re
import os
import csv
import hashlib
import tarfile


def get_init_validator(BaseValidator):

    class InitValidator(BaseValidator):

        def __init__(self):
            BaseValidator.__init__(self)
            self.output_files = {'csv': 'data_collection.csv', 'hash': 'hash.md5', 'log': 'Log.txt'}
            self.csv_valid_header = ['ParameterNumber', 'RA', 'DEC', 'freq', 'w_50', 'w_20', 'w_FREQ', 'F_int', 'F_tot', 'F_peak', 'Nvoxel', 'Nchan', 'Nspatpix']
            self.num_parameters = 176

        def check_output_files(self):
            # Check all output files are present
            files = os.listdir(self.extracted_files )

            if len(files) != len(self.output_files):
                print "Invalid number of output files"
                return False

            if set(files) != set(self.output_files.values()):
                print "Incorrectly named output file(s)"
                return False

            return True

        def check_csv_hash(self):
            # Check that the csv hash is correct
            csv_abs = os.path.join(self.extracted_files, self.output_files['csv'])
            hashfile_abs = os.path.join(self.extracted_files, self.output_files['hash'])

            with open(csv_abs, 'r') as f:
                m = hashlib.md5()
                m.update(f.read())
                csv_hash = m.digest()

            with open(hashfile_abs, 'r') as f:
                hash_file = f.read()

            print "Hash compare: {0}, {1}".format(csv_hash, hash_file)
            return csv_hash == hash_file

        def check_csv_header(self):
            # Check that the CSV header is correct
            csv_abs = os.path.join(self.extracted_files, self.output_files['csv'])
            with open(csv_abs) as f:
                csv_reader = csv.DictReader(f)
                headers = [f.strip() for f in csv_reader.fieldnames]

            print "Header compare:\n{0}\n{1}".format(headers, self.csv_valid_header)
            return headers == self.csv_valid_header

        def check_log_parameters(self):
            # Check that the log contains a duchamp run for each parameter
            log_abs = os.path.join(self.extracted_files, self.output_files['log'])
            with open(log_abs, 'r') as logfile:
                matches = re.findall('INFO:root:Running duchamp for supercube_run_[0-9]{5}\.par', logfile.read())

            if len(matches) < self.num_parameters:
                with open(log_abs, 'r') as logfile:
                    print "Log file that is invalid: {0}".format(logfile.read())

            return len(matches) >= self.num_parameters

        def __call__(self, file1):
            temp_directory = self.get_temp_directory(file1)
            self.extracted_files = os.path.join(temp_directory, 'outputs')

            with tarfile.open(file1, 'r') as f:
                f.extractall(temp_directory)

    return InitValidator


def get_compare_validator(BaseValidator):

    class CompareValidator(BaseValidator):
        def __call__(self, file1, file2):
            pass

    return CompareValidator
