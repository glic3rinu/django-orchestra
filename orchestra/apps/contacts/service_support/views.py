from contacts.models import Contact
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _


def select_contact_view(request, model_admin, extra_context=None):
    """ Intermediary page that shows a contact list with links to add view + contact_id=x """ 

    def add_to_contact_link(self):
        url = "../?contact_id=" + str(self.id)
        # This is embarsaing... In the billing app we need to keep the queryset value 
        # during some page visits, so this pice of shit is trying to keep queryset value until next jump.
        # If you know a better way to do this, I would like to know.
        #TODO: move this billing specific part to bill
        if 'HTTP_REFERER' in request.META:
            querystring = request.META['HTTP_REFERER'].split('/')[-1]
            if 'queryset' in querystring:
                queryset = querystring.split('queryset=')[1].split('&')[0]
                url += '&queryset=%s' % queryset
        return '<a href="%(url)s">%(contact_name)s</a>' % {'url': url , 'contact_name': self.fullname  }
    add_to_contact_link.short_description = _("Contact")
    add_to_contact_link.allow_tags = True

    class ContactListAdmin(admin.ModelAdmin):
        fields = ('name', 'surname')
        list_display = (add_to_contact_link, 'surname')
        actions = None
        search_fields = ['name', 'surname', 'second_surname',]
        change_list_template = 'service/select_contact.html'
        ordering = ('name',)
        
        def changelist_view(self, request, extra_context=None):
            """Renders the change view."""
            opts = self.model._meta
            s_app_label = request.META['PATH_INFO'].split('/')[-5]
            model = request.META['PATH_INFO'].split('/')[-4]
            context = { 'title': _('Select contact in order to add a new %s') % (model),
                        's_app_label': s_app_label,
                        'model': model, }
            context.update(extra_context or {})
            return super(ContactListAdmin, self).changelist_view(request, context)    

    opts = model_admin.model._meta
    context = {"add_url": reverse("admin:%s_%s_add" % (opts.app_label, opts.module_name)),}
    context.update(extra_context or {})
    
    return ContactListAdmin(Contact, model_admin.admin_site).changelist_view(request, context)

