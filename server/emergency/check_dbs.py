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
from database.boinc_database_support import WORKUNIT

def get_boinc_result_list():
    engine = create_engine(BOINC_DB_LOGIN)
    connection = engine.connect()

    workunits = connection.execute(select([WORKUNIT]).where(WORKUNIT.c.canonical_resultid != 0))

    return [workunit['name'] for workunit in workunits]

def get_sourcefinder_result_list():
    engine = create_engine(DB_LOGIN)
    connection = engine.connect()

    results = connection.execute(select([RESULT.c.workunit_name]).where(RESULT.c.result_id > 0))

    return [result['workunit_name'] for result in results]


if __name__ == '__main__':
    print len(get_boinc_result_list())
    print len(get_sourcefinder_result_list())