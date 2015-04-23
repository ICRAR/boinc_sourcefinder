#Shell script to register a testing VM
#TODO Change memory down to 256
vboxmanage createvm --name "testvm" --register
vboxmanage modicfy vm "testvm" --memory 512 --acpi on --boot1 dvd
vboxmanage modifyvm "testvm" --memory 512 --acpi on --boot1 dvd
vboxmanage modifyvm "testvm" --nic1 bridged --bridgeadapter1 eth0
vboxmanage modifyvm "testvm" --ostype Debian_64
vboxmanage storagectl "testvm" --name "IDE Controller" --add ide
vboxmanage storageattach "testvm" --storagectl "IDE Controller" --port 1 --device 0 --type hdd --medium ./vm_image.vdi
vboxmanage sharedfolder add "testvm" --name shared --hostpath /full/working/directory/name --automount
