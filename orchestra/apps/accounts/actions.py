from django.contrib import messages
from django.db import transaction
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra.admin.decorators import action_with_confirmation


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
