"""Generates the parameters set for as specified, given the user specified arguments"""

import os
import sys
from astropy.io import fits
from database.database_support import CUBE, PARAMETER_FILE, RUN
from sqlalchemy import select, insert, and_
from logging_helper import config_logger

base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))

LOGGER = config_logger(__name__)
LOGGER.info('register_cube_mod.py')


def get_cube_names(cube_directory):
    LOGGER.debug('get_cube_names')
    """Return a list of the cubes that need registering for the current run
    :param cube_directory:
    :return:
    """
    cubes = os.listdir('{0}'.format(cube_directory))  # list of cubes in the current run
    return cubes


def get_cube_data(cube_file):
    LOGGER.debug('get_cube_data')
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


def update_cube_table(connection, cube_file, run_id):
    LOGGER.debug('update_cube_table')
    """Update the database for each cube
    :param connection:
    :param cube_file:
    :param run_id:
    :return:
    """

    transaction = connection.begin
    try:
        check = connection.execute(select([RUN]).where(RUN.c.run_id == run_id))
        result = check.fetchone()
        # check to see if run exists in database
        if not result:
            LOGGER.info('Adding new run_id to the db: ' + run_id)
            run = connection.execute(
                RUN.insert(),
                run_id=run_id
            )

        check = connection.execute(select([CUBE]).where(
            and_(CUBE.c.cube_name == cube_file,
                 CUBE.c.run_id == run_id)
        )
        )
        result = check.fetchone()
        if not result:
            data = get_cube_data(cube_file)
            cube = connection.execute(
                CUBE.insert(),
                cube_name=cube_file,
                progress=0,
                ra=data[0],
                declin=data[1],
                freq=data[2],
                run_id=run_id
            )
        else:
            print "Cube is already included in database for current run"
            return 1

    except Exception, e:
        LOGGER.error('Database issue when adding cubelets', exc_info=True)
        raise


def update_parameter_files(run_id, connection, parameter_file):
    LOGGER.debug('update_parameter_files')
    """Add parameter files to the database
    :param run_id
    :param connection
    :param parameter_file
    """
    transaction = connection.begin

    try:
        result = connection.execute(select([PARAMETER_FILE]).where(
            and_(
                PARAMETER_FILE.c.run_id == run_id,
                PARAMETER_FILE.c.parameter_file == parameter_file)
        )
        )

        row = result.fetchone()

        if not row:
            LOGGER.info('Adding new parameter file to the db: ' + parameter_file)
            con_result = connection.execute(
                PARAMETER_FILE.insert(),
                run_id=run_id,
                parameter_file=parameter_file
            )
        else:
            LOGGER.info("Parameter file already exists in database: " + parameter_file)
            return

    except Exception:
        LOGGER.error('Database issue when setting range values', exc_info=True)
        raise
