from django.conf import settings as djsettings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.core import services

from . import settings


class Account(models.Model):
    user = models.OneToOneField(djsettings.AUTH_USER_MODEL,
            verbose_name=_("user"), related_name='accounts')
    type = models.CharField(_("type"), choices=settings.ACCOUNTS_TYPES,
            max_length=32, default=settings.ACCOUNTS_DEFAULT_TYPE)
    language = models.CharField(_("language"), max_length=2,
            choices=settings.ACCOUNTS_LANGUAGES,
            default=settings.ACCOUNTS_DEFAULT_LANGUAGE)
    register_date = models.DateTimeField(_("register date"), auto_now_add=True)
    comments = models.TextField(_("comments"), max_length=256, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.name
    
    @cached_property
    def name(self):
        return self.user.username


services.register(Account, menu=False)
