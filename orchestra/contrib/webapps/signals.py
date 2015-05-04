from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

from .models import WebApp


# Admin bulk deletion doesn't call model.delete()
# So, signals are used instead of model method overriding

@receiver(pre_save, sender=WebApp, dispatch_uid='webapps.type.save')
def type_save(sender, *args, **kwargs):
    instance = kwargs['instance']
    instance.type_instance.save()


@receiver(pre_delete, sender=WebApp, dispatch_uid='webapps.type.delete')
def type_delete(sender, *args, **kwargs):
    instance = kwargs['instance']
    try:
        instance.type_instance.delete()
    except KeyError:
        pass
