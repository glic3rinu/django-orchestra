from django.core.management.base import BaseCommand

from orchestra import settings
from orchestra.management.commands.startservices import ManageServiceCommand


class Command(ManageServiceCommand):
    services = settings.ORCHESTRA_STOP_SERVICES
    action = 'stop'
    option_list = BaseCommand.option_list
    help = 'Stop all related services. Usefull for reload configuration and files.'
