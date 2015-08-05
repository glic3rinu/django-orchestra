from django.utils.translation import ugettext_lazy as _

from orchestra.forms import UserCreationForm, NonStoredUserChangeForm


class CleanAddressMixin(object):
    def clean_address_domain(self):
        name = self.cleaned_data.get('address_name')
        domain = self.cleaned_data.get('address_domain')
        if name and not domain:
            msg = _("Domain should be selected for provided address name")
            raise forms.ValidationError(msg)
        return domain


class ListCreationForm(CleanAddressMixin, UserCreationForm):
    pass


class ListChangeForm(CleanAddressMixin, NonStoredUserChangeForm):
    pass
