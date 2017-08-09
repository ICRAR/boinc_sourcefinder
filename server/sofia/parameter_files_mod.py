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
    def __init__(self, name, possible_values):
        self.name = name

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
    ConfigItem("steps.doSubcube", "false"),
    ConfigItem("steps.doFlag", "false"),
    ConfigItem("steps.doSmooth", ["false", "true"]),
    ConfigItem("steps.doScaleNoise", "false"),
    ConfigItem("steps.doSCfind", "true"),
    ConfigItem("steps.doThreshold", "false"),
    ConfigItem("steps.doWavelet", "false"),
    ConfigItem("steps.doCNHI", "false"),
    ConfigItem("steps.doMerge", ["false", "true"]),
    ConfigItem("steps.doReliability",  ["false", "true"]),
    ConfigItem("steps.doParameterise",  ["false", "true"]),
    ConfigItem("steps.doWriteFilteredCube",  "false"),
    ConfigItem("steps.doWriteMask",  "false"),
    ConfigItem("steps.doWriteCat",  "true"),
    ConfigItem("steps.doMom0", "false"),
    ConfigItem("steps.doMom1", "false"),
    ConfigItem("steps.doCubelets", "false"),
    ConfigItem("steps.doDebug", "false"),
    ConfigItem("steps.doOptical", "false"),

    ConfigItem("import.inFile", INPUT_FILE),
    ConfigItem("import.weightsFile", ""),
    ConfigItem("import.maskFile", ""),
    ConfigItem("import.weightsFunction", ""),
    ConfigItem("import.subcube", "[]"),
    ConfigItem("import.subcubeMode", "pixel"),

    ConfigItem("flag.regions", "[]"),

    ConfigItem("optical.sourceCatalogue", ""),
    ConfigItem("optical.spatSize", "0.01"),
    ConfigItem("optical.specSize", "1e+5"),
    ConfigItem("optical.storeMultiCat", "false"),

    ConfigItem("smooth.kernel", "gaussian"),
    ConfigItem("smooth.edgeMode", "constant"),
    ConfigItem("smooth.kernelX", "3.0"),
    ConfigItem("smooth.kernelY", "3.0"),
    ConfigItem("smooth.kernelZ", "3.0"),

    ConfigItem("scaleNoise.statistic", "mad"),
    ConfigItem("scaleNoise.scaleX", "false"),
    ConfigItem("scaleNoise.scaleY", "false"),
    ConfigItem("scaleNoise.scaleZ", "true"),
    ConfigItem("scaleNoise.edgeX", "0"),
    ConfigItem("scaleNoise.edgeY", "0"),
    ConfigItem("scaleNoise.edgeZ", "0"),

    ConfigItem("wavelet.threshold", "5.0"),
    ConfigItem("wavelet.scaleXY", "-1"),
    ConfigItem("wavelet.scaleZ", "-1"),
    ConfigItem("wavelet.positivity", "false"),
    ConfigItem("wavelet.iterations", "3"),

    ConfigItem("SCfind.threshold", "6.0"),
    ConfigItem("SCfind.sizeFilter", "0.0"),
    ConfigItem("SCfind.maskScaleXY", "2.0"),
    ConfigItem("SCfind.maskScaleZ", "2.0"),
    ConfigItem("SCfind.edgeMode", "constant"),
    ConfigItem("SCfind.rmsMode", "negative"),
    ConfigItem("SCfind.kernels", "[[ 0, 0, 0,'b'],[ 0, 0, 3,'b'],[ 0, 0, 7,'b'],[ 0, 0, 15,'b'],[ 3, 3, 0,'b'],[ 3, 3, 3,'b'],[ 3, 3, 7,'b'],[ 3, 3, 15,'b'],[ 6, 6, 0,'b'],[ 6, 6, 3,'b'],[ 6, 6, 7,'b'],[ 6, 6, 15,'b']]"),
    ConfigItem("SCfind.kernelUnit", "pixel"),
    ConfigItem("SCfind.verbose", "true"),

    ConfigItem("CNHI.pReq", "1e-5"),
    ConfigItem("CNHI.qReq", "3.8"),
    ConfigItem("CNHI.minScale", "5"),
    ConfigItem("CNHI.maxScale", "-1"),
    ConfigItem("CNHI.medianTest", "true"),
    ConfigItem("CNHI.verbose", "1"),

    ConfigItem("threshold.threshold", "4.0"),
    ConfigItem("threshold.clipMethod", "relative"),
    ConfigItem("threshold.rmsMode", "std"),
    ConfigItem("threshold.verbose", "false"),

    ConfigItem("merge.radiusX", "3"),
    ConfigItem("merge.radiusY", "3"),
    ConfigItem("merge.radiusZ", "3"),
    ConfigItem("merge.minSizeX", "3"),
    ConfigItem("merge.minSizeY", "3"),
    ConfigItem("merge.minSizeZ", "2"),
    ConfigItem("merge.positivity", "false"),

    ConfigItem("parameters.fitBusyFunction", "false"),
    ConfigItem("parameters.optimiseMask", "false"),
    ConfigItem("parameters.dilateMask", "false"),
    ConfigItem("parameters.dilateThreshold", "0.02"),
    ConfigItem("parameters.dilatePixMax", "10"),
    ConfigItem("parameters.dilateChan", "1"),

    ConfigItem("reliability.parSpace", "['n_pix','snr_sum','snr_max']"),
    ConfigItem("reliability.logPars", "[1,1,1]"),
    ConfigItem("reliability.autoKernel", "true"),
    ConfigItem("reliability.scaleKernel", "0.5"),
    ConfigItem("reliability.usecov", "true"),
    ConfigItem("reliability.negPerBin", "1.0"),
    ConfigItem("reliability.skellamTol", "-0.5"),
    ConfigItem("reliability.kernel", "[0.15,0.05,0.1]"),
    ConfigItem("reliability.fMin", "10.0"),
    ConfigItem("reliability.threshold", "0.9"),
    ConfigItem("reliability.makePlot", "false"),

    ConfigItem("writeCat.overwrite", "true"),
    ConfigItem("writeCat.compress", "false"),
    ConfigItem("writeCat.outputDir", OUTPUT_DIR),
    ConfigItem("writeCat.basename", "sofia_output_{0}"),
    ConfigItem("writeCat.writeASCII", "true"),
    ConfigItem("writeCat.writeXML", "false"),
    ConfigItem("writeCat.writeSQL", "false"),
    ConfigItem("writeCat.parameters", "['*']")
]


def get_parameter_file_generator(base_class):

    class SofiaParameterFileGenerator(base_class):

        def create_parameter_file_data(self):
            file_count = 0

            items = []

            for config in itertools.product(*SOFIA_CONFIG):
                filename = 'supercube_run_{0}_sofia.par'.format(file_count)
                file_count += 1

                config_string = "# SoFiA Config for sourcefinder: {0}\n".format(filename)

                for idx, field in enumerate(config):
                    field_name = SOFIA_CONFIG[idx].name
                    output = field

                    if field_name == "writeCat.basename":
                        # Set an incrementing number for the output file name.
                        output = field.format(file_count)

                    config_string += "{0}   =   {1}\n".format(SOFIA_CONFIG[idx].name, output)

                items.append((filename, config_string))

            return items

    return SofiaParameterFileGenerator
