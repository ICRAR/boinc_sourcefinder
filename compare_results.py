#! /usr/bin/env python

# Simple comparison between the sourcefinder DB results and a CSV file of results.
import os, sys
base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, './server/')))

import argparse
import numpy as np
from sqlalchemy import create_engine, select
from database.database_support import RESULT
from config import DB_LOGIN


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', help='CSV file to compare to the DB', default=None)

    args = vars(parser.parse_args())
    f = args['file']

    return f


def parse_file(f):
    """
    Parse this file and return a numpy 2D array of its elements.
    We only compare on the first 3 elements of a row (ignoring the first row, and first col)
    :param f:
    :return:
    """

    row = []
    with open(f, "r") as ff:
        linecount = -1
        for line in ff:
            linecount += 1

            if linecount == 0:
                continue # Skip line one

            split = line.split()
            col = [0,0,0]
            col[0] = float(split[1])
            col[1] = float(split[2])
            col[2] = float(split[3])

            row.append(col)

    return np.array(row)


def get_db_sources():

    # SSH tunnel to the server to access the db properly

    engine = create_engine(DB_LOGIN)
    connection = engine.connect()

    table = connection.execute(select([RESULT]).where(RESULT.c.run_id == 1)).fetchall()

    row = []

    for line in table:
        col = [0,0,0]
        col[0] = float(line['RA'])
        col[1] = float(line['DEC'])
        col[2] = float(line['freq'])
        row.append(col)

    print row


def main():
    f = parse_args()
    array = parse_file(f)
    get_db_sources()


if __name__ == '__main__':
    main()