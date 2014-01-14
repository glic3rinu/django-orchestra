**This project is in early development stage**

Django Orchestra
================

Orchestra is a Django-based framework for building web hosting control panels.

[Docs](http://django-orchestra.readthedocs.org/en/latest/)


Motivation
----------
There are a lot of widely used open source hosting control panels, however, none of them seems apropiate when you already have an existing service infrastructure or simply you want your services to run on a particular architecture.

The goal of this project is to provide the tools for easily build a fully featured control panel that fits any service architecture.


Overview
--------
* Based on reusable applications, feel free to reuse what you need
* Web interface based on `django.contrib.admin`, enhaced with `admin_tools` and `fluent_dashboard`


Development or Testing Setup
-----------------------------
If you are planing to do some development or perhaps just checking out this project, you may want to consider doing it under the following setup

1. Create a basic [LXC](http://linuxcontainers.org/) container, start it, and enter.
```bash
wget https://raw2.github.com/glic3rinu/django-orchestra/master/scripts/container/create.sh -O /tmp/create.sh
chmod +x /tmp/create.sh
sudo /tmp/create.sh
sudo lxc-start -n orchestra
```

2. Deploy Django-orchestra development environment inside the container
```bash
wget https://raw2.github.com/glic3rinu/django-orchestra/master/scripts/container/deploy.sh -O /tmp/deploy.sh
chmod +x /tmp/deploy.sh
cd /tmp/ # Moving away from /root before running deploy.sh
/tmp/deploy.sh
# Django-orchestra source code is now under
~orchestra/django-orchestra
# An Orchestra instance called panel is under
~orchestra/panel
```

3. Optionally you can place your custom settings under `~orchestra/panel/panel/local_settings.py` for [example](http://django-orchestra.readthedocs.org/en/latest/).

4. And use Django's development server as usual
```bash
cd ~orchestra/panel
python manage.py runserver 0.0.0.0:8888
```

5. A convenient practice can be mounting `~orchestra` on your host machine so you can code with your favourite IDE, sshfs can be used for that
```bash
# On your host
mkdir ~<user>/orchestra
sshfs orchestra@<container-ip>: ~<user>/orchestra
```

6. To upgrade to current master just
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
sudo pip install django-orchestra
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
sudo python manage.py setuppostgres --db_user orchestra --db_password <password> --db_name <project_name>
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
sudo apt-get install nginx uwsgi uwsgi-plugin-python
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
sudo python manage.py upgradeorchestra --orchestra_version dev
```

Additionally the following command can be used in order to determine the currently installed version:
```bash
python manage.py orchestraversion
```
