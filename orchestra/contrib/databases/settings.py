from django.conf import settings

from orchestra.settings import Setting


DATABASES_TYPE_CHOICES = Setting('DATABASES_TYPE_CHOICES', (
    ('mysql', 'MySQL'),
    ('postgres', 'PostgreSQL'),
))


DATABASES_DEFAULT_TYPE = Setting('DATABASES_DEFAULT_TYPE', 'mysql', choices=DATABASES_TYPE_CHOICES)


DATABASES_DEFAULT_HOST = Setting('DATABASES_DEFAULT_HOST',
    'localhost'
)
