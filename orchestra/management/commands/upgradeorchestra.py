import functools
import os
import random
import string
from distutils.sysconfig import get_python_lib
from optparse import make_option

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from orchestra import get_version
from orchestra.utils.sys import run, check_root


r = functools.partial(run, silent=False)


def get_existing_pip_installation():
    """ returns current pip installation path """
    if run("pip freeze|grep django-orchestra", valid_codes=(0,1)).exit_code == 0:
        for lib_path in get_python_lib(), get_python_lib(prefix="/usr/local"):
            existing_path = os.path.abspath(os.path.join(lib_path, "orchestra"))
            if os.path.exists(existing_path):
                return existing_path
    return None


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--pip_only', action='store_true', dest='pip_only', default=False,
                help='Only run "pip install django-orchestra --upgrade"'),
            make_option('--orchestra_version', dest='version', default=False,
                help='Specifies what version of the Orchestra you want to install'),
            )
    
    option_list = BaseCommand.option_list
    help = "Upgrading Orchestra's installation. Desired version is accepted as argument"
    can_import_settings = False
    leave_locale_alone = True
    
    @check_root
    def handle(self, *args, **options):
        current_version = get_version()
        current_path = get_existing_pip_installation()
        
        if current_path is not None:
            desired_version = options.get('version')
            if args:
                desired_version = args[0]
            if current_version == desired_version:
                msg = "Not upgrading, you already have version %s installed"
                raise CommandError(msg % desired_version)
            # Create a backup of current installation
            base_path = os.path.abspath(os.path.join(current_path, '..'))
            char_set = string.ascii_uppercase + string.digits
            rand_name = ''.join(random.sample(char_set, 6))
            backup = os.path.join(base_path, 'orchestra.' + rand_name)
            run("mv %s %s" % (current_path, backup))
            
            # collect existing eggs previous to the installation
            eggs_regex = os.path.join(base_path, 'django_orchestra-*.egg-info')
            eggs = run('ls -d %s' % eggs_regex)
            eggs = eggs.stdout.splitlines()
            try:
                if desired_version:
                    r('pip install django-orchestra==%s' % desired_version)
                else:
                    # Did I mentioned how I hate PIP?
                    if run('pip --version|cut -d" " -f2').stdout == '1.0':
                        r('pip install django-orchestra --upgrade')
                    else:
                        # (Fucking pip)^2, it returns exit code 0 even when fails
                        # because requirement already up-to-date
                        r('pip install django-orchestra --upgrade --force')
            except CommandError:
                # Restore backup
                run('rm -rf %s' % current_path)
                run('mv %s %s' % (backup, current_path))
                raise CommandError("Problem runing pip upgrade, aborting...")
            else:
                # Some old versions of pip do not performe this cleaning ...
                # Remove all backups
                run('rm -fr %s' % os.path.join(base_path, 'orchestra\.*'))
                # Clean old egg files, yeah, cleaning PIP shit :P
                c_version = 'from orchestra import get_version; print get_version()'
                version = run('python -c "%s;"' % c_version).stdout
                for egg in eggs:
                    # Do not remove the actual egg file when upgrading twice the same version
                    if egg.split('/')[-1] != "django_orchestra-%s.egg-info" % version:
                        run('rm -fr %s' % egg)
        else:
            raise CommandError("You don't seem to have any previous PIP installation")
        
        # version specific upgrade operations
        if not options.get('pip_only'):
            call_command("postupgradeorchestra", version=current_version)
