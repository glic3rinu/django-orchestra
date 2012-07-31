# Django settings for orchestra project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'orchestra',     # Or path to database file if using sqlite3.
        'USER': 'orchestra',     # Not used with sqlite3.
        'PASSWORD': 'orchestra', # Not used with sqlite3.
        'HOST': 'localhost',     # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',              # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = '/home/orchestra/orchestra/static/'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# BUG: https://bitbucket.org/izi/django-admin-tools/issue/98/admin-css-basecss-not-found
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/home/orchestra/orchestra/media/",
    "/usr/local/lib/python2.6/dist-packages/admin_tools/media",
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '_)^f6m(%kp=@pvpd=uad-r4m*dhu)p#)rp+&amp;g37f$7=asgh08x'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
TEMPLATE_CONTEXT_PROCESSORS += (
	# Requiered by django-admin-tools
	'django.core.context_processors.request',)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'orchestra.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'orchestra.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'fluent_dashboard',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'djangoplugins',
    'djcelery',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    # Mandatory
    'common',

    # Administration
    'contacts',
    'contacts.service_support',

    # Services
    'dns.zones',
    'dns.names',
    'mail',
    'lists',
    'databases',
    'system_users',
    'web',
    'web.modules.fcgid', # depends on system_users application
    'web.modules.php',
    'human_tasks',

    # System
#    'extra_fields',
    'scheduling',       # depends on celery
    'daemons',          # depends on celery, django_transaction_signals (https://github.com/davehughes/django-transaction-signals) and django-plugins
    'daemons.methods.ssh',
    'daemons.methods.local',
    'daemons.methods.python',
#    'resources',       # depends on daemons and xhtml2pdf
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file':{
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': '/var/log/orchestra.log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

# Admin Tools
ADMIN_TOOLS_MENU = 'orchestra.menu.CustomMenu'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'fluent_dashboard.dashboard.FluentAppIndexDashboard'
ADMIN_TOOLS_INDEX_DASHBOARD = 'fluent_dashboard.dashboard.FluentIndexDashboard'
FLUENT_DASHBOARD_ICON_THEME = '../orchestra/icons'

FLUENT_DASHBOARD_APP_GROUPS = (
    ('Services', {
        'models': (
            'dns.*Zone', 'dns.*Name',
            'web.*VirtualHost', 'web.*SystemUser',
            'mail.*VirtualUser',
            'lists.*List',
            'vps.*VPS',
            'human_tasks.*HumanTask',
            'databases.*Database',
            'aps.*APSInstance',
        ),
        'collapsible': True,
    }),
    
    ('Accountancy', {
        'models': (
            'contacts.*.Contact',
            'ordering.*Order',
            'billing.*Bill',
            'payment.*Transaction',
        ),
        'collapsible': True,
    }),

    ('Administration', {
        'models': (
            'django.contrib.auth.*User',
            'djcelery.*TaskState*',
            'daemons.*Daemon',
            'resources.*Monitor',
            'extra_fields.*ExtraField',
        ),
        'collapsible': True,
    }),

)

FLUENT_DASHBOARD_APP_ICONS = {
    'zones/zone': "zone.png",
    'names/name': "name.png",
    'web/virtualhost': "virtualhost.png",
    'web/systemuser': "systemuser.png",
    'mail/virtualuser': "virtualuser.png",
    'lists/list': "list.png",
    'vps/vps': "vps.png",
    'human_tasks/humantask': "humantask.png",
    'databases/database': "database.png",
    'contacts/contact': "contact.png",
    'ordering/order': "order.png",
    'billing/bill': "bill.png",
    'payment/transaction': "transaction.png",
    'auth/user': "user.png",
    'djcelery/taskstate': "taskstate.png",
    'daemons/daemon': "daemon.png",
    'resources/monitor': "monitor.png",
    'extra_fields/extrafield': "extrafield.png",
    'aps/apsinstance': "apsinstance.png",
}


## django-celery
import djcelery
djcelery.setup_loader()
# Broker
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"
CELERY_SEND_EVENTS = True
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_DISABLE_RATE_LIMITS = True
# Use orchestra logging system instead of celer
CELERYD_HIJACK_ROOT_LOGGER = False
CELERY_SEND_TASK_ERROR_EMAILS = True
## end



from custom_settings import *
