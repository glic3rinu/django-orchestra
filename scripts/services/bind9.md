Bind9 Master and Slave
======================

1. Install bind9 service as well as some convinient utilities on master and slave servers
    ```bash
    apt-get update
    apt-get install bind9 dnsutils
    ```

2. create the zone directory on the master server
    ```bash
    mkdir /etc/bind/master
    chown bind.bind /etc/bind/master
    ```
