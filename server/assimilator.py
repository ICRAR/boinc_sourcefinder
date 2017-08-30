#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia
#    Copyright by UWA (in the framework of the ICRAR)
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#

"""
Assimilator base for sourcefinder apps
"""
import hashlib
import os
import re
import signal
import shutil
import sys
import time
import argparse

from config import get_config
from utils import module_import
from utils.logger import config_logger
from sqlalchemy import create_engine, select, and_
from Boinc import database, boinc_db, boinc_project_path, configxml

MODULE = "assimilator_mod"
LOG = config_logger(__name__)
COMPLETED_RESULT_PATH = '/home/ec2-user/completed_results'


class CubeInfo:
    """

    """
    def __init__(self, run_id, name, cube):
        """

        :param run_id:
        :param name:
        :param cube:
        :return:
        """
        self.run_id = run_id
        self.name = name
        self.id = int(cube['cube_id'])
        self.cube = cube


class Assimilator:
    """

    """
    def __init__(self, config, args):
        """

        :param args:
        :return:
        """
        # Be sure to call Assimilator.__init__(self) from child classes

        # HACK: this belongs in boinc_db.py!
        boinc_db.WU_ERROR_NO_CANONICAL_RESULT = 32

        # initialize member vars
        self.boinc_config = None
        self.config = config
        self.STOP_TRIGGER_FILENAME = boinc_project_path.project_path('stop_daemons')
        self.caught_sig_int = False
        self.pass_count = 0
        self.update_db = not args['dont_update_db']
        self.wu_id_mod = args['mod']
        self.wu_id_remainder = args['mod']
        self.one_pass = args['one_pass']
        self.one_pass_N_WU = args['one_pass_N_WU']
        self.appname = args['app']
        self.sleep_interval = args['sleep_interval']

        self.engine = None
        self.connection = None

    def check_stop_trigger(self):
        """
        Stops the daemon when not running in one_pass mode
        There are two cases when the daemon will stop:
           1) if the SIGINT signal is received
           2) if the stop trigger file is present
        """
        try:
            open(self.STOP_TRIGGER_FILENAME, 'r')
        except IOError:
            if self.caught_sig_int:
                LOG.debug("Caught SIGINT")
                sys.exit(1)
        else:
            LOG.debug("Found stop trigger")
            sys.exit(1)

    def sigint_handler(self, sig, stack):
        """
        This method handles the SIGINT signal. It sets a flag
        but waits to exit until check_stop_trigger is called
        """
        LOG.debug("Handled SIGINT")
        self.caught_sig_int = True

    @staticmethod
    def filename_hash(name, hash_fanout):
        """
        Accepts a filename (without path) and the hash fanout.
        Returns the directory bucket where the file will reside.
        The hash fanout is typically provided by the project config file.
        """
        h = hex(int(hashlib.md5(name).hexdigest()[:8], 16) % hash_fanout)[2:]

        # check for the long L suffix. It seems like it should
        # never be present but that isn't the case
        if h.endswith('L'):
            h = h[:-1]
        return h

    @staticmethod
    def copy_files(files, where):
        """
        :param files:
        :param where:
        :return:
        """
        if not os.path.exists(where):
            LOG.info("Not copying, target directory {0} does not exist.".format(where))
            return

        for f in files:
            if os.path.exists(f):
                LOG.info("Copying: {0}\n".format(f))
                shutil.copy(f, where)
            else:
                LOG.info("Not copying {0}. Doesn't exist\n".format(f))

    def get_file_path(self, result):
        """
        Accepts a result object and returns the relative path to the file.
        This method accounts for file hashing and includes the directory
        bucket in the path returned.
        """
        name = re.search('<file_name>(.*)</file_name>', result.xml_doc_in).group(1)
        fanout = int(self.boinc_config.uldl_dir_fanout)
        hashed = self.filename_hash(name, fanout)
        updir = self.boinc_config.upload_dir
        result = os.path.join(updir, hashed, name)
        return result

    @staticmethod
    def get_flat_file_path(directory, name):
        """

        :param directory:
        :param name:
        :return:
        """
        path = os.path.join(directory, name)

        if os.path.isfile(path):
            return path

        path += '.tar.gz'

        if os.path.isfile(path):
            return path

        return None

    def get_cube_info(self, wu_name):
        """
        Run ID (Can be obtained from workunit name)
        Cube ID (Can be obtained from Run ID and workunit name)

        These change for each result:
        Parameter ID (Can be obtained from Run ID and first column in CSV)
        Each of the other rows in the CSV

        Example WU name: 6_askap_cube_1_1_19
        """
        CUBE = self.config['database']['CUBE']

        underscore = wu_name.find('_')

        try:
            run_id = int(wu_name[0:underscore])
        except ValueError:
            raise Exception('Malformed WU name {0}\n'.format(wu_name))

        cube_name = wu_name[underscore + 1:]

        # First column is the cube ID
        cube = self.connection.execute(select([CUBE]).where(and_(CUBE.c.cube_name == cube_name, CUBE.c.run_id == run_id))).first()

        if cube is None:
            raise Exception("Can't find cube {0}\n".format(cube_name))

        return CubeInfo(run_id, cube_name, cube)

    def assimilate_handler(self, wu, results, canonical_result):
        """

        :param wu:
        :param results:
        :param canonical_result:
        :return:
        """
        self.engine = create_engine(self.config['DB_LOGIN'])
        self.connection = self.engine.connect()

        try:
            LOG.info('Starting assimilate handler for work unit: {0}\n'.format(wu.id))

            if not wu.canonical_result:
                LOG.info('No canonical result for wu: {0}\n'.format(wu.id))
                return 0

            canonical_result_file = self.get_file_path(canonical_result)
            cube_info = self.get_cube_info(wu.name)

            if not os.path.isfile(canonical_result_file):
                LOG.info('Canonical result file doesnt exist\n')
                return 0

            retval = self.process_result(wu, canonical_result_file, cube_info)

            if retval == 0:
                result_path = os.path.join(COMPLETED_RESULT_PATH, self.config['APP_NAME'])

                # Successful assimilation, move the the work unit file and all the other result files
                files = [self.get_file_path(r) for r in results]

                self.copy_files(files, result_path)

        finally:
            self.connection.close()

        return retval

    def process_result(self, wu, result_file, cube_info):
        """

        :param wu:
        :param result_file:
        :param cube_info:
        :return:
        """
        LOG.error("Not implemented")

    def report_errors(self, wu):
        """
        Writes error logs based on the workunit (wu) error_mask field.
        Returns True if errors were present, False otherwise.
        """
        if wu.error_mask & boinc_db.WU_ERROR_COULDNT_SEND_RESULT:
            LOG.error("[{0}] Error: couldn't send a result".format(wu.name))
            return True
        if wu.error_mask & boinc_db.WU_ERROR_TOO_MANY_ERROR_RESULTS:
            LOG.error("[{0}] Error: too many error results".format(wu.name))
            return True
        if wu.error_mask & boinc_db.WU_ERROR_TOO_MANY_TOTAL_RESULTS:
            LOG.error("[{0}] Error: too many total results".format(wu.name))
            return True
        if wu.error_mask & boinc_db.WU_ERROR_TOO_MANY_SUCCESS_RESULTS:
            LOG.error("[{0}] Error: too many success results".format(wu.name))
            return True

        return False

    def do_pass(self, app):
        """
        This method scans the database for workunits that need to be
        assimilated. It handles all processing rules passed in on the command
        line, except for -noinsert, which must be handled in assimilate_handler.
        Calls check_stop_trigger before doing any work.
        """

        did_something = False
        # check for stop trigger
        self.check_stop_trigger()
        self.pass_count += 1
        n = 0

        units = database.Workunits.find(app=app, assimilate_state=boinc_db.ASSIMILATE_READY)

        # self.logDebug("pass %d, units %d\n", self.pass_count, len(units))

        # look for workunits with correct appid and
        # assimilate_state==ASSIMILATE_READY
        for wu in units:
            # if the user has turned on the WU mod flag, adhere to it
            if self.wu_id_mod > 0:
                if wu.id % self.wu_id_mod != self.wu_id_remainder:
                    continue

            # track how many jobs have been processed
            # stop if the limit is reached
            n += 1
            if self.one_pass_N_WU > 0 and n > self.one_pass_N_WU:
                return did_something

            # only mark as dirty if the database is modified
            if self.update_db:
                did_something = True

            canonical_result = None
            LOG.debug("[{0}] assimilating: state={1}\n".format(wu.name, wu.assimilate_state))
            results = database.Results.find(workunit=wu)

            # look for canonical result for workunit in results
            for result in results:
                if result == wu.canonical_result:
                    canonical_result = result

            if canonical_result is None and wu.error_mask == 0:
                # If no canonical result found and WU had no other errors,
                # something is wrong, e.g. result records got deleted prematurely.
                # This is probably unrecoverable, so mark the WU as having
                # an assimilation error and keep going.
                wu.error_mask = boinc_db.WU_ERROR_NO_CANONICAL_RESULT
                wu.commit()

            # assimilate handler
            rc = self.assimilate_handler(wu, results, canonical_result)

            # TODO: check for DEFER_ASSIMILATION as a return value from assimilate_handler

            if self.update_db and rc == 0:
                # tag wu as ASSIMILATE_DONE
                wu.assimilate_state = boinc_db.ASSIMILATE_DONE
                wu.transition_time = int(time.time())
                wu.commit()

        # return did something result
        return did_something

    def run(self):
        """
        This function runs the class in a loop unless the
        one_pass or one_pass_WU_N flags are set. Before execution
        parse_args() is called, the xml config file is loaded and
        the SIGINT signal is hooked to the sigint_handler method.
        """
        self.boinc_config = configxml.default_config().config

        # retrieve app where name = app.name
        database.connect()
        app = database.Apps.find1(name=self.appname)
        database.close()

        signal.signal(signal.SIGINT, self.sigint_handler)

        # do one pass or execute main loop
        if self.one_pass:
            self.do_pass(app)
        else:
            # main loop
            while 1:
                database.connect()
                workdone = self.do_pass(app)
                database.close()
                if not workdone:
                    # clogging up the log file and I want to see other debug messages
                    # self.logDebug("Sleeping for {0}\n".format(self.sleep_interval))
                    time.sleep(self.sleep_interval)

        return 0

    def run_flat(self, filename):
        """
        TODO: Implement properly later if needed
        Used to test the assimilator on a file, rather than running it via the assimilate handler
        :param directory:
        :return:
        """
        """
        CUBE = self.config['database']['CUBE']

        database.connect()
        engine = create_engine(self.config['DB_LOGIN'])
        connection = engine.connect()

        # Get all cube names from the DB.
        # For each cube name, get the canonical result from the db and the name of the canonical result path

        units = engine.execute(select([CUBE]).where(CUBE.c.progress == 1))

        LOG.info("Starting flat file processor\n")
        for unit in units:
            n = "10_{0}".format(unit['cube_name'])
            LOG.info('WuName: {0}\n'.format(n))

            wu = database.Workunits.find(name=n)

            if len(wu) == 0:
                LOG.info("Can't find work unit: {0}\n".format(n))
                continue

            wu = wu[0]

            LOG.info('Starting assimilate handler for work unit: {0}\n'.format(wu.name))

            results = database.Results.find(workunit=wu)
            canonical_result = None

            for result in results:
                if result == wu.canonical_result:
                    canonical_result = result
                    break

            if canonical_result is None:
                LOG.info("No canonical result for %s\n", wu.name)
                continue

            name = re.search('<file_name>(.*)</file_name>', canonical_result.xml_doc_in).group(1)

            path = self.get_flat_file_path(filename, name)

            LOG.info("Path: %s\n", path)

            if path is None:
                LOG.info("Canonical result %s doesn't exist in path %s\n", name, directory)
                continue

            # Now assimilate the canonical result
            if self.process_result(wu, path) != 0:
                continue

        self.connection.close()
        database.close()
        """
        return 0


def parse_args():
    """

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=str, required=True, help='The name of the app to use.')
    parser.add_argument('--dont_update_db', action='store_true', default=False, help="Don't update the database.")
    parser.add_argument('--sleep_interval', type=float, default=10, help='Time to sleep before checking if work is available.')
    parser.add_argument('--one_pass', action='store_true', default=False, help='Perform only one pass through the database.')
    parser.add_argument('--one_pass_N_WU', type=int, default=0, help='Process this many work units.')
    parser.add_argument('--mod', type=int, default=0, help='Only process work units with this mod remainder.')
    parser.add_argument('--flat', type=str, default=None, help='Run the assimilator on this file, rather than on pending results')
    args = vars(parser.parse_args())

    return args

if __name__ == "__main__":
    arguments = parse_args()
    app_name = arguments['app']

    mod = module_import(MODULE, app_name)

    # Pass the base class to the module and allow it to produce a subclassed assimilator
    DerivedAssimilator = mod.get_assimilator(Assimilator)
    assimilator = DerivedAssimilator(get_config(app_name), arguments)

    if arguments['flat'] is not None:
        result = assimilator.run_flat(arguments['flat'])
    else:
        result = assimilator.run()

    sys.exit(result)
