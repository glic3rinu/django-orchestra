from rest_framework import viewsets
from rest_framework.response import Response

from orchestra.api import router
from orchestra.apps.accounts.api import AccountApiMixin

from . import settings
from .models import Website
from .serializers import WebsiteSerializer


class WebsiteViewSet(AccountApiMixin, viewsets.ModelViewSet):
    model = Website
    serializer_class = WebsiteSerializer
    filter_fields = ('name',)
    
    def metadata(self, request):
        ret = super(WebsiteViewSet, self).metadata(request)
        names = ['WEBSITES_OPTIONS', 'WEBSITES_PORT_CHOICES']
        ret['settings'] = {
            name.lower(): getattr(settings, name, None) for name in names
        }
        return ret


router.register(r'websites', WebsiteViewSet)
