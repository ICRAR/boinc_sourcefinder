__author__ = '21298244'

# Helper file for the work generator

import os
import hashlib
import py_boinc
from logging_helper import config_logger

LOGGER = config_logger(__name__)
LOGGER.info("work_generator_mod.py")


def convert_file_to_wu(wu_filename, download_dir, fanout):
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


def create_workunit(appname, wu_name, input_file_list):
    py_boinc.boinc_db_transaction_start()
    LOGGER.info('Args_file for list_Input is {0}'.format(input))
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
        size_class=0,
        priority=1,
        opaque=0,
        rsc_fpops_est=1e12,
        rsc_fpops_bound=1e14,
        rsc_memory_bound=1e8,
        rsc_disk_bound=1e8,
        additional_xml="<credit>1.0f</credit>",
        list_input_files=input_file_list)
    LOGGER.info('completed create work request')
    if retval != 0:
        py_boinc.boinc_db_transaction_rollback()
        LOGGER.info('Error writing to boinc database. boinc_create_work return value = {0}'.format(retval))
    else:
        py_boinc.boinc_db_transaction_commit()
