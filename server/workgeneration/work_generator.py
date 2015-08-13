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


# TODO initially hard coded, will add to fabric files later on
BOINC_DB_LOGIN = 'mysql://root@localhost/duchamp'
DB_LOGIN = 'mysql://root@localhost/sourcefinder'
WG_THRESHOLD = 500
BOINC_PROJECT_PATH = 'home/ec2-user/projects/duchamp'
parser = argparse.ArgumentParser()
parser.add_argument('run_id', nargs=1, help='The run_id of paramater sets that you for which you want to generate work')

args = vars(parser.parse_args())
RUN_ID = args['run_id'][0]

# make a connection with the BOINC database on the server

ENGINE = create_engine(BOINC_DB_LOGIN)
connection = ENGINE.connect()
count = connection.execute(select([func.count(RESULT.c.id)]).where(RESULT.c.server_state == 2)).first()[0]
connection.close()

LOGGER.info('Checking pending = %d : threshold = %d', count, WG_THRESHOLD)

ENGINE = create_engine(DB_LOGIN)

if count is not None and count >= WG_THRESHOLD:
    LOGGER.info('Nothing to do')
else:
    # Create parameter files from sourcefinder database
    if os.path.exists(BOINC_PROJECT_PATH):
        os.chdir("BOINC_PROJECT_PATH")
    else:  # operate in current path
        os.chdir('.')

    # check to see if parameter files for run_id exist:
    if os.path.exists('parameter_files_' + RUN_ID):
        LOGGER.info('Parameter set for run ' + RUN_ID + ' already exists')
        return_value = py_boinc.boinc_db_open()
        #return_value = py_boinc.boinc_db_transaction_rollback()
        print return_value

    else:
        LOGGER.info('No parameter_files for run_id ' + RUN_ID)
        exit()


# Check database for workunits that have server state of 2 - subtract
# that number from the WU threshold to determine how many new workunits are required


