import os

from django.core.management.base import BaseCommand, CommandError

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
                content += "* * * * * . %(venv)s/bin/activate && %(orchestra_beat)s %(site_dir)s/manage.py; deactivate" % context
            else:
                content += "* * * * * %(orchestra_beat)s %(site_dir)s/manage.py" % context
            context['content'] = content
            run("echo '%(content)s' | crontab" % context, display=True)
