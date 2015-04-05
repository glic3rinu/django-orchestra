from rest_framework import viewsets

from orchestra.api import router, SetPasswordApiMixin, LogApiMixin
from orchestra.contrib.accounts.api import AccountApiMixin

from .models import Address, Mailbox
from .serializers import AddressSerializer, MailboxSerializer


class AddressViewSet(LogApiMixin, AccountApiMixin, viewsets.ModelViewSet):
    model = Address
    serializer_class = AddressSerializer



class MailboxViewSet(LogApiMixin, SetPasswordApiMixin, AccountApiMixin, viewsets.ModelViewSet):
    model = Mailbox
    serializer_class = MailboxSerializer


router.register(r'mailboxes', MailboxViewSet)
router.register(r'addresses', AddressViewSet)
