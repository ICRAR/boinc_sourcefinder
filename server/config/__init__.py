"""
Configuration file for sourcefinder.
Run this file directly to print the configuration.

!!IF YOU MAKE A CHANGE HERE, MAKE SURE make_default.py IS CHANGED TOO!!
"""
from os.path import exists, dirname, realpath, join
from configobj import ConfigObj

config = None
config_file_name = join(dirname(realpath(__file__)), 'duchamp.settings')
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

    ############### Directory Settings ###############
    DIR_PARAM = config['paramDirectory']
    DIR_CUBE = config['cubeDirectory']
    DIR_BOINC_PROJECT_PATH = config['boincPath']

    ############### Work Generation Settings ###############
    WG_THRESHOLD = config['wgThreshold']

    ############### AMAZON SETTINGS ###############
    S3_BUCKET_NAME = config['bucket']

else:
    print "No log file!"

# Shared file system defs used by common tools.
filesystem = {'apps': '/home/ec2-user/projects/duchamp/apps/duchamp',
              'app_templates': '/home/ec2-user/projects/duchamp/app_templates/',
              'vms': '/home/ec2-user/projects/duchamp/vm/',
              'sign_executable': '/home/ec2-user/projects/duchamp/bin/sign_executable',
              'update_versions': '/home/ec2-user/projects/duchamp/bin/update_versions',
              'keys': '/home/ec2-user/projects/duchamp/keys/',
              'download': '/home/ec2-user/projects/duchamp/download/',
              'project': '/home/ec2-user/projects/duchamp/'
             }

if __name__ == '__main__':
    # Print the config
    if not config:
        print 'No config file'
    else:
        for k, v in config.iteritems():
            print '{0}: {1}'.format(k, v)
