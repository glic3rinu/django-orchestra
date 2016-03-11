import re
from collections import defaultdict
from functools import lru_cache

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from orchestra import plugins
from orchestra.utils.python import import_class

from . import settings
from .utils import normurlpath


class SiteDirective(plugins.Plugin, metaclass=plugins.PluginMount):
    HTTPD = 'HTTPD'
    SEC = 'ModSecurity'
    SSL = 'SSL'
    SAAS = 'SaaS'
    
    help_text = ""
    unique_name = False
    unique_value = False
    is_location = False
    
    @classmethod
    @lru_cache()
    def get_plugins(cls, all=False):
        if all:
            plugins = super().get_plugins()
        else:
            plugins = []
            for cls in settings.WEBSITES_ENABLED_DIRECTIVES:
                plugins.append(import_class(cls))
        return plugins
    
    @classmethod
    @lru_cache()
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
        # generators can not be @lru_cache()
        yield (None, '-------')
        options = cls.get_option_groups()
        for option in options.pop(None, ()):
            yield (option.name, option.verbose_name)
        for group, options in options.items():
            yield (group, [(op.name, op.verbose_name) for op in options])
    
    def validate_uniqueness(self, directive, values, locations):
        """ Validates uniqueness location, name and value """
        errors = defaultdict(list)
        value = directive.get('value', None)
        # location uniqueness
        location = None
        if self.is_location and value is not None:
            if not value and self.is_location:
                value = '/'
            location = normurlpath(value.split()[0])
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
        if value is not None:
            if self.unique_value and value in values.get(self.name, []):
                errors['value'].append(ValidationError(
                    _("This value is already used by other %s.") % force_text(self.get_verbose_name())
                ))
        values[self.name].append(value)
        if errors:
            raise ValidationError(errors)
    
    def validate(self, directive):
        directive.value = directive.value.strip()
        if not directive.value and self.is_location:
            directive.value = '/'
        if self.regex and not re.match(self.regex, directive.value):
            raise ValidationError({
                'value': ValidationError(_("'%(value)s' does not match %(regex)s."),
                    params={
                        'value': directive.value,
                        'regex': self.regex
                    }),
            })


class Redirect(SiteDirective):
    name = 'redirect'
    verbose_name = _("Redirection")
    help_text = _("<tt>&lt;website path&gt; &lt;destination URL&gt;</tt>")
    regex = r'^[^ ]*\s[^ ]+$'
    group = SiteDirective.HTTPD
    unique_value = True
    is_location = True
    
    def validate(self, directive):
        """ inserts default url-path if not provided """
        values = directive.value.strip().split()
        if len(values) == 1:
            values.insert(0, '/')
        directive.value = ' '.join(values)
        super(Redirect, self).validate(directive)


class Proxy(Redirect):
    name = 'proxy'
    verbose_name = _("Proxy")
    help_text = _("<tt>&lt;website path&gt; &lt;target URL&gt;</tt>")
    regex = r'^[^ ]+\shttp[^ ]+(timeout=[0-9]{1,3}|retry=[0-9]|\s)*$'


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
    regex = r'^/[^ ]+$'
    group = SiteDirective.SSL
    unique_name = True


class SSLCert(SSLCA):
    name = 'ssl-cert'
    verbose_name = _("SSL cert")
    help_text = _("Filesystem path of the certificate file.")


class SSLKey(SSLCA):
    name = 'ssl-key'
    verbose_name = _("SSL key")
    help_text = _("Filesystem path of the key file.")


class SecRuleRemove(SiteDirective):
    name = 'sec-rule-remove'
    verbose_name = _("SecRuleRemoveById")
    help_text = _("Space separated ModSecurity rule IDs.")
    regex = r'^[0-9\s]+$'
    group = SiteDirective.SEC
    is_location = True


class SecEngine(SecRuleRemove):
    name = 'sec-engine'
    verbose_name = _("SecRuleEngine Off")
    help_text = _("URL-path with disabled modsecurity engine.")
    regex = r'^/[^ ]*$'
    is_location = False


class WordPressSaaS(SiteDirective):
    name = 'wordpress-saas'
    verbose_name = "WordPress SaaS"
    help_text = _("URL-path for mounting WordPress multisite.")
    group = SiteDirective.SAAS
    regex = r'^/[^ ]*$'
    unique_value = True
    is_location = True


class DokuWikiSaaS(WordPressSaaS):
    name = 'dokuwiki-saas'
    verbose_name = "DokuWiki SaaS"
    help_text = _("URL-path for mounting DokuWiki multisite.")


class DrupalSaaS(WordPressSaaS):
    name = 'drupal-saas'
    verbose_name = "Drupdal SaaS"
    help_text = _("URL-path for mounting Drupal multisite.")


class MoodleSaaS(WordPressSaaS):
    name = 'moodle-saas'
    verbose_name = "Moodle SaaS"
    help_text = _("URL-path for mounting Moodle multisite.")
