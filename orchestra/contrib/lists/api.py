from rest_framework import viewsets

from orchestra.api import router, SetPasswordApiMixin, LogApiMixin
from orchestra.contrib.accounts.api import AccountApiMixin

from .models import List
from .serializers import ListSerializer


class ListViewSet(LogApiMixin, AccountApiMixin, SetPasswordApiMixin, viewsets.ModelViewSet):
    queryset = List.objects.all()
    serializer_class = ListSerializer
    filter_fields = ('name', 'address_domain')


router.register(r'lists', ListViewSet)
