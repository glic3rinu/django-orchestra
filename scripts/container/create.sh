#!/bin/bash


set -u

CONTAINER="/var/lib/lxc/orchestra/rootfs"
USER="orchestra"
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

chroot $CONTAINER apt-get install -y --force-yes nano git screen sudo iputils-ping python-pip

echo "root:$PASSWORD" | chroot $CONTAINER chpasswd
chroot $CONTAINER useradd orchestra -s "/bin/bash"
echo "$USER:$PASSWORD" | chroot $CONTAINER chpasswd
chroot $CONTAINER mkdir /home/$USER
chroot $CONTAINER chown $USER.$USER /home/$USER
chroot $CONTAINER adduser $USER sudo

sed -i "s/\tlocalhost$/\tlocalhost orchestra/" $CONTAINER/etc/hosts

sleep 0.1
umount $CONTAINER/{dev,sys}
trap - INT TERM EXIT
