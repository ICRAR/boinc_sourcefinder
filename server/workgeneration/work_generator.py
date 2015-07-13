# Work generator used to create workunits

import os
import argparse
import py_boinc
from sqlalchemy.engine import create_engine
from sqlalchemy import select, insert, and_
from Boinc import database
from logging_helper import LOGGER

BOINC_DB_LOGIN = 'mysql://' + 'root' + ':' + '@' + 'localhost' + ''

parser = argparse.ArgumentParser()
parser.add_argument('run_id', nargs=1, help='The run_id of paramater sets that you for which you want to generate work')

args = vars(parser.parse_args())
RUN_ID = args['run_id']

# make a connection with the BOINC database on the server

BOINC_DB_LOGIN = 'mysql://root@localhost/sourcefinder'
# Check database for workunits that have server state of 2 - subtract
# that number from the WU threshold to determine how many new workunits are required


