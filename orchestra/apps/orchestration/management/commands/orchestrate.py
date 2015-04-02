import sys

from django.core.management.base import BaseCommand
from django.db.models.loading import get_model
from django.utils.six.moves import input

from orchestra.apps.orchestration import manager
from orchestra.apps.orchestration.models import BackendOperation as Operation


class Command(BaseCommand):
    help = 'Runs orchestration backends.'
    option_list = BaseCommand.option_list
    args = "[app_label] [filter]"
    
    def handle(self, *args, **options):
        model_label = args[0]
        model = get_model(*model_label.split('.'))
        # TODO options
        action = options.get('action', 'save')
        interactive = options.get('interactive', True)
        kwargs = {}
        for comp in args[1:]:
            comps = iter(comp.split('='))
            for arg in comps:
                kwargs[arg] = next(comps).strip().rstrip(',')
        operations = []
        operations = set()
        route_cache = {}
        for instance in model.objects.filter(**kwargs):
            manager.collect(instance, action, operations=operations, route_cache=route_cache)
        scripts, block = manager.generate(operations)
        servers = []
        # Print scripts
        for key, value in scripts.items():
            server, __ = key
            backend, operations = value
            servers.append(server.name)
            sys.stdout.write('# Execute on %s\n' % server.name)
            for method, commands in backend.scripts:
                sys.stdout.write('\n'.join(commands) + '\n')
        if interactive:
            context = {
                'servers': ', '.join(servers),
            }
            msg = ("\n\nAre your sure to execute the previous scripts on %(servers)s (yes/no)? " % context)
            confirm = input(msg)
            while 1:
                if confirm not in ('yes', 'no'):
                    confirm = input('Please enter either "yes" or "no": ')
                    continue
                if confirm == 'no':
                    return
                break
#        manager.execute(scripts, block=block)

