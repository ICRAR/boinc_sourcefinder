Install steps:

Most of this is automated, but some steps must be done manually: http://boinc.berkeley.edu/trac/wiki/VboxApps#CreatingbaseVMimages

1. Run create_vm.sh to build the vm.
2. Once the VM has started, select "Graphical Install"
3. Set languages to English and location to Australia.
4. Set the hostname to boinc
5. Do not set a domain name
6. Set the root password to boinc
7. Set the full name for the non-root user to boinc, and password to boinc
8. Set click location to Western Australia
9. Select the first option for each Parition disks question
10. Select Yes for write changes to disk.
11. Select No when asked to scan another CD/DVD. Continue through the remaining package manager questions.
12. Select no for popularity contest.
13. Untick all options in software selection.
14. Install the grub boot loader.
15. Select the second device option.

16. Log in to the system
17. Open /lib/systemd/system/getty@.service and modify ExecStart to be ExecStart=-/sbin/agetty --noclear -a root %I $TERM
18. Modify /etc/default/grub to use have GRUB_TIMEOUT = 0 and run update-grub
19. Install virtualbox guest additions: mount /dev/cdrom /media/cdrom; cd /media.cdrom; sudo apt-get install -y dkms build-essential linux-headers-generic linux-headers-$(uname -r); ./VBoxLinuxAdditions.run 
20. Mount the vbox shared directory mount -t vboxsf shared /root/shared and run the install-sofia.sh script.
21. Modify /etc/fstab to start /dev/sda1 in read only mode and run zerofree /dev/sda1. Once complete, reboot and uninstall zerofree.
22. In the host machine, run vboxmanage modifyhd SoFiA.vdi --compact