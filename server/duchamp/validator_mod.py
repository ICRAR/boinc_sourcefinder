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
import shutil
import hashlib
from utils import extract_tar, make_path
from utils.logger import config_logger

LOG = config_logger(__name__)

OUTPUT_FILES = {'csv': 'data_collection.csv', 'hash': 'hash.md5', 'log': 'Log.txt'}
CSV_VALID_HEADER = ['ParameterNumber', 'RA', 'DEC', 'freq', 'w_50', 'w_20', 'w_FREQ', 'F_int', 'F_tot', 'F_peak', 'Nvoxel', 'Nchan', 'Nspatpix']
NUM_PARAMETERS = 176


def get_init_validator(BaseValidator):

    class InitValidator(BaseValidator):

        def __init__(self, config):
            BaseValidator.__init__(self, config)
            self.working_file = None

        def check_output_files(self):
            # Check all output files are present
            files = os.listdir(self.extracted_files)

            LOG.info("Files provided: {0}".format(files))

            if len(files) != len(OUTPUT_FILES):
                return False

            if set(files) != set(OUTPUT_FILES.values()):
                return False

            return True

        def check_csv_hash(self):
            # Check that the csv hash is correct
            csv_abs = os.path.join(self.extracted_files, OUTPUT_FILES['csv'])
            hashfile_abs = os.path.join(self.extracted_files, OUTPUT_FILES['hash'])

            with open(csv_abs, 'r') as f:
                m = hashlib.md5()
                m.update(f.read())
                csv_hash = m.digest()

            with open(hashfile_abs, 'r') as f:
                hash_file = f.read()

            LOG.info("Hash compare: {0} == {1}".format(m.hexdigest(), m.hexdigest()))
            return csv_hash == hash_file

        def check_csv_header(self):
            # Check that the CSV header is correct
            csv_abs = os.path.join(self.extracted_files, OUTPUT_FILES['csv'])
            with open(csv_abs) as f:
                csv_reader = csv.DictReader(f)
                headers = [f.strip() for f in csv_reader.fieldnames]

            LOG.info("Header compare: \n{0}\n{1}".format(headers, CSV_VALID_HEADER))
            return headers == CSV_VALID_HEADER

        def check_log_parameters(self):
            # Check that the log contains a duchamp run for each parameter
            log_abs = os.path.join(self.extracted_files, OUTPUT_FILES['log'])
            with open(log_abs, 'r') as logfile:
                matches = re.findall('INFO:root:Running duchamp for supercube_run_[0-9]{5}\.par', logfile.read())

            # if len(matches) < NUM_PARAMETERS:
            #     with open(log_abs, 'r') as logfile:
            #         print "Log file that is invalid: {0}".format(logfile.read())

            return len(matches) >= NUM_PARAMETERS

        def copy_to_invalid(self):
            folder = os.path.join(self.config["DIR_VALIDATOR_INVALIDS"], 'init')
            if os.path.exists(folder):
                shutil.copy(self.working_file, folder)
            else:
                LOG.info("Not copying to {0} because the path doesn't exist".format(folder))

        def __call__(self, file1):
            self.working_file = file1
            reason = None  # Reason why validation failed
            LOG.info("Validate workunit file: {0}".format(self.working_file))

            try:
                temp_directory = self.get_temp_directory(self.working_file)
                self.extracted_files = os.path.join(temp_directory, 'outputs')

                extract_tar(self.working_file, temp_directory)

                if not self.check_output_files():
                    reason = "Missing one or more output files"
                elif not self.check_csv_header():
                    reason = "CSV header is incorrect"
                elif not self.check_csv_hash():
                    reason = "CSV hash is incorrect"
                # if not self.check_log_parameters():
                #     LOG.error("Log is missing entries for some parameters. Not failing though.")

            except Exception:
                LOG.exception("Error on workunit file {0}".format(self.working_file))
                reason = "Exception"

            finally:
                self.free_temp_directory(self.working_file)

            if reason is None:
                LOG.info("Workunit file is valid: {0}".format(self.working_file))
                return 0
            else:
                LOG.info("Workunit is not valid: {0}. Reason: {1}".format(self.working_file, reason))
                self.copy_to_invalid()
                return 1

    return InitValidator


def get_compare_validator(BaseValidator):

    class CSVCompare:

        def __init__(self, csv_data):

            self.cells = None
            self.rows = None

            self.threshold = 0.0001

            self.reason = None  # Reason why the last compare failed
            self.unmatching_row = None  # The row that didn't match

            # Load the CSV rows.
            csv_reader = csv.DictReader(csv_data)
            self.cells = [a for r in csv_reader for a in r.values()]
            self.rows = [r for r in csv_reader]

        def _compare_cells(self, row1, row2):
            for cell1, cell2 in zip(row1, row2):
                if abs(float(cell1) - float(cell2)) > self.threshold:
                    return False
            return True

        def compare(self, other):
            self.unmatching_row = None
            # Search for a matching rows. All of my rows must match with one of their rows.
            for my_row in self.rows:
                found = False
                for other_row in other.rows:
                    if self._compare_cells(my_row, other_row):
                        found = True
                        break

                if not found:
                    self.unmatching_row = my_row
                    return False

            return True

        def __eq__(self, other):
            """

            :param other:
            :type other: CSVCompare
            :return:
            """
            self.reason = None
            try:
                if type(other) != type(self):
                    self.reason = "Other object is incorrect type"
                elif len(self.rows) != len(other.rows):
                    self.reason = "Length of rows differs: {0} to {1}".format(len(self.rows), len(other.rows))
                elif len(self.cells) != len(other.cells):
                    self.reason = "Length of cells differs: {0}, to {1}".format(len(self.cells), len(other.cells))
                elif not self.compare(other):
                    self.reason = "Row {0} doesn't match other".format(self.unmatching_row)

            except Exception as e:
                self.reason = "Exception: {0}".format(e.message)

            return self.reason is None

    class CompareValidator(BaseValidator):
        def __init__(self, config):
            BaseValidator.__init__(self, config)
            self.working_file1 = None
            self.working_file2 = None

        def copy_to_invalid(self):
            folder = os.path.join(self.config["DIR_VALIDATOR_INVALIDS"], 'compare')
            if os.path.exists(folder):
                shutil.copy(self.working_file1, folder)
                shutil.copy(self.working_file2, folder)
            else:
                LOG.info("Not copying to {0} because the path doesn't exist".format(folder))

        def get_csv_compare(self, result_filename):
            temp_directory = self.get_temp_directory(result_filename)
            extracted_files = os.path.join(temp_directory, 'outputs')

            extract_tar(result_filename, temp_directory)

            with open(os.path.join(extracted_files, OUTPUT_FILES['csv']), 'r') as f:
                return CSVCompare(f)

        def __call__(self, file1, file2):
            self.working_file1 = file1
            self.working_file2 = file2
            reason = None  # Reason why validation failed
            LOG.info("Validate workunit files: {0} and {1}".format(self.working_file1, self.working_file2))

            try:
                csv_compare_1 = self.get_csv_compare(self.working_file1)
                csv_compare_2 = self.get_csv_compare(self.working_file2)

                if not csv_compare_1 == csv_compare_2:
                    reason = csv_compare_1.reason

            except Exception:
                LOG.exception("Error on file workunit files: {0} and {1}".format(self.working_file1, self.working_file2))
                reason = "Exception"

            finally:
                self.free_temp_directory(self.working_file1)
                self.free_temp_directory(self.working_file2)

            if reason is None:
                LOG.info("Workunit files are valid: {0} and {1}".format(self.working_file1, self.working_file2))
                return 0
            else:
                LOG.info("Workunit files are not valid: {0} and {1}. Reason: {2}".format(self.working_file1, self.working_file2, reason))
                self.copy_to_invalid()
                return 1

    return CompareValidator
