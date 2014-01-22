from rest_framework import viewsets

from orchestra.api import router

from .models import Zone
from .serializers import ZoneSerializer


class ZoneViewSet(viewsets.ModelViewSet):
    model = Zone
    serializer_class = ZoneSerializer


router.register(r'zones', ZoneViewSet)
