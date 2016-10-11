import textwrap
from functools import partial

from django import forms
from django.contrib.admin import helpers
from django.core import validators
from django.forms.models import modelformset_factory, BaseModelFormSet
from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _

from orchestra.forms.widgets import SpanWidget

from ..core.validators import validate_password


class AdminFormMixin(object):
    """ Provides a method for rendering a form just like in Django Admin """
    def as_admin(self):
        prepopulated_fields = {}
        fieldsets = [
            (None, {
                'fields': list(self.fields.keys())
            }),
        ]
        adminform = helpers.AdminForm(self, fieldsets, prepopulated_fields)
        template = Template(
            '{% for fieldset in adminform %}'
            '   {% include "admin/includes/fieldset.html" %}'
            '{% endfor %}'
        )
        context = Context({
            'adminform': adminform
        })
        return template.render(context)


class AdminFormSet(BaseModelFormSet):
    def as_admin(self):
        template = Template(textwrap.dedent("""\
        <div class="inline-group">
        <div class="tabular inline-related last-related">
        {{ formset.management_form }}
        <fieldset class="module">
            {{ formset.non_form_errors.as_ul }}
            <table id="formset" class="form">
            {% for form in formset.forms %}
              {% if forloop.first %}
              <thead><tr>
                {% for field in form.visible_fields %}
                <th>{{ field.label|capfirst }}</th>
                {% endfor %}
              </tr></thead>
              {% endif %}
              <tr class="{% cycle row1,row2 %}">
              {% for field in form.visible_fields %}
                <td>
                {# Include the hidden fields in the form #}
                {% if forloop.first %}
                  {% for hidden in form.hidden_fields %}
                  {{ hidden }}
                  {% endfor %}
                {% endif %}
                  {{ field.errors.as_ul }}
                  {{ field }}
                </td>
              {% endfor %}
              </tr>
            {% endfor %}
            </table>
        </fieldset>
        </div>
        </div>""")
        )
        context = Context({
            'formset': self
        })
        return template.render(context)


class AdminPasswordChangeForm(forms.Form):
    """
    A form used to change the password of a user in the admin interface.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'password_missing': _("No password has been provided."),
        'bad_hash': _("Invalid password format or unknown hashing algorithm."),
    }
    required_css_class = 'required'
    password = forms.CharField(label=_("Password"), required=False,
        widget=forms.TextInput(attrs={'size':'120'}))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput,
            required=False, validators=[validate_password])
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput,
            required=False)
    
    def __init__(self, user, *args, **kwargs):
        self.related = kwargs.pop('related', [])
        self.raw = kwargs.pop('raw', False)
        self.user = user
        super().__init__(*args, **kwargs)
        self.password_provided = False
        for ix, rel in enumerate(self.related):
            self.fields['password_%i' % ix] = forms.CharField(label=_("Password"), required=False,
                widget=forms.TextInput(attrs={'size':'120'}))
            setattr(self, 'clean_password_%i' % ix, partial(self.clean_password, ix=ix))
            self.fields['password1_%i' % ix] = forms.CharField(label=_("Password"),
                widget=forms.PasswordInput, required=False)
            self.fields['password2_%i' % ix] = forms.CharField(label=_("Password (again)"),
                widget=forms.PasswordInput, required=False)
            setattr(self, 'clean_password2_%i' % ix, partial(self.clean_password2, ix=ix))
    
    def clean_password2(self, ix=''):
        if ix != '':
            ix = '_%i' % ix
        password1 = self.cleaned_data.get('password1%s' % ix)
        password2 = self.cleaned_data.get('password2%s' % ix)
        if password1 and password2:
            self.password_provided = True
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        elif password1 or password2:
            self.password_provided = True
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2
    
    def clean_password(self, ix=''):
        if ix != '':
            ix = '_%i' % ix
        password = self.cleaned_data.get('password%s' % ix)
        if password:
            # lazy loading because of passlib
            from django.contrib.auth.hashers import identify_hasher
            self.password_provided = True
            try:
                identify_hasher(password)
            except ValueError:
                raise forms.ValidationError(
                    self.error_messages['bad_hash'],
                    code='bad_hash',
                )
        return password
    
    def clean(self):
        if not self.password_provided:
            raise forms.ValidationError(
                self.error_messages['password_missing'],
                code='password_missing',
            )
    
    def save(self, commit=True):
        """
        Saves the new password.
        """
        field_name = 'password' if self.raw else 'password1'
        password = self.cleaned_data[field_name]
        if password:
            if self.raw:
                self.user.password = password
            else:
                self.user.set_password(password)
            if commit:
                try:
                    self.user.save(update_fields=['password'])
                except ValueError:
                    # password is not a field but an attribute
                    self.user.save() # Trigger the backend
        for ix, rel in enumerate(self.related):
            password = self.cleaned_data['%s_%s' % (field_name, ix)]
            if password:
                if self.raw:
                    rel.password = password
                else:
                    set_password = getattr(rel, 'set_password')
                    set_password(password)
                if commit:
                    rel.save(update_fields=['password'])
        return self.user
    
    def _get_changed_data(self):
        data = super().changed_data
        for name in self.fields.keys():
            if name not in data:
                return []
        return ['password']
    changed_data = property(_get_changed_data)


class SendEmailForm(forms.Form):
    email_from = forms.EmailField(label=_("From"),
        widget=forms.TextInput(attrs={'size': '118'}))
    to = forms.CharField(label="To", required=False)
    extra_to = forms.CharField(label="To (extra)", required=False,
        widget=forms.TextInput(attrs={'size': '118'}))
    subject = forms.CharField(label=_("Subject"),
        widget=forms.TextInput(attrs={'size': '118'}))
    message = forms.CharField(label=_("Message"),
        widget=forms.Textarea(attrs={'cols': 118, 'rows': 15}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial = kwargs.get('initial')
        if 'to' in initial:
            self.fields['to'].widget = SpanWidget(original=initial['to'])
        else:
            self.fields.pop('to')
    
    def clean_comma_separated_emails(self, value):
        clean_value = []
        for email in value.split(','):
            email = email.strip()
            if email:
                try:
                    validators.validate_email(email)
                except validators.ValidationError:
                    raise validators.ValidationError("Comma separated email addresses.")
                clean_value.append(email)
        return clean_value
    
    def clean_extra_to(self):
        extra_to = self.cleaned_data['extra_to']
        return self.clean_comma_separated_emails(extra_to)
