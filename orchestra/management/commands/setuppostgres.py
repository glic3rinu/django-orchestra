import os
from optparse import make_option

from django.core.management.base import BaseCommand

from orchestra.utils.paths import get_project_dir
from orchestra.utils.sys import run, check_root


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--db_name', dest='db_name', default='orchestra',
                help='Specifies the database to create.'),
            make_option('--db_user', dest='db_user', default='orchestra',
                help='Specifies the database to create.'),
            make_option('--db_password', dest='db_password', default='orchestra',
                help='Specifies the database to create.'),
            make_option('--db_host', dest='db_host', default='localhost',
                help='Specifies the database to create.'),
            make_option('--db_port', dest='db_port', default='5432',
                help='Specifies the database to create.'),
            make_option('--noinput', action='store_false', dest='interactive', default=True,
                help='Tells Django to NOT prompt the user for input of any kind. '
                     'You must use --username with --noinput, and must contain the '
                     'cleeryd process owner, which is the user how will perform tincd updates'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Setup PostgreSQL database.'
    
    @check_root
    def handle(self, *args, **options):
        # Configure firmware generation
        context = {
            'db_name': options.get('db_name'),
            'db_user': options.get('db_user'),
            'db_password': options.get('db_password'),
            'db_host': options.get('db_host'),
            'db_port': options.get('db_port') }
        
        run('su postgres -c "psql -c \\"CREATE USER %(db_user)s PASSWORD \'%(db_password)s\';\\""' % context, valid_codes=(0,1))
        run('su postgres -c "psql -c \\"CREATE DATABASE %(db_name)s OWNER %(db_user)s;\\""' % context, valid_codes=(0,1))
        context.update({'settings': os.path.join(get_project_dir(), 'settings.py')})
        
        if run("grep 'DATABASES' %(settings)s" % context, valid_codes=(0,1)).exit_code == 0:
            # Update existing settings_file
            run("sed -i \"s/'ENGINE': '\w*',/'ENGINE': 'django.db.backends.postgresql_psycopg2',/\" %(settings)s" % context)
            run("sed -i \"s/'NAME': '.*',/'NAME': '%(db_name)s',/\" %(settings)s" % context)
            run("sed -i \"s/'USER': '.*',/'USER': '%(db_user)s',/\" %(settings)s" % context)
            run("sed -i \"s/'PASSWORD': '.*',/'PASSWORD': '%(db_password)s',/\" %(settings)s" % context)
            run("sed -i \"s/'HOST': '.*',/'HOST': '%(db_host)s',/\" %(settings)s" % context)
            run("sed -i \"s/'PORT': '.*',/'PORT': '%(db_port)s',/\" %(settings)s" % context)
        else:
            db_config = (
                "DATABASES = {\n"
                "    'default': {\n"
                "        'ENGINE': 'django.db.backends.postgresql_psycopg2',\n"
                "        'NAME': '%(db_name)s',\n"
                "        'USER': '%(db_user)s',\n"
                "        'PASSWORD': '%(db_password)s',\n"
                "        'HOST': '%(db_host)s',\n"
                "        'PORT': '%(db_port)s',\n"
                "        'ATOMIC_REQUESTS': True,\n"
                "    }\n"
                "}\n" % context)
            context.update({'db_config': db_config})
            run('echo "%(db_config)s" >> %(settings)s' % context)
