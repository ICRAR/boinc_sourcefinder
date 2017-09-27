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

from utils.logger import config_logger
from sqlalchemy.exc import OperationalError
from utils.amazon import S3Helper, get_file_upload_key
from utils import retry_on_exception, extract_tar, get_temp_directory, free_temp_directory

LOG = config_logger(__name__)

COMPLETED_WU_PATH = '/home/ec2-user/completed_workunits'
COMPLETED_RESULT_PATH = '/home/ec2-user/completed_results'


def get_assimilator(AssimilatorBase):

    class DuchampAssimilator(AssimilatorBase):

        def process_result(self, wu, result_file, cube_info):
            """

            :param wu:
            :param result_file:
            :param cube_info:
            :return:
            """
            LOG.info("Processing result {0}", result_file)

            try:
                if cube_info.cube['progress'] == 2:
                    LOG.info('Cube {0} already has results!'.format(cube_info.name))
                    return 0

                # Extract the result file
                extract_directory = get_temp_directory(result_file)
                extract_tar(result_file, extract_directory)
                output_directory = os.path.join(extract_directory, 'outputs')

                self.store_data(wu.name, cube_info, output_directory)

            except Exception as e:
                LOG.error("Error processing work unit: {0}\n".format(e.message))
                return 1  # try again later

            finally:
                free_temp_directory(result_file)

            return 0

        def store_data(self, wu_name, cube_info, output_directory):
            RESULT = self.config['database']['RESULT']
            CUBE = self.config['database']['CUBE']
            csv_file = os.path.join(output_directory, 'data_collection.csv')

            with open(csv_file) as open_csv_file:
                csv_reader = csv.DictReader(open_csv_file)

                for row in csv_reader:
                    transaction = self.connection.begin()
                    try:
                        self.connection.execute(
                                RESULT.insert(),
                                cube_id=cube_info.id,
                                parameter_id=int(row['ParameterNumber']),
                                run_id=cube_info.run_id,
                                RA=row['RA'],
                                DEC=row['DEC'],
                                freq=row['freq'],
                                w_50=row['w_50'],
                                w_20=row['w_20'],
                                w_FREQ=row['w_FREQ'],
                                F_int=row['F_int'],
                                F_tot=row['F_tot'],
                                F_peak=row['F_peak'],
                                Nvoxel=row['Nvoxel'],
                                Nchan=row['Nchan'],
                                Nspatpix=row['Nspatpix'],
                                workunit_name=wu_name  # Reference in to the boinc DB and in to the s3 file system.
                        )
                        transaction.commit()
                        LOG.info('Successfully loaded work unit {0} in to the database'.format(wu_name))
                    except Exception as e:
                        LOG.error('Exception while loading CSV in to the database {0}'.format(e.message))
                        transaction.rollback()
                        return 1  # try again later

                retry_on_exception(lambda: (
                    self.connection.execute(CUBE.update().where(CUBE.c.cube_id == cube_info.id).values(progress=2))
                ), OperationalError, 1)  # This fails sometimes for some reason. Just retry it once

            # Copy everything in to an S3 bucket.
            for upload_file in os.listdir(output_directory):
                s3 = S3Helper(self.config["S3_BUCKET_NAME"])

                path = os.path.join(output_directory, upload_file)
                key = get_file_upload_key(self.config["APP_NAME"], wu_name, upload_file)

                s3.file_upload(path, key)

    return DuchampAssimilator
