from rest_framework import viewsets

from orchestra.api import router, LogApiMixin
from orchestra.contrib.accounts.api import AccountApiMixin

from .models import Contact
from .serializers import ContactSerializer


class ContactViewSet(LogApiMixin, AccountApiMixin, viewsets.ModelViewSet):
    model = Contact
    serializer_class = ContactSerializer


router.register(r'contacts', ContactViewSet)

