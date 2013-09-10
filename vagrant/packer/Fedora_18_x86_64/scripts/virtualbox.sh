cd /tmp
mkdir -p /mnt/vbox
if [ -f /home/zendev/VBoxGuest*.iso ]
then

    mount -o loop /home/zendev/VBoxGuest*.iso /mnt/vbox
    sh /mnt/vbox/VBoxLinuxAdditions.run
    umount /mnt/vbox
    rmdir /mnt/vbox
    rm -rf /home/zendev/VBoxGuest*.iso
fi
