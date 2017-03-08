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

# Count all of the current server states:
#   define('RESULT_SERVER_STATE_INACTIVE',       1);
#   define('RESULT_SERVER_STATE_UNSENT',         2);
#   define('RESULT_SERVER_STATE_IN_PROGRESS',    4);
#   define('RESULT_SERVER_STATE_OVER',           5);

import os, sys
from database.database_support import CUBE, PARAMETER_FILE
from database.boinc_database_support import RESULT, WORK_UNIT
from sqlalchemy.engine import create_engine
from sqlalchemy import select, func, update
from config import BOINC_DB_LOGIN, DB_LOGIN


class Stats:
    def __init__(self):
        self.total_cubes = 0
        self.cubes_without_wus = 0
        self.cubes_without_canonical_results = 0
        self.bad_canonical_results = 0

        self.result_init = 0
        self.result_success = 0
        self.result_couldnt_send = 0
        self.result_client_error = 0
        self.result_no_reply = 0
        self.result_didnt_need = 0
        self.result_validate_error = 0
        self.result_client_detached = 0

        self.result_unknown = 0

        self.server_inactive = 0
        self.server_unsent = 0
        self.server_in_progress = 0
        self.server_over = 0

        self.server_unknown = 0

    def percentage(self, stat):
        return "{0}%".format((stat / self.total_cubes) * 100)

    def summarise(self):
        # Print numbers and percentages

        print "Total Cubes: {0}".format(self.total_cubes)
        print "Cubes without work units: {0}. {1}".format(self.cubes_without_wus, self.percentage(self.cubes_without_wus))
        print "Cubes without canonical results: {0}. {1}".format(self.cubes_without_canonical_results, self.percentage(self.cubes_without_canonical_results))
        print "Cubes with bad canonical result values: {0}. {1}".format(self.bad_canonical_results, self.percentage(self.bad_canonical_results))

        print "\nResult Init: {0}. {1}".format(self.result_init, self.percentage(self.result_init))
        print "Result Success: {0}. {1}".format(self.result_success, self.percentage(self.result_success))
        print "Result Couldn't Send: {0}. {1}".format(self.result_couldnt_send, self.percentage(self.result_couldnt_send))
        print "Result Client Error: {0}. {1}".format(self.result_client_error, self.percentage(self.result_client_error))
        print "Result No Reply: {0}. {1}".format(self.result_no_reply, self.percentage(self.result_no_reply))
        print "Result Didn't Need: {0}. {1}".format(self.result_didnt_need, self.percentage(self.result_didnt_need))
        print "Result Validate Error: {0}. {1}".format(self.result_validate_error, self.percentage(self.result_validate_error))
        print "Result Client Detached: {0}. {1}".format(self.result_client_detached, self.percentage(self.result_client_detached))
        print "\nResult Unknown: {0}. {1}".format(self.result_unknown, self.percentage(self.result_unknown))

        print "\nServer State Inactive: {0}. {1}".format(self.server_inactive, self.percentage(self.server_inactive))
        print "Server State Unsent: {0}. {1}".format(self.server_unsent, self.percentage(self.server_unsent))
        print "Server State In Progress: {0}. {1}".format(self.server_in_progress, self.percentage(self.server_in_progress))
        print "Server State Over: {0}. {1}".format(self.server_over, self.percentage(self.server_over))

        print "\nServer State Unknown: {0}. {1}".format(self.server_unknown, self.percentage(self.server_unknown))


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

        wu = CONNECTION_BOINC.execute("select * from duchamp.workunit where workunit.name == {0}_{1}".format(run_id, cube.name)).first()
        #wu = CONNECTION_BOINC.execute(select([WORK_UNIT]).where(WORK_UNIT.c.name == '{0}_{1}'.format(run_id, cube.name))).first()

        if wu is None:
            stats.cubes_without_wus += 1
            continue

        if wu['canonical_resultid'] == 0:
            stats.cubes_without_canonical_results += 1
            continue

        result = CONNECTION_BOINC.execute(select([RESULT]).where(RESULT.c.id == wu['canonical_resultid'])).first()

        if result is None:
            stats.bad_canonical_results += 1
            continue

        server_state = result['server_state']
        outcome = result['outcome']

        if server_state == 1:
            stats.server_inactive += 1
        elif server_state == 2:
            stats.server_unsent += 1
        elif server_state == 4:
            stats.server_in_progress += 1
        elif server_state == 5:
            stats.server_over += 1
        else:
            stats.server_unknown += 1

        if outcome == 0:
            stats.result_init += 1
        elif outcome == 1:
            stats.result_success += 1
        elif outcome == 2:
            stats.result_couldnt_send += 1
        elif outcome == 3:
            stats.result_client_error += 1
        elif outcome == 4:
            stats.result_no_reply += 1
        elif outcome == 5:
            stats.result_didnt_need += 1
        elif outcome == 6:
            stats.result_validate_error += 1
        elif outcome == 7:
            stats.result_client_detached += 1
        else:
            stats.result_unknown += 1

    stats.summarise()

if __name__ == '__main__':
    main()
