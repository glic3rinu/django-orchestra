from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

from .models import SaaS


# Admin bulk deletion doesn't call model.delete()
# So, signals are used instead of model method overriding

@receiver(pre_save, sender=SaaS, dispatch_uid='saas.service.save')
def type_save(sender, *args, **kwargs):
    instance = kwargs['instance']
    instance.service_instance.save()


@receiver(pre_delete, sender=SaaS, dispatch_uid='saas.service.delete')
def type_delete(sender, *args, **kwargs):
    instance = kwargs['instance']
    try:
        instance.service_instance.delete()
    except KeyError:
        pass
