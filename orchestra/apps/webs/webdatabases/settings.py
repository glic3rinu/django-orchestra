from django.conf import settings



WEBDATABASES_TYPE_CHOICES = getattr(settings, 'WEBDATABASES_TYPE_CHOICES', (
    ('mysql', 'MySQL'),
    ('postgres', 'PostgreSQL'),
))


WEBDATABASES_DEFAULT_TYPE = getattr(settings, 'WEBDATABASES_DEFAULT_TYPE', 'mysql')
