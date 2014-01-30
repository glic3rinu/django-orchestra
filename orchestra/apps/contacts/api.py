from rest_framework import viewsets

from orchestra.api import router

from .models import Contact, Contract
from .serializers import ContactSerializer, ContractSerializer


class ContactViewSet(viewsets.ModelViewSet):
    model = Contact
    serializer_class = ContactSerializer


class ContractViewSet(viewsets.ModelViewSet):
    model = Contract
    serializer_class = ContractSerializer


router.register(r'contacts', ContactViewSet)
router.register(r'contracts', ContractViewSet)
