from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Resource


@receiver(post_save, sender=Resource, dispatch_uid="resources.sync_periodic_task")
def sync_periodic_task(sender, **kwargs):
    """ useing signals instead of Model.delete() override beucause of admin bulk delete() """
    instance = kwargs['instance']
    instance.sync_periodic_task()


@receiver(post_delete, sender=Resource, dispatch_uid="resources.delete_periodic_task")
def delete_periodic_task(sender, **kwargs):
    """ useing signals instead of Model.delete() override beucause of admin bulk delete() """
    instance = kwargs['instance']
    instance.sync_periodic_task(delete=True)
