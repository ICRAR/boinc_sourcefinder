#! /usr/bin/env python2.7

import os
import sys

# Setup the Python Path as we may be running this via ssh
base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))
sys.path.append(os.path.abspath(os.path.join(base_path, '../..')))
sys.path.append('/home/ec2-user/boinc_sourcefinder/server')

from utils.logging_helper import config_logger
from config import DB_LOGIN
from sqlalchemy import create_engine, select, and_
from database.database_support import CUBE, RESULT
import assimilator
import gzip as gz
import tarfile as tf
import csv
import hashlib

LOG = config_logger(__name__)
LOG.info('PYTHONPATH = {0}'.format(sys.path))

ENGINE = create_engine(DB_LOGIN)

# This represents the valid first row of the csv.
csv_valid_header = ['ParameterNumber','RA','DEC','freq','w_50','w_20','w_FREQ','F_int','F_tot','F_peak','Nvoxel','Nchan','Nspatpix']


class SourcefinderAssimilator(assimilator.Assimilator):

    def __init__(self):
        assimilator.Assimilator.__init__(self)
        self.connection = None

    def hash_filecheck(self, file, hashfile):
        with open(file, 'r') as f:
            m = hashlib.md5()
            m.update(f.read())
            hash = m.digest()

        with open(hashfile, 'r') as f:
            hash_from_file = f.readline()

        self.logNormal('Hash comparison {0} == {1}'.format(hash, hash_from_file))

        return hash == hash_from_file

    def run_test(self, wu, filename):
        """
        Used to test the assimilator on a file, rather than running it via the assimilate handler
        :param filename:
        :return:
        """

        self.process_result(wu, filename)

    def assimilate_handler(self, wu, results, canonical_result):
        self.logNormal('Starting assimilate handler for work unit: {0}'.format(wu.id))

        if not wu.canonical_result:
            self.logDebug('No canonical result for wu: {0}'.format(wu.id))
            return 0

        out_file = self.get_file_path(canonical_result)

        if os.path.isfile(out_file):
            self.logNormal('WU file at {0}'.format(out_file))
        else:
            self.logCritical('WU file does exist')
            return 0

        self.connection = ENGINE.connect()
        retval = self.process_result(wu, out_file)
        self.connection.close()

        return retval

    def process_result(self, wu, file):

        path = os.path.dirname(file)
        # File exists, good to start handling it.

        if tf.is_tarfile(file):
            # It's tar'd
            tar = tf.open(file)
            tar.extractall(path)
            tar.close()

        # CSV file should exist, confirm this
        fs = os.listdir(path)
        file_to_use = None
        hashfile = None

        for f in fs:
            if f.endswith('.csv'):
                file_to_use = f
            if f.lower().endswith('.md5'):
                hashfile = f

        if file_to_use is None:
            self.logCritical('Client uploaded a WU file, but it does not contain the required CSV file. Cannot assimilate.')
            self.logDebug('The following files were included: ')
            for f in fs:
                self.logDebug('{0}'.format(f))

            return 0

        # Confirm the CSV MD5 here
        if not self.hash_filecheck(file_to_use, hashfile):
            self.logCritical('Hash file check failed on work unit {0}'.format(wu.id))
            self.logCritical('Continuing anyway...')
            # exit? I'm not sure.

        # The CSV is there, final check is that it contains the correct header (first row) that we want

        with open(file_to_use) as f:
            csv_reader = csv.DictReader(f)
            headers = csv_reader.fieldnames

            for i in range(0, len(headers)):
                if headers[i].strip() != csv_valid_header[i]:
                    self.logCritical('Received CSV is in the wrong format. Field {0}: {1} does not match {2}'.format(i, headers[i], csv_valid_header[i]))
                    return 0

            # CSV is good from here

            # These stay constant for all of the results:
            # Run ID (Can be obtained from workunit name)
            # Cube ID (Can be obtained from Run ID and workunit name)

            # These change for each result:
            # Parameter ID (Can be obtained from Run ID and first column in CSV)
            # Each of the other rows in the CSV

            # Example WU name: 6_askap_cube_1_1_19

            try:
                run_id = int(wu.name[0])
            except ValueError:
                self.logCritical('Malformed WU name {0}'.format(wu.name))
                return 0

            cube_name = wu.name[2:]

            # First column is the cube ID
            cube_id = self.connection.execute(select([CUBE]).where(and_(CUBE.c.cube_name == cube_name, CUBE.c.run_id == run_id))).first()[0]

            # Row 1 is header
            rowcount = 1
            transaction = self.connection.begin()
            for row in csv_reader:
                rowcount += 1
                try:
                    self.connection.execute(
                            RESULT.insert(),
                            cube_id=cube_id,
                            parameter_id=int(row['ParameterNumber']),
                            run_id=run_id,
                            RA=row['RA'],
                            DEC=row['DEC'],
                            freq=row['freq'],
                            w_50=row['w_50'],
                            w_20=row['w_20'],
                            w_FREQ=row['w_FREQ'],
                            F_int=row['F_int'],
                            F_tot=row['F_tot'],
                            F_peak=row['F_peak'],
                            Nvoxel=row['Nvoxel'],
                            Nchan=row['Nchan'],
                            Nspatpix=row['Nspatpix']
                    )
                except ValueError:
                    self.logCritical('Malformed CSV. Parameter number for row {0} is invalid'.format(rowcount))
                except csv.Error as e:
                    self.logCritical('Malformed CSV. Error on line {0}: {1}'.format(csv_reader.line_num, e))
                except:
                    self.logCritical('Undefined error occurred while attempting to load CSV.')
            transaction.commit()

            self.logNormal('Successfully loaded work unit {0} in to the database'.format(wu.name))

            # Here is where we'd copy the CSV in an S3 bucket

            return 0

# --------------------------------------------
# Add the following to your assimilator file:

if __name__ == '__main__':
    asm = SourcefinderAssimilator()
    asm.run()

