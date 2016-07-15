import time
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from orchestra.contrib.orchestration import manager, Operation
from orchestra.contrib.orchestration.models import Server
from orchestra.contrib.orchestration.backends import ServiceBackend
from orchestra.utils.python import OrderedSet
from orchestra.utils.sys import confirm


class Command(BaseCommand):
    help = 'Runs orchestration backends.'
    
    def add_arguments(self, parser):
        parser.add_argument('model', nargs='?',
            help='Label of a model to execute the orchestration.')
        parser.add_argument('query', nargs='*',
            help='Query arguments for filter().')
        parser.add_argument('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.')
        parser.add_argument('-a', '--action', action='store', dest='action',
            default='save', help='Executes action. Defaults to "save".')
        parser.add_argument('-s', '--servers', action='store', dest='servers',
            default='', help='Overrides route server resolution with the provided server.')
        parser.add_argument('-b', '--backends', action='store', dest='backends',
            default='', help='Overrides backend.')
        parser.add_argument('-l', '--listbackends', action='store_true', dest='list_backends', default=False,
            help='List available baclends.')
        parser.add_argument('--dry-run', action='store_true', dest='dry', default=False,
            help='Only prints scrtipt.')
    
    
    def collect_operations(self, **options):
        model = options.get('model')
        backends = options.get('backends') or set()
        if backends:
            backends = set(backends.split(','))
        servers = options.get('servers') or set()
        if servers:
            servers = set([Server.objects.get(Q(address=server)|Q(name=server)) for server in servers.split(',')])
        action = options.get('action')
        if not model:
            models = set()
            if servers:
                for server in servers:
                    if backends:
                        routes = server.routes.filter(backend__in=backends)
                    else:
                        routes = server.routes.all()
            elif backends:
                routes = Route.objects.filter(backend__in=backends)
            else:
                raise CommandError("Model or --servers or --backends?")
            for route in routes.filter(is_active=True):
                model = route.backend_class.model_class()
                models.add(model)
            querysets = [model.objects.order_by('id') for model in models]
        else:
            kwargs = {}
            for comp in options.get('query', []):
                comps = iter(comp.split('='))
                for arg in comps:
                    kwargs[arg] = next(comps).strip().rstrip(',')
            model = apps.get_model(*model.split('.'))
            queryset = model.objects.filter(**kwargs).order_by('id')
            querysets = [queryset]
        
        operations = OrderedSet()
        route_cache = {}
        for queryset in querysets:
            for instance in queryset:
                manager.collect(instance, action, operations=operations, route_cache=route_cache)
        if backends:
            result = []
            for operation in operations:
                if operation.backend in backends:
                    result.append(operation)
            operations = result
        if servers:
            routes = []
            result = []
            for operation in operations:
                routes = [route for route in operation.routes if route.host in servers]
                operation.routes = routes
                if routes:
                    result.append(operation)
            operations = result
        return operations
    
    def handle(self, *args, **options):
        list_backends = options.get('list_backends')
        if list_backends:
            for backend in ServiceBackend.get_backends():
                self.stdout.write(str(backend).split("'")[1])
            return
        interactive = options.get('interactive')
        dry = options.get('dry')
        operations = self.collect_operations(**options)
        scripts, serialize = manager.generate(operations)
        servers = set()
        # Print scripts
        for key, value in scripts.items():
            route, __, __ = key
            backend, operations = value
            servers.add(str(route.host))
            self.stdout.write('# Execute %s on %s' % (backend.get_name(), route.host))
            for method, commands in backend.scripts:
                script = '\n'.join(commands)
                self.stdout.write(script.encode('ascii', errors='replace').decode())
        if interactive:
            context = {
                'servers': ', '.join(servers),
            }
            if not confirm("\n\nAre your sure to execute the previous scripts on %(servers)s (yes/no)? " % context):
                return
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
                    time.sleep(0.05)
            for log in logs:
                self.stdout.write(' '.join((log.backend, log.state)))
