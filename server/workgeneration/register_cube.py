"""Register a run of cubes for processing by populating the database"""

import argparse
import os
import sys
# from config import DB_LOGIN (For local testing, just defining a general login instead
from logging_helper import config_logger

base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))

LOGGER = config_logger(__name__)
LOGGER.info('Starting work registration.py')
LOGGER.info('PYTHONPATH = {0}'.format(sys.path))

from register_cube_mod import get_cube_names, update_cube_table, update_parameter_files
from sqlalchemy.engine import create_engine


parser = argparse.ArgumentParser()
parser.add_argument('cube_directory', nargs=1, help='The directory that all the new workunits are stored')
parser.add_argument('run_id', nargs=1, help='The id of the current run')
parser.add_argument('parameter_directory', nargs=1, help='The directory of the parameter files')
parser.add_argument('--db_login', nargs='?', type=str, help='the login details for the database')

args = vars(parser.parse_args())
WORKING_DIRECTORY = args['cube_directory'][0]
RUN_ID = args['run_id'][0]
PARAMETER_DIRECTORY = args['parameter_directory'][0]
DB_LOGIN = args['db_login']

LOGGER.info('DB_LOGIN is: {0}'.format(DB_LOGIN))

# TODO initially hard coded, will add to fabric files later on
if DB_LOGIN is None:
    DB_LOGIN = 'mysql://' + 'root' + ':' + '@' + 'localhost' + '/' + 'sourcefinder'

ENGINE = create_engine(DB_LOGIN)
connection = ENGINE.connect()

# get a list of the cubes to be registered
cubes = get_cube_names(WORKING_DIRECTORY)
# get run_id into numerical form
for cube in cubes:
    # check if it is actually one of the cubes
    if "askap" in cube:
        LOGGER.info('The file is ' + cube)
        LOGGER.info('Working directory is ' + WORKING_DIRECTORY + cube)
        check = update_cube_table(connection, WORKING_DIRECTORY + cube, RUN_ID)
        if check == 1:
            LOGGER.info("Cube already exists in db for run: " + RUN_ID)


# get a list of all the parameter files in the parameter directory
parameter_list = os.listdir(PARAMETER_DIRECTORY)
for param_file in parameter_list:
    # check if it is actually one of the parameter files
    if "supercube" in param_file:
        LOGGER.info('The file is ' + param_file)
        check = update_parameter_files(RUN_ID, connection, param_file)

connection.close()