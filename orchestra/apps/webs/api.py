from rest_framework import viewsets
from rest_framework.decorators import action

from orchestra.api import router

from .models import Web
from .serializers import WebSerializer


class WebViewSet(viewsets.ModelViewSet):
    model = Web
    
    @action()
    def reload(self, request, pk=None):
        pass


router.register(r'webs', WebViewSet)
