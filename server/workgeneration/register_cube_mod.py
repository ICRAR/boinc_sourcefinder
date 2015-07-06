"""Generates the parameters set for as specified, given the user specified arguments"""

import os
from astropy.io import fits
from database.database_support import CUBE, PARAMATER, PARAMATER_RANGE, RUN
from sqlalchemy import select, insert, and_
from logging_helper import LOGGER

LOGGER.info('register_cube_mod.py')


def get_cube_names(cube_directory):
    LOGGER.debug('get_cube_names')
    """Return a list of the cubes that need registering for the current run
    :param cube_directory:
    :return:
    """
    directory = os.listdir('{0}.'.format(cube_directory))  # list of cubes in the current run
    return directory


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
            LOGGER.info('Adding new run_id to the db: ' + run_id[0])
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
                ra=data[0],
                declin=data[1],
                freq=data[2],
                run_id=run_id
            )
        else:
            print "Cube is already included in database for current run"
            return 1

    except Exception:
        raise


def set_ranges(run_id, connection, parameter, parameter_string):
    LOGGER.debug('set_ranges')
    """Set the ranges for each parameter
    :param run_id
    :param connection
    :param parameter
    :param parameter_string
    """

    transaction = connection.begin
    try:
        result = connection.execute(select([PARAMATER]).where(PARAMATER.c.parameter_name == parameter))
        row = result.fetchone()

        if not row:
            LOGGER.info('Adding new parameter to the db: ' + parameter)
            con_result = connection.execute(
                PARAMATER.insert(),
                parameter_name=parameter
            )
        else:
            LOGGER.info("Parameter already exists in database: " + parameter)
            return

        param_id = con_result.inserted_primary_key[0]
        LOGGER.info('Parameter: ' + parameter + 'has ID: ' + param_id)
        run = connection.execute(select([PARAMATER_RANGE]).where(
            and_(
                PARAMATER_RANGE.c.run_id == run_id,
                PARAMATER_RANGE.c.parameter_id == param_id)
        )
        )

        row = run.fetchone()
        if not row:
            con_result = connection.execute(
                PARAMATER_RANGE.insert(),
                parameter_id=param_id,
                parameter_string=parameter_string,
                run_id=run_id
            )
        else:
            LOGGER.info("Parameter value has already been added for this parameter: " + parameter)
            return

    except Exception:
        raise
