from rest_framework import viewsets

from orchestra.api import router
from orchestra.apps.accounts.api import AccountApiMixin

from .models import Contact, InvoiceContact
from .serializers import ContactSerializer, InvoiceContactSerializer


class ContactViewSet(AccountApiMixin, viewsets.ModelViewSet):
    model = Contact
    serializer_class = ContactSerializer


class InvoiceContactViewSet(AccountApiMixin, viewsets.ModelViewSet):
    model = InvoiceContact
    serializer_class = InvoiceContactSerializer


router.register(r'contacts', ContactViewSet)
router.register(r'invoicecontacts', InvoiceContactViewSet)
