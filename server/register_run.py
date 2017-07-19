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

"""
Register a new run in the database
"""
import argparse

from config import get_config
from utils.logger import config_logger
from sqlalchemy import create_engine, select

LOG = config_logger(__name__)


class RunRegister:
    def __init__(self, config):
        """
        Initialise the RunRegister
        :param config: The config for the application
        :return:
        """
        self.config = config
        self.engine = None
        self.connection = None

    def create_run_id(self, run_id):
        """
        Register the given run ID in the database
        :param run_id: The run ID to register
        :return:
        """
        RUN = self.config["database"]["RUN"]

        # Check to see if this run is already registered
        check = self.connection.execute(select([RUN]).where(RUN.c.run_id == run_id))
        result = check.fetchone()

        if not result:
            # The run is not registered already, so register it
            LOG.info('Adding new run_id to the db: {0}'.format(run_id))
            self.connection.execute(RUN.insert(), run_id=run_id)
        else:
            LOG.info('run_id {0} is already registered.'.format(run_id))

    def register_parameters(self, run_id):
        """
        Register all parameters in the parameter file table to the given run id
        :param run_id: The run ID to register parameters to
        :return:
        """
        PARAMETER_RUN = self.config["database"]["PARAMETER_RUN"]
        PARAMETER_FILE = self.config["database"]["PARAMETER_FILE"]

        # Check which parameters already exist for this run.
        exists = set()
        result = self.connection.execute(select([PARAMETER_RUN.c.parameter_id]).where(PARAMETER_RUN.c.run_id == run_id))
        for item in result:
            exists.add(int(item['parameter_id']))

        transaction = self.connection.begin()

        try:
            # We need to make an insertion here for every single parameter that exists in the parameter_files table
            ret = self.connection.execute(select([PARAMETER_FILE]))
            for row in ret:
                if not int(row['parameter_id']) in exists:  # only add this to the DB if it does not already exist
                    self.connection.execute(PARAMETER_RUN.insert(), parameter_id=int(row['parameter_id']), run_id=run_id)

            transaction.commit()
        except Exception as e:
            transaction.rollback()
            raise e


    def __call__(self, run_id):
        """
        Run the Run ID register
        :param run_id: The run ID to register
        :return:
        """
        self.engine = create_engine(self.config["DB_LOGIN"])

        if run_id < 0:
            LOG.info('Invalid run ID specified, please specify a run id greater than 0')
            return

        # Work out which parameter files to add to the db under this run ID.
        self.connection = self.engine.connect()
        try:
            # Add this run ID
            self.create_run_id(run_id)

            # Add each of the parameter files to this run ID in the parameter_run table
            self.register_parameters(run_id)
        except Exception:
            LOG.exception("Database exception")

            return 1
        finally:
            self.connection.close()

        return 0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=str, required=True, help='The name of the app to use.')
    parser.add_argument('run_id', type=int, help='The run ID to register.')
    args = vars(parser.parse_args())

    return args

if __name__ == '__main__':
    arguments = parse_args()
    app_name = arguments['app']

    cube_register = RunRegister(get_config(app_name))

    exit(cube_register(arguments['run_id']))
