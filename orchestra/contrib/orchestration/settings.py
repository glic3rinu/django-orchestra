from os import path

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.settings import Setting


ORCHESTRATION_OS_CHOICES = Setting('ORCHESTRATION_OS_CHOICES',
    (
        ('LINUX', "Linux"),
    ),
    validators=[Setting.validate_choices]
)


ORCHESTRATION_DEFAULT_OS = Setting('ORCHESTRATION_DEFAULT_OS',
    'LINUX',
    choices=ORCHESTRATION_OS_CHOICES
)


ORCHESTRATION_SSH_KEY_PATH = Setting('ORCHESTRATION_SSH_KEY_PATH',
    path.join(path.expanduser('~'), '.ssh/id_rsa')
)


ORCHESTRATION_ROUTER = Setting('ORCHESTRATION_ROUTER',
    'orchestra.contrib.orchestration.models.Route',
    validators=[Setting.validate_import_class]
)



ORCHESTRATION_DISABLE_EXECUTION = Setting('ORCHESTRATION_DISABLE_EXECUTION',
    False
)


ORCHESTRATION_BACKEND_CLEANUP_DAYS = Setting('ORCHESTRATION_BACKEND_CLEANUP_DAYS',
    20
)


ORCHESTRATION_SSH_METHOD_BACKEND = Setting('ORCHESTRATION_SSH_METHOD_BACKEND',
    'orchestra.contrib.orchestration.methods.OpenSSH',
    help_text=_("Two methods are provided:<br>"
                "1) <tt>orchestra.contrib.orchestration.methods.OpenSSH</tt> with ControlPersist.<br>"
                "2) <tt>orchestra.contrib.orchestration.methods.Paramiko</tt> with connection pool.<br>"
                "Both perform similarly, but OpenSSH has the advantage that the connections are shared between workers. "
                "Paramiko, in contrast, has a per worker connection pool.")
)
