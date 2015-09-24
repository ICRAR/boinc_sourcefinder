# Work generator used to create workunits

import os
import sys
import argparse
from logging_helper import config_logger

LOGGER = config_logger(__name__)
LOGGER.info('Starting work generation')

base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))

from sqlalchemy.engine import create_engine
from sqlalchemy import select, insert, and_, func
import py_boinc
from database.boinc_database_support import RESULT
from Boinc import database, configxml
from database.database_support import CUBE
from work_generator_mod import convert_file_to_wu

# TODO initially hard coded, will add to fabric files later on
BOINC_DB_LOGIN = 'mysql://root@localhost/duchamp'
DB_LOGIN = 'mysql://root@localhost/sourcefinder'
WG_THRESHOLD = 500
BOINC_PROJECT_PATH = '/home/ec2-user/projects/duchamp'
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

LOGGER.info('Checking pending = %d : threshold = %d', count, WG_THRESHOLD)

if os.path.exists(BOINC_PROJECT_PATH):
    os.chdir(BOINC_PROJECT_PATH)
else:
    os.chdir('.')

ENGINE = create_engine(DB_LOGIN)
connection = ENGINE.connect()

if count is not None and count >= WG_THRESHOLD:
    LOGGER.info('Nothing to do')
else:
    boinc_config = configxml.ConfigFile().read()
    download_directory = boinc_config.config.download_dir
    fanout = long(boinc_config.config.uldl_dir_fanout)
    LOGGER.info('Download directory is ' + download_directory + ' fanout is ' + str(fanout))

    # check to see if parameter files for run_id exist:
    if os.path.exists('parameter_files_' + RUN_ID):
        LOGGER.info('Parameter set for run ' + RUN_ID + 'exists')
    else:
        LOGGER.info('No parameter_files for run_id ' + RUN_ID)
        exit()

    ret_val = py_boinc.boinc_db_open()
    if ret_val != 0:
        LOGGER.info('Could not open BOINC DB, error = {0}'.format(ret_val))

    files_to_workunits = []
    # Check for registered cubes
    registered = connection.execute(select([CUBE.c.cube_name]).where(CUBE.c.progress == 0))
    if registered is None:
        LOGGER.info("No files registered for work")
    else:
        for row in registered:  # get all workunits from wu directory
            wu_file = row[0].rpartition('/')[-1]  # get rid of path names
            files_to_workunits.append(wu_file)
        LOGGER.info('{0}'.format(files_to_workunits))

    for work_file in files_to_workunits:
        wu = convert_file_to_wu(work_file, download_directory, fanout)
        print wu

    # create workunits
    '''for work_file in input_files:
        py_boinc.boinc_db_transaction_start()
        # do stuff to the work file so we can use it in the create work function
        args_file = [work_file]  # convert workunit to the'''
