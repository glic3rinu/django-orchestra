from web.modules.fcgid import models as fcgid_app
from django.db.models import signals

def prepopulate_fcgid_directives(app, created_models, verbosity, **kwargs):
    from django.core.management import call_command

    if fcgid_app.FcgidDirective in created_models and kwargs.get('interactive', True):
        msg = ("\nYou just installed Django ISP Tools web.modules.Fcgid system."
               "\nWould you like to prepopulate it with some fcgid directives? (yes/no): ")
        confirm = raw_input(msg)
        while 1:
            if confirm not in ('yes', 'no'):
                confirm = raw_input('Please enter either "yes" or "no": ')
                continue
            if confirm == 'yes':
                call_command("prepopulatefcgiddirectives")
            break


signals.post_syncdb.connect(prepopulate_fcgid_directives,
    sender=fcgid_app, dispatch_uid = "fcgid.management.prepopulatefcgiddirectives")

