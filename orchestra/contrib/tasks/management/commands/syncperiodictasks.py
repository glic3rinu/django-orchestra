from django.core.management.base import BaseCommand
from djcelery.app import app
from djcelery.schedulers import DatabaseScheduler


class Command(BaseCommand):
    help = 'Runs Orchestra method.'
    
    def handle(self, *args, **options):
        dbschedule = DatabaseScheduler(app=app)
        self.stdout.write('\033[1m%i periodic tasks have been syncronized:\033[0m' % len(dbschedule.schedule))
        size = max([len(name) for name in dbschedule.schedule])+1
        for name, task in dbschedule.schedule.items():
            spaces = ' '*(size-len(name))
            self.stdout.write('   %s%s%s' % (name, spaces, task.schedule))
