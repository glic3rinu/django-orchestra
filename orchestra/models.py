from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from orchestra.core import backends


# Collect all post save and post delete signals in order to trigger the execution
#   of service managamente operations

def collect(action, sender, *args, **kwargs):
    collection = []
    for backend in backends.ServiceBackend.get_backends():
        for model in backend.models:
            opts = sender._meta
            if model == '%s.%s' % (opts.app_label, opts.object_name):
                collection.append((backend, kwargs['instance'], action))
                break
    return collection


@receiver(post_save)
def post_save_collector(sender, *args, **kwargs):
    backends.PENDING_OPERATIONS += collect('save', sender, *args, **kwargs)


@receiver(post_delete)
def post_delete_collector(sender, *args, **kwargs):
    backends.PENDING_OPERATIONS += collect('delete', sender, *args, **kwargs)
