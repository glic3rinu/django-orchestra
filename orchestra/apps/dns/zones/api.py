from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from orchestra.api import router, list_link

from . import settings
from .models import Zone
from .serializers import ZoneSerializer


class ZoneViewSet(viewsets.ModelViewSet):
    model = Zone
    serializer_class = ZoneSerializer
    
    @action()
    def reload(self, request, pk=None):
        pass
    
    @list_link()
    def configuration(self, request):
        return Response({
            'DNS_ZONE_DEFAULT_RECORDS': settings.DNS_ZONE_DEFAULT_RECORDS
        })


router.register(r'zones', ZoneViewSet)
