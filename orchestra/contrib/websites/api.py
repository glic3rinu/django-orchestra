from rest_framework import viewsets

from orchestra.api import router, LogApiMixin
from orchestra.contrib.accounts.api import AccountApiMixin

from . import settings
from .models import Website
from .serializers import WebsiteSerializer


class WebsiteViewSet(LogApiMixin, AccountApiMixin, viewsets.ModelViewSet):
    queryset = Website.objects.prefetch_related('domains', 'content_set__webapp', 'directives').all()
    serializer_class = WebsiteSerializer
    filter_fields = ('name', 'domains__name')
    
    def options(self, request):
        metadata = super(WebsiteViewSet, self).options(request)
        names = ['WEBSITES_OPTIONS', 'WEBSITES_PORT_CHOICES']
        metadata.data['settings'] = {
            name.lower(): getattr(settings, name, None) for name in names
        }
        return metadata


router.register(r'websites', WebsiteViewSet)
