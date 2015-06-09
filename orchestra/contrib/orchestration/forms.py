from django import forms
from orchestra.forms.widgets import SpanWidget
from orchestra.forms.widgets import paddingCheckboxSelectMultiple


class RouteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RouteForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['backend'].widget = SpanWidget()
            self.fields['backend'].required = False
            self.fields['async_actions'].widget = paddingCheckboxSelectMultiple(45)
            actions = self.instance.backend_class.actions
            self.fields['async_actions'].choices = ((action, action) for action in actions)
