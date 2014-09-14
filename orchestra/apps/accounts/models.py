from django.conf import settings as djsettings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.core import services
from orchestra.utils import send_email_template

from . import settings


class Account(models.Model):
    # Users depends on Accounts (think about what should happen when you delete an account)
    user = models.OneToOneField(djsettings.AUTH_USER_MODEL,
            verbose_name=_("user"), related_name='accounts', null=True)
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
    
    @property
    def name(self):
        return self.user.username if self.user_id else str(self.pk)
    
    @classmethod
    def get_main(cls):
        return cls.objects.get(pk=settings.ACCOUNTS_MAIN_PK)
    
    def send_email(self, template, context, contacts=[], attachments=[], html=None):
        contacts = self.contacts.filter(email_usages=contacts)
        email_to = contacts.values_list('email', flat=True)
        send_email_template(template, context, email_to, html=html,
                attachments=attachments)


services.register(Account, menu=False)
