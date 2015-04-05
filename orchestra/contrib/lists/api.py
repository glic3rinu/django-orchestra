from rest_framework import viewsets

from orchestra.api import router, SetPasswordApiMixin
from orchestra.contrib.accounts.api import AccountApiMixin

from .models import List
from .serializers import ListSerializer


class ListViewSet(AccountApiMixin, SetPasswordApiMixin, viewsets.ModelViewSet):
    model = List
    serializer_class = ListSerializer
    filter_fields = ('name',)


router.register(r'lists', ListViewSet)
