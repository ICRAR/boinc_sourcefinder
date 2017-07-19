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
Configuration file for sourcefinder.
"""
from os.path import exists, dirname, realpath, join
from configobj import ConfigObj
from utils.logger import config_logger

from database_boinc import boinc_database_def
from database_duchamp import duchamp_database_def
from database_sofia import sofia_database_def

LOG = config_logger(__name__)


class ConfigItem:
    def __init__(self, name, config_name, default):
        self.name = name
        self.config_name = config_name
        self.default = default

config_entries = [
    ############### Database Settings ###############
    ConfigItem("DB_USER_ID", "databaseUserid", "root"),
    ConfigItem("DB_PASSWORD", "databasePassword", ""),
    ConfigItem("DB_HOSTNAME", "databaseHostname", "localhost"),
    ConfigItem("DB_NAME", "databaseName", ""),
    ConfigItem("BOINC_DB_NAME", "boincDatabaseName", "duchamp"),

    ############### Directory Settings ###############
    ConfigItem("DIR_PARAM", "paramDirectory", "/home/ec2-user/sf_parameters"),
    ConfigItem("DIR_CUBE", "cubeDirectory", "/home/ec2-user/sf_cubes"),
    ConfigItem("DIR_BOINC_PROJECT_PATH", "boincPath", "/home/ec2-user/projects/duchamp"),

    ############### Work Generation Settings ###############
    ConfigItem("BOINC_DB_NAME", "wgThreshold", 500),

    ############### AMAZON SETTINGS ###############
    ConfigItem("BOINC_DB_NAME", "bucket", "icrar.sourcefinder.files"),

    ConfigItem("APP_NAME", "appName", "sourcefinder")
]


def read_config_file(filename, config_dict):
    if exists(filename):
        # Load from config file
        config_obj = ConfigObj(filename)

        for item in config_entries:
            if item.config_name in config_obj:
                config_dict[item.name] = config_obj[item.config_name]
    else:
        # Create a default
        default = ConfigObj()
        default.filename = filename
        for item in config_entries:
            default[item.config_name] = item.default
            config_dict[item.name] = item.default

        default.write()

        LOG.info("Creating a default config file for: {0}".format(filename))

    return config_dict


def get_config(app):
    """
    Returns the appropriate config for the given application
    The config for each application is stored in a file named "app.settings".
    Settings common to all configs are stored in "common.settings".
    Common settings are loaded first, then overwritten by app settings if applicable.
    :param app: The app to use.
    :return:
    """

    config = {}
    config_file_name = join(dirname(realpath(__file__)), '{0}.settings'.format(app))
    common_file_name = join(dirname(realpath(__file__)), 'common.settings'.format(app))

    # Copy the fields from common.settings first
    read_config_file(common_file_name, config)
    # Copy from the settings for this app
    read_config_file(config_file_name, config)

    # Set up database connection string
    config["DB_LOGIN"] = "mysql://" + \
                         config['DB_USER_ID'] + ":" + \
                         config['DB_PASSWORD'] + "@" + \
                         config['DB_HOSTNAME'] + "/" + \
                         config['DB_NAME']

    config["BOINC_DB_LOGIN"] = "mysql://" + \
                               config['DB_USER_ID'] + ":" + \
                               config['DB_PASSWORD'] + "@" + \
                               config['DB_HOSTNAME'] + "/" + \
                               config['BOINC_DB_NAME']

    # Add in the filesystem config
    config["filesystem"] = {
        'apps': '/home/ec2-user/projects/duchamp/apps/duchamp',
        'app_templates': '/home/ec2-user/projects/duchamp/app_templates/',
        'vms': '/home/ec2-user/projects/duchamp/vm/',
        'sign_executable': '/home/ec2-user/projects/duchamp/bin/sign_executable',
        'update_versions': '/home/ec2-user/projects/duchamp/bin/update_versions',
        'keys': '/home/ec2-user/projects/duchamp/keys/',
        'download': '/home/ec2-user/projects/duchamp/download/',
        'project': '/home/ec2-user/projects/duchamp/',
        'log': '/home/ec2-user/projects/duchamp/log_ip-10-0-131-204/',
        'old_logs': '/home/ec2-user/old_logs/',
        'validator_invalids': '/home/ec2-user/validator_invalids/'
    }

    # Add in the database tables
    config["database_boinc"] = boinc_database_def
    config["database_duchamp"] = duchamp_database_def
    config["database_sofia"] = sofia_database_def

    return config
