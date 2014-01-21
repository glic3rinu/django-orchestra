# Django settings for orchestra project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Enable persistent connections
CONN_MAX_AGE = 60*10

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'


ALLOWED_HOSTS = '*'


MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


TEMPLATE_CONTEXT_PROCESSORS =(
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "orchestra.core.context_processors.site",
)


INSTALLED_APPS = (
    # django-orchestra apps
    'orchestra',
    
    'orchestra.apps.multitenance',
    'orchestra.apps.daemons',
    'orchestra.apps.daemons.backends.ssh',
    'orchestra.apps.databases',
    'orchestra.apps.dns.zones',
    'orchestra.apps.dns.names',
    'orchestra.apps.emails',
    'orchestra.apps.entities',
    'orchestra.apps.lists',
    'orchestra.apps.systemusers',
    'orchestra.apps.webs',
    
    # Third-party apps
    'south',
    'django_extensions',
    'djcelery',
    'djcelery_email',
    'fluent_dashboard',
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'rest_framework',
    
    # Django.contrib
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
)


AUTHENTICATION_BACKENDS = [
    'orchestra.permissions.auth.OrchestraPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
]


# Email config
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'


#################################
## 3RD PARTY APPS CONIGURATION ##
#################################

# Admin Tools
#ADMIN_TOOLS_MENU = 'orchestra.menu.CustomMenu'

# Fluent dashboard
ADMIN_TOOLS_INDEX_DASHBOARD = 'fluent_dashboard.dashboard.FluentIndexDashboard'
FLUENT_DASHBOARD_ICON_THEME = '../orchestra/icons'

FLUENT_DASHBOARD_APP_GROUPS = (
    ('Services', {
        'models': (
            'orchestra.apps.systemusers.models.SystemUser',
            'orchestra.apps.webs.models.Web',
            'orchestra.apps.emails.models.Mailbox',
            'orchestra.apps.lists.models.List',
            'orchestra.apps.dns.zones.models.Zone',
            'orchestra.apps.dns.names.models.Name',
            'orchestra.apps.databases.models.Database',
            'orchestra.apps.multitenance.models.Application',
        ),
        'collapsible': True,
    }),
    ('Billing', {
        'models': (
            'orchestra.apps.entities.models.Entity',
        ),
        'collapsible': True,
    }),
    ('Administration', {
        'models': (
            'django.contrib.auth.models.User',
            'djcelery.models.TaskState',
            'orchestra.apps.daemons.models.Daemon',
        ),
        'collapsible': True,
    }),
)

FLUENT_DASHBOARD_APP_ICONS = {
    # Services
    'systemusers/systemuser': "Tux.png",
    'webs/web': "web.png",
    'emails/mailbox': "email.png",
    'lists/list': "email-alter.png",
    'zones/zone': "zone.png",
    'names/name': "dns.png",
    'databases/database': "database.png",
    'mail/virtualuser': "virtualuser.png",
    'multitenance/application': "apps.png",
    # Billing
    'entities/entity': "contact.png",
    # Administration
    'auth/user': "Mr-potato.png",
    'djcelery/taskstate': "taskstate.png",
    'daemons/daemon': "daemon.png",
}

# Django-celery
import djcelery
djcelery.setup_loader()
# Broker
BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_SEND_EVENTS = True
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_DISABLE_RATE_LIMITS = True
# Do not fill the logs with crap
CELERY_REDIRECT_STDOUTS_LEVEL = 'DEBUG'


# rest_framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'orchestra.permissions.api.OrchestraPermissionBackend',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
#    'PAGINATE_BY': 10,
#    'PAGINATE_BY_PARAM': 'page_size',
}

