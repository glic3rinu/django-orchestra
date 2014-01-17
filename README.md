**This project is in early development stage**

Django Orchestra
================

Orchestra is a Django-based framework for building web hosting control panels.

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


Installation
------------

Django-orchestra ships with a set of management commands for automating some of the installation steps.

These commands are meant to be run within a **clean** Debian-like distribution, you should be specially careful while following this guide on a customized system.

Django-orchestra can be installed in any Linux system, however it is **strongly recommended** to chose the reference platform for your deployment (Debian 7.0 wheezy and Python 2.7).


1. Create a system user for running the server
```bash
adduser orchestra
# not required but it will be very handy
sudo adduser orchestra sudo
su - orchestra
```

2. Install django-orchestra's source code
```bash
sudo apt-get install python-pip
sudo pip install django-orchestra # ==dev if you want the in-devel version
```

3. Install requirements
```bash
sudo orchestra-admin install_requirements
```

4. Create a new instance
```bash
cd ~orchestra
orchestra-admin clone <project_name> # e.g. panel
cd <project_name>
```

5. Create and configure a Postgres database
```bash
sudo python manage.py setuppostgres
python manage.py syncdb
python manage.py migrate
```

6. Create a panel administrator
```bash
python manage.py createsuperuser
```

7. Configure celeryd
```bash
sudo python manage.py setupcelery --username orchestra
```

8. Configure the web server:
```bash
python manage.py collectstatic --noinput
sudo apt-get install nginx-full uwsgi uwsgi-plugin-python
sudo python manage.py setupnginx
```


Upgrade
-------
To upgrade your Orchestra installation to the last release you can use `upgradeorchestra` management command. Before rolling the upgrade it is strongly recommended to check the [release notes](http://django-orchestra.readthedocs.org/en/latest/).
```bash
sudo python manage.py upgradeorchestra
```

Current in *development* version (master branch) can be installed by
```bash
sudo python manage.py upgradeorchestra dev
```

Additionally the following command can be used in order to determine the currently installed version:
```bash
python manage.py orchestraversion
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
