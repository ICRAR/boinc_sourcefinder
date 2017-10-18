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
Work generator used to create workunits
"""
import argparse
import os
import importlib
import hashlib
import tarfile
import shutil

from utils import form_wu_name
from config import get_config
from utils.logger import config_logger
from sqlalchemy.engine import create_engine
from sqlalchemy import select

LOG = config_logger(__name__)


class WorkGenerator:
    """
    Generates work units for a boinc app.
    """
    def __init__(self, config, py_boinc):
        """
        Create a new WorkGenerator
        :param config: App config
        :param py_boinc: The py_boinc module
        :return:
        """
        self.config = config
        self.py_boinc = py_boinc
        self.download_dir = config["DIR_DOWNLOAD"]
        self.fanout = config["FANOUT"]
        self.engine = create_engine(config["DB_LOGIN"])
        self.dont_insert = False

    def get_pending_cubes(self, run_id):
        """
        Get a set of all cubes pending work unit generator
        :param run_id: The run id to check, or None to check all run ids.
        :return: SQLAlchemy result set of all cubes.
        """
        CUBE = self.config["database"]["CUBE"]

        if run_id is not None:
            # Check for registered cubes on the specified run ID
            cube_query = select([CUBE]).where(CUBE.c.progress == 0 and CUBE.c.run_id == run_id)
        else:
            cube_query = select([CUBE]).where(CUBE.c.progress == 0)

        return self.connection.execute(cube_query)

    def get_cube_path(self, cube_name):
        """
        Gets the path of a cube name from the cube directory.
        :param cube_name: Name of the cube
        :return: Path of the cube in the cubes directory
        """
        cube_dir = self.config["DIR_CUBE"]

        if not os.path.exists(cube_dir):
            raise Exception("Cube directory {0} doesn't exist".format(cube_dir))

        for item in os.listdir(cube_dir):
            if item.startswith(cube_name):
                return os.path.join(cube_dir, item)

        return None

    def get_download_path(self, filename):
        """
        Kevins code for hashing the download directory
        :param filename: Filename to get the download path for
        :return: Boinc download path for the provided filename
        """
        s = hashlib.md5(filename).hexdigest()[:8]
        x = long(s, 16)

        # Create the directory if needed
        hash_dir_name = os.path.join(self.download_dir, "%x" % (x % self.fanout))
        if os.path.isfile(hash_dir_name):
            pass
        elif os.path.isdir(hash_dir_name):
            pass
        else:
            os.mkdir(hash_dir_name)

        # "%s/%x/%s" % (self.download_dir, x % self.fanout, filename)
        return os.path.join(hash_dir_name, filename)

    def compress_parameters(self, run_id):
        """
        Compress all parameters associated with the given run ID
        :param run_id: The run ID to get parameters for
        :return: Name of the tarfile that contains the compressed parameters
        """
        app_name = self.config["APP_NAME"]
        param_dir = self.config["DIR_PARAM"]
        PARAMETER_RUN = self.config["database"]["PARAMETER_RUN"]
        PARAMETER_FILE = self.config["database"]["PARAMETER_FILE"]

        parameter_tar_file_name = "parameters_{0}_{1}.tar.gz".format(app_name, run_id)
        parameter_tar_file_path = self.get_download_path(parameter_tar_file_name)

        if not os.path.exists(parameter_tar_file_path):
            LOG.info("Creating parameter file {0}".format(parameter_tar_file_path))
            # Need to compress the parameter files now as the tarfile doesn't exist
            parameters = self.connection.execute(select([PARAMETER_RUN]).where(PARAMETER_RUN.c.run_id == run_id))

            parameter_files = []  # Contains a list of parameter file names associated with the specified run
            for parameter in parameters:
                param_id = parameter['parameter_id']
                name = self.connection.execute(select([PARAMETER_FILE.c.parameter_file_name]).
                                               where(PARAMETER_FILE.c.parameter_id == param_id)).first()[0]

                parameter_files.append(os.path.join(param_dir, name))

            with tarfile.open(parameter_tar_file_path, "w:gz") as tar:
                for parameter_file in parameter_files:
                    # Don't compress with paths
                    tar.add(parameter_file, os.path.basename(parameter_file))

        return parameter_tar_file_name

    def create_workunit(self, wu_name, wu_file_list):
        """
        Create a work unit in the Boinc DB
        :param wu_name: The name of the work unit
        :param wu_file_list: The files for the work unit
        :return:
        """
        app_name = self.config["APP_NAME"]
        template_in = "templates/{0}_in.xml".format(app_name)
        template_out = "templates/{0}_out.xml".format(app_name)
        additional_xml = "<credit>3.0f</credit>"

        if self.dont_insert:
            LOG.info("Not performing DB insert")
            return

        self.py_boinc.boinc_db_transaction_start()

        success = py_boinc.boinc_create_work(
                app_name=app_name,
                min_quorom=2,
                max_success_results=5,
                max_error_results=5,
                delay_bound=7 * 84600,
                target_nresults=2,
                wu_name=wu_name,
                wu_template=template_in,
                result_template=template_out,
                size_class=-1,
                priority=0,
                opaque=0,
                rsc_fpops_est=1e12,
                rsc_fpops_bound=1e14,
                rsc_memory_bound=1e8,
                rsc_disk_bound=2684354560,  # 2.5GB. Decent amount of space needed for the VM image.
                additional_xml=additional_xml,
                list_input_files=wu_file_list)

        if success != 0:
            py_boinc.boinc_db_transaction_rollback()
            raise Exception("Error writing to boinc database. boinc_create_work return value = {0}".format(success))

        py_boinc.boinc_db_transaction_commit()

    def process_cube(self, cube_row):
        """
        Processes a single cube from the app database
        :param cube_row: The cube's database row
        :return:
        """
        CUBE = self.config["database"]["CUBE"]
        app_name = self.config["APP_NAME"]

        cube_name = cube_row["cube_name"]
        cube_id = cube_row["cube_id"]
        cube_run_id = cube_row["run_id"]
        cube_abs_path = self.get_cube_path(cube_name)

        wu_name = form_wu_name(app_name, cube_run_id, cube_name)
        wu_filename = wu_name + ".tar.gz"
        wu_download_path = self.get_download_path(wu_filename)

        LOG.info("Start: {0}".format(cube_name))

        # Copy the cube to the download directory
        LOG.info("Copying: {0} to {1}".format(cube_abs_path, wu_download_path))
        shutil.copyfile(cube_abs_path, wu_download_path)

        # Ensure the parameter file for this run exists
        parameter_tar_file_name = self.compress_parameters(cube_run_id)
        LOG.info("Using parameter file: {0}".format(parameter_tar_file_name))

        # Create the work unit
        wu_file_list = [wu_filename, os.path.basename(parameter_tar_file_name)]

        LOG.info("Creating work unit: {0}".format(wu_name))
        self.create_workunit(wu_name, wu_file_list)
        self.connection.execute(CUBE.update().where(CUBE.c.cube_id == cube_id).values(progress=1))  # Mark as generated

        LOG.info("Finished: {0}\n".format(cube_name))

    def __call__(self, run_id, dont_insert):
        """
        Run the work unit generator
        :param run_id: The run ID to generate work for, or None to generate work for all run IDs.
        :return:
        """
        LOG.info("Work generator started for app: {0}".format(self.config["APP_NAME"]))
        self.dont_insert = dont_insert

        self.connection = self.engine.connect()
        success = self.py_boinc.boinc_db_open()
        if success != 0:
            LOG.error("Could not open BOINC db. Error code: {0}".format(success))
            return

        num_processed = 0

        try:

            for row in self.get_pending_cubes(run_id):
                self.process_cube(row)
                num_processed += 1

        except Exception as e:
            LOG.exception("Error processing cube: {0}".format(e.message))

        finally:
            LOG.info("Cubes processed: {0}".format(num_processed))
            self.connection.close()
            self.py_boinc.boinc_db_close()


def parse_args():
    """
    Parse arguments for the program.
    :return: The arguments for the program.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=str, required=True, help='The name of the app to use.')
    parser.add_argument('--dont_insert', action='store_true', help="Don't perform inserts in to the DB", default=False)
    parser.add_argument('run_id', type=int, help='The run ID to register.')
    args = vars(parser.parse_args())

    return args


if __name__ == '__main__':
    arguments = parse_args()
    app_name = arguments['app']

    config = get_config(app_name)

    os.chdir(config["DIR_BOINC_PROJECT_PATH"]) # for pyboinc
    # Need to import pyboinc here, as we need to know the project path before importing.
    py_boinc = importlib.import_module("py_boinc")

    work_generator = WorkGenerator(config, py_boinc)

    exit(work_generator(arguments['run_id'], arguments['dont_insert']))