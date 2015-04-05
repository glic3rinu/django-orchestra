from rest_framework import viewsets

from orchestra.api import router, SetPasswordApiMixin
from orchestra.contrib.accounts.api import AccountApiMixin

from .models import Database, DatabaseUser
from .serializers import DatabaseSerializer, DatabaseUserSerializer


class DatabaseViewSet(AccountApiMixin, viewsets.ModelViewSet):
    model = Database
    serializer_class = DatabaseSerializer
    filter_fields = ('name',)


class DatabaseUserViewSet(AccountApiMixin, SetPasswordApiMixin, viewsets.ModelViewSet):
    model = DatabaseUser
    serializer_class = DatabaseUserSerializer
    filter_fields = ('username',)


router.register(r'databases', DatabaseViewSet)
router.register(r'databaseusers', DatabaseUserViewSet)
