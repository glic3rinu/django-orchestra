from rest_framework import viewsets

from orchestra.api import router

from .models import Domain
from .serializers import DomainSerializer


class DomainViewSet(viewsets.ModelViewSet):
    model = Domain
    serializer_class = DomainSerializer


router.register(r'domains', DomainViewSet)


