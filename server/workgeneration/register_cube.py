"""Register a run of cubes for processing by populating the database"""

import argparse
import os
import sys

base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))

from utils.logging_helper import config_logger

# Assume the config file is good
from config import DB_LOGIN, DIR_CUBE, DIR_PARAM

from register_cube_mod import create_cube
from sqlalchemy.engine import create_engine
from sqlalchemy import select
from database.database_support import CUBE


LOGGER = config_logger(__name__)
LOGGER.info('Starting register_cube.py')
LOGGER.info('PYTHONPATH = {0}'.format(sys.path))

engine = create_engine(DB_LOGIN)


def parse_args():
    # Only one argument, which is the run ID
    parser = argparse.ArgumentParser()
    parser.add_argument('run_id', nargs=1, help='The run ID to register to')
    args = vars(parser.parse_args())

    return args['run_id'][0]


def main():

    run_id = parse_args()

    # Ensure everything is compressed in the cubes directory
    # Note: any files already compressed are not affected
    os.system('gzip {0}/*'.format(DIR_CUBE))

    # get a list of the cubes to be registered
    cubes = os.listdir(DIR_CUBE)  # list of cubes in the current run
    cubes.sort()

    connection = engine.connect()

    for cube in cubes:
        # check if it is actually one of the cubes
        if "askap" in cube and cube.endswith('.fits.gz'):  # Must have askap in the filename and end with .fits.gz
            LOGGER.info('Registering cube {0}'.format(cube))

            cube_path = os.path.join(DIR_CUBE, cube)

            try:
                create_cube(connection, cube_path, run_id)
            except Exception as e:
                LOGGER.exception('Database exception ')

    connection.close()

if __name__ == '__main__':
    main()
