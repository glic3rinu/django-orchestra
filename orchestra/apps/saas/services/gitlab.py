from django import forms
from django.utils.translation import ugettext_lazy as _

from .options import SoftwareService, SoftwareServiceForm


class GitLabForm(SoftwareServiceForm):
    project_name = forms.CharField(label=_("Project name"), max_length=64)
    email = forms.CharField(label=_("Email"), max_length=64)


class GitLabService(SoftwareService):
    verbose_name = "GitLab"
    form = GitLabForm
    description_field = 'project_name'
