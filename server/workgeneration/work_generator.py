# Work generator used to create workunits

import argparse
import os
import shutil
import sys

base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))

from utils.logging_helper import config_logger

from config import  BOINC_DB_LOGIN, DB_LOGIN, WG_THRESHOLD, DIR_BOINC_PROJECT_PATH, DIR_PARAM


from sqlalchemy.engine import create_engine
from sqlalchemy import select, func, update
import py_boinc
from database.boinc_database_support import RESULT
from Boinc import configxml
from database.database_support import CUBE
from work_generator_mod import convert_file_to_wu, create_workunit, get_cube_path

LOGGER = config_logger(__name__)
LOGGER.info('Starting work generation')

parser = argparse.ArgumentParser()
parser.add_argument('run_id', nargs=1, help='The run_id of paramater sets that you for which you want to generate work')

args = vars(parser.parse_args())
RUN_ID = args['run_id'][0]

# make a connection with the BOINC database on the server

ENGINE = create_engine(BOINC_DB_LOGIN)
connection = ENGINE.connect()
# Fits that have server state of 2 - subtract that number from the WU threshold to determine how many new workunits are required
count = connection.execute(select([func.count(RESULT.c.id)]).where(RESULT.c.server_state == 2)).first()[0]
connection.close()

LOGGER.info('Checking pending = {0} : threshold = {1}'.format(count, WG_THRESHOLD))

# THIS MAKES EVERYTHING RUN FROM THE BOINC PROJECT PATH REMEMBER THIS RYAN...REMEMBER THIS
"""
if os.path.exists(BOINC_PROJECT_PATH):
    os.chdir(BOINC_PROJECT_PATH)
else:
    os.chdir('.')

if os.path.exists(DIR_BOINC_PROJECT_PATH):
    LOGGER.info("Boinc project path at {0} added to PYTHONPATH".format(DIR_BOINC_PROJECT_PATH))
    sys.path.append(DIR_BOINC_PROJECT_PATH)
else:
    LOGGER.error("Could not find boinc project path at {0}".format(DIR_BOINC_PROJECT_PATH))
    exit(1)
"""

ENGINE = create_engine(DB_LOGIN)
connection = ENGINE.connect()

param_abs_path = '{0}/parameter_files_'.format(DIR_PARAM) + RUN_ID

if count is not None and count >= WG_THRESHOLD:
    LOGGER.info('Nothing to do')
else:
    boinc_config = configxml.ConfigFile(os.path.join(DIR_BOINC_PROJECT_PATH, 'config.xml')).read()
    download_directory = boinc_config.config.download_dir
    fanout = long(boinc_config.config.uldl_dir_fanout)
    LOGGER.info('Download directory is {0} fanout is {1}'.format(download_directory, str(fanout)))

    # check to see if parameter files for run_id exist:
    if os.path.exists(param_abs_path):
        LOGGER.info('Parameter set for run {0} exists'.format(RUN_ID))
        # tar the parameter files
        LOGGER.info('Absolute path is {0}'.format(param_abs_path))
        ret = os.system('tar -zcvf {0}.tar.gz -C {1} {2} > /dev/null'.format(param_abs_path, DIR_PARAM, 'parameter_files_{0}'.format(RUN_ID)))
        if ret != 0:
            LOGGER.info("Could not tar properly, exiting...")
            exit(1)
        LOGGER.info('Created tar file of parameter files found in {0}'.format(param_abs_path))
    else:
        LOGGER.info('No parameter_files for run_id ' + RUN_ID)
        exit(1)

    # This part was bitching about not being in the boinc directory. sigh
    LOGGER.info('Opening BOINC DB')
    os.chdir(DIR_BOINC_PROJECT_PATH)
    ret_val = py_boinc.boinc_db_open()
    if ret_val != 0:
        LOGGER.info('Could not open BOINC DB, error = {0}'.format(ret_val))
        exit(1)

    files_to_workunits = []
    # Check for registered cubes, ONLY ON OUR RUN ID!!

    count = connection.execute(select([func.count(CUBE.c.cube_id)]).where(CUBE.c.progress == 0 and CUBE.c.run_id == RUN_ID)).first()[0]
    if count == 0:
        LOGGER.info('All workunits for cubes registered under this run ID have already been created')
    else:
        registered = connection.execute(select([CUBE.c.cube_name, CUBE.c.cube_id]).where(CUBE.c.progress == 0 and CUBE.c.run_id == RUN_ID))

        for row in registered:  # get all workunits from wu directory

            wu_abs_path = get_cube_path(row[0])
            string = row[0].rpartition('/')[-1]  # get rid of path names
            wu_file = '{0}_{1}'.format(RUN_ID, string)

            LOGGER.info('current wu is {0}'.format(wu_file))

            # Get the download directory
            wu_download_dir = convert_file_to_wu(wu_file, download_directory, fanout)
            LOGGER.info('wu download directory is {0}'.format(wu_download_dir))

            LOGGER.info('wu path is {0}'.format(wu_abs_path))

            # Copy work unit from its current path to the download dir
            shutil.copyfile(wu_abs_path, wu_download_dir)

            # Don't use the param abs path here as this is making a download dir
            param_download_dir = convert_file_to_wu('parameter_files_{0}.tar.gz'.format(RUN_ID), download_directory, fanout)
            LOGGER.info('Param download dir is {0}'.format(param_download_dir))

            # Copy parameter file from abs path in to download dir
            shutil.copyfile(param_abs_path + '.tar.gz', param_download_dir)

            # create the workunit
            file_list = [wu_file+'tar.gz', 'parameter_files_{0}.tar.gz'.format(RUN_ID)]
            print file_list
            #  convert workunit to the list. Strip off the .tar.gz part of the work unit name.
            create_workunit('duchamp', wu_file, file_list)

            connection.execute(CUBE.update().where(CUBE.c.cube_id == row[1]).values(progress=1))

    py_boinc.boinc_db_close()