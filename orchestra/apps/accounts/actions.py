from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra.admin.decorators import action_with_confirmation
from orchestra.core import services


@transaction.atomic
@action_with_confirmation()
def disable(modeladmin, request, queryset):
    num = 0
    for account in queryset:
        account.disable()
        modeladmin.log_change(request, account, _("Disabled"))
        num += 1
    msg = ungettext(
        _("Selected account and related services has been disabled."),
        _("%s selected accounts and related services have been disabled.") % num,
        num)
    modeladmin.message_user(request, msg)
disable.url_name = 'disable'
disable.verbose_name = _("Disable")


def list_contacts(modeladmin, request, queryset):
    ids = queryset.values_list('id', flat=True)
    if not ids:
        message.warning(request, "Select at least one account.")
        return
    url = reverse('admin:contacts_contact_changelist')
    url += '?account__in=%s' % ','.join(map(str, ids))
    return redirect(url)
list_contacts.verbose_name = _("List contacts")


def service_report(modeladmin, request, queryset):
    accounts = []
    for account in queryset:
        items = []
        for service in services.get():
            if service != type(account):
                items.append((service._meta, service.objects.filter(account=account)))
        sorted(items, key=lambda i: i[0].verbose_name_plural.lower())
        accounts.append((account, items))
    context = {
        'accounts': accounts,
        'date': timezone.now().today()
    }
    return render(request, 'admin/accounts/account/service_report.html', context)
