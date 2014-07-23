from rest_framework import viewsets

from orchestra.api import router
from orchestra.apps.accounts.api import AccountApiMixin

from .models import Bill
from .serializers import BillSerializer


class BillViewSet(AccountApiMixin, viewsets.ModelViewSet):
    model = Bill
    serializer_class = BillSerializer


router.register(r'bills', BillViewSet)
