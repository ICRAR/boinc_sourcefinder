__author__ = '21298244'

# Helper file for the work generator

import hashlib
import os, sys

import py_boinc
from utils.logging_helper import config_logger

base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))

from config import  DIR_CUBE, DIR_PARAM
from database.database_support import PARAMETER_RUN, PARAMETER_FILE
from sqlalchemy import select
import tarfile
from database.database_support import CUBE
import shutil

LOGGER = config_logger(__name__)
LOGGER.info("work_generator_mod.py")


def get_cube_path(cube_name):
    """
    Returns a path to a cube.fits.gz file from the cube's name.
    :param cube_name: Name of the cube
    :return: the path to the cube, or None if it couldn't be found
    """

    if not os.path.isdir(DIR_CUBE):
        return None

    for item in os.listdir(DIR_CUBE):
        if item.startswith(cube_name):
            return os.path.join(DIR_CUBE, item)

    return None


def get_download_dir(wu_filename, download_dir, fanout):
    # Kevins code for hashing the download directory
    s = hashlib.md5(wu_filename).hexdigest()[:8]
    x = long(s, 16)

    # Create the directory if needed
    hash_dir_name = "%s/%x" % (download_dir, x % fanout)
    if os.path.isfile(hash_dir_name):
        pass
    elif os.path.isdir(hash_dir_name):
        pass
    else:
        os.mkdir(hash_dir_name)

    return "%s/%x/%s" % (download_dir, x % fanout, wu_filename)


def get_parameter_files(connection, cube_run_id):
    """
    Gets a list of the parameter files for the specified cube, then compresses them in to a temp .tar.gz and returns
    the name of that file.
    :param cube_id:
    :return:
    """

    # Need a way of checking if parameter file tar.gz files already exist.
    # When looking to generate parameter file tar gile, first look in the hashed directory.
    # If the parameter file exists in the hashed directory, use that one.

    # First things first, check if the parameter files already exist in the download directory.
    # They should be in their hashed folder.

    parameter_files = []

    # First we need to check the db for all of the parameter files associated with this cube's run id
    params = connection.execute(select([PARAMETER_RUN]).where(PARAMETER_RUN.c.run_id == cube_run_id))

    for param in params:
        fname = connection.execute(select([PARAMETER_FILE.c.parameter_file_name]).
                                   where(PARAMETER_FILE.c.parameter_id == param['parameter_id'])).first()[0]

        parameter_files.append(os.path.join(DIR_PARAM, fname))

    # parameter_files now contains a list of abs paths to our .par files. Time to compress them.

    tarname = os.path.join(DIR_PARAM, 'parameters_{0}.tar.gz'.format(cube_run_id))

    tar = tarfile.open(tarname, "w:gz")

    for f in parameter_files:
        # The parameters must internally be in side a parameter_files folder. This is so the client extracts the files in to the appropriate folder.
        tar.add(f, os.path.join('parameter_files/', os.path.basename(f)))  # Added: don't compress with paths

    tar.close()

    return tarname


def process_cube(row, download_directory, fanout, connection):
    #### CUBE ####
    cube_abs_path = get_cube_path(row['cube_name'])
    wu_filename = '{0}_{1}'.format(row['run_id'], row['cube_name'])

    LOGGER.info('Current cube is {0}'.format(wu_filename))

    # Get the download directory
    wu_download_file = get_download_dir(wu_filename + '.fits.gz', download_directory, fanout)

    LOGGER.info('WU download file is {0}'.format(wu_download_file))

    # Copy the cube from its current path to the download dir
    shutil.copyfile(cube_abs_path, wu_download_file)

    #### PARAMETER FILES ####
    # First we need to grab all of the local parameter files we'll need for this and shove them in a .tar.gz

    # Get the would-be file name of the parameter download file. This should be 'parameters_(run_id)'
    param_file_name = "parameters_{0}.tar.gz".format(row['run_id'])
    param_download_file = get_download_dir(os.path.basename(param_file_name), download_directory, fanout) # get the hashed dl file

    LOGGER.info('Param download file is {0}'.format(param_download_file))

    # Added: check for already existing parameters file and use that one.
    if os.path.exists(param_download_file):
        LOGGER.info('Param download file already exists')
        # Oh look, we already have a parameters file!
        # Don't recompress because this will cause checksum issues in the boinc client
        param_path = param_download_file
    else:
        LOGGER.info('Param download file being created now...')
        # No parameter file exists at all. Build it from scratch by compressing all of the .par files now.
        param_path = get_parameter_files(connection, row['run_id'])

        # Then, we need to copy that .tar.gz to the parameter download directory
        shutil.copyfile(param_path, param_download_file)

        # Original is not needed any more
        os.remove(param_path)

    # create the workunit. First file is our cube, second is our parameters.
    # these are not absolute paths, boinc hashes these file names to get the absolute paths out of the download directory.
    # this means these two files exist somewhere in duchamp/downloads/some_hash/file_name
    file_list = [wu_filename + '.fits.gz', os.path.basename(param_path)]

    LOGGER.info(file_list)

    if create_workunit('duchamp', wu_filename, file_list):
        connection.execute(CUBE.update().where(CUBE.c.cube_name == row[1]).values(progress=1))


def create_workunit(appname, wu_name, input_file_list):
    py_boinc.boinc_db_transaction_start()

    LOGGER.info('Args_file for list_Input is {0}'.format(input_file_list))

    retval = py_boinc.boinc_create_work(
        app_name=appname,
        min_quorom=2,
        max_success_results=5,
        max_error_results=5,
        delay_bound=7 * 84600,
        target_nresults=2,
        wu_name=wu_name,
        wu_template="templates/duchamp_in.xml",
        result_template="templates/duchamp_out.xml",
        size_class=-1,
        priority=0,
        opaque=0,
        rsc_fpops_est=1e12,
        rsc_fpops_bound=1e14,
        rsc_memory_bound=1e8,
        rsc_disk_bound=2000000048,
        additional_xml="<credit>1.3f</credit>",
        list_input_files=input_file_list)

    if retval != 0:
        LOGGER.info('Error writing to boinc database. boinc_create_work return value = {0}'.format(retval))
        py_boinc.boinc_db_transaction_rollback()

        return False
    else:
        py_boinc.boinc_db_transaction_commit()

        return True
