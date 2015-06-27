"""Generates the parameters set for as specified, given the user specified arguments"""

import os
from astropy.io import fits
from database.database_support import CUBE, PARAMATER, PARAMATER_RANGE, RUN
from sqlalchemy import select, insert
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
    """Update the database for each cube
    :param connection:
    :param cube_file:
    :param run_id:
    :return:
    """

    transaction = connection.begin
    # TODO put check for run_id
    try:
        run = connection.execute(
            RUN.insert(),
            run_id=run_id
        )

    except Exception:
        transaction.rollback()
        raise

    data = get_cube_data(cube_file)
    transaction = connection.begin()
    try:
        cube = connection.execute(
            CUBE.insert(),
            cube_name=cube_file,
            ra=data[0],
            declin=data[1],
            freq=data[2],
            run_id=run_id
        )
        LOGGER.debug(cube)
        transaction.commit()

    except Exception:
        transaction.rollback()
        raise


def set_ranges(run_id, connection, parameter, parameter_string):
    transaction = connection.begin
    try:
        result = connection.execute(select([PARAMATER]))
        row = result.fetchone()

        # The initial, base case where there is nothing in the paramater table
        if row is None:
            connection.execute(
                PARAMATER.insert(),
                parameter_name=parameter
            )
        else:
            print row
        # TODO work on the other cases - e.g. if it isn't the first, but doesn't exist in the table etc

        param_id = result.inserted_primary_key[0]
        print param_id

        # test range to determine if the run_id has been used yet
        run = connection.execute(select([PARAMATER_RANGE]).where(PARAMATER_RANGE.c.run_id == run_id))
        row2 = run.fetchone()
        if row2 is None:
            i = PARAMATER_RANGE.insert()
            i.execute(
                parameter_id=param_id,
                parameter_string=parameter_string,
                run_id=run_id
            )

        transaction.comit()

    except Exception:
        transaction.rollback()
        raise
