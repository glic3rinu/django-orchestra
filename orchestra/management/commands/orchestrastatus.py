import re

from django.conf import settings as djsettings
from django.core.management.base import BaseCommand
from django.db import connections

from orchestra import settings
from orchestra.utils import paths
from orchestra.utils.sys import run

from .startservices import flatten


class Command(BaseCommand):
    def is_running(self, context, ps):
        if context['service'] == 'uwsgi':
            regex = r'.*uwsgi .*/%(project_name)s.ini.*' % context
        else:
            regex = r'.*%(service)s.*' % context
        return re.match(regex, ps)
    
    def handle(self, *args, **options):
        context = {
            'project_name': paths.get_project_name(),
            'site_dir': paths.get_site_dir(),
        }
        banner = "%(project_name)s status" % context
        self.stdout.write(banner)
        self.stdout.write('-'*len(banner))
        if djsettings.DEBUG:
            self.stdout.write(" debug enabled")
        else:
            self.stdout.write(" debug disabled")
        ps = run('ps aux').stdout.decode().replace('\n', ' ')
        for service in flatten(settings.ORCHESTRA_START_SERVICES):
            context['service'] = service
            if self.is_running(context, ps):
                self.stdout.write(" %(service)s online" % context)
            else:
                self.stdout.write(" %(service)s offline" % context)
            if service == 'nginx':
                try:
                    config_path = '/etc/nginx/conf.d/%(project_name)s.conf' % context
                    with open(config_path, 'r') as handler:
                        config = handler.read().replace('\n', ' ')
                except FileNotFoundError:
                    self.stdout.write("   * %s not found" % config_path)
                else:
                    regex = r'location\s+([^\s]+)\s+{.*uwsgi_pass unix:///var/run/uwsgi/app/%(project_name)s/socket;.*' % context
                    location = re.findall(regex, config)
                    if location:
                        self.stdout.write("   * location %s" % location[0])
                    else:
                        self.stdout.write("   * location not found")
            elif service == 'postgresql':
                db_conn = connections['default']
                try:
                    c = db_conn.cursor()
                except OperationalError:
                    self.stdout.write("   * DB connection failed")
                else:
                    self.stdout.write("   * DB connection succeeded")
        cronbeat = 'crontab -l | grep "^.*/orchestra-beat %(site_dir)s/manage.py"' % context
        if run(cronbeat, valid_codes=(0, 1)).exit_code == 0:
            self.stdout.write(" cronbeat installed")
        else:
            self.stdout.write(" cronbeat not installed")
