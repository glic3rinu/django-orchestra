#!/bin/bash

# This is a helper script for creating a basic LXC container with some convenient packages
# ./create.sh [container_name]

set -u

NAME=${1:-orchestra}
CONTAINER="/var/lib/lxc/$NAME/rootfs"
PASSWORD=$NAME
export SUITE="wheezy"


[ $(whoami) != 'root' ] && {
    echo -e "\nErr. This script should run as root\n" >&2
    exit 1
}

lxc-create -h &> /dev/null || {
    echo -e "\nErr. LXC seems to be not installed, run apt-get install lxc\n" >&2
    exit 1
}


lxc-create -n $NAME -t debian

mount --bind /dev $CONTAINER/dev
mount -t sysfs none $CONTAINER/sys
trap "umount $CONTAINER/{dev,sys}; exit 1;"INT TERM EXIT

echo "root:$PASSWORD" | chroot $CONTAINER chpasswd
sed -i "s/\tlocalhost$/\tlocalhost $NAME/" $CONTAINER/etc/hosts

chroot $CONTAINER apt-get install -y --force-yes \
    nano git screen sudo iputils-ping python2.7 python-pip wget curl

sleep 0.1
umount $CONTAINER/{dev,sys}
trap - INT TERM EXIT
