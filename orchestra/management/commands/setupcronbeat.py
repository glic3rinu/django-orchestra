import os

from django.core.management.base import BaseCommand

from orchestra.contrib.settings import Setting, parser as settings_parser
from orchestra.utils.paths import get_site_dir
from orchestra.utils.sys import run, check_non_root


class Command(BaseCommand):
    help = 'Confingure crontab to run periodic tasks and mailer with orchestra-beat.'
    
    @check_non_root
    def handle(self, *args, **options):
        context = {
            'site_dir': get_site_dir(),
            'orchestra_beat': run('which orchestra-beat').stdout.decode('utf8'),
            'venv': os.environ.get('VIRTUAL_ENV', ''),
        }
        content = run('crontab -l || true').stdout.decode('utf8')
        if 'orchestra-beat' not in content:
            if context['venv']:
                content += "\n* * * * * . %(venv)s/bin/activate && %(orchestra_beat)s %(site_dir)s/manage.py; deactivate" % context
            else:
                content += "\n* * * * * %(orchestra_beat)s %(site_dir)s/manage.py" % context
            context['content'] = content
            run("cat << EOF | crontab\n%(content)s\nEOF" % context, display=True)
        
        # Configrue settings to use threaded task backend (default)
        changes = {}
        if Setting.settings['TASKS_BACKEND'].value == 'celery':
            changes['TASKS_BACKEND'] = settings_parser.Remove()
        if 'celeryd' in Setting.settings['ORCHESTRA_START_SERVICES'].value:
            changes['ORCHESTRA_START_SERVICES'] = settings_parser.Remove()
        if 'celeryd' in Setting.settings['ORCHESTRA_RESTART_SERVICES'].value:
            changes['ORCHESTRA_RESTART_SERVICES'] = settings_parser.Remove()
        if 'celeryd' in Setting.settings['ORCHESTRA_STOP_SERVICES'].value:
            changes['ORCHESTRA_STOP_SERVICES'] = settings_parser.Remove()
        if changes:
            settings_parser.apply(changes)
