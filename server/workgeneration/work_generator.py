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
    
    input_files = []	
    #Check for registered cubes
    registered = connection.execute(select([CUBE.c.cube_name]).where(CUBE.c.progress==0))
    if registered is None:
	LOGGER.info("No files registered for work")
    else:
	for row in registered:
	    input_files.append(row)
	    LOGGER.info('{0}'.format(input_files)
    for input_file in input_files:
        args_file=[]
        args_file.apend(input_file) #for the list_input_files param, need it in list object
        retval = py_boinc.boinc_create_work(
        app_name='duchamp',
        min_quorom=2,
        max_success_results=5,
        max_error_results=5,
        delay_bound=7*84600,
        target_nresults=2,
        wu_name=input_file,
        wu_template="templates/duchamp_in.xml",
        result_template="templates/duchamp_out.xml",
	size_class=0,
	priority=1,
	opaque=0,
        rsc_fpops_est=1e12,
        rsc_fpops_bound=1e14,
        rsc_memory_bound=1e8,
        rsc_disk_bound=1e8,
	additional_xml="",
	list_input_files=input_files)
        if retval != 0:
            py_boinc.boinc_db_transaction_rollback()
            LOG.error('Error writing to boinc database. boinc_create_work return value = {0}'.format(retval))

#its that have server state of 2 - subtract
# that number from the WU threshold to determine how many new workunits are required


