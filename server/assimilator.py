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
import sys
import time
import argparse

from config import get_config
from utils import module_import
from utils.logger import config_logger

from Boinc import database, boinc_db, boinc_project_path, configxml

MODULE = "assimilator_mod"
LOG = config_logger(__name__)


class Assimilator:
    """
    Use this class to create new pure-Python Assimilators.
    To create a new assimilator:
      1) call __init__ from the new child class' __init__ method
      2) override the assimilate_handler method
      3) add the standard if __name__ == "__main__" bootstrap (see end of this file)
    """

    def __init__(self, args):
        # Be sure to call Assimilator.__init__(self) from child classes

        # HACK: this belongs in boinc_db.py!
        boinc_db.WU_ERROR_NO_CANONICAL_RESULT = 32

        # initialize member vars
        self.config = None
        self.STOP_TRIGGER_FILENAME = boinc_project_path.project_path('stop_daemons')
        self.caught_sig_int = False
        self.pass_count = 0
        self.update_db = False if args['dont_update_db'] else True
        self.noinsert = args['noinsert'] or False
        self.wu_id_mod = args['mod'] or 0
        self.wu_id_remainder = args['mod'] or 0
        self.one_pass = args['one_pass'] or False
        self.one_pass_N_WU = args['one_pass_N_WU'] or 0
        self.appname = args['app']
        self.sleep_interval = args['sleep_interval'] or 10

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

    def get_file_path(self, result):
        """
        Accepts a result object and returns the relative path to the file.
        This method accounts for file hashing and includes the directory
        bucket in the path returned.
        """
        name = re.search('<file_name>(.*)</file_name>', result.xml_doc_in).group(1)
        fanout = int(self.config.uldl_dir_fanout)
        hashed = self.filename_hash(name, fanout)
        updir = self.config.upload_dir
        result = os.path.join(updir, hashed, name)
        return result

    def assimilate_handler(self, wu, results, canonical_result):
        """
        This method is called for each workunit (wu) that needs to be
        processed. A canonical result is not guarenteed and several error
        conditions may be present on the wu. Call report_errors(wu) when
        overriding this method.

        Note that the -noinsert flag (self.noinsert) must be accounted for when
        overriding this method.
        """
        LOG.error("Handler not implemented.")

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

    def __call__(self):
        """
        This function runs the class in a loop unless the
        one_pass or one_pass_WU_N flags are set. Before execution
        parse_args() is called, the xml config file is loaded and
        the SIGINT signal is hooked to the sigint_handler method.
        """
        self.config = configxml.default_config().config

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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-app', nargs=1, help='The name of the app to use.')
    parser.add_argument('-sleep_interval', type=float, help='Time to sleep before checking if work is available')
    parser.add_argument('-one_pass', type=bool, help='Perform only one pass through the database')
    parser.add_argument('-one_pass_N_WU', type=int, help='Process this many work units')
    parser.add_argument('-noinsert', type=bool, help="Don't perform inserts in to the database")
    parser.add_argument('-dont_update_db', type=bool, help="Don't update the database")
    parser.add_argument('-mod', type=int, help="Only process work units with this mod remainder")
    args = vars(parser.parse_args())

    return args

if __name__ == "__main__":
    arguments = parse_args()
    app_name = arguments['app'][0]
    if app_name is None:
        LOG.error("Specify an app name")
        exit(1)

    mod = module_import(MODULE, app_name)
    LOG.debug("Loading module {0}.{1}".format(app_name, MODULE))

    if mod is None:
        LOG.error("Could not load module {0}.{1}".format(app_name, MODULE))
        exit(1)

    # Pass the base class to the module and allow it to produce a subclassed assimilator
    DerivedAssimilator = mod.get_assimilator(Assimilator)
    assimilator = DerivedAssimilator(get_config(app_name), arguments)

    exit(assimilator())