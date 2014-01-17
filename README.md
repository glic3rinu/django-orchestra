**This project is in early development stage**

Django Orchestra
================

Orchestra is a Django-based framework for building web hosting control panels.

Orchestra is mostly a bunch of [plugable applications](tree/master/orchestra/apps) providing common functionalities, like service management or billing.

* [Install and upgrade](INSTALL.md)
* [Documentation](http://django-orchestra.readthedocs.org/en/latest/)


Motivation
----------
There are a lot of widely used open source hosting control panels, however, none of them seems apropiate when you already have an existing service infrastructure or simply you want your services to run on a particular architecture.

The goal of this project is to provide the tools for easily build a fully featured control panel that is not tied with any particular service architecture.



Development and Testing Setup
-----------------------------
If you are planing to do some development or perhaps just checking out this project, you may want to consider doing it under the following setup

1. Create a basic [LXC](http://linuxcontainers.org/) container, start it and get inside.
```bash
wget -O /tmp/create.sh \
       https://raw2.github.com/glic3rinu/django-orchestra/master/scripts/container/create.sh
chmod +x /tmp/create.sh
sudo /tmp/create.sh
sudo lxc-start -n orchestra
```

2. Deploy Django-orchestra development environment inside the container
```bash
wget -O /tmp/deploy.sh \
       https://raw2.github.com/glic3rinu/django-orchestra/master/scripts/container/deploy.sh
chmod +x /tmp/deploy.sh
cd /tmp/ # Moving away from /root before running deploy.sh
/tmp/deploy.sh
```
Django-orchestra source code should be now under `~orchestra/django-orchestra` and an Orchestra instance called _panel_ under `~orchestra/panel`


3. Nginx is serving on port 80 but Django's development server can also be used
```bash
su - orchestra
cd panel
python manage.py runserver 0.0.0.0:8888
```

4. A convenient practice can be mounting `~orchestra` on your host machine so you can code with your favourite IDE, sshfs can be used for that
```bash
# On your host
mkdir ~<user>/orchestra
sshfs orchestra@<container-ip>: ~<user>/orchestra
```

5. To upgrade to current master just
```bash
cd ~orchestra/django-orchestra/
git pull origin master
sudo ./scripts/container/deploy.sh
```


License
-------
Copyright (C) 2013 Marc Aymerich

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
Status API Training Shop Blog About
