from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from . import settings
from .models import Mailbox, Address


# Admin bulk deletion doesn't call model.delete()
# So, signals are used instead of model method overriding

@receiver(post_delete, sender=Mailbox, dispatch_uid='mailboxes.delete_forwards')
def delete_forwards(sender, *args, **kwargs):
    # Cleanup related addresses
    instance = kwargs['instance']
    for address in Address.objects.filter(forward__regex=r'.*(^|\s)+%s($|\s)+.*' % instance.name):
        forward = address.forward.split()
        forward.remove(instance.name)
        address.forward = ' '.join(forward)
        if not address.destination:
            address.delete()
        else:
            address.save()


@receiver(pre_save, sender=Mailbox, dispatch_uid='mailboxes.create_local_address')
def create_local_address(sender, *args, **kwargs):
    mbox = kwargs['instance']
    local_domain = settings.MAILBOXES_LOCAL_DOMAIN
    if not mbox.pk and local_domain:
        Domain = Address._meta.get_field_by_name('domain')[0].rel.to
        try:
            domain = Domain.objects.get(name=local_domain)
        except Domain.DoesNotExist:
            pass
        else:
            addr, created = Address.objects.get_or_create(
                name=mbox.name, domain=domain, account_id=domain.account_id)
            if created:
                if domain.account_id == mbox.account_id:
                    addr.mailboxes.add(mbox)
                else:
                    addr.forward = mbox.name
                    addr.save(update_fields=('forward',))
