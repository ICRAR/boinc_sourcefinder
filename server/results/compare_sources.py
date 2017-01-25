"""
Looking at comparing the sources found by Duchamp with those stored in the database on pleiades.

Accessing the pleiades database requires an initial ssh connection in to sfoster@pleiades.icrar.org,
then a mysql connection to pleiades01.icrar.org with username theskynet and password theskynet.

1. Get DB connections working.
2. Work out which tables need comparison
3. Perform range comparison
4. Report similarities
5. Calculate performance metric as to how accurate the found sources were.
"""

import os
import sys

base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))

import argparse
from sqlalchemy.engine import create_engine
from sqlalchemy import select, func, update
from config import DB_LOGIN
from database.database_support import RESULT, CUBE
from sshtunnel import SSHTunnelForwarder

PLEIADES_USERNAME = "theskynet"
PLEIADES_PASSWORD = "theskynet"
PLEIADES_DB = "theskynet"  # many repeats

PLEIADES_DB_LOGIN = "mysql://" + PLEIADES_USERNAME + ":" + PLEIADES_PASSWORD + "@localhost/" + PLEIADES_DB


def parse_args():
    # SSH uname, pword

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", nargs=1, help="SSH username for pleiades connection", default="")
    parser.add_argument("-p", nargs=1, help="SSH password for pleiades connection", default="")

    args = vars(parser.parse_args())

    return args


# Initial DB connections
def get_db_connection(db_login):
    engine = create_engine(db_login)
    return engine.connect()


# Duchamp db
def get_duchamp_sources(db):
    """
    Get a list/dict of all sources found by duchamp.
    :param db:
    :return:
    """

    # Headings needed:
    # Source DB ID, Cube name, parameter used, RA, DEC, FREQ


# Other db

def main():
    args = parse_args()

    duchamp_db = get_db_connection(DB_LOGIN)

    # Grab a local list of sources found by duchamp. Might be less than ideal if there were a lot of results, but
    # we need to use an SSH tunnel for the other DB, and I can't tunnel one connection and not the other.

if __name__ == "__main__":
    main()