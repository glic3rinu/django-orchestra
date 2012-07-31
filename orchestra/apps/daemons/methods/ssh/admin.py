from django.contrib import admin
from models import SSHOption
from django import forms
from plugins import SSH

class SHHOptionAdminForm(forms.ModelForm):
    password = forms.CharField(label="SSH Password", widget=forms.PasswordInput(render_value=True), required=False)

    #    def clean(self):
#        """ If the daemon uses ssh method some fields are required """
#        cleaned_data = super(SHHOptionAdminForm, self).clean()
#        host = cleaned_data.get("daemon")
#        if daemon.save_method == SSH.get_model() or daemon.delete_method == SSH.get_model():
#            msg = "requiered field"
#            if not cleaned_data.get("user"):
#                self._errors["user"] = self.error_class([msg])
#            if not cleaned_data.get("host_keys"):
#                self._errors["host_keys"] = self.error_class([msg])
#            if not cleaned_data.get("port"):
#                self._errors["port"] = self.error_class([msg])

#        return cleaned_data

class SHHOptionInline(admin.StackedInline):
    model = SSHOption
    form = SHHOptionAdminForm
    
    class Media:
        js = ['js/collapsed_stacked_inlines.js',]
    
from common.utils.admin import insert_inline
from daemons.models import Host
insert_inline(Host, SHHOptionInline)
