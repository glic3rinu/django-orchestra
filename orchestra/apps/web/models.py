from common.signals import collect_related_objects_to_delete
from django.conf import settings as project_settings
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.translation import ugettext as _
import settings


class VirtualHost(models.Model):
    """ Apache-like virtualhost """ 
    ip = models.GenericIPAddressField(choices=settings.WEB_VIRTUALHOST_IP_CHOICES,
        default=settings.WEB_VIRTUALHOST_IP_DEFAULT)
    port = models.PositiveIntegerField(choices=settings.WEB_VIRTUALHOST_PORT_CHOICES,
        default=settings.WEB_VIRTUALHOST_PORT_DEFAULT)
    domains = models.ManyToManyField('names.Name')
    DocumentRoot = models.CharField(max_length=128, blank=True)
    unique_ident = models.CharField(max_length=128, unique=True, blank=True)
    redirect = models.CharField(max_length=64, blank=True)
    custom_directives = models.TextField(blank=True, help_text=_("custom fields in template format that will be added on the vHost definition"))

    delete_out_of_m2m = (domains,)

    def __unicode__(self):
        return "%s" % (self.ServerName)

    @property
    def ServerName(self):
        try: return self.domains.all()[0]
        except IndexError: return []
        
    @property
    def ServerAlias(self):
        alias = ""
        for domain in self.domains.all()[1:]:
            alias += "%s, " % (domain)
        return alias[:-2]
    
    def rendered_custom_directives(self):
        from django.template import Context, Template
        t = Template(self.custom_directives)
        c = Context({"object": self})
        return t.render(c)


# Register to M2M domains signal in order to create the vhost.ident 
# coz m2m is saved before the main object
@receiver(m2m_changed, sender=VirtualHost.domains.through, dispatch_uid="web.create_ident")
def create_ident(sender, **kwargs):
    if kwargs['action'] is "post_add":
        instance = kwargs['instance']
        if not instance.unique_ident:
            instance.unique_ident = "%s__%s" % (instance.pk, instance.ServerName)
            instance.save()


if 'web.fcgid' in project_settings.INSTALLED_APPS:
    from web.modules.fcgid.models import Fcgid
    @receiver(collect_related_objects_to_delete, sender=Fcgid, dispatch_uid="web.collect_virtual_hosts")
    def collect_virtual_hosts(sender, **kwargs):
        fcgid = kwargs['object']
        try: kwargs['related_collection'][VirtualHost].append(fcgid.virtual_host)
        except KeyError: kwargs['related_collection'][VirtualHost] = [fcgid.virtualhost]

