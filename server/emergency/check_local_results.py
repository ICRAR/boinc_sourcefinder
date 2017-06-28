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


def get_sourcefinder_result_list():
    engine = create_engine(DB_LOGIN)
    connection = engine.connect()

    # Get all cubes from run 10
    # Check how many have results
    cubes = connection.execute(select([CUBE]))

    results = {}

    for cube in cubes:
        # Is there a result in either runs.
        name = cube['cube_name']

        if name not in results:
            results[name] = False

        if cube['progress'] == 2:
            results[name] = True

    return results


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


def index_cubes(cubes):
    have = {}
    dont_have = {}

    for cube, has_result in cubes.iteritems():
        set_number = find_cube_set_number(cube)

        if has_result:
            dic = have
        else:
            dic = dont_have

        if set_number in dic:
            dic[set_number].append(cube)
        else:
            dic[set_number] = [cube]

    return have, dont_have

if __name__ == '__main__':

    results = get_sourcefinder_result_list()

    total_cubes = 0
    total_results = 0
    for key, value in results.iteritems():
        total_cubes += 1
        total_results += int(value > 0)

    print "Total cubes: ", total_cubes
    print "Total results: ", total_results

    have, dont_have = index_cubes(results)

    print "Ones we have"
    for key, value in have.iteritems():
        print key, len(value)

    print "Ones we dont have"
    for key, value in dont_have.iteritems():
        print key, len(value)

    """boinc_workunits = [b[3:] for b in get_boinc_result_list()]
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
    """