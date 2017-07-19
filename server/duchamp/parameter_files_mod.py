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
from utils.logger import config_logger

LOG = config_logger(__name__)


def get_parameter_file_generator(base_class):

    class DuchampParameterFileGenerator(base_class):

        def create_parameter_file_data(self):
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

    return DuchampParameterFileGenerator
