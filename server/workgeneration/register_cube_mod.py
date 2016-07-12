"""Generates the parameters set for as specified, given the user specified arguments"""

import os
import sys

base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))

from astropy.io import fits
from sqlalchemy import select, and_

from database.database_support import CUBE, PARAMETER_FILE, RUN
from utils.logging_helper import config_logger


LOGGER = config_logger(__name__)


def get_cube_data(cube_file):
    """Retrieve ra,dec,freqencey data from the .fits file
    :param cube_file:
    :return data_list:
    """

    hdulist = fits.open(cube_file)
    LOGGER.debug(hdulist[0].header[20])
    LOGGER.debug(hdulist[0].header[21])
    LOGGER.debug(hdulist[0].header[17])
    data_list = [hdulist[0].header[20], hdulist[0].header[21], hdulist[0].header[17]]
    return data_list


def create_cube(connection, cube_file, run_id):
    """
    Update the database for each cube

    :param connection:
    :param cube_file:
    :param run_id:
    :return:
    """

    # Check to see if this cube already registered

    filename = os.path.basename(cube_file)
    p = filename.find('.')
    filename = filename[:p]  # Strip off that .fits.gz

    check = connection.execute(select([CUBE]).where(and_(CUBE.c.cube_name == filename, CUBE.c.run_id == run_id)))
    result = check.fetchone()

    if not result:
        data = get_cube_data(cube_file)  # Grab the cube data from the cube file.

        transaction = connection.begin()
        try:
            connection.execute(
                CUBE.insert(),
                cube_name=filename,
                progress=0,
                ra=data[0],
                declin=data[1],
                freq=data[2],
                run_id=run_id)

            transaction.commit()

            LOGGER.info('Cube successfully registered')
            return True

        except Exception as e:
            transaction.rollback()  # Need to do the rollback here, then pass the exception in to the main code
            raise e
    else:
        # The cube is registered already
        LOGGER.info('Cube already registered in database')
        return False