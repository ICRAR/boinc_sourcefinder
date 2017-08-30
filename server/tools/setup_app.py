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
Initialise / update BOINC applications.
"""
import os
import shutil
import subprocess
import argparse
import sys
from subprocess import Popen, PIPE
from config import get_config
from ..utils import DirStack
from ..utils.logger import config_logger

LOG = config_logger(__name__)


class AppSetup:
    """

    """
    def __init__(self, config):
        """

        :param config:
        :return:
        """
        self.config = config

    def new_app(self, app_path):
        """

        :param app_path:
        :return:
        """
        # Creating a new app
        os.mkdir(app_path)
        app_templates = self.config["DIR_APP_TEMPLATES"]
        folders = os.listdir(app_templates)

        for folder in folders:
            if folder == 'base_template':
                continue  # We'll get to this later

            # Copy this folder in to the new app directory.
            LOG.info(os.path.join(app_templates, folder))
            LOG.info(os.path.join(app_path, folder))
            shutil.copytree(os.path.join(app_templates, folder), os.path.join(app_path, folder))

        folders = os.listdir(app_path)  # This should now contain all of the app platform folders
        base_template = os.path.join(app_templates, 'base_template')
        base_template_folders = os.listdir(base_template)

        for folder in folders:
            for f in base_template_folders:
                print "Copying {0} to {1}".format(f, os.path.join(app_path, folder))
                # Copy each of the files in the base_template in to each of the newly made platform path.
                shutil.copy(os.path.join(base_template, f), os.path.join(app_path, folder))

            for f in os.listdir(os.path.join(app_path, folder)):
                # Sign each file within the app folder
                self.sign_file(os.path.join(os.path.join(app_path, folder), f))

    def sign_file(self, filename):
        """

        :param filename:
        :return:
        """
        sign_filename = filename + ".sig"

        with open(filename + ".sig", 'w') as f:
            subprocess.call([self.config['PROG_SIGN_EXECUTABLE'],
                             filename,
                             os.path.join(self.config['DIR_KEYS'], 'code_sign_private')],
                            stdout=f)

        return sign_filename

    def update_app(self, app_path, vm_path):
        """

        :param app_path:
        :param vm_path:
        :return:
        """
        # Updating an app

        dstatck = DirStack()

        # We assume that the app folder has already been set up correctly

        folders = os.listdir(app_path)

        # Sign the vm
        sign_filename = self.sign_file(vm_path)

        # Each of the platform paths found in the app folder
        for folder in folders:
            # Copy the vm in

            folder = os.path.join(app_path, folder)

            LOG.info("Making link between {0} and {1}".format(vm_path, os.path.join(folder, sys.argv[2])))

            if os.path.exists(os.path.join(folder, sys.argv[2])):
                os.unlink(os.path.join(folder, sys.argv[2]))

            os.link(vm_path, os.path.join(folder, sys.argv[2]))

            # Sign it
            print "Copying vm signature in to {0}".format(folder)
            shutil.copy(sign_filename, folder)

        download_vm_path = os.path.join(self.config['DIR_DOWNLOAD'], sys.argv[2])
        if os.path.exists(download_vm_path):
            os.remove(download_vm_path)
        if os.path.exists(download_vm_path + '.gz'):
            os.remove(download_vm_path + '.gz')

        dstatck.push()
        os.chdir(self.config['DIR_BOINC_PROJECT_PATH'])

        p = Popen([self.config['PROG_UPDATE_VERSIONS']], stdin=PIPE)
        # Emulates the user going y enter y enter y enter for all of the 'do you want to add this version' prompts
        p.communicate(input='y\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\n')

        dstatck.pop()

        # If the database already contained this version, then update_versions wont copy the new VM to the
        # download directory, so we have to copy it now.

        if not os.path.exists(download_vm_path):
            LOG.info("VM is missing from download directory, copying...")
            shutil.copy(vm_path, download_vm_path)

            dstatck.push()
            os.chdir(self.config['DIR_DOWNLOAD'])

            os.system('gzip < {0} > {0}.gz'.format(sys.argv[2]))
            dstatck.pop()


def parse_args():
    """
    Parse arguments for the program
    :return: The arguments for the program.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=str, required=True, help='The name of the app to use.')
    parser.add_argument('--version', type=str, required=True, help='The app version to create/update.')
    parser.add_argument('--vm_name', type=str, required=True, help='The name of the vm file.')
    args = vars(parser.parse_args())

    return args

if __name__ == '__main__':
    arguments = parse_args()
    app_name = arguments['app']
    config = get_config(app_name)

    app_setup = AppSetup(config)

    vm_path = os.path.join(config["DIR_VMS"], arguments['vm_name'])
    app_version_path = os.path.join(config["DIR_APPS"], arguments['version'])
    exit_code = 0

    try:
        if os.path.isfile(vm_path):
            if not os.path.exists(app_version_path):
                LOG.info("The app version {0} does not exist. Creating...".format(app_version_path))
                app_setup.new_app(app_version_path)

            # App version path now exists
            LOG.info("Updating app version {0}".format(app_version_path))
            app_setup.update_app(app_version_path, vm_path)

        else:
            LOG.info("Invalid VM name given. Make sure your vm is located in {0}.".format(config["DIR_VMS"]))
            exit_code = 1

    except Exception:
        LOG.exception("Exception occurred")
        exit_code = 1


    exit(exit_code)
