"Fabric file for the BOINC Source Finder server. Sets up everything for given project names etc"

import os
import sys
import boto
import glob
import fabric

from fabric import fabric.*


USERNAME = "ec2-user"
AMI_INSTANCE = 'i-7d6d6656'
YUM_PACKAGES = 'autoconf automake binutils gcc gcc-c++ libpng-devel libstdc++46-static gdb libtool gcc-gfortran git openssl-devel mysql mysql-devel python-devel python27 python27-devel '
BOINC_PACKAGES = 'httpd httpd-devel mysql-server php php-cli php-gd php-mysql mod_fcgid php-fpm postfix ca-certificates MySQL-python'
PIP_PACKAGES = 'boto sqlalchemy mysql'
AWS_KEYS = os.path.expanduser('~/.ssh/icrar-skynet-private-test.pem')
PUBLIC_DNS = 'ec2-user@54-208-207-86.compute-1.amazonaws.com'

#def nfs_connect(shared_directory):
#   """connect the nfs server to the /projects directory of the BOINC server"""
#   sudo('mount -t nfs {0}:/{1} /projects'.format(PUBLIC_DNS, shared_directory))
    

def general_install():
    yum_update()
    
    sudo('pip install {0}'.format(PIP_PACKAGES))
    sudo('yum install {0}'.format(YUM_PACKAGES))
    #setup pythonpath
    append('/home/ec2-user/.bach_profile',
           ['',
            'PYTHONPATH=/home/ec2-user/boinc/py:/home/ec2-user/boinc_sourcefinder/server/src',
            'export PYTHONPATH'])
    
    
def boinc_install():
    yum_update()
    general_install()
    
    sudo('yum install {0}'.format(BOINC_PACKAGES))
    run('git clone git://boinc.berkeley.edu/boinc-v2.git boinc')
    with cd('/home/ec2-users/boinc'):
        run('./_autosetup')
        run('./configure --disable-client --disable-manager')
        run('make')

    sudo('usermod -a -G ec2-user apache')
    
def project_install():
    #Clone the git project
    run('git clone git://github.com/ICRAR/boinc_sourcefinder.git')
    sudo('mysql_install_db')
    sudo('chown -R mysql:mysql /var/lib/mysql/*')
    sudo('chkconfig mysqld --add')
    sudo('chkconfig mysqld on')
    sudo('service mysqld start')
    
    #Files for apache need permissions
    with cd('home/ec2-user/boinc/tools'):
        run('./make_project -v --no_query --url_base http://{0} --db_user {1} --db_host={2} --db_passwd={3} {4}'.format(env.hosts[0], env.db_username, env.db_host_name, env.dp_password, env.project_name)
    
    run('chmod 711 /home/ec2-user')
    run('chmod -R oug+r /home/ec2-user/projects/{0}'.format(env.project_name))
    run('chmod -R oug+x /home/ec2-user/projects/{0}/html'.format(env.project_name))
    run('chmod ug+w /home/ec2-user/projects/{0}/log_*'.format(env.project_name))
    run('chmod ug+wx /home/ec2-user/projects/{0}/upload'.format(env.project_name))    

    #Copy configuration files
    sudo('mkdir /home/ec2-user/boinc/sfinder')
    run('git clone git://gitub.com/ICRAR/boinc-sourcefinder.git /home/ec2-user/boinc/sfinder')



def setup_website():
    """
    Setup the website

    Copy the config files and restart the httpd daemon
    """
    local('sudo cp /home/ec2-user/projects/{0}/{0}.httpd.conf /etc/httpd/conf.d'.format(env.project_name))


def yum_update():
    """Update general machine packages"""
    sudo('yum install update')

def mount_ebs(block_name): 
    """Mount the ebs volume on the server"""
    sudo('  .xfs /dev/{0}').format(block_name)
    sudo('mkdir /home/ec2-user/boinc')
    sudo('mount /dev/{0} /home/ec2-user/boinc').format(block_name)
    append('/etc/fstab', '/dev/md0    /dev/mnt    xfs    defaults    0    2', sudo=true)

#Kevin's code
def create_instance(ebs_size, ami_name):
    """
    Create the AWS instance
    :param ebs_size:   
    """
    
    ec2_connection = boto.connect_ec2()
    
    dev_sda = blockdevicemapping.EBSBlockDeviceType(delete_on_termination=True)
    dev_sda = int(ebs_size)
    bdm['/dev/sda'] = dev_sda
     reservations = ec2_connection.run_instances(AMI_ID, instance_type=INSTANCE_TYPE, key_name=KEY_NAME, security_groups=SECURITY_GROUPS, block_device_map=bdm)
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
    return instance, ec2_connection
        fastprint('.')
        time.sleep(5)
    puts('.')

    # Return the instance


