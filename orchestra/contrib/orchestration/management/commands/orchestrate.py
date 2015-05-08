import time
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps

from orchestra.contrib.orchestration import manager, Operation
from orchestra.contrib.orchestration.models import Server
from orchestra.contrib.orchestration.backends import ServiceBackend
from orchestra.utils.python import import_class, OrderedSet, AttrDict


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
        parser.add_argument('--servers', action='store', dest='servers',
            default='', help='Overrides route server resolution with the provided server.')
        parser.add_argument('--backends', action='store', dest='backends',
            default='', help='Overrides backend.')
        parser.add_argument('--listbackends', action='store_true', dest='list_backends', default=False,
            help='List available baclends.')
        parser.add_argument('--dry-run', action='store_true', dest='dry', default=False,
            help='Only prints scrtipt.')
    
    def handle(self, *args, **options):
        list_backends = options.get('list_backends')
        if list_backends:
            for backend in ServiceBackend.get_backends():
                self.stdout.write(str(backend).split("'")[1])
            return
        model = apps.get_model(*options['model'].split('.'))
        action = options.get('action')
        interactive = options.get('interactive')
        servers = options.get('servers')
        backends = options.get('backends')
        if (servers and not backends) or (not servers and backends):
            raise CommandError("--backends and --servers go in tandem.")
        dry = options.get('dry')
        kwargs = {}
        for comp in options.get('query', []):
            comps = iter(comp.split('='))
            for arg in comps:
                kwargs[arg] = next(comps).strip().rstrip(',')
        operations = OrderedSet()
        route_cache = {}
        queryset = model.objects.filter(**kwargs).order_by('id')
        if servers:
            servers = servers.split(',')
            backends = backends.split(',')
            routes = []
            # Get and create missing Servers
            for server in servers:
                try:
                    server = Server.objects.get(address=server)
                except Server.DoesNotExist:
                    server = Server(name=server, address=server)
                    server.full_clean()
                    server.save()
                routes.append(AttrDict(host=server, async=False))
            # Generate operations for the given backend
            for instance in queryset:
                for backend in backends:
                    backend = import_class(backend)
                    operations.add(Operation(backend, instance, action, routes=routes))
        else:
            for instance in queryset:
                manager.collect(instance, action, operations=operations, route_cache=route_cache)
        scripts, serialize = manager.generate(operations)
        servers = []
        # Print scripts
        for key, value in scripts.items():
            route, __ = key
            backend, operations = value
            servers.append(str(route.host))
            self.stdout.write('# Execute on %s' % server.name)
            for method, commands in backend.scripts:
                script = '\n'.join(commands)
                self.stdout.write(script)
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
            logs = manager.execute(scripts, serialize=serialize, async=True)
            running = list(logs)
            stdout = 0
            stderr = 0
            while running:
                for log in running:
                    cstdout = len(log.stdout)
                    cstderr = len(log.stderr)
                    if cstdout > stdout:
                        self.stdout.write(log.stdout[stdout:])
                        stdout = cstdout
                    if cstderr > stderr:
                        self.stderr.write(log.stderr[stderr:])
                        stderr = cstderr
                    if log.has_finished:
                        running.remove(log)
                    time.sleep(0.1)
            for log in logs:
                self.stdout.write(' '.join((log.backend, log.state)))
