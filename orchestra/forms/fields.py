from django import forms

from .widgets import SpanWidget


class MultiSelectFormField(forms.MultipleChoiceField):
    """ http://djangosnippets.org/snippets/1200/ """
    widget = forms.CheckboxSelectMultiple
    
    def __init__(self, *args, **kwargs):
        self.max_choices = kwargs.pop('max_choices', 0)
        super(MultiSelectFormField, self).__init__(*args, **kwargs)
    
    def clean(self, value):
        if not value and self.required:
            raise forms.ValidationError(self.error_messages['required'])
        return value


class SpanField(forms.Field):
    """
    A field which renders a value wrapped in a <span> tag.
    
    Requires use of specific form support. (see ReadonlyForm or ReadonlyModelForm)
    """
    
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.get('widget', SpanWidget)
        super(SpanField, self).__init__(*args, **kwargs)
