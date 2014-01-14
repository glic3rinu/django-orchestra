#!/bin/bash

# This is a helper script for creating a basic LXC container with some convenient packages


set -u

CONTAINER="/var/lib/lxc/orchestra/rootfs"
PASSWORD="orchestra"
export SUITE="wheezy"


[ $(whoami) != 'root' ] && {
    echo -e "\nErr. This script should run as root\n" >&2
    exit 1
}

lxc-create -n orchestra -t debian

mount --bind /dev $CONTAINER/dev
mount -t sysfs none $CONTAINER/sys
trap "umount $CONTAINER/{dev,sys}; exit 1;"INT TERM EXIT

echo "root:$PASSWORD" | chroot $CONTAINER chpasswd
sed -i "s/\tlocalhost$/\tlocalhost orchestra/" $CONTAINER/etc/hosts

chroot $CONTAINER apt-get install -y --force-yes nano git screen sudo iputils-ping python2.7 python-pip

sleep 0.1
umount $CONTAINER/{dev,sys}
trap - INT TERM EXIT
