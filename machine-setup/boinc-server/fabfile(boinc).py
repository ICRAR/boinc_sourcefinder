"Fabric file for the BOINC Source Finder server. Sets up everything for given project names etc"

import glob
import boto
import os
import time
from boto.ec2 import blockdevicemapping

from fabric.api import run, sudo, put, env, require, local
from fabric.context_managers import cd
from fabric.contrib.files import append, comment
from fabric.decorators import task, serial
from fabric.operations import prompt
from fabric.utils import puts, abort, fastprint

USERNAME = 'ec2-user'
AMI_ID = 'i-7d6d6656'
INSTANCE_TYPE = 't2.small'
YUM_PACKAGES = 'autoconf automake binutils gcc gcc-c++ libpng-devel libstdc++46-static gdb libtool gcc-gfortran git openssl-devel mysql mysql-devel python-devel python27 python27-devel python-pip curl-devel'
BOINC_PACKAGES = 'httpd httpd-devel mysql-server php php-cli php-gd php-mysql mod_fcgid php-fpm postfix ca-certificates MySQL-python'
PIP_PACKAGES = 'boto sqlalchemy mysql fabric nympy scipy astropy'
AWS_KEY = os.path.expanduser('~/.ssh/icrar_theskynet_private_test.pem')
KEY_NAME = 'icrar_theskynet_private_test.pem'
PUBLIC_DNS = 'ec2-user@54-208-207-86.compute-1.amazonaws.com'
SECURITY_GROUPS = ['defaults', 'theSkynet']

# def nfs_connect(shared_directory):
#   """connect the nfs server to the /projects directory of the BOINC server"""
#   sudo('mount -t nfs {0}:/{1} /projects'.format(PUBLIC_DNS, shared_directory))

def yum_update():
    """Update general machine packages"""

    sudo('yum install update')


def mount_ebs(block_name):
    """Mount the ebs volume on the server"""
    sudo('mkfs -t ext4 /dev/{0}').format(block_name)
    sudo('mkdir /home/{0}/storage').format(env.user)
    sudo('mount /dev/{0} /home/{1}/storage').format(block_name, env.user)
    append('/etc/fstab', '/dev/{0}    /dev/mnt    ext4    defaults,nofail    0    2'.format(block_name), sudo=True)
    sudo('chown -R {0}:{0} /home/{0}/storage'.format(env.user))


# Kevin's code
def create_instance(ebs_size, ami_name):
    """
    Create the AWS instance
    :param ebs_size:
    """

    puts('Creating the instance {1} with disk size {0} GB'.format(ebs_size, ami_name))

    ec2_connection = boto.connect_ec2()

    dev_sda = blockdevicemapping.EBSBlockDeviceType(delete_on_termination=True)
    dev_sda.size = int(ebs_size)
    bdm = blockdevicemapping.BlockDeviceMapping()
    bdm['/dev/sda'] = dev_sda
    reservations = ec2_connection.run_instances(AMI_ID, instance_type=INSTANCE_TYPE, key_name=KEY_NAME,
                                                security_groups=SECURITY_GROUPS, block_device_map=bdm)
    instance = reservations.instances[0]
    # Sleep so Amazon recognizes the new instance
    for i in range(4):
        fastprint('.')
        time.sleep(5)

    # Are we running yet?
    while not instance.update() == 'running':
        fastprint('.')
        time.sleep(5)

    # Sleep a bit more Amazon recognizes the new instance
    for i in range(4):
        fastprint('.')
        time.sleep(5)
    puts('.')

    ec2_connection.create_tags([instance.id], {'Name': '{0}'.format(ami_name)})

    # The instance is started, but not useable (yet)
    puts('Started the instance now waiting for the SSH daemon to start.')
    for i in range(12):
        fastprint('.')
        time.sleep(5)
    puts('.')
    return instance, ec2_connection

    # Return the instance


def start_ami_instance(ami_id, instance_name):
    """
    Start an AMI instance running
    :param ami_id:
    :param instance_name:
    """

    puts('Starting the instance{0} from id {1}'.format(instance_name, ami_id))

    ec2_connection = boto.connect_ec2()

    reservations = ec2_connection.run_instances(ami_id, instance_type=INSTANCE_TYPE, key_name=KEY_NAME,
                                                security_groups=SECURITY_GROUPS)

    instance = reservations.instances[0]

    # sleep
    for i in range(4):
        fastprint('.')
        time.sleep(5)

    while not instance.update() == 'running':
        fastprint('.')
        time.sleep(5)

    for i in range(4):
        fastprint('.')
        time.sleep(5)
    puts('.')

    ec2_connection.create_tags([instance.id], {'Name': '{0}'.format(instance_name)})

    puts('Started the instance(s) now waiting for the ssh daemon to start.')
    for i in range(12):
        fastprint('.')
        time.sleep(5)
    puts('.')

    puts('Started the instance now waiting for the SSH daemon to start.')
    for i in range(12):
        fastprint('.')
        time.sleep(5)
    puts('.')

    # Return the instance
    return instance, ec2_connection


def general_install():
    yum_update()

    sudo('yum install {0}'.format(YUM_PACKAGES))
    sudo('pip install {0}'.format(PIP_PACKAGES))
    # setup pythonpath
    append('/home/ec2-user/.bach_profile',
           ['',
            'PYTHONPATH=/home/ec2-user/boinc/py:/home/ec2-user/boinc_sourcefinder/server/src',
            'export PYTHONPATH'])


def boinc_install():
    general_install()

    sudo('yum install {0}'.format(BOINC_PACKAGES))
    run('git clone git://boinc.berkeley.edu/boinc-v2.git boinc')
    with cd('/home/ec2-users/boinc'):
        run('./_autosetup')
        run('./configure --disable-client --disable-manager')
        run('make')
    sudo('usermod -a -G ec2-user apache')


def project_install():
    boinc_install()
    mount_ebs()
    # Clone the git project

    for user in env.list_of_users:
        sudo('useradd {0}.'.format(user))
        sudo('chmod 700 /home/{0}'.ssh.format(user))
        sudo('chown {0}:{0} /home/{0}/.ssh'.format(user))
        sudo('chmod 700 /home/{}/.ssh/authorized_keys'.format(user))
        sudo('chmod {0}:{0} /home/{0}/.ssh/authorized_keys'.format(user))
        sudo('''su -l root -c 'echo "{0} ALL = NOPASSWD:ALL" >> /etc/sudoers' '''.format(user))

    run('chmod -R oug+r /home/ec2-user/projects/{0}'.format(env.project_name))
    run('chmod -R oug+x /home/ec2-user/projects/{0}/html'.format(env.project_name))
    run('chmod ug+w /home/ec2-user/projects/{0}/log_*'.format(env.project_name))
    run('chmod ug+wx /home/ec2-user/projects/{0}/upload'.format(env.project_name))

    # Copy configuration files
    sudo('mkdir /home/ec2-user/boinc/sfinder')
    run('git clone git://gitub.com/ICRAR/boinc-sourcefinder.git /home/ec2-user/boinc/sfinder')

    sudo('mysql_install_db')
    sudo('chown -R mysql:mysql /var/lib/mysql/*')
    sudo('chkconfig mysqld --add')
    sudo('chkconfig mysqld on')
    sudo('service mysqld start')

    # Setup the database for recording WU's
    run(
        'mysql --user={0} --host={1} --password={2} < /home/ec2-user/boinc-magphys/server/src/database/create_database.sql'.format(
            env.db_username, env.db_host_name, env.db_password))

    with cd('home/ec2-user/boinc/tools'):
        run('./make_project -v --no_query --url_base http://{0} --db_user {1} --db_host={2} --db_passwd={3} {4}'.format(
            env.hosts[0], env.db_username, env.db_host_name, env.dp_password, env.project_name))


    run('''echo '# DB Settings
databaseUserid = "{0}"
databasePassword = "{1}"
databaseHostname = "{2}"
databaseName = "duchamp"
boincDatabaseName = "{3}"' > /home/ec2-user/boinc_sourcefinder/server/src/config/duchamp.settings'''.format(env.db_username,
                                                                                                    env.db_password,
                                                                                                    env.db_host_name,
                                                                                                    env.project_name))

def setup_website():
    """
    Setup the website

    Copy the config files and restart the httpd daemon
    """
    local('sudo cp /home/ec2-user/projects/{0}/{0}.httpd.conf /etc/httpd/conf.d'.format(env.project_name))


def base_setup_env():
    """

    """

    if 'ebs_size' not in env:
        prompt('EBS Size (GB)', 'ebs_size', default=50, validate=int)
    if 'ami_name' not in env:
        prompt('AMI Name', 'ami_name', default='base-python-ami')

    ec2_instance, ec2_connection = create_instance(env.ebs_size, env.ami_name)
    env.ec2_instance = ec2_instance
    env.ec2_connection = ec2_connection
    env.hosts = [ec2_instance.ip_address]

    env.user = USERNAME
    env.key_filename = AWS_KEY


def base_build_ami():
    """
    Build the base AMI
    """

    require('hosts', provided_by=[base_setup_env])

    yum_update()

    general_install()

    puts("Stopping the instance")
    env.ec2_connection.stop_instances(env.ec2_instance.id, force=True)
    while not env.ec2_instance.update() == 'stopped':
        fastprint('.')
        time.sleep(5)

    puts("The AMI is being created. Don't forget to terminate the instance if not needed")
    env.ec2_connection.create_image(env.ec2_instance.id, env.ami_name, description='The base python AMI')

    puts('All done.')


def boinc_setup_env():
    """
    Ask a series of questions before deploying to the cloud
    Allow the user to select if an Elastic IP address is to be used
    """

    ec2_connection = boto.connect_ec2()
    if 'ami_id' not in env:
        images = ec2_connection.get_all_images(owners=['self'])
        puts('Available images')
        for image in images:
            puts('Image: {0: , 15} {1: ,35} {2}'.format(image.id, image.name, image.description))
        prompt('AMI id to build from: ', 'ami_id')
    if 'ami_name' not in env:
        prompt('AMI Name: ', 'ami_name', default='base-boinc-ami')
    if 'instance_name' not in env:
        prompt('AUS insance name: ', 'instance_name', default='base-boinc-ami')

    ec2_instance, ec2_connection = start_ami_instance(env.ami_id, env.instance_name)
    env.ec2_instance = ec2_instance
    env.ec2_connection = ec2_connection
    env.hosts = [ec2_instance.ip_address]

    env.user = USERNAME
    env.key_filename = AWS_KEY


def boinc_build_ami():
    """
    Deploy the single server environment
    Deploy the single server system in the AWS cloud 
    """
    require('host', provided_by=[boinc_setup_env])

    time.sleep(5)

    boinc_install()
    project_install()

    puts("stopping the instance")
    env.ec2_connection.stop_instances(env.ec2_instance.id, force=True)
    while not env.ec2_instance.update() == 'stopped':
        fastprint('.')
        time.sleep(5)

    puts("The AMI is being created. Don't forget to terminate the instance if not needed")
    env.ec2_connection.create_image(env.ec2_instance.id, env.ami_name, description='The base BOINC AMI')

    puts('All done')


