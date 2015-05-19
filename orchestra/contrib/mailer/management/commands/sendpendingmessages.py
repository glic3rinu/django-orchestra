from django.core.management.base import BaseCommand

from orchestra.contrib.tasks.decorators import keep_state

from ...engine import send_pending


class Command(BaseCommand):
    help = 'Runs Orchestra method.'
    
    def handle(self, *args, **options):
        keep_state(send_pending)()
