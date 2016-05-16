# Register a new run, and all of the parameters that should be associated with that run.
# No args equals register with all parameters currently in the db.

import os
import sys
import argparse

base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))

from utils.logging_helper import config_logger
from database.database_support import PARAMETER_FILE, RUN, PARAMETER_RUN
from sqlalchemy import create_engine, select

from config import DIR_PARAM, DB_LOGIN

LOGGER = config_logger(__name__)
LOGGER.info('Starting register_run.py')
LOGGER.info('PYTHONPATH = {0}'.format(sys.path))


engine = create_engine(DB_LOGIN)
connection = None

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('run_id', nargs=1, help='The new run ID', default=-1, type=int)
    parser.add_argument('parameter_defs', nargs=1, help='File specifying which parameter files to include in this run', default=None)

    args = vars(parser.parse_args())
    run_id = int(args['run_id'][0])
    parameters = args['parameter_defs'][0]

    return run_id, parameters


def parse_parameter_specifier(specifier_filename):
    # Parameter specifier has the following format:

    # comments as #
    # flat values as 3 2 3 4 5 etc. separated by spaces or new lines
    # ranges specified as 3 - 60

    params = []

    with open(specifier_filename, 'r') as f:

        linecount = 0

        try:

            for line in f:

                linecount += 1

                if line.startswith('#') or line.startswith('\n'):  # totally ignore if this line starts with a #
                    continue

                line = line.strip()

                split = line.split(' ')  # split line by space

                curr_token = None
                range_next = False

                for token in split:

                    if token.startswith('#'):  # ignore the rest of this line

                        if curr_token is not None:
                            params.append(int(curr_token))

                        range_next = False
                        curr_token = None
                        break

                    if len(split) == 1:
                        params.append(int(token))
                        continue

                    if curr_token is None:  # set currtoken and check if there's a - coming up next
                        curr_token = token
                        continue

                    if token == '-':
                        range_next = True
                        continue

                    if range_next:
                        i_curtok = int(curr_token)
                        i_tok = int(token)

                        if i_curtok > i_tok:  # Bad range
                            raise Exception('Invalid range {0} - {1}'.format(curr_token, token))

                        if i_curtok == i_tok:  # Range is 1 value only
                            params.append(i_curtok)
                        else:
                            for i in range(int(curr_token), int(token) + 1):  # Several values in the range
                                params.append(i)

                        # Reset our params for the next line

                        range_next = False
                        curr_token = None
                        continue

                    params.append(int(curr_token))
                    curr_token = token

        except Exception as e:
            LOGGER.exception('Parse error on line {0} {1}'.format(linecount))

    return params


def create_run_id(run_id):

    # Check to see if this run is already registered
    check = connection.execute(select([RUN]).where(RUN.c.run_id == run_id))
    result = check.fetchone()

    if not result:
        # The run is not registered already, so register it
        LOGGER.info('Adding new run_id to the db: {0}'.format(run_id))
        connection.execute(RUN.insert(), run_id=run_id)


def register_parameters_runid(run_id, parameters):

    # Need to make a bunch of insertions in to the parameter_run table

    connection.begin()

    if parameters is None:
        # We need to make an insertion here for every single parameter that exists in the parameter_files table
        ret = connection.execute(select([PARAMETER_FILE]))
        for row in ret:
            connection.execute(PARAMETER_RUN.insert(), parameter_id=int(row['parameter_file_id']), run_id=run_id)
    else:
        for param in parameters:
            connection.execute(PARAMETER_RUN.insert(), parameter_id=int(param), run_id=run_id)

    connection.commit()


def main():

    run_id, parameters = parse_args()

    if run_id < 0:
        LOGGER.error('Invalid run ID specified, please specify a run id greater than 0')
        exit(1)

    # Work out which parameter files to add to the db under this run ID.
    if parameters is not None:
        params = parse_parameter_specifier(parameters)
    else:
        params = None

    global connection

    connection = engine.connect()

    # Add this run ID
    create_run_id(run_id)

    # Add each of the parameter files to this run ID in the parameter_run table
    register_parameters_runid(run_id, params)

    connection.close()

