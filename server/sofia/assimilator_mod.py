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

import csv
import os
import tarfile

from utils.logger import config_logger
from sqlalchemy.exc import OperationalError
from sqlalchemy import select
from utils.amazon import get_file_upload_key
from utils import retry_on_exception, extract_tar, get_temp_directory, free_temp_directory
from . import PARAMETERS as RESULT_COLUMNS
from . import form_parameter_file_name

LOG = config_logger(__name__)


def get_assimilator(AssimilatorBase):

    class SofiaAssimilator(AssimilatorBase):

        def process_result(self, wu, result_file, cube_info):
            """
            :param wu:
            :param result_file:
            :param cube_info:
            :return:
            """

            LOG.info("Processing result {0}".format(result_file))

            try:
                if cube_info.cube['progress'] == 2:
                    LOG.info('Cube {0} already has results!'.format(cube_info.name))
                    return 0

                # Extract the result file
                extract_directory = get_temp_directory(result_file)
                extract_tar(result_file, extract_directory)

                self.store_data(wu.name, cube_info, extract_directory)

            except Exception as e:
                LOG.error("Error processing work unit: {0}".format(e.message))
                return 1  # try again later

            finally:
                # This checks if the folder even exists before trying to remove it.
                free_temp_directory(result_file)

            LOG.info("Completed result {0}".format(result_file))

            return 0

        def store_data(self, wu_name, cube_info, output_directory):
            """
            :param wu_name:
            :param cube_info:
            :param output_directory:
            :return:
            """

            RESULT = self.config['database']['RESULT']
            CUBE = self.config['database']['CUBE']
            PARAMETER_FILE = self.config['database']['PARAMETER_FILE']
            csv_file = os.path.join(output_directory, 'data_collection.csv')

            LOG.info("Storing data...")

            with open(csv_file) as open_csv_file:

                has_results = not open_csv_file.read().startswith("No sources")
                open_csv_file.seek(0)

                if has_results:
                    csv_reader = csv.DictReader(open_csv_file)

                    transaction = self.connection.begin()
                    try:
                        for row in csv_reader:

                            # The parameter_number row from the CSV refers to the number found in the parameter file name
                            # e.g. supercube_run_0_sofia.par
                            # We should form a full parameter file name here, and search the DB for its ID.
                            parameter_file_name = form_parameter_file_name(int(row['parameter_number']))
                            # Look up the parameter ID in the DB
                            parameter_entry = self.connection.execute(select([PARAMETER_FILE]).where(PARAMETER_FILE.c.parameter_file_name == parameter_file_name))
                            id = parameter_entry.fetchone()['parameter_id']

                            table_insert = {column: (row[column] if row[column] != "null" else None) for column in RESULT_COLUMNS if column in row}
                            table_insert["cube_id"] = cube_info.id
                            table_insert["parameter_id"] = int(id)
                            table_insert["run_id"] = cube_info.run_id
                            table_insert["workunit_name"] = wu_name

                            self.connection.execute(RESULT.insert(), **table_insert)

                        transaction.commit()
                        LOG.info('Successfully loaded work unit {0} in to the database'.format(wu_name))

                    except Exception as e:
                        LOG.error('Exception while loading CSV in to the database {0}'.format(e.message))
                        transaction.rollback()
                        return 1  # try again later
                else:
                    LOG.info("No sources in result.")

                retry_on_exception(lambda: (
                    self.connection.execute(CUBE.update().where(CUBE.c.cube_id == cube_info.id).values(progress=2))
                ), OperationalError, 1)  # This fails sometimes for some reason. Just retry it once

            # Queue files for upload
            upload_files = os.listdir(output_directory)
            LOG.info("Compressing {0} files for upload...".format(len(upload_files)))

            tarname = os.path.join(output_directory, "archive.tar.gz")
            with tarfile.open(tarname, 'w:gz') as tf:
                for upload_file in upload_files:
                    tf.add(os.path.join(output_directory, upload_file), upload_file)

            LOG.info("Adding tar file {0} to upload queue...".format(tarname))
            key = get_file_upload_key(self.config["APP_NAME"], wu_name, tarname)
            self.queue_file_upload(tarname, key)


    return SofiaAssimilator
