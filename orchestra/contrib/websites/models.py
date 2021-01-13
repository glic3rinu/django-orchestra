import os
from collections import OrderedDict

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.core import validators
from orchestra.utils.functional import cached

from . import settings
from .directives import SiteDirective


class Website(models.Model):
    """ Models a web site, also known as virtual host """
    HTTP = 'http'
    HTTPS = 'https'
    HTTP_AND_HTTPS = 'http/https'
    HTTPS_ONLY = 'https-only'
    
    name = models.CharField(_("name"), max_length=128,
        validators=[validators.validate_name])
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
        related_name='websites')
    protocol = models.CharField(_("protocol"), max_length=16,
        choices=settings.WEBSITES_PROTOCOL_CHOICES,
        default=settings.WEBSITES_DEFAULT_PROTOCOL,
        help_text=_("Select the protocol(s) for this website<br>"
                    "<tt>HTTPS only</tt> performs a redirection from <tt>http</tt> to <tt>https</tt>."))
#    port = models.PositiveIntegerField(_("port"),
#            choices=settings.WEBSITES_PORT_CHOICES,
#            default=settings.WEBSITES_DEFAULT_PORT)
    domains = models.ManyToManyField(settings.WEBSITES_DOMAIN_MODEL, blank=True,
        related_name='websites', verbose_name=_("domains"))
    contents = models.ManyToManyField('webapps.WebApp', through='websites.Content')
    target_server = models.ForeignKey('orchestration.Server', verbose_name=_("Target Server"),
        related_name='websites')
    is_active = models.BooleanField(_("active"), default=True)
    comments = models.TextField(default="", blank=True)
    
    class Meta:
        unique_together = ('name', 'account')
    
    def __str__(self):
        return self.name
    
    @property
    def unique_name(self):
        context = self.get_settings_context()
        return settings.WEBSITES_UNIQUE_NAME_FORMAT % context
    
    @cached_property
    def active(self):
        return self.is_active and self.account.is_active
    
    def disable(self):
        self.is_active = False
        self.save(update_fields=('is_active',))
    
    def enable(self):
        self.is_active = False
        self.save(update_fields=('is_active',))
    
    def get_settings_context(self):
        """ format settings strings """
        return {
            'id': self.id,
            'pk': self.pk,
            'home': self.get_user().get_home(),
            'user': self.get_username(),
            'group': self.get_groupname(),
            'site_name': self.name,
            'protocol': self.protocol,
        }
    
    def get_protocol(self):
        if self.protocol in (self.HTTP, self.HTTP_AND_HTTPS):
            return self.HTTP
        return self.HTTPS
    
    @cached
    def get_directives(self):
        directives = OrderedDict()
        for opt in self.directives.all().order_by('name', 'value'):
            try:
                directives[opt.name].append(opt.value)
            except KeyError:
                directives[opt.name] = [opt.value]
        return directives
    
    def get_absolute_url(self):
        try:
            domain = self.domains.all()[0]
        except IndexError:
            return
        else:
            return '%s://%s' % (self.get_protocol(), domain)
    
    def get_user(self):
        return self.account.main_systemuser
    
    def get_username(self):
        return self.get_user().username
    
    def get_groupname(self):
        return self.get_username()
    
    def get_www_access_log_path(self):
        context = self.get_settings_context()
        context['unique_name'] = self.unique_name
        path = settings.WEBSITES_WEBSITE_WWW_ACCESS_LOG_PATH % context
        return os.path.normpath(path)
    
    def get_www_error_log_path(self):
        context = self.get_settings_context()
        context['unique_name'] = self.unique_name
        path = settings.WEBSITES_WEBSITE_WWW_ERROR_LOG_PATH % context
        return os.path.normpath(path)


class WebsiteDirective(models.Model):
    website = models.ForeignKey(Website, verbose_name=_("web site"),
        related_name='directives')
    name = models.CharField(_("name"), max_length=128, db_index=True,
        choices=SiteDirective.get_choices())
    value = models.CharField(_("value"), max_length=256, blank=True)
    
    def __str__(self):
        return self.name
    
    @cached_property
    def directive_class(self):
        return SiteDirective.get(self.name)
    
    @cached_property
    def directive_instance(self):
        """ Per request lived directive instance """
        return self.directive_class()
    
    def clean(self):
        self.directive_instance.validate(self)


class Content(models.Model):
    # related_name is content_set to differentiate between website.content -> webapp
    webapp = models.ForeignKey('webapps.WebApp', verbose_name=_("web application"))
    website = models.ForeignKey('websites.Website', verbose_name=_("web site"))
    path = models.CharField(_("path"), max_length=256, blank=True,
        validators=[validators.validate_url_path])
    
    class Meta:
        unique_together = ('website', 'path')
    
    def __str__(self):
        try:
            return self.website.name + self.path
        except Website.DoesNotExist:
            return self.path
    
    def clean_fields(self, *args, **kwargs):
        self.path = self.path.strip()
        return super(Content, self).clean_fields(*args, **kwargs)
    
    def clean(self):
        if not self.path:
            self.path = '/'
    
    def get_absolute_url(self):
        try:
            domain = self.website.domains.all()[0]
        except IndexError:
            return
        else:
            return '%s://%s%s' % (self.website.get_protocol(), domain, self.path)
