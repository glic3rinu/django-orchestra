#!/bin/bash

# This is a helper script for creating a basic LXC container with some convenient packages
# ./create.sh [container_name]


set -u

NAME=${1:-orchestra}
CONTAINER="/var/lib/lxc/$NAME/rootfs"
PASSWORD=$NAME
export SUITE="jessie"


[ $(whoami) != 'root' ] && {
    echo -e "\nErr. This script should run as root\n" >&2
    exit 1
}

lxc-create -h &> /dev/null || {
    echo -e "\nErr. It seems like LXC is not installed, run apt-get install lxc\n" >&2
    exit 1
}

lxc-ls | grep -E "(^|\s)$NAME($|\s)" && {
    echo -e "\nErr. Container with name $NAME already exists."
    echo -e "     You can destroy it by: sudo lxc-destroy -n $NAME\n" >&2
    exit 1
}


lxc-create -n $NAME -t debian

trap "umount $CONTAINER/{dev,sys}; exit 1;" INT TERM EXIT
mount --bind /dev $CONTAINER/dev
mount -t sysfs none $CONTAINER/sys


sed -i "s/\tlocalhost$/\tlocalhost $NAME/" $CONTAINER/etc/hosts
sed -i "s/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/" $CONTAINER/etc/locale.gen
chroot $CONTAINER locale-gen

echo -e "#!/bin/sh\nexit 101\n" > $CONTAINER/usr/sbin/policy-rc.d
chmod 755 $CONTAINER/usr/sbin/policy-rc.d

chroot $CONTAINER apt-get update
chroot $CONTAINER apt-get install -y --force-yes \
    nano git screen sudo iputils-ping python3 python3-pip wget curl dnsutils rsyslog

rm $CONTAINER/usr/sbin/policy-rc.d
chroot $CONTAINER apt-get clean


sleep 0.1
umount $CONTAINER/{dev,sys} || {
    echo "Killing processes inside the container ..."
    lsof | grep $CONTAINER | awk {'print $2'} | uniq | xargs kill
    umount $CONTAINER/{dev,sys}
}
trap - INT TERM EXIT
