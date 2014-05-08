from django import forms
from django.utils.safestring import mark_safe


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
