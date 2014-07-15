"""fabric file for the raid system that the nfs server connects to for the sourcefinder"""

import boto
from boto.
import glob 
import fabric 
import argparse

from fabric.api import *
from ec2.autoscale.launchconfig import BlockDeviceMapping

AMI_ID = 
INSTANCE_TYPE ='t1.small'
YUM_PACKAGES = 'lvm2 xfsprogs' 
USERNAME ='ec2-user'
TEST_SECURITY_GROUPS = ['sg-dd33e0b2', 'sg-9408dbfb']
AVAILABILITY_ZONE ='north-virginia-1c'


def setup_disks(disk_1, disk_2):
    """setup the RAID1 configuration on the nfs server
    :param disk_1: the name of the first disk on the instance
    :param disk_2: the name of the second disk on the instance 
    """
    
    sudo('yum install {0}'.format(YUM_PACKAGES))
    sudo('pvcreate /dev/{0} /dev/{1}'.format(disk_1, disk_2))
    sudo('vgvcreate data /dev/{0} /dev/{1}'.format(*disk_1, disk_2))
        #check we have a volume group 
    #sudo('vgdisplay')
    #want to print(?) or check what the output is 
    sudo('vcreate-m 1 --type raid1 -l 40%VG --nosync -n lvm_raid1 data')
    sudo('mkfs.xfs /dev/data/lvm_raid1')
    sudo('mkdir -p /mnt/data')
    sudo('mount /dev/data/lvm_raid1 /mnt/data')    

def yum_update():
    """Run Yum update to make sure software is up to date"""
    sudo('yum install update')
    
def setup_nfs():
    """install nfs on the server and parse client data(future)"""
    sudo('yum install nfs-utils')
    #open export folder 
    with cd('/etc/')
        append('exports', '_old')
        upload_template('exports.txt', LOCAL_EXPORTS_DIRECTORY)
        cd('../')
    sudo('service nfs start')    
    

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
    
    
def extend_lvm(disk_name_1, disk_namee_2, ebs_size, volume_group, logical_volumes):
    """extend the current raid/lvm setup with new disks that have been attached to the instance
    :param disk_name
    :param ebs_size
    :param volume_group
    """
    
    attach_new_disks(disk_name_1, disk_name_2, ebs_size, volume_group)
    sudo('umount /mnt/{0}'.format(volume_group)
    sudo('pvcreate /dev/{0} /dev/{1}'.format(disk_name_1, disk_name_2))
     #removes any drives from the volume group that aren't there or are missing
    sudo('vgremove --removemissing /dev/{0}'.format(volume_group))
    sudo('vgextend {0} /dev/{1} /dev/{2}', volume_group, disk_name_1, disk_name_2)
    sudo('lvextend -L+{0} /dev/{1}/{2}'.format(2*ebs_size, volume_group, logical_volume))
    sudo('resize2fs /mnt/{0} {1}'.format(2*volume_group)
    
    

def create_instance(ebs_size, aws_image):
    """Create and AWS instance that the NFS RAID-1 will run on
    :param: ebs_size, size of the block storage 
    :param: aws_image, image id of the aws instance
    """
    
    #requires the key files to be in the ~/.boto directory
   ec2_connection = boto.connect_ec2()  
    
    dev_sdb = blockdevicemapping.EBSBlockDeviceType(delete_on_termination=True)
    dev_sdb.size = int(ebs_size)
    dev_sdc = blockdevicemapping.EBSBlockDeviceType(delete_on_termination=True)
    dev_sdc.size = int(ebs_size)
    
    bdm = blockdevicemapping.BlockDeviceMapping()
    bdm['/dev/sdb'] = dev_sdb
    bdm['/dev/sdc'] =dev_sdc
    reservations - ec2_connection.run_instances(AMI_ID, instance_type = INSTANCE_TYPE, key_name=KEY_NAME, security_groups = SECURTIY_GROUPS, block_device_map =bdm)
    insance = reservations.instances[0]
    
    
    
