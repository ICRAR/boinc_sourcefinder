# Work generator used to create workunits

import argparse
import os
import shutil
import sys

base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))

from utils.logging_helper import config_logger

from config import  BOINC_DB_LOGIN, DB_LOGIN, WG_THRESHOLD, DIR_BOINC_PROJECT_PATH, DIR_PARAM

sys.path.append(DIR_BOINC_PROJECT_PATH) # for pyboinc

from sqlalchemy.engine import create_engine
from sqlalchemy import select, func, update
import py_boinc
from database.boinc_database_support import RESULT
from Boinc import configxml
from database.database_support import CUBE
from work_generator_mod import get_download_dir, create_workunit, get_cube_path, get_parameter_files

LOGGER = config_logger(__name__)
LOGGER.info('Starting work generation')

ENGINE = create_engine(DB_LOGIN)
connection = ENGINE.connect()

# Generate work for every cube in the database that has progress set to 0, regardless of the run ID.


def parse_args():
    # Only one argument, which is the run ID
    parser = argparse.ArgumentParser()
    parser.add_argument('run_id', nargs='?', help='The run ID to register to', default=None)
    args = vars(parser.parse_args())

    return args['run_id']


def check_threshold():
    # Checks the current number of work units that have not been processed.

    t_engine = create_engine(BOINC_DB_LOGIN) # to avoid confusion with the other variables
    t_connection = t_engine.connect()

    count = t_connection.execute(select([func.count(RESULT.c.id)]).where(RESULT.c.server_state == 2)).first()[0]
    t_connection.close()

    LOGGER.info('Checking pending = {0} : threshold = {1}'.format(count, WG_THRESHOLD))

    if count is None:  # in case of errors
        return True

    return count >= WG_THRESHOLD


def main():

    if check_threshold(): # true if we have enough already, false if we dont.
        LOGGER.info('Nothing to do')
    else:
        boinc_config = configxml.ConfigFile(os.path.join(DIR_BOINC_PROJECT_PATH, 'config.xml')).read()
        download_directory = boinc_config.config.download_dir
        fanout = long(boinc_config.config.uldl_dir_fanout)

        LOGGER.info('Download directory is {0} fanout is {1}'.format(download_directory, str(fanout)))

        run_id = parse_args()

        LOGGER.info('Opening BOINC DB')
        # os.chdir(DIR_BOINC_PROJECT_PATH)

        ret_val = py_boinc.boinc_db_open()
        if ret_val != 0:
            LOGGER.info('Could not open BOINC DB, error = {0}'.format(ret_val))
            exit(1)

        # Check for registered cubes, ONLY ON OUR RUN ID!!

        cube_count = 0

        if run_id is not None:
            # Check for registered cubes only for the specified run id.
            cube_count = connection.execute(select([func.count(CUBE.c.cube_id)]).where(CUBE.c.progress == 0 and CUBE.c.run_id == run_id)).first()[0]
            cubes = connection.execute(select([CUBE]).where(CUBE.c.progress == 0 and CUBE.c.run_id == run_id))
        else:
            # Check for all registered cubes
            cube_count = connection.execute(select([func.count(CUBE.c.cube_id)]).where(CUBE.c.progress == 0)).first()[0]
            cubes = connection.execute(select([CUBE]).where(CUBE.c.progress == 0))

        if cube_count == 0:
            if run_id is not None:
                LOGGER.info('No pending cubes for run id {0}.'.format(run_id))
            else:
                LOGGER.info('No pending cubes.')
        else:
            # We have some cubes to process

            for row in cubes:

                #### CUBE ####
                cube_abs_path = get_cube_path(row['cube_name'])
                wu_filename = '{0}_{1}'.format(row['run_id'], row['cube_name'])

                LOGGER.info('Current cube is {0}'.format(wu_filename))

                # Get the download directory
                wu_download_dir = get_download_dir(wu_filename, download_directory, fanout)

                LOGGER.info('WU download directory is {0}'.format(wu_download_dir))

                # Copy the cube from its current path to the download dir
                shutil.copyfile(cube_abs_path, os.path.join(wu_download_dir, wu_filename))

                #### PARAMETER FILES ####

                # First we need to grab all of the local parameter files we'll need for this and shove them in a .tar.gz
                param_path = get_parameter_files(connection, row['run_id'])

                param_download_dir = get_download_dir(os.path.basename(param_path), download_directory, fanout)
                LOGGER.info('Param download dir is {0}'.format(param_download_dir))

                # Then, we need to copy that .tar.gz to a parameter download directory
                shutil.copyfile(param_path, param_download_dir)

                # create the workunit
                file_list = [os.path.join(wu_download_dir, wu_filename), os.path.join(param_download_dir, 'parameters.tar.gz')]

                LOGGER.info(file_list)

                if create_workunit('duchamp', wu_filename, file_list):
                    connection.execute(CUBE.update().where(CUBE.c.cube_id == row[1]).values(progress=1))

        py_boinc.boinc_db_close()

if __name__ == '__main__':
    main()