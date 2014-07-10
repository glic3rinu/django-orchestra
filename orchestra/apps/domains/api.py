from rest_framework import viewsets
from rest_framework.decorators import link
from rest_framework.response import Response

from orchestra.api import router
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
    
    @link()
    def view_zone(self, request, pk=None):
        domain = self.get_object()
        return Response({
            'zone': domain.render_zone()
        })
    
    def metadata(self, request):
        ret = super(DomainViewSet, self).metadata(request)
        names = ['DOMAINS_DEFAULT_A', 'DOMAINS_DEFAULT_MX', 'DOMAINS_DEFAULT_NS']
        ret['settings'] = {
            name.lower(): getattr(settings, name, None) for name in names
        }
        return ret


router.register(r'domains', DomainViewSet)
