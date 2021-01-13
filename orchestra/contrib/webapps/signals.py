from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

from .models import WebApp

# Admin bulk deletion doesn't call model.delete()
# So, signals are used instead of model method overriding

@receiver(pre_save, sender=WebApp, dispatch_uid='webapps.type.save')
def type_save(sender, *args, **kwargs):
    instance = kwargs['instance']
    # Since a webapp might need to cleanup its old config files, the data
    # from the OLD VERSION of the webapp is needed.
    if instance.pk:
        instance._old_self = type(instance).objects.get(id=instance.pk)
    instance.type_instance.save()

@receiver(pre_delete, sender=WebApp, dispatch_uid='webapps.type.delete')
def type_delete(sender, *args, **kwargs):
    instance = kwargs['instance']
    instance._old_self = type(instance).objects.get(id=instance.pk)
    try:
        instance.type_instance.delete()
    except KeyError:
        pass
