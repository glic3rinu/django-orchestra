import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.core import validators, services
from orchestra.utils.functional import cached

from . import settings
from .directives import SiteDirective


class Website(models.Model):
    """ Models a web site, also known as virtual host """
    name = models.CharField(_("name"), max_length=128,
            validators=[validators.validate_name])
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
            related_name='websites')
    # TODO protocol
    port = models.PositiveIntegerField(_("port"),
            choices=settings.WEBSITES_PORT_CHOICES,
            default=settings.WEBSITES_DEFAULT_PORT)
    domains = models.ManyToManyField(settings.WEBSITES_DOMAIN_MODEL,
            related_name='websites', verbose_name=_("domains"))
    contents = models.ManyToManyField('webapps.WebApp', through='websites.Content')
    is_active = models.BooleanField(_("active"), default=True)
    
    class Meta:
        unique_together = ('name', 'account')
    
    def __unicode__(self):
        return self.name
    
    @property
    def unique_name(self):
        return settings.WEBSITES_UNIQUE_NAME_FORMAT % {
            'id': self.id,
            'pk': self.pk,
            'account': self.account.username,
            'port': self.port,
            'name': self.name,
        }
    
    @property
    def protocol(self):
        if self.port == 80:
            return 'http'
        if self.port == 443:
            return 'https'
        raise TypeError('No protocol for port "%s"' % self.port)
    
    @cached
    def get_directives(self):
        return {
            opt.name: opt.value for opt in self.directives.all()
        }
    
    def get_absolute_url(self):
        domain = self.domains.first()
        if domain:
            return '%s://%s' % (self.protocol, domain)
    
    def get_www_log_context(self):
        return {
            'home': self.account.main_systemuser.get_home(),
            'account': self.account.username,
            'name': self.name,
            'unique_name': self.unique_name
        }
    
    def get_www_access_log_path(self):
        context = self.get_www_log_context()
        path = settings.WEBSITES_WEBSITE_WWW_ACCESS_LOG_PATH % context
        return path.replace('//', '/')
    
    def get_www_error_log_path(self):
        context = self.get_www_log_context()
        path = settings.WEBSITES_WEBSITE_WWW_ERROR_LOG_PATH % context
        return path.replace('//', '/')


class Directive(models.Model):
    website = models.ForeignKey(Website, verbose_name=_("web site"),
            related_name='directives')
    name = models.CharField(_("name"), max_length=128,
            choices=SiteDirective.get_plugin_choices())
    value = models.CharField(_("value"), max_length=256)
    
    def __unicode__(self):
        return self.name
    
    @cached_property
    def directive_class(self):
        return SiteDirective.get_plugin(self.name)
    
    @cached_property
    def directive_instance(self):
        """ Per request lived directive instance """
        return self.directive_class()
    
    def clean(self):
        self.directive_instance.validate(self)


class Content(models.Model):
    webapp = models.ForeignKey('webapps.WebApp', verbose_name=_("web application"),
            related_name='contents')
    website = models.ForeignKey('websites.Website', verbose_name=_("web site"),
            related_name='contents')
    path = models.CharField(_("path"), max_length=256, blank=True,
            validators=[validators.validate_url_path])
    
    class Meta:
        unique_together = ('website', 'path')
    
    def __unicode__(self):
        try:
            return self.website.name + self.path
        except Website.DoesNotExist:
            return self.path
    
    def clean(self):
        if not self.path.startswith('/'):
            self.path = '/' + self.path
    
    def get_absolute_url(self):
        domain = self.website.domains.first()
        if domain:
            return '%s://%s%s' % (self.website.protocol, domain, self.path)


services.register(Website)
