#!/usr/bin/env bash

VM_NAME="SoFiA"
NETWORK_ADAPTER="wlps20"

# Download vm from boinc and decompress
if [ ! -f vmimage_x64.zip ]; then
    wget http://boinc.berkeley.edu/dl/vmimage_x64.zip
fi

unzip vmimage_x64.zip

mkdir -p /tmp/shared/python
mkdir -p /tmp/shared/apt

sudo apt-get install python git gcc g++ zlib1g-dev -d -o=dir::cache=/tmp/shared/apt
sudo apt-get install localpurge -d -o=dir::cache=/tmp/shared/apt
sudo apt-get install zerofree -d -o=dir::cache=/tmp/shared/apt

pip install numpy scipy astropy matplotlib --download="/tmp/shared/python"

git clone https://github.com/SoFiA-Admin/SoFiA.git
mv SoFiA /tmp/shared

exit

vboxmanage createvm --name ${VM_NAME} --register
vboxmanage modifyvm ${VM_NAME} --memory 1024 --acpi on --boot1 dvd
vboxmanage modifyvm ${VM_NAME} --nic1 bridged --bridgeadapter1 ${NETWORK_ADAPTER} --cableconnected1 on
vboxmanage modifyvm ${VM_NAME} --ostype Debian_64
vboxmanage storagectl ${VM_NAME} --name "SATA Controller" --add sata --controller IntelAHCI
vboxmanage storageattach ${VM_NAME} --storagectl "SATA Controller" --port 1 --device 0 --type hdd --medium vmimage_x64.vdi
vboxmanage sharedfolder add ${VM_NAME} --name shared --hostpath /tmp/shared --automount
vboxmanage startvm ${VM_NAME}

cp bashrc.sh /tmp/shared/
# The default BOINC vm automatically tries to run this, so we force it to run our own setup script.
cp install-sofia.sh /tmp/shared/boinc_app