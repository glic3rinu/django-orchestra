from rest_framework import viewsets

from orchestra.api import router
from orchestra.apps.accounts.api import AccountApiMixin

from .models import Address, Mailbox
from .serializers import AddressSerializer, MailboxSerializer


class AddressViewSet(AccountApiMixin, viewsets.ModelViewSet):
    model = Address
    serializer_class = AddressSerializer



class MailboxViewSet(AccountApiMixin, viewsets.ModelViewSet):
    model = Mailbox
    serializer_class = MailboxSerializer


router.register(r'mailboxes', MailboxViewSet)
router.register(r'addresses', AddressViewSet)
