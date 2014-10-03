Restricted Shell for SCP and Rsync
==================================

1. apt-get install rssh

2. Enable desired programs
    ```bash
    sed -i "s/^#allowscp/allowscp/" /etc/rssh.conf
    sed -i "s/^#allowrsync/allowrsync/" /etc/rssh.conf
    sed -i "s/^#allowsftp/allowsftp/" /etc/rssh.conf
    ```

2. Enable the shell
    ```bash
    ln -s /usr/bin/rssh /bin/rssh
    echo /bin/rssh >> /etc/shells
    ```
