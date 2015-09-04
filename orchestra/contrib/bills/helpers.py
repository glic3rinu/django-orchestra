from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


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

