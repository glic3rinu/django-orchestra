from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from . import collector, settings


# Collect all post save and post delete signals in order to trigger the execution
#   of service managamente operations


@receiver(post_save)
def post_save_collector(sender, *args, **kwargs):
   collector.collect('save', sender, *args, **kwargs)


@receiver(post_delete)
def post_delete_collector(sender, *args, **kwargs):
    collector.collect('delete', sender, *args, **kwargs)


class Server(models.Model):
    """ Machine runing daemons (services) """
    name = models.CharField(_("name"), max_length=256, unique=True)
    # TODO unique address with blank=True (nullablecharfield)
    address = models.CharField(_("address"), max_length=256, blank=True,
            help_text=_("IP address or domain name"))
    description = models.TextField(_("description"), blank=True)
    os = models.CharField(_("operative system"), max_length=32,
            choices=settings.ORCHESTRATION_OS_CHOICES,
            default=settings.ORCHESTRATION_DEFAULT_OS)
    
    def __unicode__(self):
        return self.name


class ScriptLog(models.Model):
    pass
