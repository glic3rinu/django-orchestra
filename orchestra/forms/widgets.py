from django import forms
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text


class ShowTextWidget(forms.Widget):
    def __init__(self, *args, **kwargs):
        for kwarg in ['bold', 'warning', 'hidden']:
            setattr(self, kwarg, kwargs.pop(kwarg, False))
        super(ShowTextWidget, self).__init__(*args, **kwargs)
    
    def render(self, name, value, attrs):
        value = force_text(value)
        if value is None:
            return ''
        if hasattr(self, 'initial'):
            value = self.initial
        if self.bold: 
            final_value = u'<b>%s</b>' % (value)
        else:
            final_value = '<br/>'.join(value.split('\n'))
        if self.warning:
            final_value = u'<ul class="messagelist"><li class="warning">%s</li></ul>' %(final_value)
        if self.hidden:
            final_value = u'%s<input type="hidden" name="%s" value="%s"/>' % (final_value, name, value)
        return mark_safe(final_value)
    
    def _has_changed(self, initial, data):
        return False


class ReadOnlyWidget(forms.Widget):
    def __init__(self, *args):
        if len(args) == 1:
            args = (args[0], args[0])
        self.original_value = args[0]
        self.display_value = args[1]
        super(ReadOnlyWidget, self).__init__()
    
    def render(self, name, value, attrs=None):
        if self.display_value is not None:
            return mark_safe(self.display_value)
        return mark_safe(self.original_value)
    
    def value_from_datadict(self, data, files, name):
        return self.original_value
