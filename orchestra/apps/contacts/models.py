from common.signals import service_deleted
from common.utils.models import generate_chainer_manager
from contacts import settings
from datetime import datetime
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.dispatch import receiver, Signal
from django.utils.translation import ugettext_lazy as _
from service_support.models import register as service_register
import re


class BaseContact(models.Model):
    name = models.CharField(max_length=128, unique=True)
    surname = models.CharField(max_length=30, blank=True)
    second_surname = models.CharField(max_length=30, blank=True)
    national_id = models.CharField(max_length=16)
    address = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=20, default='Barcelona', blank=True)
    zipcode = models.PositiveIntegerField(blank=True, null=True)
    province = models.CharField(max_length=20, default='Barcelona', blank=True)
    country = models.CharField(max_length=20, default='Spain')    

    def __unicode__(self):
        return str(self.subclass_instance)
        
    @property
    def subclass_instance(self):
        try: contact = self.contact
        except Contact.DoesNotExist:
            try: billing_contact = self.billingcontact
            except BillingContact.DoesNotExist: 
                try: technical_contact = self.administrativecontact
                except AdministrativeContact.DoesNotExist:
                    technical_contact = self.technicalcontact
                    return technical_contact
                else: return technical_contact
            else: return billing_contact
        else: return contact


class BillingContact(BaseContact):
    contact = models.OneToOneField('contacts.Contact')

    def __unicode__(self):
        return "%s (Bill:%s)" % (self.contact.name, self.name)


class AdministrativeContact(BaseContact):
    contact = models.OneToOneField('contacts.Contact')

    def __unicode__(self):
        return "%s (Admin:%s)" % (self.contact.name, self.name)


class TechnicalContact(BaseContact):
    contact = models.OneToOneField('contacts.Contact')

    def __unicode__(self):
        return "%s (Tech:%s)" % (self.contact.name, self.name)


class Contact(BaseContact):
    """ 
        All related people or organizations: admins, customers, staff, 
        members and your organization itself.
    """
    type = models.CharField(max_length=1, choices=settings.CONTACTS_TYPE_CHOICES, default=settings.CONTACTS_DEFAULT_TYPE)
    fax = models.PositiveIntegerField(blank=True, null=True)
    comments = models.TextField(max_length=255, blank=True)
    language = models.CharField(max_length=2, choices=settings.CONTACTS_LANGUAGE_CHOICES, default=settings.CONTACTS_DEFAULT_LANGUAGE)
    is_staff = models.BooleanField(default=False, help_text=_("member of the staff"))
    register_date = models.DateTimeField(auto_now_add=True)
    # cancel_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name
    
    @property
    def fullname(self):
        return re.sub(r"\s*$", '', ' '.join([self.name, self.surname, self.second_surname]))
    
    @property
    def phone(self):
        phone = Phone.objects.filter(contact=self, preferent=True)
        if not phone: 
            phone = Phone.objects.filter(contact=self, preferent=False)
            if not phone: return ''
        return phone[0]
    
    @property
    def email(self):
        email = Email.objects.filter(contact=self, preferent=True)
        if not email: 
            email = Email.objects.filter(contact=self, preferent=False)
            if not email: return ''
        return email[0].address
       
    @classmethod
    def get_myself(cls):
        """ Return self organization/person """
        return cls.objects.get(pk=settings.CONTACTS_CONTACT_SELF_PK)

    @property
    def billing(self):
        try: bc = BillingContact.objects.get(contact=self)
        except BillingContact.DoesNotExist: return self
        else: return bc

    @property
    def administrative(self):
        try: ac = AdministrativeContact.objects.get(contact=self)
        except AdministrativeContact.DoesNotExist: return self
        else: return ac    

    @property
    def technical(self):
        try: tc = TechnicalContact.objects.get(contact=self)
        except TechnicalContact.DoesNotExist: return self
        else: return tc    


class Phone(models.Model):
    number = models.PositiveIntegerField()
    contact = models.ForeignKey(Contact)
    preferent = models.BooleanField(default=False)
    #TODO: only one preferent per contact.

    def __unicode__(self):
        return str(self.number)

class Email(models.Model):
    address = models.EmailField()
    contact = models.ForeignKey(Contact)
    preferent = models.BooleanField(default=False)
    #TODO: only one preferent per contact
            
    def __unicode__(self):
        return str(self.address)


class ContractQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(cancel_date__isnull=True)

    def active_during(self, ini, end):
        return self.filter(Q(register_date__lt=end) & 
                           Q(Q(cancelationdate__cancelation_date__isnull=True)|Q(cancelationdate__cancelation_date__gt=ini)))

    def filter_active_by_contact(self, contact):
        return self.active().filter(contact=contact)

    def get_by_object(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return self.get(object_id=obj.pk, content_type=ct)
    
    def get_active_by_object(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return self.active().filter(object_id=obj.pk, content_type=ct)
    
    def filter_active_by_object(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return self.active().filter(object_id=obj.pk, content_type=ct)

    def filter_active_during_with_contact_model_pks(self, contact, model, pks, ini, end):
        ct = ContentType.objects.get_for_model(model)
        return self.filter(content_type=ct, contact=contact, object_id__in=pks).active_during(ini, end)

    def filter_active_by_contact_and_model(self, contact, model):
        ct = ContentType.objects.get_for_model(model)
        return self.active().filter(content_type=ct, contact=contact)


class Contract(models.Model):
    """ Services contracted by Contact """
    contact = models.ForeignKey(Contact, related_name='contract_contact')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(null=True)
    description = models.CharField(max_length=256, blank=True)
    register_date = models.DateTimeField(auto_now_add=True)
    cancel_date = models.DateTimeField(null=True, blank=True)
    content_object = generic.GenericForeignKey()

    objects = generate_chainer_manager(ContractQuerySet)

    class Meta:
        ordering = ['-register_date']
        unique_together = ('content_type', 'object_id') 
    
    def __unicode__(self):
        return "<%s: %s>" %  (self.content_type.model_class().__name__, self.description) 

    def cancel(self):
        self.cancel_date=datetime.now()
        self.save()
      
    @property
    def is_canceled(self):
        return True if self.cancel_date and self.cancel_date < datetime.now() else False

    @classmethod
    def create(cls, contact, obj):
        #TODO: deprecate in favour of Contract.objects.create(content_object=, contact=)
        ct = ContentType.objects.get_for_model(obj)
        contract = Contract(contact=contact, content_type=ct, object_id=obj.pk, description=str(obj))
        contract.save()
        return contract

    @property
    def content_object_is_deletable(self):
        return False if str(self.content_type) in settings.CONTACTS_DO_NOT_DELETE_ON_CANCEL else True
        
    @classmethod
    def content_objects_are_deletable(cls, content_class):
        return False if content_class.__name__.lower() in settings.CONTACTS_DO_NOT_DELETE_ON_CANCEL else True


contract_updated = Signal(providing_args=["instance"])


@receiver(service_deleted, dispatch_uid="contacts.service_deleted_cancel_contract")    
def service_delete_cancel_contract(sender, **kwargs):
    instance = kwargs['instance']
    if instance.__class__ in service_register.models:
        contract = instance.contract
        contract.cancel()
        contract_updated.send(sender=Contract, instance=contract)

