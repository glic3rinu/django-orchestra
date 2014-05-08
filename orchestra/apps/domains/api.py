from rest_framework import viewsets
from rest_framework.decorators import link
from rest_framework.response import Response

from orchestra.api import router, collectionlink
from orchestra.apps.accounts.api import AccountApiMixin

from . import settings
from .models import Domain
from .serializers import DomainSerializer


class DomainViewSet(AccountApiMixin, viewsets.ModelViewSet):
    model = Domain
    serializer_class = DomainSerializer
    filter_fields = ('name',)
    
    def get_queryset(self):
        qs = super(DomainViewSet, self).get_queryset()
        return qs.prefetch_related('records')
    
    @collectionlink()
    def configuration(self, request):
        names = ['DOMAINS_DEFAULT_A', 'DOMAINS_DEFAULT_MX', 'DOMAINS_DEFAULT_NS']
        return Response({
            name: getattr(settings, name, None) for name in names
        })
    
    @link()
    def view_zone(self, request, pk=None):
        domain = self.get_object()
        return Response({'zone': domain.render_zone()})


router.register(r'domains', DomainViewSet)
