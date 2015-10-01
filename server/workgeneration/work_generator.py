# Work generator used to create workunits

import os
import shutil
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
from work_generator_mod import convert_file_to_wu, create_workunit

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

# THIS MAKES EVERYTHING RUN FROM THE BOINC PROJECT PATH REMEMBER THIS RYAN...REMEMBER THIS
if os.path.exists(BOINC_PROJECT_PATH):
    os.chdir(BOINC_PROJECT_PATH)
else:
    os.chdir('.')

ENGINE = create_engine(DB_LOGIN)
connection = ENGINE.connect()

param_abs_path = ''
wu_abs_path = ''

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
        # tar the parameter files
        param_abs_path = os.path.abspath('parameter_files_{0}'.format(RUN_ID))
        LOGGER.info('Absolute path is' + param_abs_path)
        tar = 'tar -zcvf {0}.tar.gz {0}'.format('parameter_files_{0}'.format(RUN_ID))
        os.system(tar)
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
            wu_abs_path = row[0]
            string = row[0].rpartition('/')[-1]  # get rid of path names
            wu_file = '{0}_{1}'.format(RUN_ID, string)
            files_to_workunits.append(wu_file)
        LOGGER.info('{0}'.format(files_to_workunits))

    for work_file in files_to_workunits:
        wu_download_dir = convert_file_to_wu(work_file, download_directory, fanout)
        LOGGER.info('wu download directory is {0}'.format(wu_download_dir))
        wu_path = '{0}/{1}'.format(wu_download_dir, work_file)
        LOGGER.info(wu_abs_path)
        LOGGER.info('wu path is {0}'.format(wu_path))
        shutil.copy(wu_abs_path, wu_path)
        param_download_dir = wu_download_dir + '/parameter_files_{0}.tar.gz'.format(RUN_ID)
        LOGGER.info('Param path is {0}.tar.gz and download path is {1}'.format(param_abs_path, param_download_dir))
        shutil.copy(param_abs_path + '.tar.gz', param_download_dir)
        # create the workunit
        file_list = [work_file, 'parameter_files_{0}.tar.gz'.format(RUN_ID)]
        print file_list
        #  convert workunit to the list
        create_workunit('duchamp', work_file, file_list)
