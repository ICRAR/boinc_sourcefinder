"""Register a run of cubes for processing by populating the database"""

import argparse
import os
from workgeneration.register_cube_mod import update_cube_table, get_cube_names

parser = argparse.ArgumentParser()
parser.add_argument('cube_directory', nargs=1, help='The directory that all the new workunits are in store')
parser.add_argument('run_id', narg=1, help='The run_id of the database')
parser.add_argument('reconDim', narg=1, help = ' ')

'reconDim'
'snrRecon'
'scaleMin'
'minPix'
'minChan'
'flagGrowt'
'growthThr'
'threshold'