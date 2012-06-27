from django.db.models import signals
import ordering.models
#FIXME: this last import causes command crash

def prepopulate_service(app, created_models, verbosity, **kwargs):
    from django.core.management import call_command

    if ordering.models.ServiceAccounting in created_models and kwargs.get('interactive', True):
        msg = ("\nYou just installed Django ISP Tools Ordering system."
               "\nWould you like to prepopulate it with some service definitions? (yes/no): ")
        confirm = raw_input(msg)
        while 1:
            if confirm not in ('yes', 'no'):
                confirm = raw_input('Please enter either "yes" or "no": ')
                continue
            if confirm == 'yes':
                call_command("prepopulateservice", created_models)
            break


signals.post_syncdb.connect(prepopulate_service,
    sender=ordering.models, dispatch_uid = "ordering.management.prepopulateservice")

