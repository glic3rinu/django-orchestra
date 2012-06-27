from django import forms
from django.contrib import admin
from django.contrib.admin.filters import FieldListFilter, RelatedFieldListFilter
from django.contrib.admin.util import NestedObjects
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.encoding import smart_unicode
from signals import service_created, service_updated, service_deleted


class AddOrChangeInlineFormMixin(admin.options.InlineModelAdmin):
    """ This mixin class provides support for use independent forms for change and add on admin inlines
        just define them as an atribute of the inline class, ie:
        
            add_form = AddSystemUserInlineForm
            change_form = ChangeSystemUserInlineForm
     """
    def get_formset(self, request, obj=None, **kwargs):
        """ Returns a BaseInlineFormSet class for use in admin add/change views.
            Adds support for distinct between add or change inline form 
        """
        # Determine if we need to use add_form or change_form
        field_name = self.model._meta.module_name
        try: 
            getattr(obj, field_name)
        except (self.model.DoesNotExist, AttributeError): 
            self.form = self.add_form
        else: 
            self.form = self.change_form
        
        return super(AddOrChangeInlineFormMixin, self).get_formset(request, obj=obj, **kwargs) 


# Monkey-Patching models.deletion.collector in order to provide deletion on models
# with M2M field and delete_out_of_m2m attribute set to True
def m2m_collect(self, objs, source_attr=None, **kwargs):
    for obj in objs:
        if source_attr:
            related = getattr(obj, source_attr)
            if related.__class__.__name__ == 'ManyRelatedManager':
                related = related.all()[0]
            self.add_edge(related, obj)
        else:
            self.add_edge(None, obj)
    try:
        return super(NestedObjects, self).collect(objs, source_attr=source_attr, **kwargs)
    except models.ProtectedError, e:
        self.protected.update(e.protected_objects)

NestedObjects.collect = m2m_collect

