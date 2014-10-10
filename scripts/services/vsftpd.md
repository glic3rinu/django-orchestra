VsFTPd with System Users
========================


1. Install `vsftpd`
    ```bash
    apt-get install vsftpd
    ```


2. Make some configurations
    ```bash
    sed -i "s/^anonymous_enable=YES/anonymous_enable=NO/" /etc/vsftpd.conf
    sed -i "s/^#local_enable=YES/local_enable=YES/" /etc/vsftpd.conf
    sed -i "s/^#write_enable=YES/write_enable=YES/" /etc/vsftpd.conf
    # sed -i "s/^#chroot_local_user=YES/chroot_local_user=YES/" /etc/vsftpd.conf
    
    sed -i "s/^#local_umask=022/local_umask=022/" /etc/vsftpd.conf
    
    echo '/dev/null' >> /etc/shells
    ```

# TODO https://www.benscobie.com/fixing-500-oops-vsftpd-refusing-to-run-with-writable-root-inside-chroot/#comment-2051
Define option passwd_chroot_enable=yes in configuration file and change in /etc/passwd file user home directory from «/home/user» to «/home/./user» (w/o quotes).


3. Apply changes
    ```bash
    /etc/init.d/vsftpd restart
    ```
