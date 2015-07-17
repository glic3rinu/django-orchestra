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
            (None, {'fields': list(self.fields.keys())})
        ]
        adminform = helpers.AdminForm(self, fieldsets, prepopulated_fields)
        template = Template(
            '{% for fieldset in adminform %}'
            '   {% include "admin/includes/fieldset.html" %}'
            '{% endfor %}'
        )
        return template.render(Context({'adminform': adminform}))


class AdminFormSet(BaseModelFormSet):
    def as_admin(self):
        prepopulated = {}
        fieldsets = [
            (None, {'fields': list(self.form().fields.keys())})
        ]
        readonly = getattr(self.form.Meta, 'readonly_fields', ())
        if not hasattr(self.modeladmin, 'verbose_name_plural'):
            opts = self.modeladmin.model._meta
            self.modeladmin.verbose_name_plural = opts.verbose_name_plural
        inline_admin_formset = helpers.InlineAdminFormSet(self.modeladmin, self,
            fieldsets, prepopulated, readonly, model_admin=self.modeladmin)
        template = Template(
            '{% include "admin/edit_inline/tabular.html" %}'
        )
        return template.render(Context({'inline_admin_formset': inline_admin_formset}))


def adminmodelformset_factory(modeladmin, form, formset=AdminFormSet, **kwargs):
    model = kwargs.pop('model', modeladmin.model)
    formset = modelformset_factory(model, form=form, formset=formset, **kwargs)
    formset.modeladmin = modeladmin
    return formset


class AdminPasswordChangeForm(forms.Form):
    """
    A form used to change the password of a user in the admin interface.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'password_missing': _("No password has been provided."),
    }
    required_css_class = 'required'
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput,
            required=False, validators=[validate_password])
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput,
            required=False)
    
    def __init__(self, user, *args, **kwargs):
        self.related = kwargs.pop('related', [])
        self.user = user
        super(AdminPasswordChangeForm, self).__init__(*args, **kwargs)
        for ix, rel in enumerate(self.related):
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
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        elif password1 or password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2
    
    def clean(self):
        cleaned_data = super(AdminPasswordChangeForm, self).clean()
        for data in cleaned_data.values():
            if data:
                return
        raise forms.ValidationError(
            self.error_messages['password_missing'],
            code='password_missing',
        )
    
    def save(self, commit=True):
        """
        Saves the new password.
        """
        password = self.cleaned_data["password1"]
        if password:
            self.user.set_password(password)
            if commit:
                try:
                    self.user.save(update_fields=['password'])
                except ValueError:
                    # password is not a field but an attribute
                    self.user.save() # Trigger the backend
        for ix, rel in enumerate(self.related):
            password = self.cleaned_data['password1_%s' % ix]
            if password:
                set_password = getattr(rel, 'set_password')
                set_password(password)
                if commit:
                    rel.save(update_fields=['password'])
        return self.user
    
    def _get_changed_data(self):
        data = super(AdminPasswordChangeForm, self).changed_data
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
        super(SendEmailForm, self).__init__(*args, **kwargs)
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
