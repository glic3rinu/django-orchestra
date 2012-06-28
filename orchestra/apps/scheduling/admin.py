from actions import schedule, revoke
from common.forms import FormAdminDjango
from common.utils.admin import UsedContentTypeFilter, DefaultFilterMixIn, insert_list_display, insert_action, insert_list_filter
from common.utils.python import _import
from datetime import datetime
from django import forms 
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.widgets import AdminSplitDateTime
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from scheduling.models import DeletionDate, DeactivationPeriod
import settings


# TODO: The admin scheduling confirmation page needs some improvements in terms of display the correct effect of the schedule.
#       It doesn't take into account the existing schedulings in order to exactly determinate what will happends
#       with the new schedule, unfortunately this stuff is hard to implement, so for now it only takes into account the 
#       the scheduling effect of the selected objects.


class ExecutedFilter(SimpleListFilter):
    title = _('Executed')
    parameter_name = 'executed'

    def lookups(self, request, model_admin):
        return (
            ('Yes', _('Yes')),
            ('No', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(revoke_date__isnull=True, deletion_date__lt=datetime.now())
        if self.value() == 'No':
            return queryset.exclude(revoke_date__isnull=True, deletion_date__lt=datetime.now())


class ActiveFilter(SimpleListFilter):
    title = _('Active')
    parameter_name = 'active'

    def lookups(self, request, model_admin):
        return (
            ('Yes', _('Yes')),
            ('No', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(revoke_date__isnull=True)
        if self.value() == 'No':
            return queryset.filter(revoke_date__isnull=False)


def content_object_link(self):
    if not self.content_object: return ''
    opts = self.content_object._meta
    try: url = reverse('admin:%s_%s_change' % (opts.app_label, opts.module_name), args=(self.object_id,))
    except: return ''
    return '<a href="%(url)s"><b>%(content_object)s</b></a>' % {'url': url, 'content_object': self.content_object}
content_object_link.short_description = _("Content Object")
content_object_link.allow_tags = True


def revoke_date(self):
    return self.revoke_date if self.revoke_date else ''
revoke_date.short_description = _("Revoke date")
revoke_date.admin_order_field = 'revoke_date'


def executed(self):
    return False if self.revoke_date or self.deletion_date > datetime.now() else True
executed.short_description = _("Executed")
executed.boolean = True



class DeletionDateAdmin(DefaultFilterMixIn):
    list_display = ('__unicode__', content_object_link, 'object_id', 'content_type', 'register_date', executed, 'deletion_date', revoke_date)
    date_hierarchy = 'deletion_date'
    list_filter = (UsedContentTypeFilter,'register_date', 'deletion_date', 'snapshot', ExecutedFilter, ActiveFilter)
    actions = [revoke]
    default_filter = 'snapshot__exact=0'


class DeactivationExecutedFilter(ExecutedFilter):
    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(revoke_date__isnull=True, start_date__lt=datetime.now())
        if self.value() == 'No':
            return queryset.exclude(revoke_date__isnull=True, start_date__lt=datetime.now())


def executed(self):
    return False if self.revoke_date or self.start_date > datetime.now() else True
executed.short_description = _("Executed")
executed.boolean = True


def end_date(self):
    return self.end_date if self.end_date else ''
end_date.short_description = _("End date")


class DeactivationPeriodAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', content_object_link, 'object_id', 'content_type', 'register_date', executed, 'start_date', end_date, revoke_date)
    date_hierarchy = 'start_date'
    list_filter = ('content_type', 'register_date', 'start_date', 'snapshot', DeactivationExecutedFilter, ActiveFilter)
    actions = [revoke]


admin.site.register(DeletionDate, DeletionDateAdmin)
admin.site.register(DeactivationPeriod, DeactivationPeriodAdmin)


# Support for other apps ##

def cancel_date(self):
    cd = DeletionDate.get(self)
    if cd: 
        url = reverse('admin:scheduling_deletiondate_change', args=(cd.pk,))
        return '<a href="%(url)s">%(cancel_date)s</a>' % {'url': url, 'cancel_date': cd.deletion_date.strftime("%Y-%m-%d %H:%M") }
    return self.cancel_date.strftime("%Y-%m-%d %H:%M") if self.cancel_date else ''
cancel_date.short_descritpion = _("Cancel date")
cancel_date.allow_tags = True


def deactivation_periods(self):
    periods = list(self.deactivation_periods)
    if periods:
        first = periods.pop()
        for period in periods:
            if period.start_date < first.start_date:
                first = period
        end = first.end_date if first.end_date else 'indef'
        return "%s - %s" % (first.start_date.strftime("%Y-%m-%d %H:%M"), end)
    return ''
deactivation_periods.short_description = _("Deactivations")


def active(self):
    periods = list(self.deactivation_periods)
    now = datetime.now()
    if periods:
        for period in periods:
            if period.start_date < now:
                return False
    return True
active.short_description = _("Active")
active.boolean = True


class ScheduleCancelForm(forms.Form, FormAdminDjango):
    date = forms.DateTimeField(widget=AdminSplitDateTime(), initial=datetime.now)


class ConfirmCancelForm(forms.Form):
    date = forms.DateTimeField(widget=forms.HiddenInput())


class ScheduleDeactivationForm(forms.Form, FormAdminDjango):
    start_date = forms.DateTimeField(widget=AdminSplitDateTime(), initial=datetime.now)
    end_date = forms.DateTimeField(widget=AdminSplitDateTime(), required=False)


class ConfirmDeactivationForm(forms.Form):
    start_date = forms.DateTimeField(widget=forms.HiddenInput())
    end_date = forms.DateTimeField(widget=forms.HiddenInput(),required=False)


def schedule_deletion(modeladmin, request, queryset):
    return schedule(modeladmin, request, queryset, 
                    Form=ScheduleCancelForm, HiddenForm=ConfirmCancelForm, 
                    title=_("Schedule Deletion"), action_name='schedule_deletion',
                    set_method='set_cancel_date')
schedule_deletion.short_description = _("Schedule Deletion")

def schedule_deactivation(modeladmin, request, queryset):
    return schedule(modeladmin, request, queryset, 
                    Form=ScheduleDeactivationForm, HiddenForm=ConfirmDeactivationForm, 
                    title=_("Schedule Deactivation"), action_name='schedule_deactivation',
                    set_method='set_deactivation_period')
schedule_deactivation.short_description = _("Schedule Deactivation")


class ActiveFilter(SimpleListFilter):
    title = _('Active')
    parameter_name = 'scheduledesactivation'

    def lookups(self, request, model_admin):
        return (
            ('Yes', _('Yes')),
            ('No', _('No')),
        )

    def queryset(self, request, queryset):
        active_pks = []
        for obj in queryset:
            if active(obj): active_pks.append(obj.pk)
        if self.value() == 'Yes':
            return queryset.filter(pk__in=active_pks)
        if self.value() == 'No':
            return queryset.exclude(pk__in=active_pks)


for module in settings.SCHEDULING_SCHEDULABLE_MODELS:
    try: model = _import(module)
    except ImportError: continue
    insert_list_display(model, cancel_date)
    insert_list_display(model, active)
    insert_list_display(model, deactivation_periods)
    insert_action(model, schedule_deletion)
    insert_action(model, schedule_deactivation)
    insert_list_filter(model, ActiveFilter)
