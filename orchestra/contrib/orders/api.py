from rest_framework import viewsets

from orchestra.api import router
from orchestra.contrib.accounts.api import AccountApiMixin

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(AccountApiMixin, viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


router.register(r'orders', OrderViewSet)
