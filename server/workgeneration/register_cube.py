"""Register a run of cubes for processing by populating the database"""

import argparse
import os
from workgeneration.register_cube_mod import update_cube_table, get_cube_names

parser = argparse.ArgumentParser()
parser.add_argument('cube_directory', nargs=1, help='The directory that all the new workunits are stored')
parser.add_argument('run_id', nargs=1, help='The run_id of the database')
parser.add_argument('reconDim', nargs=1, help='The range of values required for reconDim parameter')
parser.add_argument('snrRecon', nargs=1, help='The range of values required for snrRecon parameter')
parser.add_argument('scaleMin', nargs=1, help='The range of values required for scaleMin parameter')
parser.add_argument('minPix', nargs=1, help='The range of values required for minChan parameter')
parser.add_argument('minChan', nargs=1, help='The range of values required for flagGrowth parameter')
parser.add_argument('flagGrowth', nargs=1, help='The flag growth values')
parser.add_argument('growthThreshold', nargs=1, help='The rannge of growth thresholds')
parser.add_argument('threshold', nargs=1, help='The threshold range')

args = vars(parser.parse_args())
WORKING_DIRECTORY = args['cube_directory'][0]
RUN_ID = args['run_id'][0]




