from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.apps.orchestration.models import BackendOperation as Operation
from orchestra.forms import widgets

from .options import SoftwareService, SoftwareServiceForm

from .. import settings


class GitLabForm(SoftwareServiceForm):
    email = forms.EmailField(label=_("Email"),
            help_text=_("Initial email address, changes on the GitLab server are not reflected here."))


class GitLaChangebForm(GitLabForm):
    user_id = forms.IntegerField(label=("User ID"), widget=widgets.ShowTextWidget,
            help_text=_("ID of this user on the GitLab server, the only attribute that not changes."))


class GitLabSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))
    user_id = serializers.IntegerField(label=_("User ID"), required=False)


class GitLabService(SoftwareService):
    name = 'gitlab'
    form = GitLabForm
    change_form = GitLaChangebForm
    serializer = GitLabSerializer
    site_domain = settings.SAAS_GITLAB_DOMAIN
    change_readonly_fileds = ('email', 'user_id',)
    verbose_name = "GitLab"
    icon = 'orchestra/icons/apps/gitlab.png'
    
    def clean_data(self):
        data = super(GitLabService, self).clean_data()
        if not self.instance.pk:
            log = Operation.execute_action(self.instance, 'validate_creation')[0]
            errors = {}
            if 'user-exists' in log.stdout:
                errors['name'] = _("User with this username already exists.")
            elif 'email-exists' in log.stdout:
                errors['email'] = _("User with this email address already exists.")
            if errors:
                raise ValidationError(errors)
        return data
