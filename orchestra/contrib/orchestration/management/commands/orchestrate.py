import sys

from django.core.management.base import BaseCommand
from django.db.models.loading import get_model

from orchestra.contrib.orchestration import manager


class Command(BaseCommand):
    help = 'Runs orchestration backends.'
    
    def add_arguments(self, parser):
        parser.add_argument('model',
            help='Label of a model to execute the orchestration.')
        parser.add_argument('query', nargs='*',
            help='Query arguments for filter().')
        parser.add_argument('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.')
        parser.add_argument('--action', action='store', dest='action',
            default='save', help='Executes action. Defaults to "save".')
        parser.add_argument('--dry-run', action='store_true', dest='dry', default=False,
            help='Only prints scrtipt.')
    
    def handle(self, *args, **options):
        model = get_model(*options['model'].split('.'))
        action = options.get('action')
        interactive = options.get('interactive')
        dry = options.get('dry')
        kwargs = {}
        for comp in options.get('query', []):
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
                script = '\n'.join(commands) + '\n'
                script = script.encode('ascii', errors='replace')
                sys.stdout.write(script.decode('ascii'))
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
        if not dry:
            logs = manager.execute(scripts, block=block)
            for log in logs:
                print(log.stdout)
                sys.stderr.write(log.stderr)
            for log in logs:
                print(log.backend, log.state)
