from rest_framework import viewsets

from orchestra.api import router, LogApiMixin
from orchestra.contrib.accounts.api import AccountApiMixin

from .models import PaymentSource, Transaction
from .serializers import PaymentSourceSerializer, TransactionSerializer


class PaymentSourceViewSet(LogApiMixin, AccountApiMixin, viewsets.ModelViewSet):
    serializer_class = PaymentSourceSerializer
    queryset = PaymentSource.objects.all()


class TransactionViewSet(LogApiMixin, viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()


router.register(r'payment-sources', PaymentSourceViewSet)
router.register(r'transactions', TransactionViewSet)
