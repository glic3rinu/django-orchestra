Installation
============

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
=======
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

