import json

from django.core.management.base import BaseCommand, CommandError

from ...engine import send_pending

class Command(BaseCommand):
    help = 'Runs Orchestra method.'
    
    def handle(self, *args, **options):
        send_pending()
