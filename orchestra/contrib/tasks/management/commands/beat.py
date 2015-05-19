from django.core.management.base import BaseCommand

from ... import beat


class Command(BaseCommand):
    help = 'Runs periodic tasks.'
    
    def handle(self, *args, **options):
        beat.run()
