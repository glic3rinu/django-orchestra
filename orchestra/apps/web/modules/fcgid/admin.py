from common.forms import RequiredInlineFormSet
from common.signals import collect_dependencies
from common.utils.admin import insert_inline
from common.widgets import ShowText
from django import forms
from django.contrib import admin
from models import Fcgid, FcgidDirective, VirtualHostFcgidDirective
from web.models import VirtualHost
import re


#TODO: keep it dry, since this is the same as phpoptions
class VirtualHostFcgidDirectiveInlineForm(forms.ModelForm):
    description = forms.CharField(label="Description", widget = ShowText(), initial='', required=False)
    
    def __init__(self, *args, **kwargs):
        super(VirtualHostFcgidDirectiveInlineForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['description'].initial = kwargs['instance'].directive.description

    def clean(self):
        # TODO: move this logic to a model field?
        cleaned_data = super(VirtualHostFcgidDirectiveInlineForm, self).clean()
        directive = cleaned_data.get("directive")
        value = cleaned_data.get("value")

        if not value:
            msg = u'Required field'
            self._errors["value"] = self.error_class([msg])
        elif not re.match(directive.regex, value):
            msg = u"%s" % directive.description
            self._errors["value"] = self.error_class([msg])
            del cleaned_data["value"]

        return cleaned_data


class VirtualHostFcgidDirectiveInline(admin.TabularInline):
    model = VirtualHostFcgidDirective
    extra = 1
    form = VirtualHostFcgidDirectiveInlineForm


class FcgidInline(admin.TabularInline):
    filter_fields_by_contact = ('user__user',)
    model = Fcgid
    formset = RequiredInlineFormSet


class FcgidDirectiveAdmin(admin.ModelAdmin):
    list_display = ('name', 'regex', 'description', 'restricted')
    list_filter = ('restricted',)


admin.site.register(FcgidDirective, FcgidDirectiveAdmin)


insert_inline(VirtualHost, FcgidInline)
insert_inline(VirtualHost, VirtualHostFcgidDirectiveInline)

