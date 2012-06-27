from django import forms
from django.contrib.admin.helpers import AdminForm
from django.template.loader import render_to_string


class RequiredInlineFormSet(forms.models.BaseInlineFormSet):
    """
    Generates an inline formset that is required
    """
    def _construct_form(self, i, **kwargs):
        """
        Override the method to change the form attribute empty_permitted
        """
        form = super(RequiredInlineFormSet, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form



class FormAdminDjango(object):
    """
    Abstract class implemented to provide form django admin like
    Usage::
       class FooForm(forms.Form, FormAdminDjango):
          ...
    """
    fieldsets = ()
    prepopulated_fields = {}
    readonly_fields = None
    model_admin = None

    def as_django_admin(self):
        if not self.fieldsets:
            self.fieldsets = [(None, {'fields': self.fields.keys()})]
        try:
            adminform = AdminForm(self, self.fieldsets, self.prepopulated_fields, self.readonly_fields, self.model_admin)
        except TypeError:  # To old django
            adminform = AdminForm(self, self.fieldsets, self.prepopulated_fields)
        return render_to_string('admin/form_admin_django.html', {'adminform': adminform, })


def get_initial_form(cls):
    """ Form for FormSets with initial values support """
    class InitialForm(forms.ModelForm):
        class Meta:
            model = cls

        def has_changed(self):
            if super(InitialForm, self).has_changed(): 
#                if self.initial:
#                    return True
                return True
            elif self.initial: 
                return True
            return False
    return InitialForm


def get_initial_formset(form):
    """ FormSet with initial values support """
    class BaseInitialFormSet(forms.models.BaseInlineFormSet):
        def __init__(self, *args, **kwargs):
            self.__initial = kwargs.pop('initial', [])
            super(BaseInitialFormSet, self).__init__(*args, **kwargs)

        def total_form_count(self):
            if self.__initial:
                return len(self.__initial) + self.extra
            return super(BaseInitialFormSet, self).total_form_count()

        def _construct_forms(self):
            return forms.formsets.BaseFormSet._construct_forms(self)

        def _construct_form(self, i, **kwargs):
            if self.__initial:
                try: kwargs['initial'] = self.__initial[i]
                except IndexError: pass
                return forms.formsets.BaseFormSet._construct_form(self, i, **kwargs)
            return super(BaseInitialFormSet, self)._construct_form(i, **kwargs)

    return forms.formsets.formset_factory(form, formset=BaseInitialFormSet)
