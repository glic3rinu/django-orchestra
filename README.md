![](orchestra/static/orchestra/icons/Emblem-important.png)  **This project is in early development stage**

Django Orchestra
================

Orchestra is a Django-based framework for building web hosting control panels.

* [Installation](#fast-deployment-setup)
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
This deployment is not suitable for production but more than enough for checking out this project.

```bash
# Create and activate a Python virtualenv
python3 -mvenv env-django-orchestra
source env-django-orchestra/bin/activate

# Install Orchestra and its dependencies
pip3 install http://git.io/django-orchestra-dev
# The only non-pip required dependency for runing pip3 install is python3-dev
sudo apt-get install python3-dev
pip3 install -r http://git.io/orchestra-requirements.txt

# Create a new Orchestra site
orchestra-admin startproject panel
python3 panel/manage.py migrate
python3 panel/manage.py runserver
```

Now you can see the web interface on http://localhost:8000/admin/


Checkout the steps for other deployments: [development](INSTALLDEV.md), [production](INSTALL.md)


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
