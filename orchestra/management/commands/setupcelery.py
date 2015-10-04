import textwrap
from optparse import make_option
from os import path

from django.core.management.base import BaseCommand

from orchestra.contrib.settings import Setting, parser as settings_parser
from orchestra.utils.paths import get_site_dir, get_orchestra_dir, get_project_dir
from orchestra.utils.sys import run, check_root


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--username', dest='username', default='orchestra',
                help='Specifies the system user that would run celeryd.'),
            make_option('--processes', dest='processes', default=2,
                help='Number of celeryd processes.'),
            make_option('--noinput', action='store_false', dest='interactive', default=True,
                help='Tells Django to NOT prompt the user for input of any kind. '
                     'You must use --username with --noinput, and must contain the '
                     'cleleryd process owner, which is the user how will perform tincd updates'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Configure Celeryd to run with your orchestra instance.'
    
    @check_root
    def handle(self, *args, **options):
        context = {
            'site_dir': get_site_dir(),
            'username': options.get('username'),
            'bin_path': path.join(get_orchestra_dir(), 'bin'),
            'processes': options.get('processes'),
            'settings': path.join(get_project_dir(), 'settings.py')
        }
        
        celery_config = textwrap.dedent("""\
            # Name of nodes to start, here we have a single node
            CELERYD_NODES="w1"
            
            # Where to chdir at start.
            CELERYD_CHDIR="%(site_dir)s"
            
            # How to call "manage.py celeryd_multi"
            CELERYD_MULTI="python3 $CELERYD_CHDIR/manage.py celeryd_multi"
            
            # Extra arguments to celeryd
            CELERYD_OPTS="-P:w1 processes -c:w1 %(processes)s -Q:w1 celery"
            
            # Name of the celery config module.
            CELERY_CONFIG_MODULE="celeryconfig"
            
            # %%n will be replaced with the nodename.
            CELERYD_LOG_FILE="/var/log/celery/%%n.log"
            CELERYD_PID_FILE="/var/run/celery/%%n.pid"
            CELERY_CREATE_DIRS=1
            
            # Full path to the celeryd logfile.
            CELERYEV_LOG_FILE="/var/log/celery/celeryev.log"
            CELERYEV_PID_FILE="/var/run/celery/celeryev.pid"
            
            # Workers should run as an unprivileged user.
            CELERYD_USER="%(username)s"
            CELERYD_GROUP="$CELERYD_USER"
            
            # Persistent revokes
            CELERYD_STATE_DB="$CELERYD_CHDIR/persistent_revokes"
            
            # Celeryev
            CELERYEV="python3 $CELERYD_CHDIR/manage.py"
            CELERYEV_CAM="djcelery.snapshot.Camera"
            CELERYEV_USER="$CELERYD_USER"
            CELERYEV_GROUP="$CELERYD_USER"
            CELERYEV_OPTS="celerycam"
            
            # Celerybeat
            CELERYBEAT="python3 ${CELERYD_CHDIR}/manage.py celerybeat"
            CELERYBEAT_USER="$CELERYD_USER"
            CELERYBEAT_GROUP="$CELERYD_USER"
            CELERYBEAT_CHDIR="$CELERYD_CHDIR"
            CELERYBEAT_OPTS="--schedule=/var/run/celerybeat-schedule --scheduler=djcelery.schedulers.DatabaseScheduler"
            """ % context
        )
        
        run("echo '%s' > /etc/default/celeryd" % celery_config)
        
        # https://raw.github.com/celery/celery/master/extra/generic-init.d/
        for script in ['celeryevcam', 'celeryd', 'celerybeat']:
            context['script'] = script
            run('cp %(bin_path)s/%(script)s /etc/init.d/%(script)s' % context)
            run('chmod +x /etc/init.d/%(script)s' % context)
            run('update-rc.d %(script)s defaults' % context)
        
        rotate = textwrap.dedent("""\
            /var/log/celery/*.log {
                weekly
                missingok
                rotate 10
                compress
                delaycompress
                notifempty
                copytruncate
            }"""
        )
        run("echo '%s' > /etc/logrotate.d/celeryd" % rotate)
        
        changes = {}
        if Setting.settings['TASKS_BACKEND'].value != 'celery':
            changes['TASKS_BACKEND'] = 'celery'
        if Setting.settings['ORCHESTRA_START_SERVICES'].value == Setting.settings['ORCHESTRA_START_SERVICES'].default:
            changes['ORCHESTRA_START_SERVICES'] = (
                    'postgresql',
                    'celeryevcam',
                    'celeryd',
                    'celerybeat',
                    ('uwsgi', 'nginx'),
                )
        if Setting.settings['ORCHESTRA_RESTART_SERVICES'].value == Setting.settings['ORCHESTRA_RESTART_SERVICES'].default:
            changes['ORCHESTRA_RESTART_SERVICES'] = (
                    'celeryd',
                    'celerybeat',
                    'uwsgi',
                )
        if Setting.settings['ORCHESTRA_STOP_SERVICES'].value == Setting.settings['ORCHESTRA_STOP_SERVICES'].default:
            changes['ORCHESTRA_STOP_SERVICES'] = (
                    ('uwsgi', 'nginx'),
                    'celerybeat',
                    'celeryd',
                    'celeryevcam',
                    'postgresql'
                )
        if changes:
            settings_parser.apply(changes)
