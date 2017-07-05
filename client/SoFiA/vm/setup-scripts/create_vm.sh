#!/usr/bin/env bash

# This script downloads and starts a SoFiA VM.

VM_NAME="SoFiA"
NETWORK_ADAPTER="enp3s0f1"
SHARED_DIR="/tmp/shared"
DEBIAN_VERSION="debian-9.0.0-amd64-netinst.iso"

cp bashrc.sh ${SHARED_DIR}
cp install-sofia.sh ${SHARED_DIR}

# Download vm
if [ ! -f ${DEBIAN_VERSION} ]; then
    wget https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/${DEBIAN_VERSION}
fi

vboxmanage createvm --name ${VM_NAME} --register
VBoxManage createhd --filename ${VM_NAME}.vdi --size 8192

vboxmanage modifyvm ${VM_NAME} --memory 1024 --acpi on --boot1 dvd
vboxmanage modifyvm ${VM_NAME} --nic1 bridged --bridgeadapter1 ${NETWORK_ADAPTER} --cableconnected1 on
vboxmanage modifyvm ${VM_NAME} --ostype Debian_64

vboxmanage storagectl ${VM_NAME} --name "IDE Controller" --add ide
vboxmanage storageattach ${VM_NAME} --storagectl "IDE Controller" --port 0 --device 0 --type dvddrive --medium ${DEBIAN_VERSION}

vboxmanage storagectl ${VM_NAME} --name "SATA Controller" --add sata --controller IntelAHCI
vboxmanage storageattach ${VM_NAME} --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium ${VM_NAME}.vdi

vboxmanage sharedfolder add ${VM_NAME} --name shared --hostpath ${SHARED_DIR} --automount

vboxmanage modifyvm ${VM_NAME} --ioapic on
vboxmanage modifyvm ${VM_NAME} --boot1 dvd --boot2 disk --boot3 none --boot4 none

vboxmanage startvm ${VM_NAME}