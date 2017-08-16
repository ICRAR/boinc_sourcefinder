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
from utils.logger import config_logger
from utils.csv_compare import CSVCompare

LOG = config_logger(__name__)

OUTPUT_FILES = {'csv': 'data_collection.csv', 'hash': 'hash.md5', 'log': 'Log.txt'}
CSV_VALID_HEADER = ['ParameterNumber', 'RA', 'DEC', 'freq', 'w_50', 'w_20', 'w_FREQ', 'F_int', 'F_tot', 'F_peak', 'Nvoxel', 'Nchan', 'Nspatpix']
NUM_PARAMETERS = 176


def get_init_validator(BaseValidator):

    class InitValidator(BaseValidator):
        @staticmethod
        def check_output_files(file_directory):
            # Check all output files are present
            files = os.listdir(file_directory)

            LOG.info("Files provided: {0}".format(files))

            if len(files) != len(OUTPUT_FILES):
                return False

            if set(files) != set(OUTPUT_FILES.values()):
                return False

            return True

        @staticmethod
        def check_csv_hash(file_directory):
            # Check that the csv hash is correct
            csv_abs = os.path.join(file_directory, OUTPUT_FILES['csv'])
            hashfile_abs = os.path.join(file_directory, OUTPUT_FILES['hash'])

            with open(csv_abs, 'r') as f:
                m = hashlib.md5()
                m.update(f.read())
                csv_hash = m.digest()

            with open(hashfile_abs, 'r') as f:
                hash_file = f.read()

            LOG.info("Hash compare: {0} == {1}".format(m.hexdigest(), m.hexdigest()))
            return csv_hash == hash_file

        @staticmethod
        def check_csv_header(file_directory):
            # Check that the CSV header is correct
            csv_abs = os.path.join(file_directory, OUTPUT_FILES['csv'])
            with open(csv_abs) as f:
                csv_reader = csv.DictReader(f)
                headers = [f.strip() for f in csv_reader.fieldnames]

            LOG.info("Header compare: \n{0}\n{1}".format(headers, CSV_VALID_HEADER))
            return headers == CSV_VALID_HEADER

        @staticmethod
        def check_log_parameters(file_directory):
            # Check that the log contains a duchamp run for each parameter
            log_abs = os.path.join(file_directory, OUTPUT_FILES['log'])
            with open(log_abs, 'r') as logfile:
                matches = re.findall('INFO:root:Running duchamp for supercube_run_[0-9]{5}\.par', logfile.read())

            # if len(matches) < NUM_PARAMETERS:
            #     with open(log_abs, 'r') as logfile:
            #         print "Log file that is invalid: {0}".format(logfile.read())

            return len(matches) >= NUM_PARAMETERS

        def validate(self, file_directory, result_id):
            file_directory = os.path.join(file_directory, "outputs")
            if not self.check_output_files(file_directory):
                return "Missing one or more output files"

            elif not self.check_csv_header(file_directory):
                return "CSV header is incorrect"

            elif not self.check_csv_hash(file_directory):
                return "CSV hash is incorrect"

            return None

    return InitValidator


def get_compare_validator(BaseValidator):
    class CompareValidator(BaseValidator):
        def validate(self, file1_directory, file2_directory):
            file1_path = os.path.join(file1_directory, "outputs", OUTPUT_FILES['csv'])
            file2_path = os.path.join(file2_directory, "outputs", OUTPUT_FILES['csv'])
            with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
                csv_compare_1 = CSVCompare(file1)
                csv_compare_2 = CSVCompare(file2)

            if not csv_compare_1 == csv_compare_2:
                return csv_compare_1.reason

            return None

    return CompareValidator
