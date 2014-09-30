from rest_framework import viewsets

from orchestra.api import router, SetPasswordApiMixin
from orchestra.apps.accounts.api import AccountApiMixin

from .models import SystemUser
from .serializers import SystemUserSerializer


class SystemUserViewSet(AccountApiMixin, SetPasswordApiMixin, viewsets.ModelViewSet):
    model = SystemUser
    serializer_class = SystemUserSerializer


router.register(r'systemusers', SystemUserViewSet)
