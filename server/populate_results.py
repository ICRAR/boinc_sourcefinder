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
Needs to open the Duchamp and SoFiA database.

duchamp runs: 10, 11

args:
    app (app DB we'll be loading from)
    category (category in the results DB we'll be placing these results into)
    runs (runs we'll be using from that app)
"""

import os
import argparse

from config import get_config
from config.database_results import result_database_def as results_db
from utils import module_import
from sqlalchemy import create_engine, select, distinct

MODULE = "populate_results_mod"
PARAMETERS = results_db["PARAMETERS"]
CATEGORY = results_db["CATEGORY"]
CUBELET = results_db["CUBELET"]


class ResultsPopulator:
    def __init__(self, config, args):
        self.config = config
        self.category = args["category"]
        self.run_ids = args["run_ids"]

        self.connection = None
        self.connection_result = None
        self.category_id = None

        pass

    def _load_parameter_files(self):
        """
        Get all the parameter files registered for this app (unique, don't put in duplicates).
        Load unique versions of each in to the results database.
        :return:
        """
        PARAMETER_FILE = self.config["database"]["PARAMETER_FILE"]

        print "Loading parameters"

        for f in self.connection.execute(select([distinct(PARAMETER_FILE.c.parameter_file_name)])):
            # Insert parameters that don't already exist in the results DB.
            filename = f['parameter_file_name']
            path = os.path.join(self.config["DIR_PARAM"], filename)

            with open(path, 'r') as parameter_file:
                data = parameter_file.read()

            if self.connection_result.execute(select([PARAMETERS]).where(PARAMETERS.c.name == filename)).fetchone() is None:
                print "Adding parameter {0} to database. Size: {1}".format(filename, len(data))
                self.connection_result.execute(PARAMETERS.insert(), name=filename, category_id=self.category_id, text=data)

    def _load_cubes(self):
        """
        Get all cubes in the specified runs that have a progress of 2. (Completed cubes)
        Load each in to the results database.
        :return:
        """
        CUBE = self.config["database"]["CUBE"]

        print "Loading cubes"

        for r in self.run_ids:
            print "Run ID: {0}".format(r)

            for c in self.connection.execute(select([CUBE]).where(CUBE.c.run_id == r and CUBE.c.progress == 2)):
                # These are all cubes that are within the specified run IDs and have been completed
                name = c["cube_name"]

                if self.connection_result.execute(select([CUBELET]).where(CUBELET.c.name == name)).fetchone() is None:
                    print "Adding cube {0} to database.".format(name)
                    self.connection_result.execute(CUBELET.insert(), name=name, category_id=self.category_id, ra=c["ra"], dec=c["declin"], freq=c["freq"])

    def _load_results(self):
        """
        Get all results for cubes in the specified runs that have a progress of 2. (Results for cubes).
        Load each in to the results database.
        """
        pass

    def __call__(self):

        engine = create_engine(self.config['DB_LOGIN'])
        engine_result = create_engine(self.config["BASE_DB_LOGIN"] + 'sourcefinder_results')
        self.connection = engine.connect()
        self.connection_result = engine_result.connect()

        category = self.connection_result.execute(select([CATEGORY]).where(CATEGORY.c.name == self.category)).fetchone()

        if category is None:
            raise Exception('Invalid category provided.')

        self.category_id = category["id"]

        print "Run IDs: {0}".format(self.run_ids)

        self._load_parameter_files()
        self._load_cubes()
        self._load_results()



def parse_args():
    """
    Parse arguments for the program.
    :return: The arguments for the program.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=str, required=True, help='The name of the app to read data from.')
    parser.add_argument('--category', type=str, help='The output category to import data to.')
    parser.add_argument('--run_ids', type=int, nargs="*", help='The run IDs to get data for.')
    args = vars(parser.parse_args())

    return args


if __name__ == "__main__":
    arguments = parse_args()
    app_name = arguments['app']

    mod = module_import(MODULE, app_name)

    # Pass the base class to the module and allow it to produce a subclassed assimilator
    DerivedPopulator = mod.get_populator(ResultsPopulator)
    populator = DerivedPopulator(get_config(app_name), arguments)

    exit(populator())
