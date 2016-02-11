from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.forms import widgets

from .options import SoftwareService
from .. import settings
from ..forms import SaaSBaseForm


class WordPressForm(SaaSBaseForm):
    email = forms.EmailField(label=_("Email"),
        help_text=_("A new user will be created if the above email address is not in the database.<br>"
                    "The username and password will be mailed to this email address."))
    
    def __init__(self, *args, **kwargs):
        super(WordPressForm, self).__init__(*args, **kwargs)
        if self.is_change:
            admin_url = 'http://%s/wp-admin/' % self.instance.get_site_domain()
            help_text = 'Admin URL: <a href="{0}">{0}</a>'.format(admin_url)
            self.fields['site_url'].help_text = mark_safe(help_text)


class WordPressChangeForm(WordPressForm):
    blog_id = forms.IntegerField(label=("Blog ID"), widget=widgets.SpanWidget, required=False,
        help_text=_("ID of this blog used by WordPress, the only attribute that doesn't change."))


class WordPressDataSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))
    blog_id = serializers.IntegerField(label=_("Blog ID"), allow_null=True, required=False)


class WordPressService(SoftwareService):
    name = 'wordpress'
    verbose_name = "WordPress"
    form = WordPressForm
    change_form = WordPressChangeForm
    serializer = WordPressDataSerializer
    icon = 'orchestra/icons/apps/WordPress.png'
    change_readonly_fields = ('email', 'blog_id')
    site_domain = settings.SAAS_WORDPRESS_DOMAIN
    allow_custom_url = settings.SAAS_WORDPRESS_ALLOW_CUSTOM_URL
