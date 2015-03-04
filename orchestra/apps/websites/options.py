from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from orchestra.utils.python import import_class

from . import settings


# TODO multiple and unique validation support in the formset
class SiteOption(object):
    unique = True
    
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.verbose_name = kwargs.pop('verbose_name', name)
        self.help_text = kwargs.pop('help_text', '')
        for k,v in kwargs.iteritems():
            setattr(self, k, v)
    
    def validate(self, website):
        if self.regex and not re.match(self.regex, website.value):
            raise ValidationError({
                'value': ValidationError(_("'%(value)s' does not match %(regex)s."),
                    params={
                        'value': website.value,
                        'regex': self.regex
                    }),
            })


directory_protection = SiteOption('directory_protection',
    verbose_name=_("Directory protection"),
    help_text=_("Space separated ..."),
    regex=r'^([\w/_]+)\s+(\".*\")\s+([\w/_\.]+)$',
)

redirect = SiteOption('redirect',
    verbose_name=_("Redirection"),
    help_text=_("<tt>&lt;website path&gt; &lt;destination URL&gt;</tt>"),
    regex=r'^[^ ]+\s[^ ]+$',
)

proxy = SiteOption('proxy',
    verbose_name=_("Proxy"),
    help_text=_("<tt>&lt;website path&gt; &lt;target URL&gt;</tt>"),
    regex=r'^[^ ]+\shttp[^ ]+(timeout=[0-9]{1,3}|retry=[0-9]|\s)*$',
)

ssl_ca = SiteOption('ssl_ca',
    verbose_name=_("SSL CA"),
    help_text=_("Filesystem path of the CA certificate file."),
    regex=r'^[^ ]+$'
)

ssl_cert = SiteOption('ssl_cert',
    verbose_name=_("SSL cert"),
    help_text=_("Filesystem path of the certificate file."),
    regex=r'^[^ ]+$',
)

ssl_key = SiteOption('ssl_key',
    verbose_name=_("SSL key"),
    help_text=_("Filesystem path of the key file."),
    regex=r'^[^ ]+$',
)

sec_rule_remove = SiteOption('sec_rule_remove',
    verbose_name=_("SecRuleRemoveById"),
    help_text=_("Space separated ModSecurity rule IDs."),
    regex=r'^[0-9\s]+$',
)

sec_engine = SiteOption('sec_engine',
    verbose_name=_("Modsecurity engine"),
    help_text=_("<tt>On</tt> or <tt>Off</tt>, defaults to On"),
    regex=r'^(On|Off)$',
)

user_group = SiteOption('user_group',
    verbose_name=_("SuexecUserGroup"),
    help_text=_("<tt>user [group]</tt>, username and optional groupname."),
    # TODO validate existing user/group
    regex=r'^[\w/_]+(\s[\w/_]+)*$',
)

error_document = SiteOption('error_document',
    verbose_name=_("ErrorDocumentRoot"),
    help_text=_("&lt;error code&gt; &lt;URL/path/message&gt;<br>"
          "<tt>&nbsp;500 http://foo.example.com/cgi-bin/tester</tt><br>"
          "<tt>&nbsp;404 /cgi-bin/bad_urls.pl</tt><br>"
          "<tt>&nbsp;401 /subscription_info.html</tt><br>"
          "<tt>&nbsp;403 \"Sorry can't allow you access today\"</tt>"),
    regex=r'[45]0[0-9]\s.*',
)


ssl = [
    ssl_ca,
    ssl_cert,
    ssl_key,
]

sec = [
    sec_rule_remove,
    sec_engine,
]

httpd = [
    directory_protection,
    redirect,
    proxy,
    user_group,
    error_document,
]


_enabled = None

def get_enabled():
    global _enabled
    if _enabled is None:
        from . import settings
        _enabled = {}
        for op in settings.WEBSITES_ENABLED_OPTIONS:
            op = import_class(op)
            _enabled[op.name] = op
    return _enabled
