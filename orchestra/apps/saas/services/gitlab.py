from django import forms
from django.utils.translation import ugettext_lazy as _

from orchestra.forms import PluginDataForm

from .options import SoftwareService


class GitLabForm(PluginDataForm):
    username = forms.CharField(label=_("Username"), max_length=64)
    password = forms.CharField(label=_("Password"), max_length=64)
    project_name = forms.CharField(label=_("Project name"), max_length=64)
    email = forms.EmailField(label=_("Email"))


class GitLabService(SoftwareService):
    verbose_name = "GitLab"
    form = GitLabForm
    description_field = 'project_name'
    icon = 'saas/icons/gitlab.png'
