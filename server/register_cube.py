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
Register all cubes in the cubes directory in the database
"""
import os
import argparse
import glob

from config import get_config
from utils.logger import config_logger
from utils import make_path
from sqlalchemy.engine import create_engine
from sqlalchemy import select, and_
from astropy.io import fits

LOG = config_logger(__name__)


class CubeRegister:
    def __init__(self, config):
        self.config = config
        self.run_id = None

    @staticmethod
    def get_cube_data(cube_file):
        """Retrieve ra,dec,freqencey data from the .fits file
        :param cube_file:
        :return data_list:
        """

        hdulist = fits.open(cube_file)
        LOG.debug(hdulist[0].header[20])
        LOG.debug(hdulist[0].header[21])
        LOG.debug(hdulist[0].header[17])
        data_list = [hdulist[0].header[20], hdulist[0].header[21], hdulist[0].header[17]]
        return data_list

    def create_cube(self, cube_file):
        """
        Update the database for each cube

        :param cube_file:
        :return:
        """
        CUBE = self.config["database"]["CUBE"]
        engine = create_engine(self.config["DB_LOGIN"])
        connection = engine.connect()

        try:
            filename = os.path.basename(cube_file)
            p = filename.find('.')
            filename = filename[:p]  # Strip off that .fits.gz

            check = connection.execute(select([CUBE]).where(and_(CUBE.c.cube_name == filename, CUBE.c.run_id == self.run_id)))
            result = check.fetchone()

            if not result:
                data = self.get_cube_data(cube_file)  # Grab the cube data from the cube file.

                connection.execute(
                        CUBE.insert(),
                        cube_name=filename,
                        progress=0,
                        ra=data[0],
                        declin=data[1],
                        freq=data[2],
                        run_id=self.run_id)

                LOG.info('Cube {0} successfully registered'.format(filename))

            else:
                # The cube is registered already
                LOG.info('Cube {0} already registered in database'.format(filename))
        finally:
            connection.close()

    def __call__(self, run_id, glob_str):
        self.run_id = run_id
        cube_dir = self.config["DIR_CUBE"]

        make_path(cube_dir)

        # Ensure everything is compressed in the cubes directory
        # Note: any files already compressed are not affected
        os.system('gzip {0}/*'.format(cube_dir))

        # get a list of the cubes to be registered
        if glob_str is not None:
            cubes = glob.iglob(cube_dir + glob_str)
        else:
            cubes = os.listdir(cube_dir)

        try:
            for cube in sorted(cubes):
                cube = os.path.basename(cube)
                # check if it is actually one of the cubes
                if "askap" in cube and cube.endswith('.fits.gz'):  # Must have askap in the filename and end with .fits.gz
                    cube_path = os.path.join(cube_dir, cube)
                    self.create_cube(cube_path)
        except Exception:
            LOG.exception('Database exception')

            return 1

        return 0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=str, required=True, help='The name of the app to use.')
    parser.add_argument('--glob', type=str, required=False, default=None, help='A glob string to use to specify which cubes to process.')
    parser.add_argument('run_id', type=int, help='The run ID to register to.')
    args = vars(parser.parse_args())

    return args

if __name__ == '__main__':
    arguments = parse_args()
    app_name = arguments['app']

    cube_register = CubeRegister(get_config(app_name))

    exit(cube_register(arguments['run_id'], arguments['glob']))
