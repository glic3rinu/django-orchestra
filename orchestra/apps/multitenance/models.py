from django.db import models
from django.utils.translation import ugettext_lazy as _


class Application(models.Model):
    name = models.TextField(_("name"), max_length=256)
    description = models.TextField(_("description"))


class Tenant(models.Model):
    application = models.OneToOneField(Application, verbose_name=_("Application"))
    data = models.TextField(blank=True)
