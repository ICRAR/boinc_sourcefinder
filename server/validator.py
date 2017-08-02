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
import hashlib
import tarfile

from config import get_config
from utils import module_import, make_path, remove_path
from utils.logger import config_logger

MODULE = "parameter_files_mod"
LOG = config_logger(__name__)


class Validator:
    def __init__(self, config):
        self.config = config
        self.extract_directory_base = "/tmp/tmp_output_{0}"

    def get_temp_directory(self, filename):
        hash = hashlib.md5(filename).hexdigest()[:8]
        directory_name = self.extract_directory_base.format(long(hash, 16))

        make_path(directory_name)

        return directory_name

    def free_temp_directory(self, filename):
        hash = hashlib.md5(filename).hexdigest()[:8]
        directory_name = self.extract_directory_base.format(long(hash, 16))

        remove_path(directory_name)

    def __call__(self):
        LOG.error("Not implemented")


def init_validate(module, config, arguments):
    InitValidator = module.get_init_validator(Validator)
    validator = InitValidator(config)

    return validator(arguments['file1'])


def compare_validate(module, config, arguments):
    CompareValidator = module.get_compare_validator(Validator)
    validator = CompareValidator(config)

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
    init.set_defaults(func=init_validate)

    compare = subparsers.add_parser('compare', parents=[base_parser], help='Compare validation')
    compare.add_argument('file1', type=str, help='The first file to compare.')
    compare.add_argument('file2', type=str, help='The second file to compare.')
    compare.set_defaults(func=compare_validate)

    return vars(parser.parse_args())

if __name__ == '__main__':
    arguments = parse_args()

    app_name = arguments['app']

    config = get_config(app_name)
    module = module_import(MODULE, app_name)

    sys.exit(arguments['func'](module, config, arguments))
