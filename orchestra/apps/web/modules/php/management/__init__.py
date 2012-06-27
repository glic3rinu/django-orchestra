from web.modules.php import models as php_app
from django.db.models import signals

def prepopulate_php_directives(app, created_models, verbosity, **kwargs):
    from django.core.management import call_command

    if php_app.PHPDirective in created_models and kwargs.get('interactive', True):
        msg = ("\nYou just installed Django ISP Tools web.modules.php system."
               "\nWould you like to prepopulate it with some PHP directives? (yes/no): ")
        confirm = raw_input(msg)
        while 1:
            if confirm not in ('yes', 'no'):
                confirm = raw_input('Please enter either "yes" or "no": ')
                continue
            if confirm == 'yes':
                call_command("prepopulatephpdirectives")
            break


signals.post_syncdb.connect(prepopulate_php_directives,
    sender=php_app, dispatch_uid = "php.management.prepopulatephpdirectives")

