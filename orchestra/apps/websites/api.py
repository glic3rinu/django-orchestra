from rest_framework import viewsets
from rest_framework.response import Response

from orchestra.api import router, collectionlink
from orchestra.apps.accounts.api import AccountApiMixin

from . import settings
from .models import Website
from .serializers import WebsiteSerializer


class WebsiteViewSet(AccountApiMixin, viewsets.ModelViewSet):
    model = Website
    serializer_class = WebsiteSerializer
    filter_fields = ('name',)
    
    @collectionlink()
    def configuration(self, request):
        names = ['WEBSITES_OPTIONS', 'WEBSITES_PORT_CHOICES']
        return Response({
            name: getattr(settings, name, None) for name in names
        })


router.register(r'websites', WebsiteViewSet)
