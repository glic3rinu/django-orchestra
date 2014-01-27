from django.conf import settings



DATABASES_TYPE_CHOICES = getattr(settings, 'DATABASES_TYPE_CHOICES', (
    ('mysql', 'MySQL'),
    ('postgres', 'PostgreSQL'),
))


DATABASES_DEFAULT_TYPE = getattr(settings, 'DATABASES_DEFAULT_TYPE', 'mysql')
