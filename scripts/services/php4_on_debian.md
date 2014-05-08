PHP 4.4.9 for Debian Wheezy / Jessie
====================================

**This recipe is for compiling a Debian Wheezy/Jessie compatible version of PHP 4.4.9**


1. Debootstrap a Debian Wheezy
    ```bash
    debootstrap --include=build-essential wheezy php4strap
    chroot php4strap
    ```


2. Download and install PHP 4.4.9
    ```bash
    mkdir /tmp/php4-build
    cd /tmp/php4-build
    wget http://de.php.net/get/php-4.4.9.tar.bz2/from/this/mirror -O php-4.4.9.tar.bz2
    tar jxf php-4.4.9.tar.bz2
    ```


3. Install PHP building dependencies
    ```bash
    cat /etc/apt/sources.list | sed "s/^deb /deb-src /" >> /etc/apt/sources.list
    apt-get update
    apt-get build-dep php5
    ```

4. Create some links
    ```bash
    ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/
    ln -s /usr/lib/x86_64-linux-gnu/libpng.so /usr/lib/
    ln -s /usr/lib/x86_64-linux-gnu/libexpat.so /usr/lib/
    ln -s /usr/lib/x86_64-linux-gnu/libmysqlclient.so /usr/lib/libmysqlclient.so
    ```

4. Configure PHP4

    *Notice that some common features are not enabled, this is because are not supported by related libraries that ship with modern Debian releases*

    ```bash
    ./configure --prefix=/usr/local/php4 \
                --enable-force-cgi-redirect \
                --enable-fastcgi \
                --with-config-file-path=/usr/local/etc/php4/cgi \
                --with-gettext \
                --with-jpeg-dir=/usr/local/lib \
                --with-mysql=/usr \
                --with-pear \
                --with-png-dir=/usr/local/lib \
                --with-xml \
                --with-zlib \
                --with-zlib-dir=/usr/include \
                --enable-bcmath \
                --enable-calendar \
                --enable-magic-quotes \
                --enable-sockets \
                --enable-track-vars \
                --enable-mbstring \
                --enable-memory-limit \
                --with-bz2 \
                --enable-dba \
                --enable-dbx \
                --with-iconv \
                --with-mime-magic \
                --disable-shmop \
                --enable-sysvmsg \
                --enable-wddx \
                --with-xmlrpc \
                --enable-yp \
                --with-gd
    ```

5. Compile and install PHP4
    ```bash
    make
    make install
    strip /usr/local/php4/bin/*
    ```


6. Grab the binaries
    ```bash
    exit
    scp -r php4strap/usr/local/php4 root@destination-server:/usr/local/
    ```


7. I needed to install some extra dependecies on my server
    ```bash
    apt-get install libmysqlclient18 libpng12-0 libjpeg8
    ```

