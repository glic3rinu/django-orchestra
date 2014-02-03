from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import action

from orchestra.api import router

from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    model = User
    serializer_class = UserSerializer
    
    @action()
    def change_password(self, request, pk=None):
        pass


router.register(r'users', UserViewSet)
