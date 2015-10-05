from django import forms

from orchestra.forms.widgets import SpanWidget, paddingCheckboxSelectMultiple


class RouteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RouteForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['backend'].required = False
            try:
                backend_class = self.instance.backend_class
            except KeyError:
                self.fields['backend'].widget = SpanWidget(
                    display='<span style="color:red">%s NOT AVAILABLE</span>' % self.instance.backend)
            else:
                self.fields['backend'].widget = SpanWidget()
                actions = backend_class.actions
                self.fields['async_actions'].widget = paddingCheckboxSelectMultiple(45)
                self.fields['async_actions'].choices = ((action, action) for action in actions)
