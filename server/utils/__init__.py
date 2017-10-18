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

import os
import errno
import tarfile
import importlib
import shutil
import hashlib
from logger import config_logger

LOG = config_logger(__name__)
EXTRACT_DIRECTORY_BASE = "/tmp/sourcefinder_{0}"


class DirStack:
    """
    DirStack is a simple helper class that allows the user to push directories on to the stack then
    pop them off later. If you want to change the working directory of the program, use stack.push() then
    os.chdir(dir).
    Later, to restore the previous directory, use stack.pop()
    """

    def __init__(self):
        self.stack = []

    def push(self):
        self.stack.append(os.getcwd())

    def pop(self):
        os.chdir(self.stack.pop())


def retry_on_exception(function, exception, num_retries):

    while num_retries > 0:
        try:
            return function()
        except exception:
            num_retries -= 1


def make_path(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def remove_path(path):
    try:
        shutil.rmtree(path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


def extract_tar(tar, path):
    with tarfile.open(tar) as tf:
        make_path(path)
        tf.extractall(path)


def form_wu_name(app_name, run_id, cube_name):
    """
    The wu name format uses the following formatting style:
    "app_name"_"run_id"_"cube_name"
    The first underscore marks the end of the app name.
    The second marks the end of the run id.
    After the second, the cube name can contain as many underscores as it likes.
    :param app_name: Name of the app
    :param run_id: Run ID for the workunit
    :param cube_name: Cube name for the workunit
    :return:
    """
    # Sanity check app_name
    if isinstance(app_name, basestring) and "_" in app_name:
        raise Exception("App name contains underscore!")

    return "{0}_{1}_{2}".format(app_name, run_id, cube_name)


def split_wu_name(wu_name):
    """
    Splits a work unit name in to an app_name, run_id and cube_name tuple.
    This will also work on result names, returning a slightly different cube name
    (with a _1, _2 etc. at the end based on the result)
    :param wu_name: The work unit name
    :return: tuple containing the app name, run id and cube name
    """

    try:
        underscore1 = wu_name.find('_')
        underscore2 = wu_name.find('_', underscore1 + 1)

        if underscore1 == -1 or underscore2 == -1:
            raise Exception("Bad underscores")

        app_name = wu_name[0:underscore1]
        run_id = int(wu_name[underscore1 + 1:underscore2])
        cube_name = wu_name[underscore2 + 1:]

    except Exception as e:
        raise Exception('Malformed WU name: {0}. {1}'.format(wu_name, e.message))

    return app_name, run_id, cube_name


def get_temp_directory(filename):
    raw_hash = hashlib.md5(filename).hexdigest()[:8]
    directory_name = EXTRACT_DIRECTORY_BASE.format(long(raw_hash, 16))

    make_path(directory_name)

    return directory_name


def free_temp_directory(filename):
    raw_hash = hashlib.md5(filename).hexdigest()[:8]
    directory_name = EXTRACT_DIRECTORY_BASE.format(long(raw_hash, 16))

    try:
        remove_path(directory_name)
    except:
        pass  # Best effort cleanup. If we don't remove it, whatever, it's in the tmp directory anyway.


def module_import(module_name, app_name):
    LOG.debug("Loading module {0}.{1}".format(app_name, module_name))
    import_path = app_name + '.' + module_name
    module = importlib.import_module(import_path)

    if module is None:
        LOG.error("Could not load module {0}.{1}".format(app_name, module_name))
        exit(1)

    return module
