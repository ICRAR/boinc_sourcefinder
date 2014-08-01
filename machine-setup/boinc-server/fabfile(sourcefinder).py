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
PLATFORMS = ["x86_64-apple-darwin"]

def create_version_xml(directory):
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
        <physical_name>vm_image.vdi</phscial_name> 
        <main_program/>
        <copy_file/>
        <logical_name>vm_image.vdi</logical_name>
        <gzip/>
    </file>
    <dont_throttle/>
</version>'''
    outfile.close()
    

def copy_files(app_version):
    """
    Copy the application files to their respective directories 
    """
    for platform in PLATFORMS:
        local('mkdir -p /home/ec2-user/projects/{3}/apps/{0}/{1}/{2}'.format(APP_NAME, app_version, platform, env.project_name))
        for file in glob('home/ec2-user/boinc_sourcefinder/client/platforms/{0}'.format(platform))
            head, tail = split(filename)
            local('cp {0} /home/ec2-user/projects/{4}/apps/{1}/{2}/{3}/{5}_{2}'.format(filename, APP_NAME, app_version, platform, env.project_name, tail))
            local('cp /home/ec2-user/boinc_sourcefinder/client/src/boinc-client/vm_image /home/ec2-user/projects/{3}/apps/{0}/{1}/{2}'.format(APP_NAME, app_version, platform, env.project_name)
        if platform in WINDOWS_PLATFORMS:
            create_version_xml(platform, app_version, '/home/ec2-user/projects/{3}/apps/{0}/{1}/{2}'.format(APP_NAME, app_version, platform, env.project_name), '.exe')
        else:
            create_version_xml(platform, app_version, '/home/ec2-user/projects/{3}/apps/{0}/{1}/{2}'.format(APP_NAME, app_version, platform, env.project_name), '')

def edit_files():
    """
    Edit the files that need editing (apache, config et) 
    """
    
    #Edit the project.inc
    file_editor = FileEditor()
    file_editor.substitute('REPLACE WITH PROJECT NAME', to='vm_test_1')
    file_editor.subsitute('REPLACE WITH URL', to='vm_test_1')
    file_editor.substitute('REPLACE WITH COPYRIGHT HOLDER', to = 'The International Centre for Radio Astronomy Research')
    file_editor.substitute('')#the url base, with the public dns of the instance
    
    file_editor = FileEditor()
    file.editor.substitute('<tasks>', end='</daemons>', to='''
     <task>
      <cmd>
        antique_file_deleter -d 2
      </cmd>
      <period>
        24 hours
      </period>
      <disabled>
        0
      </disabled>
      <output>
        antique_file_deleter.out
      </output>
    </task>
    <task>
      <cmd>
        db_dump -d 2 --dump_spec ../db_dump_spec.xml
      </cmd>
      <period>
        24 hours
      </period>
      <disabled>
        0
      </disabled>
      <output>
        db_dump.out
      </output>
    </task>
    <task>
      <cmd>
        run_in_ops ./update_uotd.php
      </cmd>
      <period>
        1 days
      </period>
      <disabled>
        0
      </disabled>
      <output>
        update_uotd.out
      </output>
    </task>
    <task>
      <cmd>
        run_in_ops ./update_forum_activities.php
      </cmd>
      <period>
        1 hour
      </period>
      <disabled>
        0
      </disabled>
      <output>
        update_forum_activities.out
      </output>
    </task>
    <task>
      <cmd>
        update_stats
      </cmd>
        1 days
      </period>
      <disabled>
        0
      </disabled>
      <output>
        update_stats.out
      </output>
    </task>
    <task>
      <cmd>
       run_in_ops ./update_profile_pages.php
      </cmd>
      <period>
        24 hours
      </period>
      <disabled>
        0
      </disabled>
      <output>
        update_profile_pages.out
      </output>
    </task>
    <task>
      <cmd>
        run_in_ops ./team_import.php
      </cmd>
      <period>
        24 hours
      </period>
      <disabled>
        1
      </disabled>
      <output>
        team_import.out
      </output>
    </task>
    <task>
      <cmd>
        run_in_ops ./notify.php
      </cmd>
      <period>
        24 hours
      </period>
      <disabled>
        0
      </disabled>
      <output>
        notify.out
      </output>
    </task>
          <period>
        24 hours
      </period>
      <disabled>
        0
      </disabled>
      <output>
        badge_assign.out
      </output>
    </task>
  </tasks>
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
        sample_assimilator -app vm_test_1
      </cmd>
    </daemon>''')
    
def setup_website():
    '''
    Setup the website
    Copy the config files and restart the httpd daemon
    '''
    local('sudo cp /home/ec2-user/projects/{0}/{0}.httpd.conf /etc/httpd/conf.d'.format(env.project_name))
    
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
        local('stage_file --gzip --copy in')
        local('bin/create_work --appname {0} --wu_name in --wu_templates/{0}_in.xml --result_template templates/{0}_out.xml in'.format(env.project_name))


def start_daemons():    
    """
    Start the BOINC daemons
    """
    
    local('cd home/ec2-user/projects/{0}/bin/start'.format(env.project_name))