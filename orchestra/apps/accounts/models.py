from django.conf import settings as django_settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import settings


class Account(models.Model):
    user = models.OneToOneField(django_settings.AUTH_USER_MODEL, related_name='accounts')
    type = models.CharField(_("type"), max_length=32, choices=settings.ACCOUNTS_TYPES,
            default=settings.ACCOUNTS_DEFAULT_TYPE)
    language = models.CharField(_("language"), max_length=2,
            choices=settings.ACCOUNTS_LANGUAGES,
            default=settings.ACCOUNTS_DEFAULT_LANGUAGE)
    register_date = models.DateTimeField(_("register date"), auto_now_add=True)
    comments = models.TextField(_("comments"), max_length=256, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.name
    
    @property
    def name(self):
        self._cached_name = getattr(self, '_cached_name', self.user.username)
        return self._cached_name
