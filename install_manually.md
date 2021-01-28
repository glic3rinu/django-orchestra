# System requirements:
The most important requirement is use python3.6
we need install this packages:
```
bind9utils 
ca-certificates 
gettext 
libcrack2-dev
libxml2-dev
libxslt1-dev
python3
python3-pip
python3-dev
ssh-client
wget
xvfb
zlib1g-dev
git
iceweasel
dnsutils
```
We need install too a *wkhtmltopdf* package
You can use one of your OS or get it from original.
This it is in https://wkhtmltopdf.org/downloads.html 

# pip installations
We need install this packages:
```
Django==1.10.5
django-fluent-dashboard==0.6.1
django-admin-tools==0.8.0
django-extensions==1.7.4
django-celery==3.1.17
celery==3.1.23
kombu==3.0.35
billiard==3.3.0.23
Markdown==2.4
djangorestframework==3.4.7
ecdsa==0.11
Pygments==1.6
django-filter==0.15.2
jsonfield==0.9.22
python-dateutil==2.2
https://github.com/glic3rinu/passlib/archive/master.zip
django-iban==0.3.0
requests
phonenumbers
django-countries
django-localflavor
amqp
anyjson
pytz
cracklib 
lxml==3.3.5
selenium 
xvfbwrapper 
freezegun 
coverage 
flake8 
django-debug-toolbar==1.3.0 
django-nose==1.4.4 
sqlparse 
pyinotify 
PyMySQL
```

If you want to use Orchestra you need to install from pip like this:
```
pip3 install http://git.io/django-orchestra-dev
```

But if you want develop orquestra you need to do this:
```
git clone https://github.com/ribaguifi/django-orchestra
pip install -e django-orchestra
```

# Database
For default use sqlite3 if you want to use postgresql you need install this packages:

```
psycopg2 postgresql
```

You can use it for debian or ubuntu:

```
sudo apt-get install python3-psycopg2 postgresql-contrib
```

Remember create a database for your project and give permitions for the correct user like this:

```
psql -U postgres
psql (12.4)
Digite «help» para obtener ayuda.

postgres=# CREATE database orchesta;
postgres=# CREATE USER orchesta WITH PASSWORD 'orquesta';
postgres=# GRANT ALL PRIVILEGES ON DATABASE orchesta TO orchesta;
```

# Create new project
You can use orchestra-admin for create your new project
```
orchestra-admin startproject <project_name> # e.g. panel
cd <project_name>
```

Next we need change the settings.py for configure the correct database

In settings.py we need change the DATABASE section like this:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'orchestra'
	'USER': 'orchestra',
        'PASSWORD': 'orchestra',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 60*10
    }
}
```

For end you need to do the migrations:

```
python3 manage.py migrate
```
