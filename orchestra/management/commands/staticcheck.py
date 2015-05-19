from django.core.management.base import BaseCommand

from orchestra.utils.paths import get_orchestra_dir, get_site_dir
from orchestra.utils.sys import run


class Command(BaseCommand):
    help = "Run flake8 syntax checks."
    
    def handle(self, *filenames, **options):
        flake = run('flake8 {%s,%s} | grep -v "W293\|E501"' % (get_orchestra_dir(), get_site_dir()))
        self.stdout.write(flake.stdout.decode('utf8'))
