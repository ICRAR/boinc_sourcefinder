"""Register a run of cubes for processing by populating the database"""

import argparse
import os
import sys

base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))

from utils.logging_helper import config_logger

# Assume the config file is good
from config import DB_LOGIN, DIR_CUBE, DIR_PARAM

from register_cube_mod import update_cube_table, update_parameter_files
from sqlalchemy.engine import create_engine


LOGGER = config_logger(__name__)
LOGGER.info('Starting register_cube.py')
LOGGER.info('PYTHONPATH = {0}'.format(sys.path))

# Get command line args
parser = argparse.ArgumentParser()
parser.add_argument('run_id', nargs=1, help='The id of the current run')
args = vars(parser.parse_args())

# Set local variables based on imported config and command line
WORKING_DIRECTORY = DIR_CUBE
PARAMETER_DIRECTORY = DIR_PARAM
RUN_ID = args['run_id'][0]

ENGINE = create_engine(DB_LOGIN)
connection = ENGINE.connect()

# Compress everything in the cubes directory
# Note: any files already compressed are not affected
os.system('gzip {0}/*'.format(WORKING_DIRECTORY))

# get a list of the cubes to be registered
cubes = os.listdir(WORKING_DIRECTORY)  # list of cubes in the current run
cubes.sort()
LOGGER.info('Cube names are {0}'.format(cubes))

for cube in cubes:
    # check if it is actually one of the cubes
    if "askap" in cube:
        LOGGER.info('The file is ' + cube)

        abs_dir = os.path.abspath('{0}/{1}'.format(WORKING_DIRECTORY, cube))
        LOGGER.info('Working directory is {0}'.format(abs_dir))

        filename = os.path.basename(abs_dir)
        p = filename.find('.')
        filename = filename[:p]

        check = update_cube_table(connection, filename, RUN_ID)

        if check == 1:
            LOGGER.info("{0} already exists in db for run: ".format(cube) + RUN_ID)

# get a list of all the parameter files in the parameter directory
parameter_list = os.listdir('{0}/parameter_files_{1}'.format(PARAMETER_DIRECTORY, RUN_ID))
parameter_list.sort()
LOGGER.info('Parameter names are {0}'.format(parameter_list))
for param_file in parameter_list:
    # check if it is actually one of the parameter files
    if "supercube" in param_file:
        LOGGER.info('The file is ' + param_file)
        check = update_parameter_files(RUN_ID, connection, param_file)

connection.close()
