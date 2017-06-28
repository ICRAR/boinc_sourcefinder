#!/usr/bin/env bash

# Run this on the host machine to install SoFiA
echo "Installing SoFiA Packages..."
# INSTALL HERE
sleep 2

echo "Building SoFiA"
# INSTALL HERE
sleep 2
python setup.py build --force --no-gui=True

echo "Setting up bashrc"
sleep 2
/bin/cp /shared/bashrc.sh ~/.bashrc -rf

echo "Cleaning up..."
sleep 2
apt-get -y remove gfortran
apt-get -y remove fdutils
apt-get -y remove eject
apt-get -y remove doc-debian
apt-get -y remove doc-text-linux
apt-get -y remove ispell
apt-get -y remove laptop-detect
apt-get -y remove mutt
apt-get -y remove manpages
apt-get -y remove nano
apt-get -y remove ssh-client
apt-get -y remove ssh-server
apt-get -y remove openssl
apt-get -y remove ssh
apt-get -y remove usbutils
apt-get -y remove w3m
apt-get -y remove tcsh
apt-get -y remove gcc
apt-get -y remove g++

localpurge

telinit 1
mount -o remount, ro /dev/sda1
zerofree -v /dev/sda1

apt-get -y remove localpurge
apt-get -y remove zerofree

echo "Done"
sleep 2
