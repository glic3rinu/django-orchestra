from common.actions import delete_selected
from common.utils.admin import insert_dynamic_inline, delete_dynamic_inline, UsedContentTypeFilter
from common.utils.models import group_by
from common.widgets import ShowText
from datetime import datetime
from django import forms
from django.contrib import admin, messages
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _
from resources.models import Monitoring, Monitor


class MonitoringAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('content_object', 'content_type', 'resource', 'limit', 'current', 'last', 'date',)
    search_fields = ['content_type__model', 'monitor__resource',]
    list_filter = [UsedContentTypeFilter, 'monitor__resource']


class MonitorAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'content_type', 'resource', 'allow_limit', 'allow_unlimit', 
                    'default_initial', 'block_size', 'algorithm', 'period', 'crontab', 'active')
    list_filter = ('active', 'allow_limit', 'allow_unlimit', 'resource', 'algorithm', 'period')
    list_editable = ('allow_limit', 'allow_unlimit', 'default_initial', 'block_size', 'algorithm', 'period',) 
    actions = ['disable_selected', 'enable_selected']
    fieldsets = ((None,        {'fields': (('daemon'),
                                           ('resource'),),
                 }),
                 ('Templates', {'fields': (('monitoring_template', 'monitoring_method'),
                                           ('exceed_trigger_template', 'exceed_trigger_method'),
                                           ('recover_trigger_template', 'recover_trigger_method'),),
                 }),
                 (None,        {'fields': (('allow_limit', 'allow_unlimit', 'default_initial'),),
                 }),
                 (None,        {'fields': (('block_size', 'algorithm', 'period'),),
                 }),
                 ('Schedule',   {'fields': (('interval',), 
                                           ('crontab',),),
                 }),)

    def get_actions(self, request):
        actions = super(MonitorAdmin, self).get_actions(request)
        description = getattr(delete_selected, 'short_description', 'delete selected')
        actions['delete_selected'] = (delete_selected, 'delete_selected', description)
        return actions

    @transaction.commit_on_success
    def disable_selected(modeladmin, request, queryset):
        for monitor in queryset:
            monitor.disable()
            if monitor.has_partners:
                grouped = Monitor.get_grouped()
                insert_dynamic_inline(grouped, Monitoring, limit_form_factory, save_monitors)
            else:
                delete_dynamic_inline(monitor.daemon.content_type, Monitoring)
        messages.add_message(request, messages.INFO, _("All Selected monitors has been disabled"))
        return

    @transaction.commit_on_success
    def enable_selected(modeladmin, request, queryset):
        for monitor in queryset:
            monitor.enable()
            insert_dynamic_inline(Monitor.get_grouped(), Monitoring, limit_form_factory, save_monitors)
        messages.add_message(request, messages.INFO, _("All Selected monitors has been enabled"))
        return        

    def initialize(self, *args, **kwargs): pass

#    def save_model(self, request, obj, form, change):
#        #FIXME: insert new inline in an existing inline breaks.
#        super(MonitorAdmin, self).save_model(request, obj, form, change)
#        insert_dynamic_inline(Monitor.get_grouped(), Monitoring, limit_form_factory, save_monitors)


#    def delete_model(self, request, obj):
#        #TODO: make bulk delete compatible with this shit. 
#        super(MonitorAdmin, self).delete_model(request, obj)
#        if obj.has_partners:
#            grouped = Monitor.get_grouped()
#            insert_dynamic_inline(grouped, Monitoring, limit_form_factory, save_monitors)
#        else:
#            delete_dynamic_inline(obj.daemon.content_type, Monitoring)


@receiver(post_save, sender=Monitor, dispatch_uid="resources.maintain_dynamic_forms")
@receiver(post_delete, sender=Monitor, dispatch_uid="resources.maintain_dynamic_forms")
def maintain_dynamic_forms(sender, **kwargs):
    obj = kwargs['instance']
    if obj.has_partners:
        insert_dynamic_inline(Monitor.get_grouped(), Monitoring, limit_form_factory, save_monitors)
    else:
        delete_dynamic_inline(obj.daemon.content_type, Monitoring)


admin.site.register(Monitoring, MonitoringAdmin)
admin.site.register(Monitor, MonitorAdmin)


def limit_form_factory(name, monitors, _model):
    """ return an ModelForm class based on _model and with their monitors limit fields """
    
    dct = {}
    fields = []
    initial = False

    for monitor in monitors:
        resource = monitor.resource
        if monitor.allow_limit: 
            help_text = "Limit for %s." % (resource)
            if monitor.allow_unlimit: help_text += "0 means unlimited."
            dct[resource+"_limit"] = forms.IntegerField(initial=monitor.default_initial, help_text=help_text) 
            initial = True
            fields.append(resource+"_limit")
        dct["current_"+resource] = forms.CharField(max_length=100, required=False, widget = ShowText(), initial='No data')
        fields.append("current_"+resource)
            
    class Meta: 
        model = _model
    Meta.fields = tuple(fields) 
    dct['Meta'] = Meta

    def has_changed(self):
        """ In order to save initial values return True if it has been set """
        return initial
        
    dct['has_changed'] = has_changed    

    # Warn there is a conflic with multiple daemons.
    warning_field = forms.CharField(max_length=100, 
                                    required=False, 
                                    widget = ShowText(warning=True),
                                    initial="Sorry but this form field will not be rendered util you save this object")
                                    
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs) 
        obj = self.instance.content_object
        g_monitors = group_by(monitors.__class__, 'resource', monitors, dictionary=True, queryset=False)
        if obj: 
            for resource in g_monitors:
                monitor = Monitor.get_monitor(obj, resource)
                if monitor.allow_limit:
                    self.fields[monitor.resource+"_limit"].initial = Monitoring.get_limit(obj=obj,monitor=monitor)
                self.fields["current_"+monitor.resource].initial = Monitoring.get_current(obj=obj, monitor=monitor)               
        else:
            for resource in g_monitors:
                display = True
                monitor = g_monitors[resource][0]
                if len(g_monitors[resource]) > 1:
                    ant_mon = monitor
                    for _monitor in g_monitors[resource]:
                        if _monitor.has_different_configuration(ant_mon): 
                            display = False
                        ant_mon = _monitor  
                if not display:
                    if monitor.allow_limit:
                        self.fields[monitor.resource+"_limit"]=warning_field
                #TODO: How to know when there is no monitor? maybe passing some extra kwarg arg, then do this: 
                #    self.fields[monitor.resource+"_limit"].widget=forms.HiddenInput()
                #    self.fields[monitor.resource+"_limit"].required=False         
                #    self.fields[monitor.resource+"_current"].widget=forms.HiddenInput()
                
    dct['__init__'] = __init__
    return type(name,(forms.ModelForm,),dct) 


def save_monitors(self, monitors, form):
    """ save limit monitors """ 
    g_monitors = group_by(monitors.__class__, 'resource', monitors, dictionary=True, queryset=False)
    for resource in g_monitors:
        try: monitor = Monitor.get_monitor(self.instance, resource)
        except Monitor.DoesNotExist: pass
        else: 
            if monitor.allow_limit: 
                limit = form.cleaned_data[monitor.resource+"_limit"]
                if not limit:
                    limit = monitor.default_initial
                monitoring = Monitoring(
                    limit = limit,
                    monitor = monitor, 
                    content_type = monitor.content_type, 
                    object_id = self.instance.pk,
                    date = datetime.now())
                try: last = Monitoring.objects.by_object(self.instance, monitor=monitor).get_last()
                except Monitoring.DoesNotExist: monitoring.save()
                else:
                    if last.limit != limit:
                        monitoring.save()
    
    #TODO: this is fucking clunky
    try: return monitoring
    except: return self.instance


insert_dynamic_inline(Monitor.get_grouped(), Monitoring, limit_form_factory, save_monitors)
