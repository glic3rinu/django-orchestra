import copy

from django.contrib.admin import helpers
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext, ugettext_lazy as _
from django.template.response import TemplateResponse

from orchestra.admin.forms import adminmodelformset_factory
from orchestra.admin.utils import get_object_from_url, change_url
from orchestra.utils.python import AttrDict

from .forms import RecordForm, RecordEditFormSet
from .models import Record


def view_zone(modeladmin, request, queryset):
    zone = queryset.get()
    context = {
        'opts': modeladmin.model._meta,
        'object': zone,
        'title': _("%s zone content") % zone.origin.name
    }
    return TemplateResponse(request, 'admin/domains/domain/view_zone.html', context)
view_zone.url_name = 'view-zone'
view_zone.verbose_name = _("View zone")


def edit_records(modeladmin, request, queryset):
    formsets = []
    for domain in queryset.prefetch_related('records'):
        modeladmin_copy = copy.copy(modeladmin)
        modeladmin_copy.model = Record
        link = '<a href="%s">%s</a>' % (change_url(domain), domain.name)
        modeladmin_copy.verbose_name_plural = mark_safe(link)
        RecordFormSet = adminmodelformset_factory(
            modeladmin_copy, RecordForm, formset=RecordEditFormSet, extra=1, can_delete=True)
        formset = RecordFormSet(queryset=domain.records.all(), prefix=domain.id)
        formset.instance = domain
        formset.cls = RecordFormSet
        formsets.append(formset)
    
    if request.POST.get('post') == 'generic_confirmation':
        posted_formsets = []
        all_valid = True
        for formset in formsets:
            instance = formset.instance
            formset = formset.cls(
                request.POST, request.FILES, queryset=formset.queryset, prefix=instance.id)
            formset.instance = instance
            if not formset.is_valid():
                all_valid = False
            posted_formsets.append(formset)
        formsets = posted_formsets
        if all_valid:
            for formset in formsets:
                for form in formset.forms:
                    form.instance.domain_id = formset.instance.id
                formset.save()
                fake_form = AttrDict({
                    'changed_data': False
                })
                change_message = modeladmin.construct_change_message(request, fake_form, [formset])
                modeladmin.log_change(request, formset.instance, change_message)
            num = len(formsets)
            message = ungettext(
                _("Records for one selected domain have been updated."),
                _("Records for %i selected domains have been updated.") % num,
                num)
            modeladmin.message_user(request, message)
            return
    
    opts = modeladmin.model._meta
    context = {
        'title': _("Edit records"),
        'action_name': 'Edit records',
        'action_value': 'edit_records',
        'display_objects': [],
        'queryset': queryset,
        'opts': opts,
        'app_label': opts.app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'formsets': formsets,
        'obj': get_object_from_url(modeladmin, request),
    }
    return render(request, 'admin/domains/domain/edit_records.html', context)


def add_records(modeladmin, request, queryset):
    # TODO
    pass
