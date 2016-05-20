from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.utils import change_url


def validate_contact(request, bill, error=True):
    """ checks if all the preconditions for bill generation are met """
    msg = _('{relation} account "{account}" does not have a declared invoice contact. '
            'You should <a href="{url}#invoicecontact-group">provide one</a>')
    valid = True
    send = messages.error if error else messages.warning
    if not hasattr(bill.account, 'billcontact'):
        account = force_text(bill.account)
        url = reverse('admin:accounts_account_change', args=(bill.account_id,))
        message = msg.format(relation=_("Related"), account=account, url=url)
        send(request, mark_safe(message))
        valid = False
    main = type(bill).account.field.rel.to.objects.get_main()
    if not hasattr(main, 'billcontact'):
        account = force_text(main)
        url = reverse('admin:accounts_account_change', args=(main.id,))
        message = msg.format(relation=_("Main"), account=account, url=url)
        send(request, mark_safe(message))
        valid = False
    return valid


def set_context_emails(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    bills = []
    for bill in queryset:
        emails = ', '.join(bill.get_billing_contact_emails())
        bills.append(format_html('{0}: <a href="{1}">{2}</a> <i>{3}</i>',
            capfirst(opts.verbose_name), change_url(bill), bill, emails)
        )
    return {
        'display_objects': bills
    }
