from django.core.management.base import BaseCommand

from orchestra.management.commands.startservices import ManageServiceCommand
from orchestra.settings import ORCHESTRA_RESTART_SERVICES


class Command(ManageServiceCommand):
    services = ORCHESTRA_RESTART_SERVICES
    action = 'restart'
    option_list = BaseCommand.option_list
    help = 'Restart all related services. Usefull for reload configuration and files.'
