"""Register a run of cubes for processing by populating the database"""

import argparse
# import os
from register_cube_mod import get_cube_names, get_cube_data, set_ranges, update_cube_table
# from config import DB_LOGIN (For local testing, just defining a general login instead
from sqlalchemy.engine import create_engine
from logging_helper import config_logger

LOGGER = config_logger(__name__)
LOGGER.info('Starting work registration.py')

parser = argparse.ArgumentParser()
parser.add_argument('cube_directory', nargs=1, help='The directory that all the new workunits are stored')

parser.add_argument('run_id', nargs=1, help='The run_id of the database')
parser.add_argument('--reconDim', default='*', help='The range of values required for reconDim parameter')
parser.add_argument('--snrRecon', default='*', help='The range of values required for snrRecon parameter')
parser.add_argument('--scaleMin', default='*', help='The range of values required for scaleMin parameter')
parser.add_argument('--minPix', default='*', help='The range of values required for minChan parameter')
parser.add_argument('--minChan', default='*', help='The range of values required for flagGrowth parameter')
parser.add_argument('--flagGrowth', default='*', help='The flag growth values')
parser.add_argument('--growthThreshold', default='*', help='The rannge of growth thresholds')
parser.add_argument('--threshold', default='*', help='The threshold range')

args = vars(parser.parse_args())
WORKING_DIRECTORY = args['cube_directory'][0]
RUN_ID = args['run_id']
RECON_DIM = args['reconDim']
SNR_DIM = args['snrRecon']
SCALE_MIN = args['scaleMin']
MIN_PIX = args['minPix']
MIN_CHAN = args['minChan']
FLAG_GROWTH = args['flagGrowth']
GROWTH_THRESHOLD = args['growthThreshold']
THRESHOLD = args['threshold']

# TODO initially hard coded, will add to fabric files later on
DB_LOGIN = 'mysql://' + 'root' + ':' + '@' + 'localhost' + '/' + 'sourcefinder'

parameter_list = [RECON_DIM, SNR_DIM, SCALE_MIN, MIN_PIX, MIN_CHAN, FLAG_GROWTH, GROWTH_THRESHOLD,
                  THRESHOLD]

parameter_name_list = ['recon_dim', 'snr_dim', 'scale_min', 'min_pix', 'min_chan', 'flag_growth', 'growth_threshold', 'threshold']

ENGINE = create_engine(DB_LOGIN)
connection = ENGINE.connect()

# get a list of the cubes to be registered
cubes = get_cube_names(WORKING_DIRECTORY)
# get run_id into numerical form
for cube in cubes:
    LOGGER.info('The file is ' + cube)
    if "askap" in cube:
        LOGGER.info('Working directory is ' + WORKING_DIRECTORY + cube)
        check = update_cube_table(connection, WORKING_DIRECTORY + cube, RUN_ID)
        if check == 1:
            LOGGER.info("Cube already exists in db for run: " + RUN_ID[0])


i = 0
for parameter in parameter_list:
    parameter_string = parameter.split('[]')
    set_ranges(RUN_ID, connection, parameter_name_list[i], parameter_string)
    i += 1

connection.close()
