#!/usr/bin/env bash

# This script is to be run on the virtual machine. It installs sofia from packages downloaded by the host machine.

SHARED_DIR="/root/shared"

# Run this on the host machine to install SoFiA
echo "Installing SoFiA Packages..."
apt-get update
apt-get -y install python git gcc g++ zlib1g-dev localepurge zerofree python-pip

echo "Installing SoFiA Python Packages..."
pip install numpy scipy astropy matplotlib

echo "Building SoFiA"
cd ${SHARED_DIR}
git clone https://github.com/SoFiA-Admin/SoFiA.git
mv SoFiA /root
cd /root/SoFiA
python setup.py build --force --no-gui=True

echo "Setting up bashrc"
/bin/cp ${SHARED_DIR}/bashrc.sh ~/.bashrc -rf
chmod +x ~/.bashrc
sleep 2

echo "Cleaning up..."
sleep 2

apt-get -y remove ispell manpages nano ssh-client openssl ssh gcc g++ localepurge zerofree busybox debconf-i18n logrotate manpages os-prober rsyslog wamerican
dpkg --purge `dpkg --get-selections | grep deinstall | cut -f1`

rm -rf /usr/share/locale/
rm -rf /usr/share/doc/
rm -rf /usr/share/man/
rm -rf /var/log/
rm -rf /var/cache/debconf/
rm -rf /var/lib/apt/lists/

tune2fs -c -1 /dev/sda1

apt-get autoremove
apt-get autoclean
apt-get clean

echo "Done"
sleep 2
