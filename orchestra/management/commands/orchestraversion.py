from django.core.management.base import NoArgsCommand

from orchestra import get_version


class Command(NoArgsCommand):
    help = 'Shows django-orchestra version'

    def handle_noargs(self, **options):
        self.stdout.write(get_version())
