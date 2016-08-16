# This is for setting up the VM client app on the boinc server.

import os, sys, shutil, subprocess
from subprocess import Popen, PIPE
from time import sleep

base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))

class DirStack:
    """
    DirStack is a simple helper class that allows the user to push directories on to the stack then
    pop them off later. If you want to change the working directory of the program, use stack.push() then
    os.chdir(dir).
    Later, to restore the previous directory, use stack.pop()
    """

    def __init__(self):
        self.stack = []

    def push(self):
        self.stack.append(os.getcwd())

    def pop(self):
        os.chdir(self.stack.pop())

# Arg1 the app version to update
# Arg2 path to the VM to set up

filesystem = {'apps': '/home/ec2-user/projects/duchamp/apps/duchamp',
              'app_templates': '/home/ec2-user/projects/duchamp/app_templates/',
              'vms': '/home/ec2-user/projects/duchamp/vm/',
              'sign_executable': '/home/ec2-user/projects/duchamp/bin/sign_executable',
              'update_versions': '/home/ec2-user/projects/duchamp/bin/update_versions',
              'keys': '/home/ec2-user/projects/duchamp/keys/',
              'download': '/home/ec2-user/projects/duchamp/download/',
              'project': '/home/ec2-user/projects/duchamp/'
}


def new_app(app_path):
    # Creating a new app
    os.mkdir(app_path)

    folders = os.listdir(filesystem['app_templates'])

    for folder in folders:
        if folder == 'base_template':
            continue  # We'll get to this later

        # Copy this folder in to the new app directory.
        print os.path.join(filesystem['app_templates'], folder)
        print os.path.join(app_path, folder)
        sleep(5)
        shutil.copytree(os.path.join(filesystem['app_templates'], folder), os.path.join(app_path, folder))

    folders = os.listdir(app_path)  # This should now contain all of the app platform folders
    base_template = os.path.join(filesystem['app_templates'], 'base_template')
    base_template_folders = os.listdir(base_template)

    for folder in folders:
        for f in base_template_folders:
            print "Coping {0} to {1}".format(f, os.path.join(app_path, folder))
            shutil.copy(os.path.join(base_template, f), os.path.join(app_path, folder))  # Copy each of the files in the base_template in to each of the newly made platform path.

        for f in os.listdir(folder):
            # Sign each file within the app folder
            sign_file(f)


def sign_file(filename):
    with open(filename + ".sig", 'w') as f:
        subprocess.call([filesystem['sign_executable'],
                         filename,
                         os.path.join(filesystem['keys'], 'code_sign_private')]
                        ,
                        stdout=f)


def update_app(app_path, vm_path):
    # Updating an app

    dstatck = DirStack()

    # We assume that the app folder has already been set up correctly

    folders = os.listdir(app_path)

    # Sign the vm
    sign_file(os.path.join(filesystem['vms'], sys.argv[2]))

    sign_filename = os.path.join(filesystem['vms'], sys.argv[2]) + ".sig"

    # Each of the platform paths found in the app folder
    for folder in folders:
        # Copy the vm in

        folder = os.path.join(app_path, folder)

        print "Making link between {0} and {1}".format(vm_path, os.path.join(folder, sys.argv[2]))

        if os.path.exists(os.path.join(folder, sys.argv[2])):
            os.unlink(os.path.join(folder, sys.argv[2]))

        os.link(vm_path, os.path.join(folder, sys.argv[2]))

        # Sign it
        print "Copying vm signature in to {0}".format(sign_file)
        shutil.copy(sign_filename, folder)

    download_vm_path = os.path.join(filesystem['download'], sys.argv[2])
    if os.path.exists(download_vm_path):
        os.remove(download_vm_path)
    if os.path.exists(download_vm_path + '.gz'):
        os.remove(download_vm_path + '.gz')

    dstatck.push()
    os.chdir(filesystem['project'])

    p = Popen([filesystem['update_versions']], stdin=PIPE)
    p.communicate(input='y\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\n')  # Emulates the user going y enter y enter y enter for all of the 'do you want to add this version' prompts

    dstatck.pop()

    # If the database already contained this version, then update_versions wont copy the new VM to the download directory, so we have to copy it now.

    if not os.path.exists(download_vm_path):
        print "VM is missing from download directory, copying..."
        shutil.copy(vm_path, download_vm_path)

        dstatck.push()
        os.chdir(filesystem['download'])

        os.system('gzip < {0} > {0}.gz'.format(sys.argv[2]))
        dstatck.pop()

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

