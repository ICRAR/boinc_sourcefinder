# This is for setting up the VM client app on the boinc server.

import os, sys, shutil, subprocess
from subprocess import Popen, PIPE, STDOUT
from sqlalchemy import create_engine

# Arg1 the app version to update
# Arg2 path to the VM to set up

filesystem = {'apps': '/home/ec2-user/projects/duchamp/apps/duchamp',
              'app_templates': '/home/ec2-user/projects/duchamp/app_templates/',
              'vms': '/home/ec2-user/projects/duchamp/vm/',
              'sign_executable': '/home/ec2-user/projects/duchamp/bin/sign_executable',
              'update_versions': '/home/ec2-user/projects/duchamp/bin/update_versions',
              'keys': '/home/ec2-user/projects/duchamp/keys/',
              'download': '/home/ec2-user/projects/duchamp/download/'
}


def new_app(app_path):
    # Creating a new app
    os.mkdir(app_path)

    folders = os.listdir(filesystem['app_templates'])

    for folder in folders:
        if folder == 'base_template':
            continue  # We'll get to this later

        # Copy this folder in to the new app directory.
        shutil.copytree(os.path.join(filesystem['app_templates'], folder), os.path.join(app_path, folder))

    folders = os.listdir(app_path)  # This should now contain all of the app platform folders
    base_template_folders = os.listdir(os.path.join(filesystem['app_templates'], 'base_template'))

    for folder in folders:
        for f in base_template_folders:
            shutil.copy(f, folder)  # Copy each of the files in the base_template in to each of the newly made platform path.


def update_app(app_path, vm_path):
    # Updating an app

    # We assume that the app folder has already been set up correctly

    folders = os.listdir(app_path)

    # Each of the platform paths found in the app folder
    for folder in folders:
        # Copy the vm in
        folder = os.path.join(app_path, folder)
        if os.path.exists(os.path.join(folder, sys.argv[2])):
            os.remove(os.path.join(folder, sys.argv[2]))

        shutil.copy(vm_path, folder)

        # Sign it
        sign_file = os.path.join(folder, sys.argv[2])

        with open(sign_file, 'w') as f:

            subprocess.call([filesystem['sign_executable'],
                             os.path.join(folder, sys.argv[2]),
                             os.path.join(filesystem['keys'], 'code_sign_private')]
                            ,
                            stdout=f)

    download_vm_path = os.path.join(filesystem['download'], sys.argv[2])
    if os.path.exists(download_vm_path):
        os.remove(download_vm_path)
    if os.path.exists(download_vm_path + '.gz'):
        os.remove(download_vm_path + '.gz')

    p = Popen([filesystem['update_versions']], stdin=PIPE)
    p.communicate(input='y\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\n')  # Emulates the user going y enter y enter y enter for all of the 'do you want to add this version' prompts


def main():
    app_version_path = os.path.join(filesystem['apps'], sys.argv[1])  # This should be the app version
    vm_path = os.path.join(filesystem['vms'], sys.argv[2])  # This should be the path to the duchamp VM.vdi

    if not os.path.isfile(vm_path):
        print "Invalid VM path given. Make sure your vm is located in {0}".format(filesystem['vms'])
        return

    if not os.path.exists(app_version_path):
        print "The app version {0} does not exist. Creating".format(app_version_path)
        new_app(app_version_path)

    # App version path now exists
    update_app(app_version_path, vm_path)

if __name__ == '__main__':
    main()

