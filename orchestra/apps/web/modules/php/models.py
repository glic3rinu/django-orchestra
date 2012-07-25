from django.db import models
from django.utils.translation import ugettext as _
import settings


class PHP(models.Model):
    virtualhost = models.OneToOneField('web.VirtualHost', related_name='php')
    version = models.CharField(max_length=5, choices=settings.WEB_PHPVERSION_CHOICES, default=settings.WEB_PHPVERSION_DEFAULT)

    @property
    def directives(self):
        return VirtualHostPHPDirective.objects.filter(virtualhost=self.virtualhost)


class PHPDirective(models.Model):
    """ Custom php.ini directives """
    name = models.CharField(max_length=32)
    regex = models.CharField(max_length=256, help_text=_('regex expresion that validates provided values'))
    description = models.CharField(max_length=256, help_text=_('Description of what the regex is suppose to do'))
    restricted = models.BooleanField(default=False, help_text=_('Only superuser can assign this kind of directive'))

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class VirtualHostPHPDirective(models.Model):
    virtualhost = models.ForeignKey('web.VirtualHost', related_name='phpdirectives')
    directive = models.ForeignKey(PHPDirective)
    value = models.CharField(max_length=16)

    class Meta:
        unique_together = ('virtualhost', 'directive')

    def __unicode__(self):
        return str(self.directive)

    @property
    def name(self):
        return self.directive.name
