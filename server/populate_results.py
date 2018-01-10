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
SOURCE = results_db["SOURCE"]

class ResultsPopulator:
    def __init__(self, config, args):
        self.config = config
        self.category = args["category"]
        self.run_ids = args["run_ids"]

        self.connection = None
        self.connection_result = None
        self.category_id = None

        pass

    def _get_result_parameter_id(self, parameter_id):
        """
        Convert this parameter ID, from the non-result database, to a parameter ID from the result database.
        :param parameter_id:
        :return:
        """
        PARAMETER_FILE = self.config["database"]["PARAMETER_FILE"]

        name = self.connection.execute(select([PARAMETER_FILE]).where(PARAMETER_FILE.c.parameter_id == parameter_id)).first()["parameter_file_name"]
        return self.connection_result.execute(select([PARAMETERS]).where(PARAMETERS.c.name == name)).first()["id"]


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

        for run_id in self.run_ids:
            print "Run ID: {0}".format(run_id)

            for cube in self.connection.execute(select([CUBE]).where(CUBE.c.run_id == run_id and CUBE.c.progress == 2)):
                # These are all cubes that are within the specified run IDs and have been completed
                name = cube["cube_name"]

                cube_insert = {
                    "name": name,
                    "category_id": self.category_id,
                    "ra": cube["ra"],
                    "dec": cube["declin"],
                    "freq": cube["freq"]
                }

                existing_cube = self.connection_result.execute(select([CUBELET]).where(CUBELET.c.name == name)).fetchone()

                if existing_cube is None:
                    print "Adding cube {0} to database.".format(name)
                    cube_insert["id"] = self.connection_result.execute(CUBELET.insert(), cube_insert)
                else:
                    cube_insert["id"] = existing_cube["id"]

                self._load_results(cube["cube_id"], cube_insert)

    def _load_results(self, original_cube_id, cube):
        """
        Get all results for cubes in the specified runs that have a progress of 2. (Results for cubes).
        Load each in to the results database.
        """
        RESULT = self.config["database"]["RESULT"]
        cube_id = cube["id"]

        print "Loading results for {0}".format(cube["name"])

        for result in self.connection.execute(select([RESULT]).where(RESULT.c.cube_id == original_cube_id)):
            # Get the parameters associated with this result
            try:
                result_parameter_id = self._get_result_parameter_id(result["parameter_id"])

                print "Loading result {0}".format(result["result_id"])

                if self.connection_result.execute(select([SOURCE]).where(SOURCE.c.original_id == result["result_id"])) is None:
                    self.connection_result.execute(SOURCE.insert(),
                                                   cubelet_id=cube_id,
                                                   parameters_id=result_parameter_id,
                                                   original_id=result["result_id"],
                                                   ra=result["RA"],
                                                   dec=result["DEC"],
                                                   freq=result["freq"],
                                                   w_20=result["w_20"],
                                                   w_50=result["w_50"],
                                                   w_freq=result["w_FREQ"],
                                                   f_int=result["F_int"],
                                                   f_tot=result["F_tot"],
                                                   f_peak=result["F_peak"],
                                                   n_voxel=result["Nvoxel"],
                                                   n_chan=result["Nchan"],
                                                   n_spatpix=result["Nspatpix"])
            except Exception as e:
                print "Error loading result {0}: {1}".format(result["result_id"], e.message)

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
