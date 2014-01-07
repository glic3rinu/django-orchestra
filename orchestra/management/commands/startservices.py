from optparse import make_option

from django.core.management.base import BaseCommand

from orchestra.settings import START_SERVICES
from orchestra.utils.system import run, check_root


def run_tuple(services, action, options, optional=False):
    if isinstance(services, str):
        services = [services]
    for service in services:
        if options.get(service):
            err_codes = [0,1] if optional else [0]
            e = run('service %s %s' % (service, action), err_codes=err_codes)
            if e.return_code == 1:
                return False
    return True


def flatten(nested, depth=0):
    if hasattr(nested, '__iter__'):
        for sublist in nested:
            for element in flatten(sublist, depth+1):
                yield element
    else:
        yield nested



class ManageServiceCommand(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(ManageServiceCommand, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + tuple(
            make_option('--no-%s' % service, action='store_false', dest=service, default=True,
                 help='Do not %s %s' % (self.action, service)) for service in flatten(self.services)
            )
    
    @check_root
    def handle(self, *args, **options):
        for service in self.services:
            if isinstance(service, str):
                run_tuple(service, self.action, options)
            else:
                failure = True
                for opt_service in service:
                    if run_tuple(opt_service, self.action, options, optional=True):
                        failure = False
                        break
                if failure:
                    str_services = [ str(s) for s in service ]
                    self.stderr.write('Error %sing %s' % (self.action, ' OR '.join(str_services)))


class Command(ManageServiceCommand):
    services = START_SERVICES
    action = 'start'
    option_list = BaseCommand.option_list
    help = 'Start all related services. Usefull for reload configuration and files.'
