"Fabric file for the BOINC Source Finder server. Sets up everything for given project names etc"

import glob
import boto
import os
import time
from boto.ec2 import blockdevicemapping

from fabric.api import run, sudo, put, env, require, local
from fabric.context_managers import cd
from fabric.contrib.files import append, comment, exists
from fabric.decorators import task, serial
from fabric.operations import prompt
from fabric.utils import puts, abort, fastprint

from os.path import exists as local_exists

USERNAME = 'ec2-user'
AMI_ID = 'ami-6869aa05' #'ami-7d6d6656'. This is the default amazon ami.
INSTANCE_TYPE = 't2.small'

YUM_PACKAGES = 'autoconf automake binutils gcc gcc-c++ libpng-devel libstdc++46-static gdb libtool gcc-gfortran git openssl-devel mysql mysql-devel python-devel python27 python27-devel python-pip curl-devel gfortran blas-devel lapack-devel'
BOINC_PACKAGES = 'httpd httpd-devel mysql-server php php-cli php-gd php-mysql mod_fcgid php-fpm postfix ca-certificates MySQL-python'
PIP_PACKAGES = 'boto sqlalchemy mysql fabric numpy scipy astropy'

AWS_KEY = os.path.expanduser('~/.ssh/icrar_theskynet_private_test.pem')
KEY_NAME = 'icrar_theskynet_private_test' # the key name to use to connect to the server
# PUBLIC_DNS = 'ec2-user@54-208-207-86.compute-1.amazonaws.com' unused
SECURITY_GROUPS = ['sg-dd33e0b2'] # TheSkyNet security group
SUBNET_ID = 'subnet-794e7d16' # production = subnet-5390a03c
# NETWORK = 'vpc=b493a3db' # production = vpc-53af9f3c unused
PROJECT_NAME = 'duchamp'
PARAMETERS_DIRECTORY = "~/sf_parameters"
CUBES_DIRECTORY = "~/sf_cubes"
DEFAULT_S3_BUCKET = "icrar.sourcefinder.files"

# def nfs_connect(shared_directory):
#   """connect the nfs server to the /projects directory of the BOINC server"""
#   sudo('mount -t nfs {0}:/{1} /projects'.format(PUBLIC_DNS, shared_directory))


def yum_update():
    """Update general machine packages"""

    sudo('yum update')


def mount_ebs(block_name):
    """Mount the ebs volume on the server"""
    sudo('mkfs -t ext4 /dev/{0}'.format(block_name))
    sudo('mkdir /home/{0}/storage'.format(env.user))
    sudo('mount /dev/{0} /home/{1}/storage'.format(block_name, env.user))
    append('/etc/fstab', '/dev/{0}    /dev/mnt    ext4    defaults,nofail    0    2'.format(block_name), sudo=True)
    sudo('chown -R {0}:{0} /home/{0}/storage'.format(env.user))


# Kevin's code
def create_instance(ebs_size, ami_name, ec2_connection):
    """
    Create the AWS instance
    :param ebs_size:
    """

    puts('Creating the instance {1} with disk size {0} GB'.format(ebs_size, ami_name))

    # ec2_connection = boto.connect_ec2()

    dev_sda = blockdevicemapping.EBSBlockDeviceType(delete_on_termination=True)
    dev_sda.size = int(ebs_size)
    bdm = blockdevicemapping.BlockDeviceMapping()
    bdm['/dev/xvda'] = dev_sda # bdm['/dev/sda'] = dev_sda

    # Now we need to specify a network interface like this to get a public IP.
    interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(subnet_id=SUBNET_ID,
                                                                        groups=SECURITY_GROUPS,
                                                                        associate_public_ip_address=True)
    interfaces = boto.ec2.networkinterface.NetworkInterfaceCollection(interface)

    reservations = ec2_connection.run_instances(AMI_ID,
                                                instance_type=INSTANCE_TYPE,
                                                key_name=KEY_NAME,
                                                block_device_map=bdm,
                                                network_interfaces=interfaces,
                                                # security_group_ids=SECURITY_GROUPS,
                                                # subnet_id=SUBNET_ID
                                                )
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
    return instance

    # Return the instance


def start_ami_instance(ami_id, instance_name):
    """
    Start an AMI instance running
    :param ami_id:
    :param instance_name:
    """

    puts('Starting the instance {0} from id {1}'.format(instance_name, ami_id))

    ec2_connection = boto.connect_ec2()

    interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(subnet_id=SUBNET_ID,
                                                                        groups=SECURITY_GROUPS,
                                                                        associate_public_ip_address=True)

    interfaces = boto.ec2.networkinterface.NetworkInterfaceCollection(interface)

    reservations = ec2_connection.run_instances(ami_id, instance_type=INSTANCE_TYPE, key_name=KEY_NAME,
                                                network_interfaces=interfaces)

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
    puts("updating yum...")
    yum_update()

    puts("installing yum packages...")
    sudo('yum install {0}'.format(YUM_PACKAGES))

    puts("installing pip packages...")
    sudo('pip install {0}'.format(PIP_PACKAGES))
    # setup pythonpath
    append('/home/ec2-user/.bash_profile',
           ['',
            'PYTHONPATH=/home/ec2-user/boinc/py:/home/ec2-user/boinc_sourcefinder/server/src',
            'export PYTHONPATH'])


def boinc_install():

    sudo('yum install {0}'.format(BOINC_PACKAGES))
    if not exists('boinc'):
        run('git clone https://github.com/BOINC/boinc.git')
        with cd('/home/ec2-user/boinc'):
            run('./_autosetup')
            run('./configure --disable-client --disable-manager')
            run('make')
    sudo('usermod -a -G ec2-user apache')


def project_install():
    # boinc_install() done before this anyway
    # Clone the git project
    user = 'ec2-user'#, 'apache']

    try:
        sudo('useradd {0}.'.format(user))
        sudo('chmod 700 /home/{0}'.format(user))
        sudo('chown {0}:{0} /home/{0}/.ssh'.format(user))
        sudo('chmod 700 /home/{}/.ssh/authorized_keys'.format(user))
        sudo('chown {0}:{0} /home/{0}/.ssh/authorized_keys'.format(user))
        sudo('''su -l root -c 'echo "{0} ALL = NOPASSWD:ALL" >> /etc/sudoers' '''.format(user))
    except:
        pass # already done

    # Copy configuration files
    try:
        sudo('mkdir /home/ec2-user/boinc_sourcefinder')
        sudo('git clone https://github.com/sam6321/boinc_sourcefinder.git /home/ec2-user/boinc_sourcefinder')
        sudo('mkdir ~/sf_cubes')
        sudo('mkdir ~/sf_parameters')
    except:
        pass

    with cd("/home/ec2-user/boinc_sourcefinder"):
        sudo("git pull")

    try:
        sudo('mysql_install_db')
        sudo('chown -R mysql:mysql /var/lib/mysql/*')
        sudo('chkconfig mysqld --add')
        sudo('chkconfig mysqld on')
        sudo('service mysqld start')
    except:
        pass

    #if env.db_hostname == 'localhost':  # Create a user for the DB and change the default one's password, only if we're using localhost as our DB
    #    run('''mysql -u root "CREATE USER '{1}'@'localhost' IDENTIFIED BY '{0}';"'''.format(env.db_password, env.db_username)) # "ALTER USER 'root'@'localhost' IDENTIFIED BY {0};

    # Setup the database for recording WU's
    run(
        'mysql --user={0} --host={1} --password={2} < /home/ec2-user/boinc_sourcefinder/server/database/create_database.sql'.format(
            env.db_username, env.db_hostname, env.db_password))

    if not exists('home/ec2-user/projects/{0}/'.format(PROJECT_NAME)):
        with cd('/home/ec2-user/boinc/tools'):
            sudo('rm /home/ec2-user/projects/{0}/ -rf'.format(PROJECT_NAME))
            run('./make_project --delete_prev_inst --drop_db_first -v --no_query --url_base http://{0} --db_user {1} --db_host={2} --db_passwd={3} {4}'.format(
                env.hosts[0], env.db_username, env.db_hostname, env.db_password, PROJECT_NAME))

    sudo('chmod -R oug+r /home/ec2-user/projects/{0}'.format(PROJECT_NAME))
    sudo('chmod -R oug+x /home/ec2-user/projects/{0}/html'.format(PROJECT_NAME))
    sudo('chmod ug+w /home/ec2-user/projects/{0}/log_*'.format(PROJECT_NAME))
    sudo('chmod ug+wx /home/ec2-user/projects/{0}/upload'.format(PROJECT_NAME))

    if exists("/home/ec2-user/boinc_sourcefinder/server/config/duchamp.settings"):
        sudo("rm /home/ec2-user/boinc_sourcefinder/server/config/duchamp.settings")

    sudo('''echo '# DB Settings
databaseUserid = {0}
databasePassword = {1}
databaseHostname = {2}
databaseName = sourcefinder
boincDatabaseName = {3}
paramDirectory = /home/ec2-user/sf_parameters
cubeDirectory = /home/ec2-user/sf_cubes
boincPath = /home/ec2-user/projects/duchamp
wgThreshold = 500
bucket = icrar.sourcefinder.files' > /home/ec2-user/boinc_sourcefinder/server/config/duchamp.settings'''.format(env.db_username,
                                                                                                    env.db_password,
                                                                                                    env.db_hostname,
                                                                                                    PROJECT_NAME))
    # Create the initial set of parameter files
    sudo('python /home/ec2-user/boinc_sourcefinder/server/workgeneration/generate_parameter_files.py')

    # Modify the config.xml file to match our project settings.


def setup_website():
    """
    Setup the website

    Copy the config files and restart the httpd daemon
    """
    sudo('cp /home/ec2-user/projects/{0}/{0}.httpd.conf /etc/httpd/conf.d'.format(PROJECT_NAME))
    sudo('service httpd start')


def create_vm():
    """
    Sets up the virtual machine for the BOINC clients
    :return:
    """

    # Move VM from git directory to VM directory under the boinc directory.
    try:
        sudo("mkdir /home/ec2-user/projects/{0}/vm".format(PROJECT_NAME))
    except:
        pass

    if not exists("/home/ec2-user/DuchampVM.vdi.gz"):
        if not local_exists("DuchampVM.vdi.gz"):
            puts("Missing DuchampVM.vdi.gz VM file.")
            puts("Please place the VM file in the same file as the fabric script, and ensure it is named correctly")

            return False

        puts("Uploading VM to server...")
        put('DuchampVM.vdi.gz', "/home/ec2-user/DuchampVM.vdi.gz".format(PROJECT_NAME), use_sudo=True)

    sudo("cp /home/ec2-user/DuchampVM.vdi.gz /home/ec2-user/projects/{0}/vm/DuchampVM.vdi.gz".format(PROJECT_NAME))

    with cd("/home/ec2-user/projects/{0}/vm/".format(PROJECT_NAME)):
        sudo('gunzip DuchampVM.vdi.gz'.format(PROJECT_NAME))

    sudo("cp /home/ec2-user/boinc_sourcefinder/machine-setup/app_templates /home/ec2-user/projects/{0}/ -r".format(PROJECT_NAME))

    # Run the setup_app.py script to set up the VM correctly
    sudo('mkdir /home/ec2-user/projects/{0}/apps/duchamp'.format(PROJECT_NAME))
    sudo("python /home/ec2-user/boinc_sourcefinder/server/setup_app.py 1.0 DuchampVM.vdi".format(PROJECT_NAME))


def base_setup_env():
    """
    Sets up a server to run boinc on.
    """
    print env

    if 'ebs_size' not in env:
        prompt('EBS Size (GB)', 'ebs_size', default=50, validate=int)
    if 'ami_name' not in env:
        prompt('AMI Name', 'ami_name', default='base-python-ami')

    ec2_connection = boto.connect_ec2()

    instances = [i for r in ec2_connection.get_all_reservations() for i in r.instances]

    ec2_instance = None
    for i in instances:
        if 'Name' in i.tags:
            if i.tags['Name'] == env.ami_name:
                ec2_instance = i
                break

    if ec2_instance is None:  # boot up an instance if one doesn't exist.
        ec2_instance = create_instance(env.ebs_size, env.ami_name, ec2_connection)

    env.ec2_instance = ec2_instance
    env.ec2_connection = ec2_connection
    env.hosts = [ec2_instance.ip_address]

    env.user = USERNAME
    env.key_filename = AWS_KEY

    puts("Provide this as part of the command line for the next part: -H {0} ".format(ec2_instance.ip_address))


def base_build_ami():
    """
    Build the base AMI
    """
    puts('Building the amazon instance for server use...')

    require('hosts', provided_by=[base_setup_env])

    puts('Updating yum')
    yum_update()

    puts('Performing general install')
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

    if 'instance_name' not in env:
        prompt('Enter an instance name to use: ', 'instance_name', default='base-boinc-ami')

    instances = [i for r in ec2_connection.get_all_reservations() for i in r.instances]

    ec2_instance = None
    for i in instances:
        if 'Name' in i.tags:
            if i.tags['Name'] == env.instance_name:
                ec2_instance = i
                break

    if ec2_instance is None:
        if 'ami_id' not in env:
            images = ec2_connection.get_all_images(owners=['self'])
            puts('Available images')
            for image in images:
                puts('Image: {0} {1} {2}'.format(image.id, image.name, image.description))
            prompt('Instance is not running. Enter an AMI to build the instance from: ', 'ami_id')

            puts('Attempting to start ami instance')
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
    # puts('env = ')
    # print env

    require('hosts', provided_by=[boinc_setup_env])
    require('db_username', used_for="Setting up the database.")
    require('db_password', used_for="Setting up the database.")
    require('db_hostname', used_for="Setting up the database.")

    # time.sleep(5)

    puts('Updating packages...')
    general_install()

    puts('Installing boinc...')
    boinc_install()

    # puts('setting up ebs') doesnt appear to be needed?
    # mount_ebs("xvda") # testing with SDA3

    puts('Installing sourcefinder project...')
    project_install()

    puts('Setting up website')
    setup_website()

    puts("Attempting to create client VM")
    if not create_vm():
        return False

    puts("stopping the instance")
    env.ec2_connection.stop_instances(env.ec2_instance.id, force=True)
    while not env.ec2_instance.update() == 'stopped':
        fastprint('.')
        time.sleep(5)

    puts("Server install has completed successfully. The running server will now be saved as an AMI.")
    prompt("Please enter an AMI name for the server instance:", 'ami_name', default="Sourcefinder server AMI")

    puts("The AMI is being created. Don't forget to terminate the instance if not needed")
    env.ec2_connection.create_image(env.ec2_instance.id, env.ami_name, description='The base BOINC AMI')

    puts('All done')


