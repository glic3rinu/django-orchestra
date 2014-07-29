from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.core import accounts
from orchestra.models.fields import MultiSelectField

from . import settings


class Contact(models.Model):
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
            related_name='contacts', null=True)
    short_name = models.CharField(_("short name"), max_length=128)
    full_name = models.CharField(_("full name"), max_length=256, blank=True)
    email = models.EmailField()
    email_usage = MultiSelectField(_("email usage"), max_length=256, blank=True,
            choices=settings.CONTACTS_EMAIL_USAGES,
            default=settings.CONTACTS_DEFAULT_EMAIL_USAGES)
    phone = models.CharField(_("phone"), max_length=32, blank=True)
    phone2 = models.CharField(_("alternative phone"), max_length=32, blank=True)
    address = models.TextField(_("address"), blank=True)
    city = models.CharField(_("city"), max_length=128, blank=True,
            default=settings.CONTACTS_DEFAULT_CITY)
    zipcode = models.PositiveIntegerField(_("zip code"), null=True, blank=True)
    country = models.CharField(_("country"), max_length=20, blank=True,
            default=settings.CONTACTS_DEFAULT_COUNTRY)
    
    def __unicode__(self):
        return self.short_name


class InvoiceContact(models.Model):
    account = models.OneToOneField('accounts.Account', verbose_name=_("account"),
            related_name='invoicecontact')
    name = models.CharField(_("name"), max_length=256)
    address = models.TextField(_("address"))
    city = models.CharField(_("city"), max_length=128,
            default=settings.CONTACTS_DEFAULT_CITY)
    zipcode = models.PositiveIntegerField(_("zip code"))
    country = models.CharField(_("country"), max_length=20,
            default=settings.CONTACTS_DEFAULT_COUNTRY)
    vat = models.CharField(_("VAT number"), max_length=64)


accounts.register(Contact)
