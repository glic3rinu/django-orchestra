Webalizer
=========


1. Install `vsftpd`
    ```bash
    apt-get install webalizer
    ```


2. Modify Apache/Nginx log postrotate
    ```bash
    for i in /home/httpd/webalizer/*.conf; do
        file=$(grep ^LogFile "$i" | tr -s ' ' | cut -f2 -d ' ').1
        if [ -f "$file" ]; then
            /usr/bin/webalizer -q -c "$i" "$file" 2>&1 \
                # Supress truncating warnings
                | grep -v '^Warning: Truncating oversized ' >&2
        fi
    done
    ```
