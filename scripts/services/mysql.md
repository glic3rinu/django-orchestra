MySQL
=====

apt-get install mysql-server

sed -i "s/bind-address            = 127.0.0.1/bind-address            = 0.0.0.0/" /etc/mysql/my.cnf
