from django.contrib.auth import get_user_model
from rest_framework import viewsets

from orchestra.api import router, SetPasswordApiMixin
from orchestra.apps.accounts.api import AccountApiMixin

from .serializers import UserSerializer


class UserViewSet(AccountApiMixin, SetPasswordApiMixin, viewsets.ModelViewSet):
    model = get_user_model()
    serializer_class = UserSerializer


router.register(r'users', UserViewSet)
