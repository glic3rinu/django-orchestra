from django.contrib.admin import helpers
from django.forms.models import modelformset_factory, BaseModelFormSet
from django.template import Template, Context


class AdminFormMixin(object):
    """ Provides a method for rendering a form just like in Django Admin """
    def as_admin(self):
        prepopulated_fields = {}
        fieldsets = [
            (None, {'fields': self.fields.keys()})
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
            (None, {'fields': self.form().fields.keys()})
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


def adminmodelformset_factory(modeladmin, form):
    formset = modelformset_factory(modeladmin.model, extra=0,
            form=form, formset=AdminFormSet)
    formset.modeladmin = modeladmin
    return formset
