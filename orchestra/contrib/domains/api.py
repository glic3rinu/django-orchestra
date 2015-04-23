from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from orchestra.api import router
from orchestra.contrib.accounts.api import AccountApiMixin

from . import settings
from .models import Domain
from .serializers import DomainSerializer


class DomainViewSet(AccountApiMixin, viewsets.ModelViewSet):
    serializer_class = DomainSerializer
    filter_fields = ('name',)
    queryset = Domain.objects.all()
    
    def get_queryset(self):
        qs = super(DomainViewSet, self).get_queryset()
        return qs.prefetch_related('records')
    
    @detail_route()
    def view_zone(self, request, pk=None):
        domain = self.get_object()
        return Response({
            'zone': domain.render_zone()
        })
    
    def options(self, request):
        metadata = super(DomainViewSet, self).options(request)
        names = ['DOMAINS_DEFAULT_A', 'DOMAINS_DEFAULT_MX', 'DOMAINS_DEFAULT_NS']
        metadata.data['settings'] = {
            name.lower(): getattr(settings, name, None) for name in names
        }
        return metadata


router.register(r'domains', DomainViewSet)
