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
Module to generate parameter files for Duchamp
"""
import os
from ..utils.logger import config_logger
from sqlalchemy.engine import create_engine
from sqlalchemy import select

LOG = config_logger(__name__)


class ParameterFileGenerator:

    def __init__(self, config):
        self.config = config
        self.engine = None
        self.connection = None

    @staticmethod
    def create_parameter_file_data():
        """
        This is fairly ghastly at the moment, but it's used so infrequently that there's not much point of making it
        better.
        :return:
        """
        # fixed parameters
        ImageFile = 'input.fits'
        flagRejectbeforeMerge = 'true'
        flagATrous = 'true'
        flagAdjacent = 'true'

        # variable parameters
        outname = 'duchamp-output'  # !!!!! This needs to be the same name all the time and not altered below
        threshold = [2, 3, 4, 5]  # this is the threshold in sigma
        sigma = 86e-6

        for i in range(0, len(threshold)):
            # noinspection PyAugmentAssignment
            threshold[i] = threshold[i] * sigma

        reconDim = [1, 3]
        snrRecon = [1, 2]
        scaleMin = [2, 3]
        minPix = [10]
        minChan = [3, 5]
        flagGrowth = [1, 0]  # grow the sources
        growthThreshold = [1, 2]  # this is the grow-threshold in sigma

        for i in range(0, len(growthThreshold), 1):
            # noinspection PyAugmentAssignment
            growthThreshold[i] = growthThreshold[i] * sigma

        counter = 0

        parameters = {}
        for i in range(0, len(threshold), 1):
            for j in range(0, len(reconDim), 1):
                for k in range(0, len(snrRecon), 1):
                    for l in range(0, len(scaleMin), 1):
                        for m in range(0, len(minPix), 1):
                            for n in range(0, len(minChan), 1):
                                for o in range(0, len(flagGrowth), 1):

                                    if flagGrowth[o] == 1:
                                        for p in range(0, len(growthThreshold), 1):
                                            if growthThreshold[p] < threshold[i]:
                                                counter += 1
                                                parfile = 'supercube_run' + '_' + str(counter) + '.par'

                                                if counter < 10000:
                                                    parfile = 'supercube_run' + '_0' + str(counter) + '.par'
                                                if counter < 1000:
                                                    parfile = 'supercube_run' + '_00' + str(counter) + '.par'
                                                if counter < 100:
                                                    parfile = 'supercube_run' + '_000' + str(counter) + '.par'
                                                if counter < 10:
                                                    parfile = 'supercube_run' + '_0000' + str(counter) + '.par'

                                                fileText = 'ImageFile              ' + ImageFile + '\n' + \
                                                           'outFile                ' + outname + '_' + parfile + '\n' + \
                                                           'flagSeparateHeader      true \n' + \
                                                           'flagRejectBeforeMerge  ' + flagRejectbeforeMerge + '\n' + \
                                                           'flagATrous             ' + flagATrous + '\n' + \
                                                           'flagAdjacent           ' + flagAdjacent + '\n' + \
                                                           'threshold              ' + str(threshold[i]) + '\n' + \
                                                           'reconDim               ' + str(reconDim[j]) + '\n' + \
                                                           'snrRecon               ' + str(snrRecon[k]) + '\n' + \
                                                           'scaleMin               ' + str(scaleMin[l]) + '\n' + \
                                                           'minPix                 ' + str(minPix[m]) + '\n' + \
                                                           'minChannels            ' + str(minChan[n]) + '\n' + \
                                                           'flagGrowth              true \n' + \
                                                           'growthThreshold        ' + str(growthThreshold[p]) + '\n'
                                                parameters[parfile] = fileText

                                    if flagGrowth[o] == 0:
                                        counter += 1
                                        parfile = 'supercube_run' + '_' + str(counter) + '.par'

                                        if counter < 10000:
                                            parfile = 'supercube_run' + '_0' + str(counter) + '.par'
                                        if counter < 1000:
                                            parfile = 'supercube_run' + '_00' + str(counter) + '.par'
                                        if counter < 100:
                                            parfile = 'supercube_run' + '_000' + str(counter) + '.par'
                                        if counter < 10:
                                            parfile = 'supercube_run' + '_0000' + str(counter) + '.par'

                                        fileText = 'ImageFile              ' + ImageFile + '\n' + \
                                                   'outFile                ' + outname + '_' + parfile + '\n' + \
                                                   'flagSeparateHeader      true \n' + \
                                                   'flagRejectBeforeMerge  ' + flagRejectbeforeMerge + '\n' + \
                                                   'flagATrous             ' + flagATrous + '\n' + \
                                                   'flagAdjacent           ' + flagAdjacent + '\n' + \
                                                   'threshold              ' + str(threshold[i]) + '\n' + \
                                                   'reconDim               ' + str(reconDim[j]) + '\n' + \
                                                   'snrRecon               ' + str(snrRecon[k]) + '\n' + \
                                                   'scaleMin               ' + str(scaleMin[l]) + '\n' + \
                                                   'minPix                 ' + str(minPix[m]) + '\n' + \
                                                   'minChannels            ' + str(minChan[n]) + '\n' + \
                                                   'flagGrowth              false \n'

                                        parameters[parfile] = fileText

        return parameters

    def create_parameter_files(self, file_data):
        parameter_file = self.config["DIR_PARAM"]
        for k, v in file_data.iteritems():
            with open(os.path.join(parameter_file, k), 'w') as new_file:
                new_file.write(v)

    def register_parameter_files(self, file_data):
        PARAMETER_FILE = self.config["database_duchamp"]["PARAMETER_FILE"]

        transaction = self.connection.begin()
        try:
            for k, v in file_data.iteritems():
                check = self.connection.execute(select([PARAMETER_FILE]).where(PARAMETER_FILE.c.parameter_file_name == k))
                result = check.fetchone()

                if not result:
                    LOG.info("Registering file: {0}".format(k))
                    self.connection.execute(PARAMETER_FILE.insert(), parameter_file_name=k)
            transaction.commit()
        except Exception as e:
            transaction.rollback()
            raise e

    def __call__(self, add_to_db):
        self.engine = create_engine(self.config["DB_LOGIN"])
        self.connection = self.engine.connect()

        if not os.path.exists(self.config["DIR_PARAM"]):
            os.makedirs(self.config["DIR_PARAM"])

        try:
            file_data = self.create_parameter_file_data()

            self.create_parameter_files(file_data)
            if add_to_db:
                self.register_parameter_files(file_data)

        except Exception:
            LOG.exception("Database error")

            return 1
        finally:
            self.connection.close()

        return 0
