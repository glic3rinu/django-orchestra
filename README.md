![](orchestra/static/orchestra/icons/Emblem-important.png)  **This project is in early development stage**

Django Orchestra
================

Orchestra is a Django-based framework for building web hosting control panels.

* [Documentation](http://django-orchestra.readthedocs.org/)
* [Install and upgrade](INSTALL.md)
* [Roadmap](ROADMAP.md)


Motivation
----------
There are a lot of widely used open source hosting control panels, however, none of them seems apropiate when you already have an existing service infrastructure or simply you want your services to run on a particular architecture.

The goal of this project is to provide the tools for easily build a fully featured control panel that is not tied to any particular service architecture.


Overview
--------

Django-orchestra is mostly a bunch of [plugable applications](orchestra/apps) providing common functionalities, like service management, resource monitoring or billing.

The admin interface relies on [Django Admin](https://docs.djangoproject.com/en/dev/ref/contrib/admin/), but enhaced with [Django Admin Tools](https://bitbucket.org/izi/django-admin-tools) and [Django Fluent Dashboard](https://github.com/edoburu/django-fluent-dashboard). [Django REST Framework](http://www.django-rest-framework.org/) is used for the REST API, with it you can build your client-side custom user interface.

Every app is [reusable](https://docs.djangoproject.com/en/dev/intro/reusable-apps/), this means that you can add any Orchestra application into your Django project `INSTALLED_APPS` strigh away.
However, Orchestra also provides glue, tools and patterns that you may find very convinient to use. Checkout the [documentation](http://django-orchestra.readthedocs.org/) if you want to know more.

![](docs/images/index-screenshot.png)

Fast Deployment Setup
---------------------
To only run the Python interface follow these steps:

```bash
# Create a new virtualenv
python3 -mvenv env-django-orchestra
source env-django-orchestra/bin/activate

# Install Orchestra and its dependencies
pip3 install django-orchestra==dev \
  --allow-external django-orchestra \
  --allow-unverified django-orchestra
sudo apt-get install python3.4-dev libxml2-dev libxslt1-dev libcrack2-dev
pip3 install -r \
  https://raw.githubusercontent.com/glic3rinu/django-orchestra/master/requirements.txt

# Create an orchestra instance
orchestra-admin startproject panel
python3 panel/manage.py migrate accounts
python3 panel/manage.py migrate
python3 panel/manage.py runserver
```

None of the services will work but you can see the web interface on http://localhost:8000/admin


Development and Testing Setup
-----------------------------
If you are planing to do some development or perhaps just checking out this project, you may want to consider doing it under the following setup

1. Create a basic [LXC](http://linuxcontainers.org/) container, start it and get inside.
    ```bash
    wget -O /tmp/create.sh \
      https://raw.github.com/glic3rinu/django-orchestra/master/scripts/container/create.sh
    sudo bash /tmp/create.sh
    sudo lxc-start -n orchestra
    # root/root
    ```

2. Deploy Django-orchestra development environment **inside the container**
    ```bash
    # Make sure your container is connected to the Internet
    # Probably you will have to configure the NAT first:
    #   sudo iptables -t nat -A POSTROUTING -s `container_ip` -j MASQUERADE
    wget -O /tmp/deploy.sh \
      https://raw.github.com/glic3rinu/django-orchestra/master/scripts/container/deploy.sh
    cd /tmp/ # Moving away from /root before running deploy.sh
    bash /tmp/deploy.sh
    ```
    Django-orchestra source code should be now under `~orchestra/django-orchestra` and an Orchestra instance called _panel_ under `~orchestra/panel`


3. Nginx should be serving on port 80, but Django's development server can be used as well:
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

5. To upgrade to current master just re-run the deploy script
    ```bash
    sudo ~orchestra/django-orchestra/scripts/container/deploy.sh
    ```


License
-------
Copyright (c) 2014 - Marc Aymerich and individual contributors.
All Rights Reserved.

Django-orchestra is licensed under The BSD License (3 Clause, also known as
the new BSD license). The license is an OSI approved Open Source
license and is GPL-compatible(1).

The license text can also be found here:
http://www.opensource.org/licenses/BSD-3-Clause

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.
* Neither the name of Marc Aymerich, nor the
  names of its contributors may be used to endorse or promote products
  derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Ask Solem OR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
