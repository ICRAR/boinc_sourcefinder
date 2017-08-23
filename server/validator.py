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
Validator base for Sourcefinder apps
"""
import argparse
import os
import sys
import shutil

from config import get_config
from utils import module_import, extract_tar, get_temp_directory, free_temp_directory
from utils.logger import config_logger

MODULE = "validator_mod"
LOG = config_logger(__name__)


class InitValidator:
    def __init__(self, config, test_mode):
        self.config = config
        self.test_mode = test_mode

        self.working_file = None

    def copy_to_invalid(self):
        folder = os.path.join(self.config["DIR_VALIDATOR_INVALIDS"], 'init')
        if os.path.exists(folder):
            shutil.copy(self.working_file, folder)
        else:
            LOG.info("Not copying to {0} because the path doesn't exist".format(folder))

    def validate(self, file_directory, result_id):
        LOG.info("Not implemented")
        return "Not implemented"

    def __call__(self, file1, result_id):
        self.working_file = file1

        LOG.info("{0} Validate workunit file: {1}".format(config['APP_NAME'], self.working_file))

        file_directory = get_temp_directory(self.working_file)

        try:
            extract_tar(self.working_file, file_directory)
            reason = self.validate(file_directory, result_id)

        except:
            LOG.exception("Exception during validation")
            reason = "Exception"

        finally:
            free_temp_directory(self.working_file)

        if reason is None:
            LOG.info("Workunit file is valid")
            return 0
        else:
            LOG.info("Workunit file is not valid. Reason: {0}".format(reason))
            self.copy_to_invalid()
            return 1


class CompareValidator:
    def __init__(self, config, test_mode):
        self.config = config
        self.test_mode = test_mode

        self.working_file1 = None
        self.working_file2 = None

    def copy_to_invalid(self):
        folder = os.path.join(self.config["DIR_VALIDATOR_INVALIDS"], 'compare')
        if os.path.exists(folder):
            shutil.copy(self.working_file1, folder)
            shutil.copy(self.working_file2, folder)
        else:
            LOG.info("Not copying to {0} because the path doesn't exist".format(folder))

    def validate(self, file1_directory, file2_directory):
        LOG.info("Not implemented")
        return "Not implemented"

    def __call__(self, file1, file2):
        self.working_file1 = file1
        self.working_file2 = file2

        LOG.info("{0} Validate workunit files: {1} and {2}".format(config['APP_NAME'], self.working_file1, self.working_file2))

        file1_directory = get_temp_directory(self.working_file1)
        file2_directory = get_temp_directory(self.working_file2)

        try:
            extract_tar(self.working_file1, file1_directory)
            extract_tar(self.working_file2, file2_directory)
            reason = self.validate(file1_directory, file2_directory)

        except:
            LOG.exception("Exception during validation")
            reason = "Exception"

        finally:
            free_temp_directory(self.working_file1)
            free_temp_directory(self.working_file2)

        if reason is None:
            LOG.info("Workunit files are valid")
            return 0
        else:
            LOG.info("Workunit files are not valid. Reason: {0}".format(reason))
            self.copy_to_invalid()
            return 1


def init_validate(module, config, arguments):
    Validator = module.get_init_validator(InitValidator)
    validator = Validator(config, arguments['test'])

    return validator(arguments['file'], arguments['result_id'])


def compare_validate(module, config, arguments):
    Validator = module.get_compare_validator(CompareValidator)
    validator = Validator(config, arguments['test'])

    return validator(arguments['file1'], arguments['file2'])


def parse_args():
    """
    Init validator takes in one arg, the name of the file to check.
    Compare validator takes two args, the name of each file to compare together.
    :return:
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument('--app', type=str, required=True, help='The name of the app to use.')

    init = subparsers.add_parser('init', parents=[base_parser], help='Init validation')
    init.add_argument('file', type=str, help='The name of the file to validate.')
    init.add_argument('result_id', type=int, help='The result ID of the result.')
    init.add_argument('--test', action="store_true", default=False, help='Run the validator in test mode for unit tests')
    init.set_defaults(func=init_validate)

    compare = subparsers.add_parser('compare', parents=[base_parser], help='Compare validation')
    compare.add_argument('file1', type=str, help='The first file to compare.')
    compare.add_argument('file2', type=str, help='The second file to compare.')
    compare.add_argument('--test', action="store_true", default=False, help='Run the validator in test mode for unit tests')
    compare.set_defaults(func=compare_validate)

    return vars(parser.parse_args())

if __name__ == '__main__':
    arguments = parse_args()

    app_name = arguments['app']

    config = get_config(app_name)
    module = module_import(MODULE, app_name)

    sys.exit(arguments['func'](module, config, arguments))
