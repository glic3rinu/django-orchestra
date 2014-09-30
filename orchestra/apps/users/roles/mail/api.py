from rest_framework import viewsets

from orchestra.api import router
from orchestra.apps.accounts.api import AccountApiMixin

from .models import Address, Mailbox
from .serializers import AddressSerializer, MailboxSerializer


class AddressViewSet(AccountApiMixin, viewsets.ModelViewSet):
    model = Address
    serializer_class = AddressSerializer



class MailboxViewSet(viewsets.ModelViewSet):
    model = Mailbox
    serializer_class = MailboxSerializer
    
    def get_queryset(self):
        qs = super(MailboxViewSet, self).get_queryset()
        qs = qs.select_related('user')
        return qs.filter(user__account=self.request.user.account_id)


router.register(r'mailboxes', MailboxViewSet)
router.register(r'addresses', AddressViewSet)
