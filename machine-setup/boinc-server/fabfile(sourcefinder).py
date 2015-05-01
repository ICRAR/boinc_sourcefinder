"""Fabric file for the sourcefinder test/Duchamp application (set up so it can be changed for Duchamp with minimal difficulty)"""


import sys

sys.path.append('..')

from glob import glob
from os.path import splitext, split
from fabric.operations import local
from fabric.state import env

APP_NAME = "duchamp"
PLATFORMS = ["x86_64-apple-darwin__vbox64, windows_x86_64__vbox64, x86_64-pc-linux-gnu__vbox64"]

def create_version_xml(platform, app_version, directory):
    """
    Create the version.xml file
    :param platform:
    :param app_version:
    :param directory:
    :param exe:
    """
    
    outfile = open(directory + '/version.xml', 'w')
    outfile.write(
    '''<version>
        <file>
            <physical_name>vboxwrapper_26105_{0}</phscial_name>
            <main_program/>
            <copy_file/>
            <logical_name>vboxwrapper</logical_name>
        </file>
        <file>
            <physical_name>DuchampTestClone.vdi<physical_name>
            <copy_file/>
            <gzip/>
            <file/>
        <file>
            <physical_name>vbox_job_{1}</physical_name>
            <logical_name>vbox_job</logical_name>
            <copy_file/>
        </file>
        <dont_throttle/>
        <api_version>7.5.0</api_version>
    </version>'''.format(platform, app_version))
    outfile.close()

def create_plan_class_xml(project_directory):
    outfile = open(project_directory + '/plan_class_spec.xml', 'w')
    outfile.write(
    '''<plan_classes>
        <plan_class>
            <name>vbox</name>
            <virtualbox/>
            <is64bit/>
        </plan_class>
    </plan_classes>''')
    outfile.close()


def copy_files(app_version):
   """
    Copy the application files to their respective directories 
    """
   for platform in PLATFORMS:
        local('mkdir -p /home/ec2-user/projects/{3}/apps/{0}/{1}/{2}'.format(APP_NAME, app_version, platform, env.project_name))
        for filename in glob('home/ec2-user/boinc_sourcefinder/client/platforms/{0}'.format(platform)):
            head, tail = split(filename)
            local('cp {0} /home/ec2-user/projects/{4}/apps/{1}/{2}/{3}/{5}_{2}'.format(filename, APP_NAME, app_version, platform, env.project_name, tail))

def sign_files(app_version):      
  """
  Sign the application files 
  """

  for platform in PLATFORMS:
    for filename in glob('/home/ec2-user/projects/{3}/apps/{0}/{0}/{1}/{2}/*'.format(APP_NAME, app_version, platform, env.project_name)):
        path_ext = splitext(filename)
        if len(path_ext == 2 and (path_ext) == '.sig' or path_ext[1] == '.xml'):
            pass
        else:
            local('home/ec2-user/projects/{1}/bin/sign_executable {0} /home/ec2-user/projects/{1}/keys/code_sign_private > {0}.sig'.format(filename, env.project_name))


def create_first_version():
    """
    Create the first version 
    Create the first versions of the files
    """    
    
    #local('cp -R /home/ec2-user/boinc_sourcefinder/server/templates/ /home/ec2-user/projects/{0}'.format(env.project_name))
    #local('cp -R /home/ec2-user/boinc_sourcefinder/server/ /home/ec2-user/projects/{0}'.format(env.project_name))
    copy_files(1)
    
    local('cd /home/ec2-user/projects/{0}; bin/xadd'.format(env.project_name))
    local('cd /home/ec2-user/projects/{0}; yes | bin/update_versions'.format(env.project_name))


def start_daemons():    
    """
    Start the BOINC daemons
    """
    
    local('cd home/ec2-user/projects/{0}/bin/start'.format(env.project_name))