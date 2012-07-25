from common.signals import collect_related_objects_to_delete, service_created, service_updated
from django.conf import settings as django_settings
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
import re
import settings


class Name(models.Model):
    """ Tracks and manage the registration of domain names. 
        Also useful for other models that needs domains: i.e. web.VirtualHost """
    name = models.CharField(max_length=255)
    extension = models.CharField(max_length=8, choices=settings.DNS_EXTENSIONS, default=settings.DNS_DEFAULT_EXTENSION)
    register_provider = models.CharField(max_length=255, blank=True,
        choices=settings.DNS_REGISTER_PROVIDER_CHOICES, default=settings.DNS_DEFAULT_REGISTER_PROVIDER)
    # TODO: this will be needed when support for domain registration is provided
#    administrative_contact = models.ForeignKey('contacts.BaseContact', related_name='administrative_name_set', null=True, blank=True)
#    technical_contact = models.ForeignKey('contacts.BaseContact', related_name='technical_name_set', null=True, blank=True) 
#    billing_contact = models.ForeignKey('contacts.BaseContact', related_name='billing_name_set', null=True, blank=True)

    # TODO: create a virtual relation with zone in order to deprecate the signal approach of auto deletions.

    class Meta:
        unique_together = ('name', 'extension')
    
    def __unicode__(self):
        return "%s.%s" % (self.name, self.extension)

    def save(self, *args, **kwargs):
        if self.pk:
            old = Name.objects.get(pk=self.pk)
            if old.name != self.name or old.extension != self.extension:
                #TODO: raise form error
                raise AttributeError('Change name or extension are not allowed')
        super(Name, self).save(*args, **kwargs)

    def get_zone(self):
        """ return a related Zone if exists, else return None """
    
        entair_origin = "%s.%s" % (self.name, self.extension)
        position = entair_origin.rindex('.')
        stop = False
        
        while not stop:
            try: position = entair_origin.rindex('.', 0, position)
            except ValueError: 
                origin = entair_origin
                record = ''
                stop = True
            else:
                origin = entair_origin[position+1:]
                record = entair_origin[:position]
            
            zone = Zone.objects.filter(origin=origin, record__name=record).distinct()
            if len(zone) > 0: return zone[0]     
        
        return None

    def get_record(self):
        zone = self.get_zone()
        domain_name = "%s.%s" % (self.name, self.extension)
        record_name = re.sub("\.%s$" % zone.origin.replace('.', '\.'), '', domain_name)
        return Record.objects.get(name=record_name, zone=zone)

    @classmethod
    def get_extension(cls, domain):
        s_cmp = lambda n, k: k[0].count('.') - n[0].count('.');
        for ext, ext_ in sorted(settings.DNS_EXTENSIONS, cmp=s_cmp):
            if re.match(".*\.%s$" % ext.replace('.', '\.'), domain):
                return ext
        return AttributeError('extention not found')

    @classmethod
    def split(cls, domain):
        ext = cls.get_extension(domain)
        name = re.sub("\.%s$" % ext.replace('.', '\.'), '', domain)
        return name, ext


class NameServer(models.Model):
    """ Used for domain registration process """
    name = models.ForeignKey(Name)
    hostname = models.CharField(max_length=255)
    ip = models.IPAddressField(null=True, blank=True)
    
    def __unicode__(self):
        return str(self.hostname)   


if 'dns.zones' in django_settings.INSTALLED_APPS:
    from dns.zones.models import Zone

    @receiver(service_created, sender=Zone, dispatch_uid="name.create_names")
    @receiver(service_updated, sender=Zone, dispatch_uid="name.update_names")
    def create_names(sender, **kwargs):
        # 1. Deletes on Zone doesn't affect names
        # 2. Creates and Updates on Zone only produces creates on Name
        zone = kwargs['instance']
        request = kwargs['request']
        for domain_name in zone.get_names():
            name, extension = Name.split(domain_name)
            try: Name.objects.get(name=name, extension=extension)
            except Name.DoesNotExist:
                new_name = Name(name=name, extension=extension, register_provider='')
                new_name.save()
                service_created.send(sender=Name, request=request, instance=new_name, origin=zone)

    @receiver(collect_related_objects_to_delete, sender=Name, dispatch_uid="zone.collect_zones")
    def collect_zones(sender, **kwargs):
        """ For a given Name colect their related Zones for future deletion """
        name = kwargs['object']
        zone = name.get_zone()
        if zone:
            if zone.origin == "%s.%s" % (name.name, name.extension):
                if not Name in kwargs['related_collection'].keys():
                    kwargs['related_collection'][Name] = []
                kwargs['related_collection'][Name].append(zone)
            else:
                if not Record in kwargs['related_collection'].keys():
                    kwargs['related_collection'][Record] = []
                kwargs['related_collection'][Record].append(name.get_record())

