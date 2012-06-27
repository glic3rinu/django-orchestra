from django.utils.safestring import mark_safe
from django.contrib.admin import widgets
import re

class ContactRelatedFieldWidgetWrapper(widgets.RelatedFieldWidgetWrapper):
    """ Add '?contact_id=X' to adminform addlink """ 
    
    def __init__(self, widget, rel, admin_site, can_add_related=None, contact_id=None):
        super(ContactRelatedFieldWidgetWrapper, self).__init__(widget, rel, admin_site, can_add_related=can_add_related)
        if contact_id: self.contact_id = contact_id

    def render(self, *args, **kwargs):
        self.widget.choices = self.choices
        output = [self.widget.render(*args, **kwargs)]
        p = re.compile( '/add/"' )
        output[0] = p.sub('/add/?contact_id=%s"' % self.contact_id, output[0])
        return mark_safe(u''.join(output)) 

