import re
import os
from optparse import make_option

from django.core.management.base import BaseCommand

from orchestra.utils.paths import get_site_dir
from orchestra.utils.sys import run, check_root


def deprecate_periodic_tasks(names):
    from djcelery.models import PeriodicTask
    for name in names:
        PeriodicTask.objects.filter(name=name).delete()
    run('rabbitmqctl stop_app')
    run('rabbitmqctl reset')
    run('rabbitmqctl start_app')
    run('service celeryd restart')


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--no-restart', action='store_false', dest='restart', default=True,
                help='Only install local requirements'),
            make_option('--specifics', action='store_true', dest='specifics_only',
                default=False, help='Only run version specific operations'),
            make_option('--no-upgrade-notes', action='store_false', default=True,
                dest='print_upgrade_notes', help='Do not print specific upgrade notes'),
            make_option('--from', dest='version', default=False,
                help="Orchestra's version from where you are upgrading, i.e 0.0.1"),
            )
    
    option_list = BaseCommand.option_list
    help = 'Upgrades django-orchestra installation'
    # This command must be able to run in an environment with unsatisfied dependencies
    leave_locale_alone = True
    can_import_settings = False
    requires_model_validation = False
    
    @check_root
    def handle(self, *args, **options):
        version = options.get('version')
        upgrade_notes = []
        if version:
            version_re = re.compile(r'^\s*(\d+)\.(\d+)\.(\d+).*')
            minor_release = version_re.search(version)
            if minor_release is not None:
                major, major2, minor = version_re.search(version).groups()
            else:
                version_re = re.compile(r'^\s*(\d+)\.(\d+).*')
                major, major2 = version_re.search(version).groups()
                minor = 0
            # Represent version as two digits per number: 1.2.2 -> 10202
            version = int(str(major) + "%02d" % int(major2) + "%02d" % int(minor))
            
            # Pre version specific upgrade operations
            if version < '001':
                pass
        
        if not options.get('specifics_only'):
            # Common stuff
            orchestra_admin = os.path.join(os.path.dirname(__file__), '../../bin/')
            orchestra_admin = os.path.join(orchestra_admin, 'orchestra-admin')
            run('chmod +x %s' % orchestra_admin)
            run("%s install_requirements" % orchestra_admin)
            
            manage_path = os.path.join(get_site_dir(), 'manage.py')
            run("python %s collectstatic --noinput" % manage_path)
            run("python %s migrate --noinput accounts" % manage_path)
            run("python %s migrate --noinput" % manage_path)
            if options.get('restart'):
                run("python %s restartservices" % manage_path)
        
        if not version:
            self.stderr.write('\n'
                'Next time you migth want to provide a --from argument in order '
                'to run version specific upgrade operations\n')
            return
        
        # Post version specific operations
        if version <= '001':
            pass
        
        if upgrade_notes and options.get('print_upgrade_notes'):
            self.stdout.write('\n\033[1m\n'
                '    ===================\n'
                '    ** UPGRADE NOTES **\n'
                '    ===================\n\n' +
                '\n'.join(upgrade_notes) + '\033[m\n')
