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
Validator implementation for SoFiA
"""
import os
from utils import split_wu_name
from utils.logger import config_logger
from utils.csv_compare import CSVCompare
from sqlalchemy.engine import create_engine
from sqlalchemy import select, func

LOG = config_logger(__name__)

# Validate on:

# Init
# Number of parameters returned (ensure they match the number registered in the db)
# Ensure the CSV contains "No sources\n" or starts with "parameter_number"

# Compare
# Compare the contents of the CSV files in the same way as duchamp.

# Others are optional, but we need these two
OUTPUT_FILES = ['data_collection.csv', 'Log.txt']


def get_init_validator(BaseValidator):

    class InitValidator(BaseValidator):

        def get_parameter_count(self, result_id):
            RESULT = self.config["database_boinc"]["RESULT"]
            PARAMETER_RUN = self.config["database"]["PARAMETER_RUN"]
            # Get the run ID from the BOINC DB's result name
            engine = create_engine(self.config["BOINC_DB_LOGIN"])
            connection = engine.connect()
            try:
                result = connection.execute(select([RESULT]).where(RESULT.c.id == result_id)).first()
                _, run_id, _ = split_wu_name(result['name'])
            finally:
                connection.close()

            # Get the set of parameters from the sofia db.
            engine = create_engine(self.config["DB_LOGIN"])
            connection = engine.connect()
            try:
                return connection.execute(select([func.count(PARAMETER_RUN.c.run_id)]).where(PARAMETER_RUN.c.run_id == run_id)).first()[0]
            finally:
                connection.close()

        def check_output_files(self, file_directory, result_id):
            # Check that data collection.csv and log.txt are present
            files = os.listdir(file_directory)

            LOG.info("Files provided: {0}".format(files))

            for f in OUTPUT_FILES:
                if f not in files:
                    # Required file is missing.
                    return False

            # Check that the number of parameters for this file is correct.
            file_count = 0
            if self.test_mode:
                # In test mode we don't want to access the DB, so just use a hard coded value.
                parameter_count = 4
            else:
                parameter_count = self.get_parameter_count(result_id)

            for f in files:
                if f.endswith("_cat.xml.out"):  # Name of the stdout files. These are present for each parameter set run.
                    file_count += 1

            LOG.info("Parameter count: {0}, File count: {1}".format(parameter_count, file_count))

            return file_count == parameter_count

        @staticmethod
        def check_csv(file_directory):
            # Check that the csv file either starts with "parameter_number" or "No sources"
            csv_path = os.path.join(file_directory, "data_collection.csv")

            with open(csv_path, 'r') as f:
                data = f.read()

                if data.startswith("No sources\n") or data.startswith("parameter_number"):
                    return True

            return False

        def validate(self, file_directory, result_id):
            if not self.check_output_files(file_directory, result_id):
                return "Issue with output files"

            elif not self.check_csv(file_directory):
                return "Issue with CSV"

            return None

    return InitValidator


def get_compare_validator(BaseValidator):

    class CompareValidator(BaseValidator):
        def validate(self, file1_directory, file2_directory):
            file1_path = os.path.join(file1_directory, 'data_collection.csv')
            file2_path = os.path.join(file2_directory, 'data_collection.csv')
            with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
                csv_compare_1 = CSVCompare(file1)
                csv_compare_2 = CSVCompare(file2)

            if not csv_compare_1 == csv_compare_2:
                return csv_compare_1.reason

            return None

    return CompareValidator
