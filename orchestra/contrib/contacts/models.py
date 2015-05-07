from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.core import validators
from orchestra.models.fields import MultiSelectField

from . import settings
from .validators import validate_phone


class ContactQuerySet(models.QuerySet):
    def filter(self, *args, **kwargs):
        usages = kwargs.pop('email_usages', [])
        qs = models.Q()
        for usage in usages:
            qs = qs | models.Q(email_usage__regex=r'.*(^|,)+%s($|,)+.*' % usage)
        return super(ContactQuerySet, self).filter(qs, *args, **kwargs)


class Contact(models.Model):
    BILLING = 'BILLING'
    EMAIL_USAGES = (
        ('SUPPORT', _("Support tickets")),
        ('ADMIN', _("Administrative")),
        (BILLING, _("Billing")),
        ('TECH', _("Technical")),
        ('ADDS', _("Announcements")),
        ('EMERGENCY', _("Emergency contact")),
    )
    
    objects = ContactQuerySet.as_manager()
    
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
        related_name='contacts', null=True)
    short_name = models.CharField(_("short name"), max_length=128)
    full_name = models.CharField(_("full name"), max_length=256, blank=True)
    email = models.EmailField()
    email_usage = MultiSelectField(_("email usage"), max_length=256, blank=True,
        choices=EMAIL_USAGES,
        default=settings.CONTACTS_DEFAULT_EMAIL_USAGES)
    phone = models.CharField(_("phone"), max_length=32, blank=True,
        validators=[validate_phone])
    phone2 = models.CharField(_("alternative phone"), max_length=32, blank=True,
        validators=[validate_phone])
    address = models.TextField(_("address"), blank=True)
    city = models.CharField(_("city"), max_length=128, blank=True)
    zipcode = models.CharField(_("zip code"), max_length=10, blank=True,
        validators=[
            RegexValidator(r'^[0-9,A-Z]{3,10}$',
                           _("Enter a valid zipcode."), 'invalid')
        ])
    country = models.CharField(_("country"), max_length=20, blank=True,
        choices=settings.CONTACTS_COUNTRIES,
        default=settings.CONTACTS_DEFAULT_COUNTRY)
    
    def __str__(self):
        return self.full_name or self.short_name
    
    def clean(self):
        self.short_name = self.short_name.strip()
        self.full_name = self.full_name.strip()
        self.phone = self.phone.strip()
        self.phone2 = self.phone2.strip()
        self.address = self.address.strip()
        self.city = self.city.strip()
        self.country = self.country.strip()
        errors = {}
        if self.address and not (self.city and self.zipcode and self.country):
            errors['__all__'] = _("City, zipcode and country must be provided when address is provided.")
        if self.zipcode and not self.country:
            errors['country'] = _("Country must be provided when zipcode is provided.")
        elif self.zipcode and self.country:
            try:
                validators.validate_zipcode(self.zipcode, self.country)
            except ValidationError as error:
                errors['zipcode'] = error
        if errors:
            raise ValidationError(errors)
