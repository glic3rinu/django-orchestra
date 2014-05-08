from rest_framework import viewsets
from rest_framework.response import Response

from orchestra.api import router, collectionlink
from orchestra.apps.accounts.api import AccountApiMixin

from . import settings
from .models import WebApp
from .serializers import WebAppSerializer


class WebAppViewSet(AccountApiMixin, viewsets.ModelViewSet):
    model = WebApp
    serializer_class = WebAppSerializer
    filter_fields = ('name',)
    
    @collectionlink()
    def configuration(self, request):
        names = [
            'WEBAPPS_BASE_ROOT', 'WEBAPPS_TYPES', 'WEBAPPS_WEBAPP_OPTIONS',
            'WEBAPPS_PHP_DISABLED_FUNCTIONS', 'WEBAPPS_DEFAULT_TYPE'
        ]
        return Response({
            name: getattr(settings, name, None) for name in names
        })


router.register(r'webapps', WebAppViewSet)
