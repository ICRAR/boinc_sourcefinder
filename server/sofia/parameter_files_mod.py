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
Module to generate parameter files for Sofia
"""
import itertools
from utils.logger import config_logger

LOG = config_logger(__name__)

INPUT_FILE = "/root/shared/input.fits"
OUTPUT_DIR = "/root/shared/output/"


class ConfigItem:
    def __init__(self, format, possible_values):
        self.format = format

        if type(possible_values) != list:
            possible_values = [possible_values]

        self.possible_values = possible_values

    def __getitem__(self, item):
        return self.possible_values[item]

    def __len__(self):
        return len(self.possible_values)

    def __iter__(self):
        return iter(self.possible_values)

SOFIA_CONFIG = [
    ConfigItem("steps.doSubcube = {0}", "false"),
    ConfigItem("steps.doFlag = {0}", "false"),
    ConfigItem("steps.doSmooth = {0}", "false"),
    ConfigItem("steps.doScaleNoise = {0}", "false"),
    ConfigItem("steps.doSCfind = {0}", "true"),
    ConfigItem("steps.doThreshold = {0}", "false"),
    ConfigItem("steps.doWavelet = {0}", "false"),
    ConfigItem("steps.doCNHI = {0}", "false"),
    ConfigItem("steps.doMerge = {0}", "true"),
    ConfigItem("steps.doReliability = {0}", "true"),
    ConfigItem("steps.doParameterise = {0}", "true"),
    ConfigItem("steps.doWriteFilteredCube = {0}", "false"),
    ConfigItem("steps.doWriteMask = {0}", "false"),
    ConfigItem("steps.doWriteCat = {0}", "true"),
    ConfigItem("steps.doMom0 = {0}", "false"),
    ConfigItem("steps.doMom1 = {0}", "false"),
    ConfigItem("steps.doCubelets = {0}", "false"),
    ConfigItem("steps.doDebug = {0}", "false"),
    ConfigItem("steps.doOptical = {0}", "false"),

    ConfigItem("import.inFile = {0}", INPUT_FILE),
    ConfigItem("import.weightsFile = {0}", ""),
    ConfigItem("import.maskFile = {0}", ""),
    ConfigItem("import.weightsFunction = {0}", ""),
    ConfigItem("import.subcube = {0}", "[]"),
    ConfigItem("import.subcubeMode = {0}", "pixel"),

    ConfigItem("flag.regions = {0}", "[]"),

    ConfigItem("optical.sourceCatalogue = {0}", ""),
    ConfigItem("optical.spatSize = {0}", "0.01"),
    ConfigItem("optical.specSize = {0}", "1e+5"),
    ConfigItem("optical.storeMultiCat = {0}", "false"),

    ConfigItem("smooth.kernel = {0}", "gaussian"),
    ConfigItem("smooth.edgeMode = {0}", "constant"),
    ConfigItem("smooth.kernelX = {0}", "3.0"),
    ConfigItem("smooth.kernelY = {0}", "3.0"),
    ConfigItem("smooth.kernelZ = {0}", "3.0"),

    ConfigItem("scaleNoise.statistic = {0}", "mad"),
    ConfigItem("scaleNoise.scaleX = {0}", "false"),
    ConfigItem("scaleNoise.scaleY = {0}", "false"),
    ConfigItem("scaleNoise.scaleZ = {0}", "true"),
    ConfigItem("scaleNoise.edgeX = {0}", "0"),
    ConfigItem("scaleNoise.edgeY = {0}", "0"),
    ConfigItem("scaleNoise.edgeZ = {0}", "0"),

    ConfigItem("wavelet.threshold = {0}", "5.0"),
    ConfigItem("wavelet.scaleXY = {0}", "-1"),
    ConfigItem("wavelet.scaleZ = {0}", "-1"),
    ConfigItem("wavelet.positivity = {0}", "false"),
    ConfigItem("wavelet.iterations = {0}", "3"),

    ConfigItem("SCfind.threshold = {0}", ["3.0", "4.0", "5.0"]),
    ConfigItem("SCfind.sizeFilter = {0}", "0.0"),
    ConfigItem("SCfind.maskScaleXY = {0}", "2.0"),
    ConfigItem("SCfind.maskScaleZ = {0}", "2.0"),
    ConfigItem("SCfind.edgeMode = {0}", "constant"),
    ConfigItem("SCfind.rmsMode = {0}", "negative"),
    ConfigItem("SCfind.kernels = {0}", ["[[0, 0, 0, 'b'], [0, 0, 3, 'b'], [0, 0, 7, 'b'], [0, 0, 15, 'b'], [3, 3, 0, 'b'], [3, 3, 3, 'b'], [3, 3, 7, 'b'], [3, 3, 15, 'b'], [6, 6, 0, 'b'], [6, 6, 3, 'b'], [6, 6, 7, 'b'], [6, 6, 15, 'b']]",
                                  "[[0, 0, 0, 'b'], [0, 0, 3, 'b'], [0, 0, 7, 'b'], [0, 0, 15, 'b'], [0, 0, 31, 'b'], [0, 0, 63, 'b'], [3, 3, 0, 'b'], [3, 3, 3, 'b'], [3, 3, 7, 'b'], [3, 3, 15, 'b'], [3, 3, 31, 'b'], [3, 3, 63, 'b']]",
                                  "[[0, 0, 0, 'b'], [0, 0, 3, 'b'], [0, 0, 7, 'b'], [3, 3, 0, 'b'], [3, 3, 3, 'b'], [3, 3, 7, 'b'], [6, 6, 0, 'b'], [6, 6, 3, 'b'], [6, 6, 7, 'b'], [10, 10, 0, 'b'], [10, 10, 3, 'b'], [10, 10, 7, 'b']]"]),
    ConfigItem("SCfind.kernelUnit = {0}", "pixel"),
    ConfigItem("SCfind.verbose = {0}", "true"),

    ConfigItem("CNHI.pReq = {0}", "1e-5"),
    ConfigItem("CNHI.qReq = {0}", "3.8"),
    ConfigItem("CNHI.minScale = {0}", "5"),
    ConfigItem("CNHI.maxScale = {0}", "-1"),
    ConfigItem("CNHI.medianTest = {0}", "true"),
    ConfigItem("CNHI.verbose = {0}", "1"),

    ConfigItem("threshold.threshold = {0}", "4.0"),
    ConfigItem("threshold.clipMethod = {0}", "relative"),
    ConfigItem("threshold.rmsMode = {0}", "std"),
    ConfigItem("threshold.verbose = {0}", "false"),

    ConfigItem("merge.radiusX = {0}\nmerge.radiusY = {0}\nmerge.radiusZ = {0}", ["1", "3", "5"]),
    ConfigItem("merge.minSizeX = {0}\nmerge.minSizeY = {0}\nmerge.minSizeZ = {0}", ["3", "5", "10"]),
    ConfigItem("merge.positivity = {0}", "false"),

    ConfigItem("parameters.fitBusyFunction = {0}", "false"),
    ConfigItem("parameters.optimiseMask = {0}", "false"),
    ConfigItem("parameters.dilateMask = {0}", ["true", "false"]),
    ConfigItem("parameters.dilateThreshold = {0}", "0.02"),
    ConfigItem("parameters.dilatePixMax = {0}", "10"),
    ConfigItem("parameters.dilateChan = {0}", "1"),

    ConfigItem("reliability.parSpace = {0}", "['n_pix','snr_sum','snr_max']"),
    ConfigItem("reliability.logPars = {0}", "[1,1,1]"),
    ConfigItem("reliability.autoKernel = {0}", "true"),
    ConfigItem("reliability.scaleKernel = {0}", ["0.4", "0.5", "0.6"]),
    ConfigItem("reliability.usecov = {0}", "true"),
    ConfigItem("reliability.negPerBin = {0}", "1.0"),
    ConfigItem("reliability.skellamTol = {0}", "-0.5"),
    ConfigItem("reliability.kernel = {0}", "[0.15,0.05,0.1]"),
    ConfigItem("reliability.fMin = {0}", "10.0"),
    ConfigItem("reliability.threshold = {0}", "0.5"),
    ConfigItem("reliability.makePlot = {0}", "false"),

    ConfigItem("writeCat.overwrite = {0}", "true"),
    ConfigItem("writeCat.compress = {0}", "false"),
    ConfigItem("writeCat.outputDir = {0}", OUTPUT_DIR),
    ConfigItem("writeCat.basename = {0}", "sofia_output_{0}"),
    ConfigItem("writeCat.writeASCII = {0}", "false"),
    ConfigItem("writeCat.writeXML = {0}", "true"),
    ConfigItem("writeCat.writeSQL = {0}", "false"),
    ConfigItem("writeCat.parameters = {0}", "['*']")
]


def get_parameter_file_generator(base_class):

    class SofiaParameterFileGenerator(base_class):

        def create_parameter_file_data(self):
            items = []

            for file_count, config in enumerate(itertools.product(*SOFIA_CONFIG)):
                filename = 'supercube_run_{0}_sofia.par'.format(file_count)
                config_string = "# SoFiA Config for sourcefinder: {0}\n".format(filename)

                for idx, field in enumerate(config):
                    field_format = SOFIA_CONFIG[idx].name
                    output = field

                    if field_format.startswith("writeCat.basename"):
                        # Set an incrementing number for the output file name.
                        output = field.format(file_count)

                    config_string += "{0}\n".format(SOFIA_CONFIG[idx].format.format(output))

                items.append((filename, config_string))

            return items

    return SofiaParameterFileGenerator
