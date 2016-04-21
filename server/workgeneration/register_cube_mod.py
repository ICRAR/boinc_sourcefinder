"""Generates the parameters set for as specified, given the user specified arguments"""

import os
import sys

from astropy.io import fits
from sqlalchemy import select, and_

from database.database_support import CUBE, PARAMETER_FILE, RUN
from utils.logging_helper import config_logger

base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))

LOGGER = config_logger(__name__)
#LOGGER.info('register_cube_mod.py')


def get_cube_data(cube_file):
    """Retrieve ra,dec,freqencey data from the .fits file
    :param cube_file:
    :return data_list:
    """

    # LOGGER.debug('get_cube_data')

    hdulist = fits.open(cube_file)
    LOGGER.debug(hdulist[0].header[20])
    LOGGER.debug(hdulist[0].header[21])
    LOGGER.debug(hdulist[0].header[17])
    data_list = [hdulist[0].header[20], hdulist[0].header[21], hdulist[0].header[17]]
    return data_list


def update_cube_table(connection, cube_file, run_id):
    """

    Update the database for each cube
        :param connection:
    :param cube_file:
    :param run_id:
    :return:
    """
    #LOGGER.debug('update_cube_table')

    transaction = connection.begin()

    try:
        # Check to see if this run is already registered
        check = connection.execute(select([RUN]).where(RUN.c.run_id == run_id))
        result = check.fetchone()

        if not result:
            # The run is not registered already, so register it
            LOGGER.info('Adding new run_id to the db: ' + run_id)
            connection.execute(
                RUN.insert(),
                run_id=run_id)

        # Check to see if this cube already registered?
        check = connection.execute(select([CUBE]).where(and_(CUBE.c.cube_name == cube_file, CUBE.c.run_id == run_id)))
        result = check.fetchone()

        if not result:
            # The cube is not registered already, so register it
            data = get_cube_data(cube_file)

            # Only register the cube with the actual name of the file. No .fits.gz or path.
            filename = os.path.basename(cube_file)
            p = filename.find('.')
            filename = filename[:p]

            connection.execute(
                CUBE.insert(),
                cube_name=filename,
                progress=0,
                ra=data[0],
                declin=data[1],
                freq=data[2],
                run_id=run_id)
        else:
            # The cube is registered already
            transaction.rollback()
            return 1

    except Exception:
        LOGGER.error('Database issue when adding cubelets', exc_info=True)
        transaction.rollback()
        raise

    transaction.commit()


def update_parameter_files(run_id, connection, parameter_file):
    """Add parameter files to the database
    :param run_id
    :param connection
    :param parameter_file
    """
    LOGGER.debug('update_parameter_files')

    transaction = connection.begin()

    try:
        check = connection.execute(select([PARAMETER_FILE]).where(
            and_(PARAMETER_FILE.c.run_id == run_id,
                 PARAMETER_FILE.c.parameter_file == parameter_file)))
        result = check.fetchone()

        if not result:
            LOGGER.info('Adding new parameter file to the db: ' + parameter_file)
            connection.execute(
                PARAMETER_FILE.insert(),
                run_id=run_id,
                parameter_file=parameter_file)
        else:
            LOGGER.info("Parameter file already exists in database: " + parameter_file)
            transaction.rollback()
            return

    except Exception:
        LOGGER.error('Database issue when setting range values', exc_info=True)
        transaction.rollback()
        raise

    transaction.commit()
