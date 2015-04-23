"""fabric file for the raid system that the nfs server connects to for the sourcefinder"""

import boto
import glob
import fabric 
import argparse

from fabric.api import *
from boto.ec2 import blockdevicemapping
import time

INSTANCE_TYPE ='t1.small'
YUM_PACKAGES = 'mdadm xfsprogs' 
USERNAME ='ec2-user'
TEST_SECURITY_GROUPS = ['sg-dd33e0b2', 'sg-9408dbfb']
AVAILABILITY_ZONE ='north-virginia-1c'


def setup_disks(disk_1, disk_2):
    """setup the RAID1 configuration on the nfs server
    :param disk_1: the name of the first disk on the instance
    :param disk_2: the name of the second disk on the instance 
    """
    yum_update()
    yum_install()
    sudo('mdadm create --verbose /dev/md0 --level=mirror --raid-devices=2 /dev/{0} /dev/{1}').format(disk_1, disk_2)
    sudo('-i')
    sudo('mdadm --detail --scan >> /etc/mdadm.conf')



def yum_install():
    """Install nfs packages"""
    sudo('yum install {0}').format(YUM_PACKAGES)
    
def yum_update():
    """Run Yum update to make sure software is up to date"""
    sudo('yum install update')
    
def setup_nfs():
    """install nfs on the server and parse client data"""
    sudo('yum install nfs-utils')
    #open export folder 
    with cd('/etc/')
        sudo('vi etc/exports')  
    sudo('chkconfig nfs on')
    sudo('service rpcbind start')
    sudo('service nfs start')
    sudo('vi etc/exports')

    

def attach_new_disks(disk_name_1,disk_name_2, ebs_size, volume_group):
    """extend the volumes of the server
    :param disk_name_1
    :param disk_name_2
    :param ebs_size
    :param volume_group
    """

    ec2_connection = boto.connect_ec2
    dev_new_disk_1= blockdevicemapping.EBSBlockDeviceType(delete_on_termination=True)
    dev_new_disk_1 = int(ebs_size) #size is in gigabytes
    dev_new_disk_2 = blockdevicemapping.EBSBlockDeviceType(delete_on_termination=True)
    dev_new_disk_2 = int(ebs_size) 
    bdm = blockdevicemapping.BlockDeviceMapping()
    bdm['/dev/{0}.'.format(disk_name_1)] = dev_new_disk_2
    bdm['/dev/{0}'.format(disk_name_2)] = dev_new_disk_2
    
#Remove and change for   

    

def create_instance(ebs_size, aws_image):
    """Create and AWS instance that the NFS RAID-1 will run on
    :param: ebs_size, size of the block storage 
    :param: aws_image, image id of the aws instance
    """
    ebs_size
    
    #requires the key files to be in the ~/.boto directory
    ec2_connection = boto.connect_ec2()
    
    dev_sdb = blockdevicemapping.EBSBlockDeviceType(delete_on_termination=True)
    dev_sdb.size = int(ebs_size)
    dev_sdc = blockdevicemapping.EBSBlockDeviceType(delete_on_termination=True)
    dev_sdc.size = int(ebs_size)

    
    bdm = blockdevicemapping.BlockDeviceMapping()
    bdm['/dev/sdb'] = dev_sdb
    bdm['/dev/sdc'] =dev_sdc
    reservations = ec2_connection.run_instances(AMI_ID, instance_type = INSTANCE_TYPE, key_name=KEY_NAME, security_groups = SECURTIY_GROUPS, block_device_map =bdm)

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

    # Return the instance
    return instance, ec2_connection
    
    
    
