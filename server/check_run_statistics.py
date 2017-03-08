# Get all of the cubes in the specified run id.
# Build the work unit name for each cube.
# Get all of the work units <- this is list of all work units in the specified run.
# Get all of the results, one for each work unit.

# Count all of the current result outcomes :
#   define('RESULT_OUTCOME_INIT',             0);
#   define('RESULT_OUTCOME_SUCCESS',          1);
#   define('RESULT_OUTCOME_COULDNT_SEND',     2);
#   define('RESULT_OUTCOME_CLIENT_ERROR',     3);
#   define('RESULT_OUTCOME_NO_REPLY',         4);
#   define('RESULT_OUTCOME_DIDNT_NEED',	      5);
#   define('RESULT_OUTCOME_VALIDATE_ERROR',   6);
#   define('RESULT_OUTCOME_CLIENT_DETACHED',  7);

RESULT_OUTCOME_INIT = 0
RESULT_OUTCOME_SUCCESS = 1
RESULT_OUTCOME_COULDNT_SEND = 2
RESULT_OUTCOME_CLIENT_ERROR = 3
RESULT_OUTCOME_NO_REPLY = 4
RESULT_OUTCOME_DIDNT_NEED = 5
RESULT_OUTCOME_VALIDATE_ERROR = 6
RESULT_OUTCOME_CLIENT_DETACHED = 7

# Count all of the current server states:
#   define('RESULT_SERVER_STATE_INACTIVE',       1);
#   define('RESULT_SERVER_STATE_UNSENT',         2);
#   define('RESULT_SERVER_STATE_IN_PROGRESS',    4);
#   define('RESULT_SERVER_STATE_OVER',           5);

RESULT_SERVER_STATE_INACTIVE = 1
RESULT_SERVER_STATE_UNSENT = 2
RESULT_SERVER_STATE_IN_PROGRESS = 4
RESULT_SERVER_STATE_OVER = 5

RESULT_NEW = 0
RESULT_FILES_DOWNLOADING = 1
RESULT_FILES_DOWNLOADED = 2
RESULT_COMPUTE_ERROR = 3
RESULT_FILES_UPLOADING = 4
RESULT_FILES_UPLOADED = 5
RESULT_ABORTED = 6
RESULT_UPLOAD_FAILED = 7

import os, sys
from database.database_support import CUBE, PARAMETER_FILE
from database.boinc_database_support import RESULT, WORK_UNIT
from sqlalchemy.engine import create_engine
from sqlalchemy import select, func, update
from config import BOINC_DB_LOGIN, DB_LOGIN


class Stats:
    def __init__(self):
        self.total_cubes = 0        # Total number of cubes (work units)
        self.total_results = 0      # Total number of results
        self.canonical_results = 0  # Number of work units with a canonical result

        self.outcome_bad = 0        # Bad outcomes
        self.outcome_good = 0       # Good outcomes

        self.client_bad = 0         # Bad client states
        self.client_inprogress = 0  # Clients still in progress
        self.client_good = 0        # Good client states

        self.server_inactive = 0
        self.server_unsent = 0
        self.server_inprogress = 0
        self.server_over = 0

    def percentage(self, stat, percent):
        return "{0}%".format((stat / float(percent)) * 100)

    def summarise(self):
        # Print numbers and percentages

        print "Total Cubes: {0}".format(self.total_cubes)
        print "Total Results: {0}".format(self.total_results)
        print "Total Canonical Results: {0}. {1}".format(self.canonical_results, self.percentage(self.canonical_results, self.total_cubes))
        print "Average Results Per Cube: {0}".format(self.total_results / float(self.total_cubes))

        print "\nGood Results: {0}. {1}".format(self.outcome_good, self.percentage(self.outcome_good, self.total_results))
        print "Bad Results: {0}. {1}".format(self.outcome_bad, self.percentage(self.outcome_bad, self.total_results))

        print "\nClient Bad: {0}. {1}".format(self.client_bad, self.percentage(self.client_bad, self.total_results))
        print "Client InProgress: {0}. {1}".format(self.client_inprogress, self.percentage(self.client_inprogress, self.total_results))
        print "Client Good: {0}. {1}".format(self.client_good, self.percentage(self.client_good, self.total_results))

        print "\nServer Inactive: {0}. {1}".format(self.server_inactive, self.percentage(self.server_inactive, self.total_results))
        print "Server Unsent: {0}. {1}".format(self.server_unsent, self.percentage(self.server_unsent, self.total_results))
        print "Server InProgress: {0}. {1}".format(self.server_inprogress, self.percentage(self.server_inprogress, self.total_results))
        print "Server Over: {0}. {1}".format(self.server_over, self.percentage(self.server_over, self.total_results))


def make_connection(login):
    engine = create_engine(login)
    return engine.connect()

CONNECTION_BOINC = make_connection(BOINC_DB_LOGIN)
CONNECTION = make_connection(DB_LOGIN)


def parse_args():
    if len(sys.argv) != 2:
        return None
    return int(sys.argv[1])


def main():
    run_id = parse_args()

    if run_id is None:
        print "Please specify a single run id as a parameter."
        return

    stats = Stats()

    cubes = CONNECTION.execute(select([CUBE]).where(CUBE.c.run_id == run_id))

    for cube in cubes:
        stats.total_cubes += 1

        wu = CONNECTION_BOINC.execute(select([WORK_UNIT]).where(WORK_UNIT.c.name == '{0}_{1}'.format(run_id, cube['cube_name']))).first()

        if wu is None:
            continue

        if wu['canonical_resultid'] != 0:
            stats.canonical_results += 1

        results = CONNECTION_BOINC.execute(select([RESULT]).where(RESULT.c.workunitid == wu['id']))

        for result in results:
            server_state = result['server_state']
            client_state = result['client_state']
            outcome = result['outcome']
            stats.total_results += 1

            if outcome == RESULT_OUTCOME_CLIENT_ERROR:
                stats.outcome_bad += 1
            else:
                stats.outcome_good += 1

            if client_state == RESULT_COMPUTE_ERROR or client_state == RESULT_ABORTED or client_state == RESULT_UPLOAD_FAILED:
                stats.client_bad += 1
            elif client_state == RESULT_FILES_DOWNLOADED or client_state == RESULT_FILES_DOWNLOADING or client_state == RESULT_FILES_UPLOADING:
                stats.client_inprogress += 1
            else:
                stats.client_good += 1

            if server_state == RESULT_SERVER_STATE_INACTIVE:
                stats.server_inactive += 1
            elif server_state == RESULT_SERVER_STATE_UNSENT:
                stats.server_unsent += 1
            elif server_state == RESULT_SERVER_STATE_IN_PROGRESS:
                stats.server_inprogress += 1
            elif server_state == RESULT_SERVER_STATE_OVER:
                stats.server_over += 1

    stats.summarise()

if __name__ == '__main__':
    main()
