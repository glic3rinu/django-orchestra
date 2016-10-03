from functools import partial, wraps

from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.admin.utils import NestedObjects, quote
from django.contrib.auth import get_permission_codename
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import router
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.text import capfirst
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra.core import services

from . import settings


def list_contacts(modeladmin, request, queryset):
    ids = queryset.order_by().values_list('id', flat=True).distinct()
    if not ids:
        messages.warning(request, "Select at least one account.")
        return
    url = reverse('admin:contacts_contact_changelist')
    url += '?account__in=%s' % ','.join(map(str, ids))
    return redirect(url)
list_contacts.short_description = _("List contacts")


def list_accounts(modeladmin, request, queryset):
    accounts = queryset.order_by().values_list('account_id', flat=True).distinct()
    if not accounts:
        messages.warning(request, "Select at least one instance.")
        return
    url = reverse('admin:contacts_contact_changelist')
    url += '?id__in=%s' % ','.join(map(str, accounts))
    return redirect(url)
list_accounts.short_description = _("List accounts")


def service_report(modeladmin, request, queryset):
    # TODO resources
    accounts = []
    fields = []
    registered_services = services.get()
    # First we get related manager names to fire a prefetch related
    for name, field in queryset.model._meta.fields_map.items():
        model = field.related_model
        if model in registered_services and model != queryset.model:
            fields.append((model, name))
    fields = sorted(fields, key=lambda f: f[0]._meta.verbose_name_plural.lower())
    fields = [field for model, field in fields]
    
    for account in queryset.prefetch_related(*fields):
        items = []
        for field in fields:
            related_manager = getattr(account, field)
            items.append((related_manager.model._meta, related_manager.all()))
        accounts.append((account, items))
    
    context = {
        'accounts': accounts,
        'date': timezone.now().today()
    }
    return render(request, settings.ACCOUNTS_SERVICE_REPORT_TEMPLATE, context)


def delete_related_services(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    using = router.db_for_write(modeladmin.model)
    collector = NestedObjects(using=using)
    collector.collect(queryset)
    registered_services = services.get()
    related_services = []
    to_delete = []
    
    admin_site = modeladmin.admin_site
    
    def format(obj, account=False):
        has_admin = obj.__class__ in admin_site._registry
        opts = obj._meta
        no_edit_link = '%s: %s' % (capfirst(opts.verbose_name), force_text(obj))
        
        if has_admin:
            try:
                admin_url = reverse(
                    'admin:%s_%s_change' % (opts.app_label, opts.model_name),
                    None, (quote(obj._get_pk_val()),)
                )
            except NoReverseMatch:
                # Change url doesn't exist -- don't display link to edit
                return no_edit_link
            
            # Display a link to the admin page.
            context = (capfirst(opts.verbose_name), admin_url, obj)
            if account:
                context += (_("services to delete:"),)
                return format_html('{} <a href="{}">{}</a> {}', *context)
            return format_html('{}: <a href="{}">{}</a>', *context)
        else:
            # Don't display link to edit, because it either has no
            # admin or is edited inline.
            return no_edit_link
    
    def format_nested(objs, result):
        if isinstance(objs, list):
            current = []
            for obj in objs:
                format_nested(obj, current)
            result.append(current)
        else:
            result.append(format(objs))
    
    for nested in collector.nested():
        if isinstance(nested, list):
            # Is lists of objects
            current = []
            is_service = False
            for service in nested:
                if type(service) in registered_services:
                    if service == main_systemuser:
                        continue
                    current.append(format(service))
                    to_delete.append(service)
                    is_service = True
                elif is_service and isinstance(service, list):
                    nested = []
                    format_nested(service, nested)
                    current.append(nested[0])
                    is_service = False
                else:
                    is_service = False
            related_services.append(current)
        elif isinstance(nested, modeladmin.model):
            # Is account
            # Prevent the deletion of the main system user, which will delete the account
            main_systemuser = nested.main_systemuser
            related_services.append(format(nested, account=True))
    
    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.
    if request.POST.get('post'):
        accounts = len(queryset)
        msg = _("Related services deleted and account disabled.")
        for account in queryset:
            account.is_active = False
            account.save(update_fields=('is_active',))
            modeladmin.log_change(request, account, msg)
        if accounts:
            relateds = len(to_delete)
            for obj in to_delete:
                obj_display = force_text(obj)
                modeladmin.log_deletion(request, obj, obj_display)
                obj.delete()
            context = {
                'accounts': accounts,
                'relateds': relateds,
            }
            msg = _("Successfully disabled %(accounts)d account and deleted %(relateds)d related services.") % context
            modeladmin.message_user(request, msg, messages.SUCCESS)
        # Return None to display the change list page again.
        return None
    
    if len(queryset) == 1:
        objects_name = force_text(opts.verbose_name)
    else:
        objects_name = force_text(opts.verbose_name_plural)
    
    model_count = {}
    for model, objs in collector.model_objs.items():
        count = 0
        # discount main systemuser
        if model is modeladmin.model.main_systemuser.field.rel.to:
            count = len(objs) - 1
        # Discount account
        elif model is not modeladmin.model and model in registered_services:
            count = len(objs)
        if count:
            model_count[model._meta.verbose_name_plural] = count
    if not model_count:
        modeladmin.message_user(request, _("Nothing to delete"), messages.WARNING)
        return None
    context = dict(
        admin_site.each_context(request),
        title=_("Are you sure?"),
        objects_name=objects_name,
        deletable_objects=[related_services],
        model_count=dict(model_count).items(),
        queryset=queryset,
        opts=opts,
        action_checkbox_name=helpers.ACTION_CHECKBOX_NAME,
    )
    request.current_app = admin_site.name
    # Display the confirmation page
    template = 'admin/%s/%s/delete_related_services_confirmation.html' % (app_label, opts.model_name)
    return TemplateResponse(request, template, context)
delete_related_services.short_description = _("Delete related services")


def disable_selected(modeladmin, request, queryset, disable=True):
    opts = modeladmin.model._meta
    app_label = opts.app_label
    verbose_action_name = _("disabled") if disable else _("enabled")
    # The user has already confirmed the deletion.
    # Do the disable and return a None to display the change list view again.
    if request.POST.get('post'):
        n = 0
        for account in queryset:
            account.disable() if disable else account.enable()
            modeladmin.log_change(request, account, verbose_action_name.capitalize())
            n += 1
        modeladmin.message_user(request, ungettext(
            _("One account has been successfully %s.") % verbose_action_name,
            _("%i accounts have been successfully %s.") % (n, verbose_action_name),
            n)
        )
        return None
    
    user = request.user
    admin_site = modeladmin.admin_site
    
    def format(obj):
        has_admin = obj.__class__ in admin_site._registry
        opts = obj._meta
        no_edit_link = '%s: %s' % (capfirst(opts.verbose_name), force_text(obj))
        if has_admin:
            try:
                admin_url = reverse(
                    'admin:%s_%s_change' % (opts.app_label, opts.model_name),
                    None,
                    (quote(obj._get_pk_val()),)
                )
            except NoReverseMatch:
                # Change url doesn't exist -- don't display link to edit
                return no_edit_link
            
            p = '%s.%s' % (opts.app_label, get_permission_codename('delete', opts))
            if not user.has_perm(p):
                perms_needed.add(opts.verbose_name)
            # Display a link to the admin page.
            context = (capfirst(opts.verbose_name), admin_url, obj)
            return format_html('{}: <a href="{}">{}</a>', *context)
        else:
            # Don't display link to edit, because it either has no
            # admin or is edited inline.
            return no_edit_link
    
    display = []
    for account in queryset:
        current = []
        for related in account.get_services_to_disable():
            current.append(format(related))
        display.append([format(account), current])
    
    if len(queryset) == 1:
        objects_name = force_text(opts.verbose_name)
    else:
        objects_name = force_text(opts.verbose_name_plural)
    
    context = dict(
        admin_site.each_context(request),
        action_name='disable_selected' if disable else 'enable_selected',
        disable=disable,
        title=_("Are you sure?"),
        objects_name=objects_name,
        deletable_objects=display,
        queryset=queryset,
        opts=opts,
        action_checkbox_name=helpers.ACTION_CHECKBOX_NAME,
    )
    request.current_app = admin_site.name
    template = 'admin/%s/%s/disable_selected_confirmation.html' % (app_label, opts.model_name)
    return TemplateResponse(request, template, context)
disable_selected.short_description = _("Disable selected accounts")
disable_selected.url_name = 'disable'
disable_selected.tool_description = _("Disable")


enable_selected = partial(disable_selected, disable=False)
enable_selected.__name__ = 'enable_selected'
enable_selected.url_name = 'enable'
enable_selected.tool_description = _("Enable")
