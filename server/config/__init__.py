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
from database_sofiabeta import sofiabeta_database_def

LOG = config_logger(__name__)


class ConfigItem:
    def __init__(self, name, config_name, default, dtype=str):
        self.name = name
        self.config_name = config_name
        self.default = default
        self.dtype = dtype


class ConfigPath:
    def __init__(self, name, path_format, *args):
        self.name = name
        self.path_format = path_format
        self.format_args = args

    def get_path(self, d):
        def get_value(value):
            if value in d:
                return d[value]

            return ""

        actual_args = [get_value(a) for a in self.format_args]  # Look up the args in the given dictionary
        return self.path_format.format(*actual_args)

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

    ConfigItem("FANOUT", "fanout", 1024, int),

    ############### AMAZON SETTINGS ###############
    ConfigItem("S3_BUCKET_NAME", "bucket", "icrar.sourcefinder.files"),

    ConfigItem("APP_NAME", "appName", "sourcefinder")
]

extra_paths = [
    ConfigPath("DIR_APP", "{0}/apps/{1}", "DIR_BOINC_PROJECT_PATH", "APP_NAME"),
    ConfigPath("DIR_APP_TEMPLATES", "{0}/app_templates/{1}", "DIR_BOINC_PROJECT_PATH", "APP_NAME"),
    ConfigPath("DIR_VMS", "{0}/vm", "DIR_BOINC_PROJECT_PATH"),
    ConfigPath("PROG_SIGN_EXECUTABLE", "{0}/bin/sign_executable", "DIR_BOINC_PROJECT_PATH"),
    ConfigPath("PROG_UPDATE_VERSIONS", "{0}/bin/update_versions", "DIR_BOINC_PROJECT_PATH"),
    ConfigPath("DIR_KEYS", "{0}/keys", "DIR_BOINC_PROJECT_PATH"),
    ConfigPath("DIR_DOWNLOAD", "{0}/download", "DIR_BOINC_PROJECT_PATH"),
    ConfigPath("DIR_LOG", "{0}/log_ip-10-0-131-204", "DIR_BOINC_PROJECT_PATH")
]


def read_config_file(filename, config_dict):
    if exists(filename):
        # Load from config file
        config_obj = ConfigObj(filename)

        for item in config_entries:
            if item.config_name in config_obj:
                config_dict[item.name] = item.dtype(config_obj[item.config_name])
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


def get_config(app=None):
    """
    Returns the appropriate config for the given application
    The config for each application is stored in a file named "app.settings".
    Settings common to all configs are stored in "common.settings".
    Common settings are loaded first, then overwritten by app settings if applicable.
    :param app: The app to use.
    :return:
    """

    config = {}

    common_file_name = join(dirname(realpath(__file__)), 'common.settings'.format(app))
    # Copy the fields from common.settings first
    read_config_file(common_file_name, config)

    # Add in the database tables
    config["database_boinc"] = boinc_database_def
    config["database_sourcefinder"] = duchamp_database_def
    config["database_sourcefinder_sofia"] = sofia_database_def
    config["database_sourcefinder_sofiabeta"] = sofiabeta_database_def
    config["DB_NAME"] = ""

    if app is not None:
        # Load app specific settings
        config_file_name = join(dirname(realpath(__file__)), '{0}.settings'.format(app))
        # Copy from the settings for this app
        read_config_file(config_file_name, config)

        config["DIR_APPS"] = join(config["DIR_BOINC_PROJECT_PATH"], "apps/{0}".format(app))

        # Set the database def for this module.
        config["database"] = config["database_{0}".format(config["DB_NAME"])]

    base_db_login = "mysql://" + \
                    config['DB_USER_ID'] + ":" + \
                    config['DB_PASSWORD'] + "@" + \
                    config['DB_HOSTNAME'] + "/"

    # Set up database connection string
    config["BASE_DB_LOGIN"] = base_db_login
    config["DB_LOGIN"] = base_db_login + config['DB_NAME']
    config["BOINC_DB_LOGIN"] = base_db_login + config['BOINC_DB_NAME']

    config["DIR_OLD_LOGS"] = "/home/ec2-user/old_logs/"
    config["DIR_VALIDATOR_INVALIDS"] = "/home/ec2-user/validator_invalids/"

    for item in extra_paths:
        config[item.name] = item.get_path(config)

    return config
