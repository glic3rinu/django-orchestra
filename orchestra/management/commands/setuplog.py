import os
import textwrap

from django.core.management.base import BaseCommand

from orchestra.contrib.settings import parser as settings_parser
from orchestra.utils.paths import get_project_dir, get_site_dir, get_project_name
from orchestra.utils.sys import run, check_root, confirm


class Command(BaseCommand):
    help = 'Configures LOGGING setting, creates logging dir and configures logrotate.'
    
    def add_arguments(self, parser):
        parser.add_argument('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.')
    
    @check_root
    def handle(self, *args, **options):
        interactive = options.get('interactive')
        context = {
            'site_dir': get_site_dir(),
            'settings_path': os.path.join(get_project_dir(), 'settings.py'),
            'project_name': get_project_name(),
            'log_dir': os.path.join(get_site_dir(), 'log'),
            'log_path': os.path.join(get_site_dir(), 'log', 'orchestra.log')
        }
        has_logging = not run('grep "^LOGGING\s*=" %(settings_path)s' % context, valid_codes=(0,1)).exit_code
        if has_logging:
            if not interactive:
                self.stderr.write("Project settings already defines LOGGING setting, doing nothing.")
                return
            msg = ("\n\nYour project settings file already defines a LOGGING setting.\n"
                   "Do you want to override it? (yes/no): ")
            if not confirm(msg):
                return
            settings_parser.save({
                'LOGGING': settings_parser.Remove(),
            })
        setuplogrotate = textwrap.dedent("""\
            mkdir %(log_dir)s && chown --reference=%(site_dir)s %(log_dir)s
            touch %(log_path)s
            chown --reference=%(log_dir)s %(log_path)s
            echo '%(log_dir)s/*.log {
              copytruncate
              daily
              rotate 5
              compress
              delaycompress
              missingok
              notifempty
            }' > /etc/logrotate.d/orchestra.%(project_name)s
            cat << 'EOF' >> %(settings_path)s
            
            LOGGING = {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'simple': {
                        'format': '%%(asctime)s %%(name)s %%(levelname)s %%(message)s'
                    },
                },
                'handlers': {
                    'file': {
                        'class': 'logging.FileHandler',
                        'filename': '%(log_path)s',
                        'formatter': 'simple'
                    },
                },
                'loggers': {
                    'orchestra': {
                        'handlers': ['file'],
                        'level': 'INFO',
                        'propagate': True,
                    },
                    'orm': {
                        'handlers': ['file'],
                        'level': 'INFO',
                        'propagate': True,
                    },
                },
            }
            EOF""") % context
        run(setuplogrotate, display=True)
