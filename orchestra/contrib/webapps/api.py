from rest_framework import viewsets

from orchestra.api import router, LogApiMixin
from orchestra.contrib.accounts.api import AccountApiMixin

from . import settings
from .models import WebApp
from .serializers import WebAppSerializer


class WebAppViewSet(LogApiMixin, AccountApiMixin, viewsets.ModelViewSet):
    queryset = WebApp.objects.all()
    serializer_class = WebAppSerializer
    filter_fields = ('name',)
    
    def options(self, request):
        metadata = super(WebAppViewSet, self).options(request)
        names = [
            'WEBAPPS_BASE_DIR', 'WEBAPPS_TYPES', 'WEBAPPS_WEBAPP_OPTIONS',
            'WEBAPPS_PHP_DISABLED_FUNCTIONS', 'WEBAPPS_DEFAULT_TYPE'
        ]
        metadata.data['settings'] = {
            name.lower(): getattr(settings, name, None) for name in names
        }
        return metadata


router.register(r'webapps', WebAppViewSet)
