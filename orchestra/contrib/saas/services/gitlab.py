from django import forms
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.forms import widgets

from .. import settings
from ..forms import SaaSPasswordForm
from .options import SoftwareService


class GitLabForm(SaaSPasswordForm):
    email = forms.EmailField(label=_("Email"),
        help_text=_("Initial email address, changes on the GitLab server are not reflected here."))


class GitLaChangeForm(GitLabForm):
    user_id = forms.IntegerField(label=("User ID"), widget=widgets.SpanWidget,
        help_text=_("ID of this user used by GitLab, the only attribute that doesn't change."))


class GitLabSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))
    user_id = serializers.IntegerField(label=_("User ID"), allow_null=True, required=False)


class GitLabService(SoftwareService):
    name = 'gitlab'
    form = GitLabForm
    change_form = GitLaChangeForm
    serializer = GitLabSerializer
    site_domain = settings.SAAS_GITLAB_DOMAIN
    change_readonly_fields = ('email', 'user_id',)
    verbose_name = "GitLab"
    icon = 'orchestra/icons/apps/gitlab.png'
