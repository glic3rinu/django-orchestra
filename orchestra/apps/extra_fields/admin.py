from common.utils.admin import insert_generic_plugin_inlines, delete_generic_plugin_inlines, UsedContentTypeFilter
from django import forms
from django.contrib import admin, messages
from django.contrib.contenttypes import generic
from extra_fields.models import ExtraField, ExtraValue
from functools import partial


class ExtraFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'content_type', 'raw_initial', 'help_text',)
    list_filter = [UsedContentTypeFilter]
    inlines = []

    def save_model(self, request, obj, form, change):
        super(ExtraFieldAdmin, self).save_model(request, obj, form, change)
        related = ExtraField.objects.filter(content_type=obj.content_type)
        insert_generic_plugin_inlines([[obj.content_type, related]], ExtraValue, make_extravalue_form, save_extravalue)        
        

    def delete_model(self, request, obj):
        super(ExtraFieldAdmin, self).delete_model(request, obj)        
        grouped = ExtraField.get_grouped()
        if grouped:
            insert_generic_plugin_inlines(grouped, ExtraField, make_extravalue_form, save_extravalue)
        else:
            delete_generic_plugin_inlines(obj.content_type, ExtraValue)


class ExtraValueAdmin(admin.ModelAdmin):
    list_display = ('extra_field', 'content_type', 'content_object', 'raw_value',)


admin.site.register(ExtraField, ExtraFieldAdmin)
admin.site.register(ExtraValue, ExtraValueAdmin)


#TODO: override form.has_changed in order to save default initial values
#TODO: Create generic plugin insertion on common.admin.py BasePlugin. For resources and extravalues.

def make_extravalue_form(name, extra_fields, _model):
    """ return an ModelForm class based on _model and with their monitors limit fields """
    
    dct = {}
    fields = []

    for field in extra_fields:
        dct[field.field_name] = field.get_form_field()
        fields.append(field.field_name)

    class Meta:
        model = _model
        
    Meta.fields = tuple(fields)
    dct['Meta'] = Meta

    def has_changed(self):
        """ In order to save initial values return True if it has been set """
        return True

    dct['has_changed'] = has_changed

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        obj = self.instance.content_object
        if obj: 
            for field in extra_fields:
                try: self.fields[field.field_name].initial = ExtraValue.objects.get_by_object_extra_field(obj, field).value
                except: pass

    dct['__init__'] = __init__
    return type(name,(forms.ModelForm,),dct)


def save_extravalue(self, extra_fields, form):
    for field in extra_fields:
        value = form.cleaned_data[field.field_name]
        try: 
            extravalue = ExtraValue.objects.get_by_object_extra_field(self.instance, field)
        except:
            extravalue = ExtraValue(extra_field = field,
                content_type = field.content_type, 
                object_id = self.instance.pk)
        extravalue.raw_value = value
        extravalue.save()
    return extravalue


insert_generic_plugin_inlines(ExtraField.get_grouped(), ExtraValue, make_extravalue_form, save_extravalue)
