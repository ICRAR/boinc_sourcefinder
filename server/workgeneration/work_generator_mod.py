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
    parameter_files = []

    # First we need to check the db for all of the parameter files associated with this cube's run id
    params = connection.execute(select([PARAMETER_RUN]).where(PARAMETER_RUN.c.run_id == cube_run_id))

    for param in params:
        fname = connection.execute(select([PARAMETER_FILE.c.parameter_file_name]).
                                   where(PARAMETER_FILE.c.parameter_file_id == param['parameter_id'])).first()[0]

        parameter_files.append(os.path.join(DIR_PARAM, fname))

    # parameter_files now contains a list of abs paths to our .par files. Time to compress them.

    tarname = os.path.join(DIR_PARAM, 'parameters.tar.gz')

    with tarfile.open(tarname, "w:gz") as tar:
        for f in parameter_files:
            tar.add(f)

    return tarname






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
        additional_xml="<credit>1.0f</credit>",
        list_input_files=input_file_list)

    if retval != 0:
        LOGGER.info('Error writing to boinc database. boinc_create_work return value = {0}'.format(retval))
        py_boinc.boinc_db_transaction_rollback()

        return False
    else:
        py_boinc.boinc_db_transaction_commit()

        return True
