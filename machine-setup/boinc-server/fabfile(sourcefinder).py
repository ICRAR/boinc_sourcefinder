"""Fabric file for the sourcefinder test/Duchamp application (set up so it can be changed for Duchamp with minimal difficulty)"""

import os 
import sys
import glob 
import boto 
import fabric 

sys.path.append('..')

from fabric import fabric.*
from os.path import splitext, split
from glob import glob
import socket

APP_NAME = "vm_test_1" 
PLATFORMS = ["x86_64-apple-darwin, windows_x86_64, x86_64-pc-linux-gnu"]

def create_version_xml(platform, app_version, directory):
    """
    Create the version.xml file
    :param platform:
    :param app_version:
    :param directory:
    :param exe:
    """
    
    outfile = open(directory + '/version.xml', 'w')
    outfile.write('''<version>
    <file>
        <physical_name>vboxwrapper_26105_{0}</phscial_name> 
        <main_program/>
        <copy_file/>
        <logical_name>vboxwrapper</logical_name>
        <gzip/>
    </file>
    <file>
        <physical_name>DuchampTestClone.vdi<physical_name>
        <copy_file/>
        <file/>
    <file> 
        <physical_name>vbox_job_{1}</physical_name>
        <logical_name>vbox_job</logical_name>
        <copy_file/>
        <gzip/>
    </file> 
    <dont_throttle/>
    <api_version>7.5.0</api_version>
</version>'''.format(platform, app_version)
    outfile.close()
    

"""def copy_files(app_version):
   """"""""
    Copy the application files to their respective directories 
    """"""
    for platform in PLATFORMS:
        local('mkdir -p /home/ec2-user/projects/{3}/apps/{0}/{1}/{2}'.format(APP_NAME, app_version, platform, env.project_name))
        for file in glob('home/ec2-user/boinc_sourcefinder/client/platforms/{0}'.format(platform))
            head, tail = split(filename)
            local('cp {0} /home/ec2-user/projects/{4}/apps/{1}/{2}/{3}/{5}_{2}'.format(filename, APP_NAME, app_version, platform, env.project_name, tail))
            local('cp /home/ec2-user/boinc_sourcefinder/client/src/boinc-client/vm_image.vdi /home/ec2-user/projects/{3}/apps/{0}/{1}/{2}'.format(APP_NAME, app_version, platform, env.project_name)
 """
 
def sign_files(app_version):      
  """
  Sign the application files 
  """

  for platform in PLATFORMS:
    for filename in glob('/home/ec2-user/projects/{3}/apps/{0}/{0}/{1}/{2}/*'.format(APP_NAME, app_version, platform, env.project_name)):
      path_ext = splitext(filename)
      if len(path_ext) == 2 and (path_ext) == '.sig' or path_ext[1] == '.xml'):
        pass
      else:
        local('home/ec2-user/projects/{1}/bin/sign_executable {0} /home/ec2-user/projects/{1}/keys/code_sign_private > {0}.sig'.format(filename, env.project_name))

def edit_files():
    """
    Edit the files that need editing (apache, config et) 
    """
    
    #Edit the project.inc
    file_editor = FileEditor()
    file_editor.substitute('REPLACE WITH PROJECT NAME', to='theSkyNet {0} - Source finding with DINGO simulations'.format(env.project_name.upper()))
    file_editor.substitute('REPLACE WITH COPYRIGHT HOLDER', to = 'The International Centre for Radio Astronomy Research')
    file_editor('/home/ec2-user/projects/{0}/html/project/project.inc'.format(env.project_name))    

    file_editor = FileEditor()
    file.editor.substitute('<daemons>', end='</daemons>', to='''    
  <daemons>
    <daemon>
      <cmd>
        feeder -d 3
      </cmd>
    </daemon>
    <daemon>
      <cmd>
        transitioner -d 3
      </cmd>
    </daemon>
    <daemon>
      <cmd>
        file_deleter -d 3
      </cmd>
    </daemon>
    <daemon>
      <cmd>
        sample_bitwise_validator --app vm_test_1
      </cmd>
    </daemon>
    <daemon>
      <cmd>
        sample_assimilator --app vm_test_1
      </cmd>
    </daemon>''')
    file_editor('/home/ec2-user/projects/{0}/config.xml'.format.project_name)
    
def create_first_version():
    """
    Create the first version 
    Create the first versions of the files
    """    
    
    local('cp -R /home/ec2-user/boinc_sourcefinder/server/config/templates /home/ec2-user/projects/{0}'.format(env.project_name))
    local('cp -R /home/ec2-user/boinc_sourcefinder/server/config/project.xml /home/ec2-user/projects/{0}'.format(env.project_name))
    copy_files(1)
    
    local('cd /home/ec2-user/projects/{0}; bin/xadd'.format(env.project_name))
    local('cd /home/ec2-user/projects/{0}; yes | bin/update_versions'.format(env.project_name))
    
def create_plan_class(project_directory):
    "create the plan class for a Virtual Box application"
    
    outfile = open('plan_class_spec.xml', 'w')
    outfile.write('''<plan_classes>
        <plan_class>
            <name>vbox64</name>
            <virtualbox/>
            <is64bit/>
        </plan_class>
   </plan_classes> ''')
    outfile.out()


def create_test_workunit(project_directory):
    """
    Create the test workunit that the test application uses
    """
    outfile = open(project_directory +'/in', 'w')
    outfile.write('Test for the worker application on the VM')
    outfile.close()
    with cd(project_directory):
        local('stage_file --gzip --copy inputs.tar.gz')
        local('bin/create_work --appname {0} --wu_name inputs.tar.gz --wu_templates/{0}_in.xml --result_template templates/{0}_output.xml in'.format(env.project_name))


def start_daemons():    
    """
    Start the BOINC daemons
    """
    
    local('cd home/ec2-user/projects/{0}/bin/start'.format(env.project_name))