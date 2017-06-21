#! /usr/bin/env python

import os
import sys

# Setup the Python Path as we may be running this via ssh
base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '/home/ec2-user/projects/duchamp/py')))
sys.path.append('/home/ec2-user/boinc_sourcefinder/server')
sys.path.append('/home/ec2-user/boinc_sourcefinder/server/assimilator')

from config import DB_LOGIN, BOINC_DB_LOGIN, S3_BUCKET_NAME, filesystem
from sqlalchemy import create_engine, select, and_
from sqlalchemy.exc import OperationalError
from database.database_support import CUBE, RESULT
from database.boinc_database_support import WORK_UNIT

# Get names of cubes that we have progress 2 for.
# Get names of workunits with canonical resultid > 0

def get_boinc_result_list():
    engine = create_engine(BOINC_DB_LOGIN)
    connection = engine.connect()

    workunits = connection.execute(select([WORK_UNIT]).where(WORK_UNIT.c.canonical_resultid != 0))

    return [workunit['name'] for workunit in workunits]

def get_sourcefinder_result_list():
    engine = create_engine(DB_LOGIN)
    connection = engine.connect()

    results = connection.execute(select([CUBE]).where(CUBE.c.progress == 2))

    return [result['cube_name'] for result in results]


def collect_file_names(directory, file_list):
    dir_objects = [os.path.join(directory, d) for d in os.listdir(directory)]

    filenames = [f for f in dir_objects if os.path.isfile(f)]
    dirnames = [d for d in dir_objects if os.path.isdir(d)]

    for f in filenames:
        name = os.path.basename(f)
        file_list.add(name[3: name.find('r') - 3])

    for d in dirnames:
        collect_file_names(d, file_list)


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


def find_index_difference(index1, index2):
    diff = {}
    for key in index1:
        if key not in index2:
            diff[key] = list(index1[key])
            continue

        values1 = index1[key]
        values2 = set(index2[key])

        for value in values1:
            if value not in values2:
                if key not in diff:
                    diff[key] = [value]
                else:
                    diff[key].append(value)

    return diff
if __name__ == '__main__':
    boinc_workunits = [b[3:] for b in get_boinc_result_list()]
    sourcefinder_processed_cubes = [s for s in get_sourcefinder_result_list()]

    workunit_index = index_cubes(boinc_workunits)
    sourcefinder_index = index_cubes(sourcefinder_processed_cubes)

    index_diff = find_index_difference(workunit_index, sourcefinder_index)

    print "Total boinc workunits: {0}".format(len(boinc_workunits))
    print "Total total processed cubes: {0}".format(len(sourcefinder_processed_cubes))

    ones_to_get = []

    print "index_diff"
    for key in index_diff:
        print key, len(index_diff[key])
        ones_to_get += index_diff[key]

    with open('ones_to_get.txt', 'w') as f:
        ones_to_get.sort()
        for entry in ones_to_get:
            f.write(entry)
            f.write('\n')