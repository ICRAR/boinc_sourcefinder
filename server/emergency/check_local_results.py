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
    dir_objects = [os.path.join(directory, d) for d in os.listdir(directory)]

    filenames = [f for f in dir_objects if os.path.isfile(f)]
    dirnames = [d for d in dir_objects if os.path.isdir(d)]

    for f in filenames:
        name = os.path.basename(f)
        file_list.add(name[3: name.find('r') - 3])

    for d in dirnames:
        collect_file_names(d, file_list)


def collect_db_names(name_list):
    engine = create_engine(DB_LOGIN)
    connection = engine.connect()

    cubes = connection.execute(select([CUBE]).where(CUBE.c.cube_id > 0))
    for cube in cubes:
        name_list.append(cube['cube_name'])


def is_number(char):
    return char in '0123456789'


def find_cube_set_number(name):

    numbers = ''
    first_number_idx = 0
    for i in range(0, len(name)):
        if is_number(name[i]):
            first_number_idx = i
            break

    while is_number(name[first_number_idx]):
        numbers += name[first_number_idx]
        first_number_idx += 1

    return int(numbers)


def index_cubes(names):
    index = {}

    for name in names:
        set_number = find_cube_set_number(name)
        if set_number in index:
            index[set_number].append(name)
        else:
            index[set_number] = [name]

    return index

if __name__ == '__main__':
    file_names = set()
    db_names = []
    ones_we_have = []
    ones_we_dont_have = []

    print find_cube_set_number('askap_cube_1_8_22')
    print find_cube_set_number('askap_cube_22_8_22')

    collect_file_names('/home/ec2-user/upload', file_names)
    collect_db_names(db_names)

    db_index = index_cubes(db_names)
    files_index = index_cubes(file_names)

    for name in db_names:
        if name in file_names:
            ones_we_have.append(name)
        else:
            ones_we_dont_have.append(name)

    ones_we_dont_have.sort()
    ones_we_have.sort()

    print "Total db cubes: {0}".format(len(db_names))

    print "db_index"
    for key in db_index:
        print key, len(db_index[key])

    print "Total flat files: {0}".format(len(file_names))

    print "file_names"
    for key in file_names:
        print key, len(files_index[key])

    print "We have: "
    print len(ones_we_have)

    print "We don't have: "
    print len(ones_we_dont_have)
