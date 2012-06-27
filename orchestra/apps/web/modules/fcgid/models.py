from common.signals import collect_dependencies
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext as _
import settings
from web.models import VirtualHost


class FcgidDirective(models.Model):
    name = models.CharField(max_length=32)
    regex = models.CharField(max_length=256, help_text=_('Regex expresion that validates provided values'))
    description = models.CharField(max_length=256, help_text=_('Description of what the regex is suppose to do'))
    restricted = models.BooleanField(default=False, help_text=_('Only superuser can assign this kind of directive'))

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Fcgid(models.Model):
    virtualhost = models.OneToOneField('web.VirtualHost', related_name='fcgid')
    user = models.ForeignKey('system_users.SystemUser')
    group = models.ForeignKey('system_users.SystemGroup', default=settings.WEB_DEFAULT_FCGID_GROUP_PK)
    
    def __unicode__(self):
        return str(self.user)

    @property
    def directives(self):
        return VirtualHostFcgidDirective.objects.filter(virtualhost=self.virtualhost)


@receiver(collect_dependencies, sender=VirtualHost, dispatch_uid="fcgid.collect_fcgids")
def collect_virtual_hosts(sender, **kwargs):
    #TODO: it will be better to create a virtualField isn't it?
    vh = kwargs['object']
    # maybe the fcgid is not yet created
    #TODO: check when it can happends? admin.vhost add and ordering checking dependencies
    try: kwargs['collection'].append(vh.fcgid)
    except Fcgid.DoesNotExist: pass


class VirtualHostFcgidDirective(models.Model):
    virtualhost = models.ForeignKey('web.VirtualHost', related_name='fcgidirectives')
    directive = models.ForeignKey(FcgidDirective)
    value = models.CharField(max_length=16)

    class Meta:
        unique_together = ('virtualhost', 'directive')

    def __unicode__(self):
        return str(self.directive)

    @property
    def name(self):
        return self.directive.name

