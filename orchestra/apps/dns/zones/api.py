from rest_framework import viewsets
from rest_framework.decorators import action

from orchestra.api import router

from .models import Zone
from .serializers import ZoneSerializer


class ZoneViewSet(viewsets.ModelViewSet):
    model = Zone
    serializer_class = ZoneSerializer
    
    @action()
    def reload(self, request, pk=None):
        pass


router.register(r'zones', ZoneViewSet)
