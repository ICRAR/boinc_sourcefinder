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
from sqlalchemy import create_engine, select, func

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

    def get_parameters(self, run_id, divisions, part):
        """
        Gets all parameters that need to be registered to the specified run id.
        Any parameters already registered are not included in this list.
        :param run_id:
        :param divisions:
        :param part:
        :return:
        """
        PARAMETER_FILE = self.config["database"]["PARAMETER_FILE"]
        PARAMETER_RUN = self.config["database"]["PARAMETER_RUN"]

        exists = set(int(item['parameter_id'])
                     for item
                     in self.connection.execute(select([PARAMETER_RUN.c.parameter_id]).where(PARAMETER_RUN.c.run_id == run_id)))

        parameter_ids = [p for p in self.connection.execute(select([PARAMETER_FILE.c.parameter_id]))]

        # Divide the total number of parameter files up in to segments, then pull out the segment we're going to use
        size = len(parameter_ids)
        division_size = size / divisions

        start = part * division_size
        end = start + division_size

        if part == divisions:
            end += size % divisions

        return [p for p in parameter_ids[start:end] if p not in exists]

    def register_parameters(self, run_id, parameter_ids):
        """
        Register all parameters in the parameter file table to the given run id
        :param run_id: The run ID to register parameters to
        :param parameter_ids: The parameter IDs to register
        :return:
        """
        PARAMETER_RUN = self.config["database"]["PARAMETER_FILE"]

        transaction = self.connection.begin()

        try:
            for parameter_id in parameter_ids:
                LOG.info("Adding parameter id {0}".format(parameter_id))
                self.connection.execute(PARAMETER_RUN.insert(), parameter_id=parameter_id, run_id=run_id)

            transaction.commit()
        except Exception as e:
            transaction.rollback()
            raise e

    def __call__(self, run_id, divisions, part, dont_insert):
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

            parameters = self.get_parameters(run_id, divisions, part)

            # Add each of the parameter files to this run ID in the parameter_run table
            if dont_insert:
                LOG.info("Will insert: {0}".format(parameters))
            else:
                self.register_parameters(run_id, parameters)
        except Exception:
            LOG.exception("Database exception")

            return 1
        finally:
            self.connection.close()

        return 0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=str, required=True, help='The name of the app to use.')
    parser.add_argument('--dont_insert', action='store_true', help="Don't perform inserts in to the DB", default=False)
    parser.add_argument('run_id', type=int, help='The run ID to register.')
    parser.add_argument('divisions', type=int, default=1, help='Number of categories to divide the parameters in to.')
    parser.add_argument('part', type=int, default=1, help='Which part of the divisions should be included in this run?')
    # e.g. 4 1 means "this run contains the first quarter of all parameters.
    args = vars(parser.parse_args())

    if args['part'] > args['divisions'] or args['part'] < 0:
        print "Invalid part. Must be lower than divisions and greater than 0."
        exit(1)

    return args

if __name__ == '__main__':
    arguments = parse_args()
    app_name = arguments['app']

    run_resister = RunRegister(get_config(app_name))

    exit(run_resister(arguments['run_id'], arguments['divisions'], arguments['part'], arguments['dont_insert']))
