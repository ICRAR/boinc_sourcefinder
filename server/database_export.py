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
Export all data from the Sourcefinder databases in to one, combined database.
"""

import os, sys
from config import get_config
from utils.logger import config_logger
from config.database_results import result_database_def as result_database
from sqlalchemy import create_engine, select

LOG = config_logger(__name__)


def convert_result_duchamp(result):
    """
    Takes a result from the duchamp database and converts it to one
    that's compatible with the result database.
    :param result: The database row from Duchamp.
    :return: A dictionary containing the values suitable for the result database.
    """
    return {
        "ra": result["RA"],
        "dec": result["DEC"],
        "freq": result["freq"],
        "w_20": result["w_20"],
        "w_50": result["w_50"],
        "w_freq": result["w_FREQ"],
        "f_int": result["F_int"],
        "f_tot": result["F_tot"],
        "f_peak": result["F_peak"],
        "n_voxel": result["Nvoxel"],
        "n_chan": result["Nchan"],
        "n_spatpix": result["Nspatpix"]
    }


def convert_result_sofia(result):
    """
    Takes a result from the sofia database and converts it to one
    that's compatible with the result database.
    :param result: The database row from SoFiA.
    :return: A dictionary containing the values suitable for the result database.
    """
    return {
        "ra": result["ra"],
        "dec": result["dec"],
        "freq": result["freq"],
        "w_20": result["w20"],
        "w_50": result["w50"],
        "w_freq": result["frew"],
        "f_int": result["f_int"],
        "f_tot": None,
        "f_peak": result["f_peak"],
        "n_voxel": None,
        "n_chan": result["n_chan"],
        "n_spatpix": result["n_pix"] # I think this mapping is correct.
    }


class DatabaseExporter:
    EXPORT_RUNID_MAP = {
        "sofia": {
            15: "10mb",  # All parameters in one
            16: "10mb",  # Split in to 16 -> 19
            17: "10mb",
            18: "10mb",
            19: "10mb"
        },

        "duchamp": {
            10: "10mb",
            11: "10mb"
        }
    }

    def __init__(self, config, build_result_fn, results_login):
        self.config = config
        self.build_result = build_result_fn

        self.engine = None
        self.connection = None

        self.results_login = results_login
        self.results_engine = None
        self.results_connection = None

    def _populate_parameters(self):
        path = self.config["DIR_PARAM"]
        PARAMETER_FILE = self.config["database"]["PARAMETER_FILE"]
        PARAMETERS = result_database["PARAMETERS"]

        # Set of parameters in the app's db
        parameters = self.connection.execute(select([PARAMETER_FILE]))
        # Set of parameters that already exist in the results DB
        results_parameters = set(item["name"] for item in self.results_connection.execute(select([PARAMETERS])))

        # Go through each parameter in the app's db and add it to
        # the results DB if it doesn't already exist there
        for parameter in parameters:
            try:
                name = parameter["parameter_file_name"]
                if name not in results_parameters:
                    # Get the contents of this file
                    with open(os.path.join(path, name), 'w') as f:
                        contents = f.read()

                    self.results_connection.execute(PARAMETERS.insert(),
                                                    name=name,
                                                    text=contents)
            except Exception as e:
                LOG.exception("Exception while populating parameter file {0}".format(parameter["parameter_file_name"]))

    def _populate_cubelets(self):
        pass

    def _populate_sources(self):
        pass

    def __call__(self):
        self.engine = create_engine(self.config["DB_LOGIN"])
        self.connection = self.engine.connect()

        self.results_engine = create_engine(self.results_login)
        self.results_connection = self.results_engine.connect()

        # Populate parameters for each category.
        self._populate_parameters()

        # Populate cubelets for each category.
        self._populate_cubelets()

        # Populate sources for each category.
        self._populate_sources()

if __name__ == "__main__":
    # Needs to get results from both the sourcefinder and sourcefinder_sofia database
    # and collect it in to one.
    db_login = sys.argv[1]

    exporter_duchamp = DatabaseExporter(get_config("duchamp"), convert_result_duchamp, db_login)
    exporter_sofia = DatabaseExporter(get_config("sofia"), convert_result_sofia, db_login)

    exporter_duchamp()




