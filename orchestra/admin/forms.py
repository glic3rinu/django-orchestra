from django.template import Template, Context
from django.contrib.admin.helpers import AdminForm


class AdminFormMixin(object):
    """ Provides a method for rendering a form just like in Django Admin """
    def as_admin(self):
        prepopulated_fields = {}
        fieldsets = [
            (None, {'fields': self.fields.keys()})
        ]
        adminform = AdminForm(self, fieldsets, prepopulated_fields)
        template = Template(
            '{% for fieldset in adminform %}'
            '{% include "admin/includes/fieldset.html" %}'
            '{% endfor %}'
        )
        return template.render(Context({'adminform': adminform}))
