#! /usr/bin/env python

# Go through all of the XML folders in the app_templates folder and update the version.xml file.

import os
import sys

from boinc_sourcefinder.server.utils import DirStack
from boinc_sourcefinder.server.config import filesystem

base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))

base_xml = """<version>
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

# 0 - app executable name
# 1 - VM name
# 2 - vbox_job xml config name

dstack = DirStack()

def parse_args():
    return {'vm_name': sys.argv[1]}

def fix_app_version_xml(app_path, vm_name, xml_config_name):
    print 'Fixing {0}'.format(app_path)
    basename = os.path.basename
    dstack.push()
    os.chdir(app_path)

    exe_name = ''
    version_xml_path = os.path.join(app_path, 'version.xml')

    for item in os.listdir(app_path):
        if item.startswith('vboxwrapper'):
            exe_name = item
            break

    with open(version_xml_path, 'w') as f:
        new_xml = base_xml.format(basename(exe_name), basename(vm_name), basename(xml_config_name))
        print 'New XML: {0}'.format(new_xml)
        f.write(new_xml)

    dstack.pop()


def main():
    # Base template should contain one xml, which is the LATEST vbox_job.xml
    # All other folders should contain a version.xml (which will be modified) and a vboxwrapper program.

    args = parse_args()

    apps = []
    vbox_config_name = ''
    vm_name = os.path.join(filesystem['vms'], args['vm_name'])
    base_template_folder = os.path.join(filesystem['app_templates'], 'base_template')

    for folder in os.listdir(filesystem['app_templates']):
        if folder == 'base_template':
            continue

        apps.append(os.path.join(filesystem['app_templates'], folder))
        print 'Found app folder: {0}'.format(apps[-1])

    for f in os.listdir(base_template_folder):
        if f.startswith('vbox_job'):
            vbox_config_name = os.path.join(base_template_folder, f)
            break

    for app in apps:
        fix_app_version_xml(app, vm_name, vbox_config_name)

if __name__ == '__main__':
    main()