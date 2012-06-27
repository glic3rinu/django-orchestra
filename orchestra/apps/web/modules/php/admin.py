from common.utils.admin import insert_inline
from common.widgets import ShowText
from django import forms
from django.contrib import admin
from models import PHP, PHPDirective, VirtualHostPHPDirective
import re
from web.models import VirtualHost


#TODO: keep it dry, since this is the same as fcgiddirective
class VirtualHostPHPDirectiveInlineForm(forms.ModelForm):
    description = forms.CharField(label="Description", widget = ShowText(), initial='', required=False)
    
    def __init__(self, *args, **kwargs):
        super(VirtualHostPHPDirectiveInlineForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['description'].initial = kwargs['instance'].directive.description

    def clean(self):
        cleaned_data = super(VirtualHostPHPDirectiveInlineForm, self).clean()
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


class VirtualHostPHPDirectiveInline(admin.TabularInline):
    model = VirtualHostPHPDirective
    extra = 1
    form = VirtualHostPHPDirectiveInlineForm


class PHPInlineForm(forms.ModelForm):
    """ save default php version """
    
    def has_changed(self):
        if not self.instance.pk and self.instance.version: return True
        return super(PHPInlineForm, self).has_changed()


class PHPInline(admin.TabularInline):
    model = PHP
    form = PHPInlineForm


class PHPDirectiveAdmin(admin.ModelAdmin):
    list_display = ('name', 'regex', 'description', 'restricted')
    list_filter = ('restricted',)


admin.site.register(PHPDirective, PHPDirectiveAdmin)


insert_inline(VirtualHost, PHPInline)
insert_inline(VirtualHost, VirtualHostPHPDirectiveInline)

