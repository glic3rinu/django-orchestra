from django.apps import apps
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from . import settings
from .models import List


DOMAIN_MODEL = apps.get_model(settings.LISTS_DOMAIN_MODEL)


@receiver(pre_delete, sender=DOMAIN_MODEL, dispatch_uid="lists.clean_address_name")
def clean_address_name(sender, **kwargs):
    domain = kwargs['instance']
    for list in List.objects.filter(address_domain_id=domain.pk):
        list.address_name = ''
        list.address_domain_id = None
        list.save(update_fields=('address_name', 'address_domain_id'))

