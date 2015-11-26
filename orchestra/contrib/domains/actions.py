import copy

from django.contrib import messages
from django.contrib.admin import helpers
from django.db.models import Q
from django.db.models.functions import Concat, Coalesce
from django.forms.models import modelformset_factory
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext, ugettext_lazy as _
from django.template.response import TemplateResponse

from orchestra.admin.utils import get_object_from_url, change_url, admin_link
from orchestra.utils.python import AttrDict

from .forms import RecordForm, RecordEditFormSet, SOAForm
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
view_zone.short_description = _("View zone")


def edit_records(modeladmin, request, queryset):
    selected_ids = queryset.values_list('id', flat=True)
    # Include subodmains
    queryset = queryset.model.objects.filter(
        Q(top__id__in=selected_ids) | Q(id__in=selected_ids)
    ).annotate(
        structured_id=Coalesce('top__id', 'id'),
        structured_name=Concat('top__name', 'name')
    ).order_by('-structured_id', 'structured_name')
    formsets = []
    for domain in queryset.prefetch_related('records'):
        modeladmin_copy = copy.copy(modeladmin)
        modeladmin_copy.model = Record
        prefix = '' if domain.is_top else '&nbsp;'*8
        context = {
            'url': change_url(domain),
            'name': prefix+domain.name,
            'title': '',
        }
        if domain.id not in selected_ids:
            context['name'] += '*'
            context['title'] = _("This subdomain was not explicitly selected "
                                 "but has been automatically added to this list.")
        link = '<a href="%(url)s" title="%(title)s">%(name)s</a>' % context
        modeladmin_copy.verbose_name_plural = mark_safe(link)
        RecordFormSet = modelformset_factory(
            Record, form=RecordForm, formset=RecordEditFormSet, extra=1, can_delete=True)
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
        'action_name': _("Edit records"),
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


def set_soa(modeladmin, request, queryset):
    if queryset.filter(top__isnull=False).exists():
        msg = _("Set SOA on subdomains is not possible.")
        modeladmin.message_user(request, msg, messages.ERROR)
        return
    form = SOAForm()
    if request.POST.get('post') == 'generic_confirmation':
        form = SOAForm(request.POST)
        if form.is_valid():
            updates = {name: value for name, value in form.cleaned_data.items() if value}
            change_message = _("SOA set %s") % str(updates)[1:-1]
            for domain in queryset:
                for name, value in updates.items():
                    if name.startswith('clear_'):
                        name = name.replace('clear_', '')
                        value = ''
                    setattr(domain, name, value)
                modeladmin.log_change(request, domain, change_message)
                domain.save()
            num = len(queryset)
            msg = ungettext(
                _("SOA record for one domain has been updated."),
                _("SOA record for %s domains has been updated.") % num,
                num
            )
            modeladmin.message_user(request, msg)
            return
    opts = modeladmin.model._meta
    context = {
        'title': _("Set SOA for selected domains"),
        'content_message': '',
        'action_name': _("Set SOA"),
        'action_value': 'set_soa',
        'display_objects': [admin_link('__str__')(domain) for domain in queryset],
        'queryset': queryset,
        'opts': opts,
        'app_label': opts.app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'form': form,
        'obj': get_object_from_url(modeladmin, request),
    }
    return render(request, 'admin/orchestra/generic_confirmation.html', context)
set_soa.short_description = _("Set SOA for selected domains")
