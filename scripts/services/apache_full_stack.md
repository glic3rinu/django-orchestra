Apache 2 MPM Event with PHP-FPM, FCGID and SUEXEC on Debian Jessie
==================================================================

The goal of this setup is having a high-performance state-of-the-art deployment of Apache and PHP while being compatible with legacy applications.

* Apache Event MPM engine handles requests asynchronously, instead of using a dedicated thread or process per request.

* PHP-FPM is a FastCGI process manager included in modern versions of PHP.
    Compared to FCGID it provides better process management features and enables the OPCache to be shared between workers.

* FCGID and SuEXEC are used for legacy apps that need older versions of PHP (i.e. PHP 5.2 or PHP 4)


*Sources:*
  * Source http://wiki.apache.org/httpd/PHP-FPM


*Related:*
  * [PHP4 on debian](php4_on_debian.md)
  * [VsFTPd](vsftpd.md)
  * [Webalizer](webalizer.md)



1. Install the machinery
    ```bash
    apt-get update
    apt-get install apache2-mpm-event php5-fpm libapache2-mod-fcgid apache2-suexec-custom php5-cgi
    ```

# TODO libapache2-mod-auth-pam is no longer part of the debian distribution,
#       replace with libapache2-mod-authnz-external pwauth

2. Enable some convinient Apache modules
    ```bash
    a2enmod suexec
    a2enmod ssl
    #a2enmod auth_pam
    a2enmod proxy_fcgi
    ```


3. Configure `suexec-custom`
    ```bash
    sed -i "s#/var/www#/home#" /etc/apache2/suexec/www-data
    sed -i "s#public_html#webapps#" /etc/apache2/suexec/www-data
    ```


4. Create logs directory for virtualhosts
    ```bash
    mkdir -p /var/log/apache2/virtual/
    chown -R www-data:www-data /var/log/apache2
    ```


5. Restart Apache
    ```bash
    service apache2 restart
    ```







* ExecCGI
    ```bash
    <Directory /home/*/webapps/>
        Options +ExecCGI
    </Directory>
    ```

* Permissions
<Directory /home/*/webapps>
        Require all granted
</Directory>



# TODO pool per website or pool per user? memory consumption 
events.mechanism = epoll
# TODO multiple master processes, opcache is held in master, and reload/restart affects all pools
# http://mattiasgeniar.be/2014/04/09/a-better-way-to-run-php-fpm/

TODO CHRoot
    https://andrewbevitt.com/tutorials/apache-varnish-chrooted-php-fpm-wordpress-virtual-host/

    ```bash
    echo '
    [vhost]
    istemplate = 1
    listen.mode = 0660
    pm = ondemand
    pm.max_children = 5
    pm.process_idle_timeout = 10s
    pm.max_requests = 200
    ' > /etc/php5/fpm/conf.d/vhost-template.conf
    ```

    ```bash
    mkdir -p /var/run/fpm/socks/
    chmod 771 /var/run/fpm/socks
    chown orchestra.orchestra /var/run/fpm/socks
    ```
