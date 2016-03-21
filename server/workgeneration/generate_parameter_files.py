#! /usr/bin/env python# A script to create parameter files with a predefined set of parameters - script originally called generate_parameter_files.py, written by Attilla Poppingimport argparseimport osimport sysbase_path = os.path.dirname(__file__)sys.path.append(os.path.abspath(os.path.join(base_path, '..')))from utils.logging_helper import config_loggerfrom config import DIR_PARAMLOGGER = config_logger(__name__)LOGGER.info('Starting generate_parameter_files.py')LOGGER.info('PYTHONPATH = {0}'.format(sys.path))parser = argparse.ArgumentParser()parser.add_argument('run_id', nargs=1, help='The id of the current run')args = vars(parser.parse_args())RUN_ID = args['run_id'][0]# create a directory of the files with the run_idparameter_file_directory = DIR_PARAM + '/parameter_files_' + RUN_IDif os.path.exists(parameter_file_directory):    LOGGER.info('Run already exists for RUN_ID {0}'.format(RUN_ID))    exit(1)else:    os.makedirs(parameter_file_directory)    os.chdir(parameter_file_directory)# fixed parametersImageFile = 'input.fits'flagRejectbeforeMerge = 'true'flagATrous = 'true'flagAdjacent = 'true'# variable parametersoutname = 'duchamp-output'  # !!!!! This needs to be the same name all the time and not altered belowthreshold = [2, 3, 4, 5]  # this is the threshold in sigmasigma = 86e-6for i in range(0, len(threshold), 1):    # noinspection PyAugmentAssignment    threshold[i] = threshold[i] * sigmareconDim = [1, 3]snrRecon = [1, 2]scaleMin = [2, 3]minPix = [10]minChan = [3, 5]flagGrowth = [1, 0]  # grow the sourcesgrowthThreshold = [1, 2]  # this is the grow-threshold in sigmafor i in range(0, len(growthThreshold), 1):    # noinspection PyAugmentAssignment    growthThreshold[i] = growthThreshold[i] * sigmacounter = 0parameters = dict()  # !!!!!!!! The name of this variable is important - needs to be "parameters"for i in range(0, len(threshold), 1):    for j in range(0, len(reconDim), 1):        for k in range(0, len(snrRecon), 1):            for l in range(0, len(scaleMin), 1):                for m in range(0, len(minPix), 1):                    for n in range(0, len(minChan), 1):                        for o in range(0, len(flagGrowth), 1):                            if flagGrowth[o] == 1:                                for p in range(0, len(growthThreshold), 1):                                    if growthThreshold[p] < threshold[i]:                                        counter += 1                                        parfile = 'supercube_run' + '_' + str(counter) + '.par'                                        if counter < 10000:                                            parfile = 'supercube_run' + '_0' + str(counter) + '.par'                                        if counter < 1000:                                            parfile = 'supercube_run' + '_00' + str(counter) + '.par'                                        if counter < 100:                                            parfile = 'supercube_run' + '_000' + str(counter) + '.par'                                        if counter < 10:                                            parfile = 'supercube_run' + '_0000' + str(counter) + '.par'                                        fileText = 'ImageFile              ' + ImageFile + '\n' + \                                                   'outFile                ' + outname + '_' + parfile + '\n' + \                                                   'flagSeparateHeader      true \n' + \                                                   'flagRejectBeforeMerge  ' + flagRejectbeforeMerge + '\n' + \                                                   'flagATrous             ' + flagATrous + '\n' + \                                                   'flagAdjacent           ' + flagAdjacent + '\n' + \                                                   'threshold              ' + str(threshold[i]) + '\n' + \                                                   'reconDim               ' + str(reconDim[j]) + '\n' + \                                                   'snrRecon               ' + str(snrRecon[k]) + '\n' + \                                                   'scaleMin               ' + str(scaleMin[l]) + '\n' + \                                                   'minPix                 ' + str(minPix[m]) + '\n' + \                                                   'minChannels            ' + str(minChan[n]) + '\n' + \                                                   'flagGrowth              true \n' + \                                                   'growthThreshold        ' + str(growthThreshold[p]) + '\n'                                        parameters[parfile] = fileText                            if flagGrowth[o] == 0:                                counter += 1                                parfile = 'supercube_run' + '_' + str(counter) + '.par'                                if counter < 10000:                                    parfile = 'supercube_run' + '_0' + str(counter) + '.par'                                if counter < 1000:                                    parfile = 'supercube_run' + '_00' + str(counter) + '.par'                                if counter < 100:                                    parfile = 'supercube_run' + '_000' + str(counter) + '.par'                                if counter < 10:                                    parfile = 'supercube_run' + '_0000' + str(counter) + '.par'                                fileText = 'ImageFile              ' + ImageFile + '\n' + \                                           'outFile                ' + outname + '_' + parfile + '\n' + \                                           'flagSeparateHeader      true \n' + \                                           'flagRejectBeforeMerge  ' + flagRejectbeforeMerge + '\n' + \                                           'flagATrous             ' + flagATrous + '\n' + \                                           'flagAdjacent           ' + flagAdjacent + '\n' + \                                           'threshold              ' + str(threshold[i]) + '\n' + \                                           'reconDim               ' + str(reconDim[j]) + '\n' + \                                           'snrRecon               ' + str(snrRecon[k]) + '\n' + \                                           'scaleMin               ' + str(scaleMin[l]) + '\n' + \                                           'minPix                 ' + str(minPix[m]) + '\n' + \                                           'minChannels            ' + str(minChan[n]) + '\n' + \                                           'flagGrowth              false \n'                                parameters[parfile] = fileText# Print the dictionaryfor k, v in parameters.iteritems():    filename = k    LOGGER.info('creating file {0}'.format(filename))    with open(filename, 'w') as newfile:        newfile.write(v)