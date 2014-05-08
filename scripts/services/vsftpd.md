VsFTPd with System Users
========================


1. Install `vsftpd`
    ```bash
    apt-get install vsftpd
    ```


2. Make some configurations
    ```bash
    sed -i "s/anonymous_enable=YES/anonymous_enable=NO/" /etc/vsftpd.conf
    sed -i "s/#local_enable=YES/local_enable=YES/" /etc/vsftpd.conf
    sed -i "s/#write_enable=YES/write_enable=YES" /etc/vsftpd.conf
    sed -i "s/#chroot_local_user=YES/chroot_local_user=YES/" /etc/vsftpd.conf

    echo '/bin/false' >> /etc/shells
    ```


3. Apply changes
    ```bash
    /etc/init.d/vsftpd restart
    ```
