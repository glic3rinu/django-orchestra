from orchestra.core.validators import validate_hostname

from orchestra.contrib.settings import Setting


DATABASES_TYPE_CHOICES = Setting('DATABASES_TYPE_CHOICES',
    (
        ('mysql', 'MySQL'),
        ('postgres', 'PostgreSQL'),
    ),
    validators=[Setting.validate_choices]
)


DATABASES_DEFAULT_TYPE = Setting('DATABASES_DEFAULT_TYPE',
    'mysql',
    choices=DATABASES_TYPE_CHOICES,
)


DATABASES_DEFAULT_HOST = Setting('DATABASES_DEFAULT_HOST',
    'localhost',
#    validators=[validate_hostname],
)


DATABASES_MYSQL_DB_DIR = Setting('DATABASES_MYSQL_DB_DIR',
    '/var/lib/mysql',
)
