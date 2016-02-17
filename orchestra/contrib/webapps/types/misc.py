import os

from django import forms
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from ..options import AppOption

from . import AppType
from .php import PHPApp, PHPAppForm, PHPAppSerializer


class StaticApp(AppType):
    name = 'static'
    verbose_name = "Static"
    help_text = _("This creates a Static application under ~/webapps/&lt;app_name&gt;<br>"
                  "Apache2 will be used to serve static content and execute CGI files.")
    icon = 'orchestra/icons/apps/Static.png'
    option_groups = (AppOption.FILESYSTEM,)
    
    def get_directive(self):
        return ('static', self.instance.get_path())


class WebalizerApp(AppType):
    name = 'webalizer'
    verbose_name = "Webalizer"
    directive = ('static', '%(app_path)s%(site_name)s')
    help_text = _(
        "This creates a Webalizer application under ~/webapps/&lt;app_name&gt;-&lt;site_name&gt;<br>"
        "Statistics will be collected once this app is mounted into one or more Websites.")
    icon = 'orchestra/icons/apps/Stats.png'
    option_groups = ()
    
    def get_directive(self):
        webalizer_path = os.path.join(self.instance.get_path(), '%(site_name)s')
        webalizer_path = os.path.normpath(webalizer_path)
        return ('static', webalizer_path)


class SymbolicLinkForm(PHPAppForm):
    path = forms.CharField(label=_("Path"), widget=forms.TextInput(attrs={'size':'100'}),
        help_text=_("Path for the origin of the symbolic link."))


class SymbolicLinkSerializer(PHPAppSerializer):
    path = serializers.CharField(label=_("Path"))


class SymbolicLinkApp(PHPApp):
    name = 'symbolic-link'
    verbose_name = "Symbolic link"
    form = SymbolicLinkForm
    serializer = SymbolicLinkSerializer
    icon = 'orchestra/icons/apps/SymbolicLink.png'
    change_readonly_fields = ('path',)
