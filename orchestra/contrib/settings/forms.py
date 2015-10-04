import math
from copy import deepcopy
from functools import partial

from django import forms
from django.core.exceptions import ValidationError
from django.forms.formsets import formset_factory
from django.utils.functional import Promise
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.forms import ReadOnlyFormMixin, widgets
from orchestra.utils.python import format_exception

from . import parser


class SettingForm(ReadOnlyFormMixin, forms.Form):
    TEXTAREA = partial(
        forms.CharField,
        widget=forms.Textarea(attrs={
            'cols': 65,
            'rows': 2,
            'style': 'font-family: monospace',
        }))
    CHARFIELD = partial(
        forms.CharField,
        widget=forms.TextInput(attrs={
            'size': 65,
            'style': 'font-family: monospace',
        }))
    NON_EDITABLE = partial(forms.CharField, widget=widgets.SpanWidget, required=False)
    FORMFIELD_FOR_SETTING_TYPE = {
            bool: partial(forms.BooleanField, required=False),
            int: forms.IntegerField,
            float: forms.FloatField,
            tuple: TEXTAREA,
            list: TEXTAREA,
            dict: TEXTAREA,
            Promise: CHARFIELD,
            str: CHARFIELD,
        }
    
    name = forms.CharField(label=_("name"))
    default = forms.CharField(label=_("default"))
    
    class Meta:
        readonly_fields = ('name', 'default')
    
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        if initial:
            self.setting_type = initial['type']
            self.setting = initial['setting']
            setting = self.setting
            if setting.serializable:
                serialized_value = parser.serialize(initial['value'])
                serialized_default = parser.serialize(initial['default'])
            else:
                serialized_value = parser.NotSupported()
                serialized_default = parser.NotSupported()
            if not setting.editable or isinstance(serialized_value, parser.NotSupported):
                field = self.NON_EDITABLE
            else:
                choices = setting.choices
                field = forms.ChoiceField
                multiple = setting.multiple
                if multiple:
                    field = partial(
                        forms.MultipleChoiceField,
                        widget=forms.CheckboxSelectMultiple)
                if choices:
                    # Lazy loading
                    if callable(choices):
                        choices = choices()
                    if not multiple:
                        choices = tuple((parser.serialize(val), verb) for val, verb in choices)
                    field = partial(field, choices=choices)
                else:
                    field = self.FORMFIELD_FOR_SETTING_TYPE.get(
                        self.setting_type, self.NON_EDITABLE)
                    field = deepcopy(field)
            real_field = field
            while isinstance(real_field, partial):
                real_field = real_field.func
            # Do not serialize following form types
            value = initial['value']
            default = initial['default']
            self.changed = bool(value != default)
            if real_field not in (forms.MultipleChoiceField, forms.BooleanField):
                value = serialized_value
                default = serialized_default
            initial['value'] = value
            initial['default'] = default
        super(SettingForm, self).__init__(*args, **kwargs)
        if initial:
            self.fields['value'] = field(label=_("value"))
            if isinstance(self.fields['value'].widget, forms.Textarea):
                rows = math.ceil(len(value)/65)
                self.fields['value'].widget.attrs['rows'] = rows
            self.fields['name'].help_text = mark_safe(setting.help_text)
            self.fields['name'].widget.attrs['readonly'] = True
            self.app = initial['app']
        
    def clean_value(self):
        value = self.cleaned_data['value']
        if not value:
            return parser.NotSupported()
        if not isinstance(value, str):
            value = parser.serialize(value)
        try:
            value = eval(value, parser.get_eval_context())
        except Exception as exc:
            raise ValidationError(format_exception(exc))
        self.setting.validate_value(value)
#        if not isinstance(value, self.setting_type):
#            if self.setting_type in (tuple, list) and isinstance(value, (tuple, list)):
#                value = self.setting_type(value)
        return value


SettingFormSet = formset_factory(SettingForm, extra=0)
