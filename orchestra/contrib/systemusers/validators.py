import os

from django.core.exceptions import ValidationError


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
