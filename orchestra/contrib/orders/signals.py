from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from orchestra.core import services

from . import helpers, settings
from .models import Order


# TODO perhas use cache = caches.get_request_cache() to cache an account delete and don't processes get_related_objects() if the case
# FIXME https://code.djangoproject.com/ticket/24576
# TODO build a cache hash table {model: related, model: None}
@receiver(post_delete, dispatch_uid="orders.cancel_orders")
def cancel_orders(sender, **kwargs):
    if sender._meta.app_label not in settings.ORDERS_EXCLUDED_APPS:
        instance = kwargs['instance']
        # Account delete will delete all related orders, no need to maintain order consistency
        if isinstance(instance, Order.account.field.rel.to):
            return
        if type(instance) in services:
            for order in Order.objects.by_object(instance).active():
                order.cancel()
        elif not hasattr(instance, 'account'):
            # FIXME Indeterminate behaviour
            related = helpers.get_related_object(instance)
            if related and related != instance:
                type(related).objects.get(pk=related.pk)


@receiver(post_save, dispatch_uid="orders.update_orders")
def update_orders(sender, **kwargs):
    if sender._meta.app_label not in settings.ORDERS_EXCLUDED_APPS:
        instance = kwargs['instance']
        if type(instance) in services:
            Order.objects.update_by_instance(instance)
        elif not hasattr(instance, 'account'):
            related = helpers.get_related_object(instance)
            if related and related != instance:
                Order.objects.update_by_instance(related)
