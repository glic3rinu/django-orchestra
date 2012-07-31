from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.db.models import Model
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _


def content_object_link(self):
    if not self.content_object: return ''
    opts = self.content_object._meta
    url = reverse('admin:%s_%s_change' % (opts.app_label, opts.module_name), args=(self.object_id,))
    return '<a href="%(url)s"><b>%(content_object)s</b></a>' % {'url': url, 'content_object': self.content_object}
content_object_link.short_description = _("Content Object")
content_object_link.allow_tags = True


def get_modeladmin(model): 
    for k,v in admin.site._registry.iteritems(): 
        if k is model: return v 


class DefaultFilterMixIn(admin.ModelAdmin):
    #TODO: change the approach: 
    #    since there is no way to know if All is selected or not, modify the filter queryset and 
    #    specify a filter for All, that way we can know if it is selected or not. 
    def changelist_view(self, request, *args, **kwargs):
        if self.default_filter:
            try:
                test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
                key = self.default_filter.split('=')[0]
                if test and test[-1] and not test[-1].startswith('?') and not request.GET.has_key(key):
                    url = reverse('admin:%s_%s_changelist' % (self.opts.app_label, self.opts.module_name))
                    return HttpResponseRedirect("%s?%s" % (url, self.default_filter))
            except KeyError: pass
        return super(DefaultFilterMixIn, self).changelist_view(request, *args, **kwargs)            


class UsedContentTypeFilter(SimpleListFilter):
    title = _('Content type')
    parameter_name = 'content_type'

    def lookups(self, request, model_admin):
        qset = model_admin.model._default_manager.all().order_by()
        result = ()
        # PK must be an string, so lets iterate...
        for pk, name in qset.values_list('content_type', 'content_type__name').distinct():
            result += ((str(pk), name.capitalize()),)
        return result
            
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type=self.value())


def delete_inline(model, inline_identify):
    model_admin = admin.site._registry[model]
    for ix in range(len(model_admin.inlines)):
        if hasattr(model_admin.inlines[ix], 'inline_identify'):
            if model_admin.inlines[ix].inline_identify == inline_identify: 
                model_admin.inlines.remove(model_admin.inlines[ix])
                #model_admin.inline_instances.remove(model_admin.inline_instances[ix])


def insert_inline(model, inline, head=False):
    """ Insert model inline into an existing model_admin """
    model_admin = admin.site._registry[model]
    if hasattr(inline, 'inline_identify'):
        delete_inline(model, inline.inline_identify)
    # Avoid inlines defined on parent class be shared between subclasses
    # Seems that if we use tuples they are lost in some conditions like changing the tuple in modeladmin.__init__ 
    if not model_admin.inlines: model_admin.__class__.inlines = []
    if head:
        model_admin.inlines = [inline] + model_admin.inlines
    else:
        model_admin.inlines.append(inline)


def insert_list_filter(model, filter):
    model_admin = admin.site._registry[model]
    if not model_admin.list_filter: model_admin.__class__.list_filter = []
    model_admin.list_filter += (filter,)


def insert_list_display(model, field):
    model_admin = admin.site._registry[model]
    if not model_admin.list_display: model_admin.__class__.list_display = []
    model_admin.list_display += (field,)    


def insert_action(model, action):
    model_admin = admin.site._registry[model]
    if not model_admin.actions: model_admin.__class__.actions = [action]
    else: model_admin.actions.append(action)


def insert_dynamic_inline(grouped_objects, _model, inline_form_factory, save_objects):
    """ 
        Creates and insert an admin inline form based on the input
    """
    for content_type, objects in grouped_objects:
        #TODO: do it with GenericTabularInline
        model = content_type.model_class()
        name = str(model) + "Form"
        
        Form = inline_form_factory(name, objects, model)
        Formset = generic.generic_inlineformset_factory(_model, form=Form, max_num=1, can_order=False)
       
        def save_new(self, form, commit=True):
            return save_objects(self, objects, form)
            
        def save_existing(self, form, instance, commit=True):
            save_objects(self, objects, form)
            
        def total_form_count(self): return 1
        
        Formset.save_new = save_new    
        Formset.save_existing = save_existing
        Formset.total_form_count = total_form_count
        
        class GenericPluginInline(generic.GenericStackedInline): 
            model = _model
            form = Form
            formset = Formset
            can_delete = False
            max_num = 1
            #Give a predictable unique identification in order to future replacement/deletion
            inline_identify = "%s:%s" % (content_type, model._meta.module_name)

        delete_inline(content_type.model_class(), "%s:%s" % (content_type, model._meta.module_name))
        insert_inline(model, GenericPluginInline)


def delete_dynamic_inline(content_type, model):
    delete_inline(content_type.model_class(), "%s:%s" % (content_type, model._meta.module_name))
    
