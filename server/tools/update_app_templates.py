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
Sets up the app templates for a BOINC app.
Requires:
    a folder with the vboxwrappers
    an app name
    a VM image name
    a vbox job name
"""

import os
import shutil
import argparse
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import get_config
from utils.logger import config_logger

LOG = config_logger(__name__)

version_xml = """<version>
    <file>
	<physical_name>{0}</physical_name>
        <main_program/>
        <copy_file/>
        <logical_name>vboxwrapper</logical_name>
    </file>
    <file>
	<physical_name>{1}</physical_name>
        <logical_name>vm_image.vdi</logical_name>
        <copy_file/>
        <gzip/>
    </file>
    <file>
         <physical_name>{2}</physical_name>
         <logical_name>vbox_job.xml</logical_name>
         <copy_file/>
    </file>
    <dont_throttle/>
    <api_version>7.5.0</api_version>
</version>"""


class AppTemplateSetup:
    def __init__(self, config):
        self.config = config

    def __call__(self, args):
        # Look at the base_template folder
        #   Get the name of the vbox_job file stored there
        # For each folder, apart from base_template
        #   Create a version.xml file in the folder with the vboxwrapper name, the vm name, and the vboxjob file from base
        #   template.
        app_templates_path = self.config["DIR_APP_TEMPLATES"]
        base_template_path = os.path.join(app_templates_path, "base_template")
        vbox_job_file = [f for f in os.listdir(base_template_path) if f.startswith("vbox_job")][0]
        folders = [os.path.join(app_templates_path, f) for f in os.listdir(app_templates_path) if f != "base_template"]

        for folder in folders:
            version_path = os.path.join(folder, "version.xml")
            app_name = [f for f in os.listdir(folder) if f.startswith("vboxwrapper")][0]

            with open(version_path, "w") as f:
                f.write(version_xml.format(app_name, args["vm_name"], vbox_job_file))

        return 0


def parse_args():
    """
    Parse arguments for the program
    :return: The arguments for the program.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=str, required=True, help='The name of the app to use.')
    parser.add_argument('--vm_name', type=str, required=True, help='The name of the vm file.')
    args = vars(parser.parse_args())

    return args

if __name__ == "__main__":
    arguments = parse_args()
    app_name = arguments['app']
    config = get_config(app_name)

    app_setup = AppTemplateSetup(config)

    exit(app_setup(arguments))