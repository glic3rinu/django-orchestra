from rest_framework import viewsets

from orchestra.api import router, LogApiMixin
from orchestra.contrib.accounts.api import AccountApiMixin

from .models import PaymentSource, Transaction
from .serializers import PaymentSourceSerializer, TransactionSerializer


class PaymentSourceViewSet(LogApiMixin, AccountApiMixin, viewsets.ModelViewSet):
    model = PaymentSource
    serializer_class = PaymentSourceSerializer


class TransactionViewSet(LogApiMixin, viewsets.ModelViewSet):
    model = Transaction
    serializer_class = TransactionSerializer


router.register(r'payment-sources', PaymentSourceViewSet)
router.register(r'transactions', TransactionViewSet)
