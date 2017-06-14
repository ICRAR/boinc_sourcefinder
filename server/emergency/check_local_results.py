#! /usr/bin/env python

import os
import sys

# Setup the Python Path as we may be running this via ssh
base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '/home/ec2-user/projects/duchamp/py')))
sys.path.append('/home/ec2-user/boinc_sourcefinder/server')
sys.path.append('/home/ec2-user/boinc_sourcefinder/server/assimilator')

from config import DB_LOGIN, S3_BUCKET_NAME, filesystem
from sqlalchemy import create_engine, select, and_
from sqlalchemy.exc import OperationalError
from database.database_support import CUBE, RESULT

# Need to get list of all result file names from db
# Need to get list of all result file names that exist.
# Compare lists and determine which result files exist in the db but not in the filesystem


def collect_file_names(directory, file_list):
    dir_objects = os.listdir(directory)

    print dir_objects

    filenames = [f for f in dir_objects if os.path.isfile(f)]
    dirnames = [d for d in dir_objects if os.path.isdir(d)]

    for f in filenames:
        file_list.append(os.path.basename(f))

    for d in dirnames:
        collect_file_names(d, file_list)


def collect_db_names(name_list):
    engine = create_engine(DB_LOGIN)
    connection = engine.connect()

    cubes = connection.execute(select([CUBE]).where(CUBE.c.cube_id > 0))
    for cube in cubes:
        name_list.add(cube['cube_name'])

if __name__ == '__main__':
    file_names = []
    db_names = set()
    ones_we_have = []
    ones_we_dont_have = []

    collect_file_names('/home/ec2-user/upload', file_names)
    collect_db_names(db_names)

    for name in file_names:
        if name in db_names:
            ones_we_have.append(name)
        else:
            ones_we_dont_have.append(name)

    ones_we_dont_have.sort()
    ones_we_have.sort()

    print "We have: "
    for entry in ones_we_have:
        print entry

    print "We don't have: "
    for entry in ones_we_dont_have:
        print entry
