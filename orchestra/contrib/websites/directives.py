import re
from collections import defaultdict

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from orchestra.plugins import Plugin
from orchestra.utils.functional import cached
from orchestra.utils.python import import_class

from . import settings
from .utils import normurlpath


class SiteDirective(Plugin):
    HTTPD = 'HTTPD'
    SEC = 'ModSecurity'
    SSL = 'SSL'
    SAAS = 'SaaS'
    
    help_text = ""
    unique_name = False
    unique_value = False
    unique_location = False
    
    @classmethod
    @cached
    def get_plugins(cls):
        plugins = []
        for cls in settings.WEBSITES_ENABLED_DIRECTIVES:
            plugins.append(import_class(cls))
        return plugins
    
    @classmethod
    @cached
    def get_option_groups(cls):
        groups = {}
        for opt in cls.get_plugins():
            try:
                groups[opt.group].append(opt)
            except KeyError:
                groups[opt.group] = [opt]
        return groups
    
    @classmethod
    def get_choices(cls):
        """ Generates grouped choices ready to use in Field.choices """
        # generators can not be @cached
        yield (None, '-------')
        options = cls.get_option_groups()
        for option in options.pop(None, ()):
            yield (option.name, option.verbose_name)
        for group, options in options.items():
            yield (group, [(op.name, op.verbose_name) for op in options])
    
    def validate_uniqueness(self, directive, values, locations):
        """ Validates uniqueness location, name and value """
        errors = defaultdict(list)
        # location uniqueness
        location = None
        if self.unique_location:
            location = normurlpath(directive['value'].split()[0])
        if location is not None and location in locations:
            errors['value'].append(ValidationError(
                "Location '%s' already in use by other content/directive." % location
            ))
        else:
            locations.add(location)
        
        # name uniqueness
        if self.unique_name and self.name in values:
            errors[None].append(ValidationError(
                _("Only one %s can be defined.") % self.get_verbose_name()
            ))
        
        # value uniqueness
        value = directive.get('value', None)
        if value is not None:
            if self.unique_value and value in values.get(self.name, []):
                errors['value'].append(ValidationError(
                    _("This value is already used by other %s.") % force_text(self.get_verbose_name())
                ))
        values[self.name].append(value)
        if errors:
            raise ValidationError(errors)
    
    def validate(self, website):
        if self.regex and not re.match(self.regex, website.value):
            raise ValidationError({
                'value': ValidationError(_("'%(value)s' does not match %(regex)s."),
                    params={
                        'value': website.value,
                        'regex': self.regex
                    }),
            })


class Redirect(SiteDirective):
    name = 'redirect'
    verbose_name = _("Redirection")
    help_text = _("<tt>&lt;website path&gt; &lt;destination URL&gt;</tt>")
    regex = r'^[^ ]+\s[^ ]+$'
    group = SiteDirective.HTTPD
    unique_value = True
    unique_location = True


class Proxy(SiteDirective):
    name = 'proxy'
    verbose_name = _("Proxy")
    help_text = _("<tt>&lt;website path&gt; &lt;target URL&gt;</tt>")
    regex = r'^[^ ]+\shttp[^ ]+(timeout=[0-9]{1,3}|retry=[0-9]|\s)*$'
    group = SiteDirective.HTTPD
    unique_value = True
    unique_location = True


class ErrorDocument(SiteDirective):
    name = 'error-document'
    verbose_name = _("ErrorDocumentRoot")
    help_text = _("&lt;error code&gt; &lt;URL/path/message&gt;<br>"
                  "<tt>&nbsp;500 http://foo.example.com/cgi-bin/tester</tt><br>"
                  "<tt>&nbsp;404 /cgi-bin/bad_urls.pl</tt><br>"
                  "<tt>&nbsp;401 /subscription_info.html</tt><br>"
                  "<tt>&nbsp;403 \"Sorry can't allow you access today\"</tt>")
    regex = r'[45]0[0-9]\s.*'
    group = SiteDirective.HTTPD
    unique_value = True


class SSLCA(SiteDirective):
    name = 'ssl-ca'
    verbose_name = _("SSL CA")
    help_text = _("Filesystem path of the CA certificate file.")
    regex = r'^[^ ]+$'
    group = SiteDirective.SSL
    unique_name = True


class SSLCert(SiteDirective):
    name = 'ssl-cert'
    verbose_name = _("SSL cert")
    help_text = _("Filesystem path of the certificate file.")
    regex = r'^[^ ]+$'
    group = SiteDirective.SSL
    unique_name = True


class SSLKey(SiteDirective):
    name = 'ssl-key'
    verbose_name = _("SSL key")
    help_text = _("Filesystem path of the key file.")
    regex = r'^[^ ]+$'
    group = SiteDirective.SSL
    unique_name = True


class SecRuleRemove(SiteDirective):
    name = 'sec-rule-remove'
    verbose_name = _("SecRuleRemoveById")
    help_text = _("Space separated ModSecurity rule IDs.")
    regex = r'^[0-9\s]+$'
    group = SiteDirective.SEC
    unique_location = True


class SecEngine(SiteDirective):
    name = 'sec-engine'
    verbose_name = _("SecRuleEngine Off")
    help_text = _("URL path with disabled modsecurity engine.")
    regex = r'^/[^ ]*$'
    group = SiteDirective.SEC
    unique_value = True


class WordPressSaaS(SiteDirective):
    name = 'wordpress-saas'
    verbose_name = "WordPress SaaS"
    help_text = _("URL path for mounting wordpress multisite.")
    group = SiteDirective.SAAS
    regex = r'^/[^ ]*$'
    unique_value = True
    unique_location = True


class DokuWikiSaaS(SiteDirective):
    name = 'dokuwiki-saas'
    verbose_name = "DokuWiki SaaS"
    help_text = _("URL path for mounting wordpress multisite.")
    group = SiteDirective.SAAS
    regex = r'^/[^ ]*$'
    unique_value = True
    unique_location = True


class DrupalSaaS(SiteDirective):
    name = 'drupal-saas'
    verbose_name = "Drupdal SaaS"
    help_text = _("URL path for mounting wordpress multisite.")
    group = SiteDirective.SAAS
    regex = r'^/[^ ]*$'
    unique_value = True
    unique_location = True
