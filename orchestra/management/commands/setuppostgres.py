import os
import textwrap
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from orchestra.utils.paths import get_project_dir
from orchestra.utils.python import random_ascii
from orchestra.utils.sys import run, check_root


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        # Get defaults from settings, if exists
        try:
            defaults = settings.DATABASES['default']
        except (AttributeError, KeyError):
            defaults = {}
        else:
            if defaults['ENGINE'] != 'django.db.backends.postgresql_psycopg2':
                defaults = {}
        
        self.option_list = BaseCommand.option_list + (
            make_option('--db_name', dest='db_name',
                default=defaults.get('DB_NAME', 'orchestra'),
                help='Specifies the database to create.'),
            make_option('--db_user', dest='db_user',
                default=defaults.get('DB_USER', 'orchestra'),
                help='Specifies the database to create.'),
            make_option('--db_password', dest='db_password',
                default=defaults.get('PASSWORD', ''),
                help='Specifies the database password, random if not specified.'),
            make_option('--db_host', dest='db_host',
                default=defaults.get('HOST', 'localhost'),
                help='Specifies the database to create.'),
            make_option('--db_port', dest='db_port',
                default=defaults.get('PORT', '5432'),
                help='Specifies the database to create.'),
            make_option('--noinput', action='store_false', dest='interactive', default=True,
                help='Tells Django to NOT prompt the user for input of any kind. '
                     'You must use --username with --noinput, and must contain the '
                     'cleeryd process owner, which is the user how will perform tincd updates'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Setup PostgreSQL database.'
    
    def run_postgres(self, cmd, *args, **kwargs):
        return run('su postgres -c "psql -c \\"%s\\""' % cmd, *args, **kwargs)
    
    @check_root
    def handle(self, *args, **options):
        interactive = options.get('interactive')
        db_password = options.get('db_password')
        context = {
            'db_name': options.get('db_name'),
            'db_user': options.get('db_user'),
            'db_password': db_password,
            'db_host': options.get('db_host'),
            'db_port': options.get('db_port'),
            'default_db_password': db_password or random_ascii(10),
        }
        
        create_user = "CREATE USER %(db_user)s PASSWORD '%(default_db_password)s';"
        alter_user = "ALTER USER %(db_user)s WITH PASSWORD '%(db_password)s';"
        create_database = "CREATE DATABASE %(db_name)s OWNER %(db_user)s;"
        
        # Create or update user
        if self.run_postgres(create_user % context, valid_codes=(0,1)).exit_code == 1:
            if interactive and not db_password:
                msg = ("Postgres user '%(db_user)s' already exists, "
                       "please provide a password [%(default_db_password)s]: " % context)
                context['db_password'] = input(msg) or context['default_db_password']
                self.run_postgres(alter_user % context)
                msg = "Updated Postgres user '%(db_user)s' password: '%(db_password)s'"
                self.stdout.write(msg % context)
            elif db_password:
                self.run_postgres(alter_user % context)
                msg = "Updated Postgres user '%(db_user)s' password: '%(db_password)s'"
                self.stdout.write(msg % context)
            else:
                raise CommandError("Postgres user '%(db_user)s' already exists and "
                                   "--db_pass has not been provided." % context)
        else:
            context['db_password'] = context['default_db_password']
            msg = "Created new Postgres user '%(db_user)s' with password '%(db_password)s'"
            self.stdout.write(msg % context)
        self.run_postgres(create_database % context, valid_codes=(0,1))
        
        context.update({
            'settings': os.path.join(get_project_dir(), 'settings.py')
        })
        
        if run("grep '^DATABASES\s*=\s*{' %(settings)s" % context, valid_codes=(0,1)).exit_code == 0:
            # Update existing settings_file
            run(textwrap.dedent("""sed -i \\
                -e "s/'ENGINE':[^#]*/'ENGINE': 'django.db.backends.postgresql_psycopg2',  /" \\
                -e "s/'NAME':[^#]*/'NAME': '%(db_name)s',  /" \\
                -e "s/'USER':[^#]*/'USER': '%(db_user)s',  /" \\
                -e "s/'PASSWORD':[^#]*/'PASSWORD': '%(db_password)s',  /" \\
                -e "s/'HOST':[^#]*/'HOST': '%(db_host)s',  /" \\
                -e "s/'PORT':[^#]*/'PORT': '%(db_port)s',  /" %(settings)s\
                """) % context
            )
        else:
            db_config = textwrap.dedent("""\
                DATABASES = {
                    'default': {
                        'ENGINE': 'django.db.backends.postgresql_psycopg2',
                        'NAME': '%(db_name)s',
                        'USER': '%(db_user)s',
                        'PASSWORD': '%(db_password)s',
                        'HOST': '%(db_host)s',
                        'PORT': '%(db_port)s',
                        'ATOMIC_REQUESTS': True,
                    }
                }""") % context
            context.update({
                'db_config': db_config
            })
            run('echo "%(db_config)s" >> %(settings)s' % context)
