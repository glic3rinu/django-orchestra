import os

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import Operation


def validate_paths_exist(user, paths):
    operations = []
    user.paths_to_validate = paths
    operations.extend(Operation.create_for_action(user, 'validate_paths_exist'))
    logs = Operation.execute(operations)
    stderr = '\n'.join([log.stderr for log in logs])
    if 'path does not exists' in stderr:
        raise ValidationError(stderr)


def validate_home(user, data, account):
    """ validates home based on account and data['shell'] """
    if not 'username' in data and not user.pk:
        # other validation will have been raised for required username
        return
    user = type(user)(
        username=data.get('username') or user.username,
        shell=data.get('shell') or user.shell,
    )
    if 'home' in data and data['home']:
        home = os.path.normpath(data['home'])
        user_home = user.get_base_home()
        account_home = account.main_systemuser.get_home()
        if user.has_shell:
            if home != user_home:
                raise ValidationError({
                    'home': _("Not a valid home directory.")
                })
        elif home not in (user_home, account_home):
            raise ValidationError({
                'home': _("Not a valid home directory.")
            })
        if 'directory' in data and data['directory']:
            path = os.path.join(data['home'], data['directory'])
            try:
                validate_paths_exist(user, (path,))
            except ValidationError as err:
                raise ValidationError({
                    'directory': err,
                })
