# Work generator used to create workunits

import os
import argparse
import py_boinc
from sqlalchemy.engine import create_engine
from sqlalchemy import select, insert, and_, func

from database.boinc_database_support import RESULT
from Boinc import database
from logging_helper import config_logger
from work_generator_mod import generate_parameter_set

LOGGER = config_logger(__name__)
LOGGER.info('Starting work generation')

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
    if not os.path.exists('parameters_' + RUN_ID):
        LOGGER.info('Creating parameter files')
        connection = ENGINE.connect()
        retval = generate_parameter_set(connection, RUN_ID)


    else:
        LOGGER.info('Parameter set for run ' + RUN_ID + 'already exists')
        # Continue with generation (using boinc db api stuffsss)

# Check database for workunits that have server state of 2 - subtract
# that number from the WU threshold to determine how many new workunits are required


