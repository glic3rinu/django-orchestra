from rest_framework import viewsets

from orchestra.api import router
from orchestra.apps.accounts.api import AccountApiMixin

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(AccountApiMixin, viewsets.ModelViewSet):
    model = Order
    serializer_class = OrderSerializer

router.register(r'orders', OrderViewSet)
