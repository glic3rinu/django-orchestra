from rest_framework import viewsets

from orchestra.api import router, SetPasswordApiMixin, LogApiMixin
from orchestra.contrib.accounts.api import AccountApiMixin

from .models import Database, DatabaseUser
from .serializers import DatabaseSerializer, DatabaseUserSerializer


class DatabaseViewSet(LogApiMixin, AccountApiMixin, viewsets.ModelViewSet):
    queryset = Database.objects.prefetch_related('users').all()
    serializer_class = DatabaseSerializer
    filter_fields = ('name',)


class DatabaseUserViewSet(LogApiMixin, AccountApiMixin, SetPasswordApiMixin, viewsets.ModelViewSet):
    queryset = DatabaseUser.objects.prefetch_related('databases').all()
    serializer_class = DatabaseUserSerializer
    filter_fields = ('username',)


router.register(r'databases', DatabaseViewSet)
router.register(r'databaseusers', DatabaseUserViewSet)
