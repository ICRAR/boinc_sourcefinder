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

from boinc_sourcefinder.server.config import get_config

# Populates the visualisation database with values from the specified app's database
# What this needs to do:
#   Create the app entry for this app if it doesn't exist in the visualisation DB.
#   Get a list of all cubes in the cubes folder
#   Get a list of the results for those cubes. Only select results in the specified run ID.
#   For each result, make a Source entry corresponding to that result
#       If the cube for this result isn't in the DB, add it.
#       If the slice for this result isn't in the DB, add it.
#       Extract the slice image from the fits file for this cube and move it to the uploading directory.
#       Create the source entry.
#       Work out the list of people (usernames) that contributed to this source.
#           If any of those people don't exist in this DB, add them
#           Add the 'found_by' references that link this source to each of these people.
# Source should be ready for plotting.

"""
Cubes folder - This folder contains all of the cubes that we have access to right now. The system will
               look for results only for the cubes in this folder.
Image upload folder - This folder contains all of the images we're going to upload to S3. Each image is
                      a slice out of a cube.
"""
import argparse
from  import get_config
from config import read_config
from sqlalchemy.engine import create_engine

class VisualisationPopulator:
    def __init__(self, config, config_vis):
        self.config = config
        self.config_vis = config_vis

        self.engine_vis = create_engine()  # Engine to connect to visualisation database
        self.connection_vis = None  # Connection to visualisation database

        self.engine = create_engine(self.config["DB_LOGIN"])  # Engine to connect to Sourcefinder database
        self.connection = None  # Connection to Sourcefinder database

    def connect(self):
        """
        Connects to the Sourcefinder and Visualisation databases
        :return:
        """
        self.connection =

    def create_app(self, app_name):
        """
        Creates an app with the specified name and returns its app ID in the visualisation database.
        If an app with the specified name already exists, it returns its app ID.
        :param app_name: The app name to add.
        :return: The app ID of the newly created app, or the pre-existing app
        """


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=str, required=True, help='The name of the app to use.')
    parser.add_argument('--run_id', type=int, required=True, help='The run ID to get the data from.')
    return vars(parser.parse_args())

if __name__ == "__main__":
    arguments = parse_args()
    app_name = arguments['app']

    config_vis = read_config("visualisation.settings")

    populator = VisualisationPopulator(config_vis)