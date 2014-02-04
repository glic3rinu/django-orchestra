from rest_framework import viewsets

from orchestra.api import router

from .models import Server
from .serializers import ServerSerializer


class ServerViewSet(viewsets.ModelViewSet):
    model = Server
    serializer_class = ServerSerializer


router.register(r'servers', ServerViewSet)
