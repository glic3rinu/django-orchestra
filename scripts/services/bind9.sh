#!/bin/bash

# Installs and confingures bind9 to work with Orchestra


apt-get update
apt-get install bind9

echo "nameserver 127.0.0.1" > /etc/resolv.conf
