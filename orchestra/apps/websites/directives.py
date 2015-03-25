import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from orchestra.plugins import Plugin
from orchestra.utils.functional import cached
from orchestra.utils.python import import_class

from . import settings


class SiteDirective(Plugin):
    HTTPD = 'HTTPD'
    SEC = 'ModSecurity'
    SSL = 'SSL'
    SAAS = 'SaaS'
    
    help_text = ""
    unique_name = False
    unique_value = False
    
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
    def get_plugin_choices(cls):
        """ Generates grouped choices ready to use in Field.choices """
        # generators can not be @cached
        yield (None, '-------')
        options = cls.get_option_groups()
        for option in options.pop(None, ()):
            yield (option.name, option.verbose_name)
        for group, options in options.iteritems():
            yield (group, [(op.name, op.verbose_name) for op in options])
    
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


class Proxy(SiteDirective):
    name = 'proxy'
    verbose_name = _("Proxy")
    help_text = _("<tt>&lt;website path&gt; &lt;target URL&gt;</tt>")
    regex = r'^[^ ]+\shttp[^ ]+(timeout=[0-9]{1,3}|retry=[0-9]|\s)*$'
    group = SiteDirective.HTTPD
    unique_value = True


class ErrorDocument(SiteDirective):
    name = 'error_document'
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
    name = 'ssl_ca'
    verbose_name = _("SSL CA")
    help_text = _("Filesystem path of the CA certificate file.")
    regex = r'^[^ ]+$'
    group = SiteDirective.SSL
    unique_name = True


class SSLCert(SiteDirective):
    name = 'ssl_cert'
    verbose_name = _("SSL cert")
    help_text = _("Filesystem path of the certificate file.")
    regex = r'^[^ ]+$'
    group = SiteDirective.SSL
    unique_name = True


class SSLKey(SiteDirective):
    name = 'ssl_key'
    verbose_name = _("SSL key")
    help_text = _("Filesystem path of the key file.")
    regex = r'^[^ ]+$'
    group = SiteDirective.SSL
    unique_name = True


class SecRuleRemove(SiteDirective):
    name = 'sec_rule_remove'
    verbose_name = _("SecRuleRemoveById")
    help_text = _("Space separated ModSecurity rule IDs.")
    regex = r'^[0-9\s]+$'
    group = SiteDirective.SEC


class SecEngine(SiteDirective):
    name = 'sec_engine'
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


class DokuWikiSaaS(SiteDirective):
    name = 'dokuwiki-saas'
    verbose_name = "DokuWiki SaaS"
    help_text = _("URL path for mounting wordpress multisite.")
    group = SiteDirective.SAAS
    regex = r'^/[^ ]*$'
    unique_value = True


class DrupalSaaS(SiteDirective):
    name = 'drupal-saas'
    verbose_name = "Drupdal SaaS"
    help_text = _("URL path for mounting wordpress multisite.")
    group = SiteDirective.SAAS
    regex = r'^/[^ ]*$'
    unique_value = True
