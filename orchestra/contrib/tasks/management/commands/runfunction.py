from django.core.management.base import BaseCommand

from orchestra.utils.python import import_class

from ... import keep_state, get_id, get_name


class Command(BaseCommand):
    help = 'Runs Orchestra method.'
    
    def add_arguments(self, parser):
        parser.add_argument('method',
            help='Python path to the method to execute.')
        parser.add_argument('args', nargs='*',
            help='Additional arguments passed to the method.')
    
    def handle(self, *args, **options):
        method = import_class(options['method'])
        kwargs = {}
        arguments = []
        for arg in args:
            if '=' in args:
                name, value = arg.split('=')
                if value.isdigit():
                    value = int(value)
                kwargs[name] = value
            else:
                if arg.isdigit():
                    arg = int(arg)
                arguments.append(arg)
        args = arguments
        keep_state(method)(get_id(), get_name(method), *args, **kwargs)
