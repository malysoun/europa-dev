# install europa interna deps
rpm -i http://cmyum.zenoss.loc/yum/zenossdeps-private-5.0.x-1.fc18.x86_64.rpm 

rpm -i http://cmyum.zenoss.loc/yum/5.0.x/fc/18/os/x86_64/kernel-3.9.11-200.aufs.fc18.x86_64.rpm http://cmyum.zenoss.loc/yum/5.0.x/fc/18/os/x86_64/kernel-headers-3.9.11-200.aufs.fc18.x86_64.rpm

yum -y install 	aufs-util lxc


