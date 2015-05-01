"""
The very small configuration file!
"""
from os.path import exists, dirname
from configobj import ConfigObj


config_file_name = dirname(__file__) + '/duchamp.settings'
if exists(config_file_name):
    config = ConfigObj(config_file_name)
    ############### Database Settings ###############
    DB_USER_ID = config['databaseUserid']
    DB_PASSWORD = config['databasePassword']
    DB_HOSTNAME = config['databaseHostname']
    DB_NAME = config['databaseName']
    BOINC_DB_NAME = config['boincDatabaseName']
    DB_LOGIN = "mysql://" + DB_USER_ID + ":" + DB_PASSWORD + "@" + DB_HOSTNAME + "/" + DB_NAME
    BOINC_DB_LOGIN = "mysql://" + DB_USER_ID + ":" + DB_PASSWORD + "@" + DB_HOSTNAME + "/" + BOINC_DB_NAME