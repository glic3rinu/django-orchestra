from django.conf import settings



DATABASES_TYPE_CHOICES = getattr(settings, 'DATABASES_TYPE_CHOICES', (
    ('mysql', 'MySQL'),
    ('postgres', 'PostgreSQL'),
))


DATABASES_DEFAULT_TYPE = getattr(settings, 'DATABASES_DEFAULT_TYPE', 'mysql')


DATABASES_DEFAULT_HOST = getattr(settings, 'DATABASES_DEFAULT_HOST', 'localhost')
