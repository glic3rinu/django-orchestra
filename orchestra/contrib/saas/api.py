from rest_framework import viewsets

from orchestra.api import router, LogApiMixin
from orchestra.contrib.accounts.api import AccountApiMixin

from .models import SaaS
from .serializers import SaaSSerializer


class SaaSViewSet(LogApiMixin, AccountApiMixin, viewsets.ModelViewSet):
    queryset = SaaS.objects.all()
    serializer_class = SaaSSerializer
    filter_fields = ('name',)


router.register(r'saas', SaaSViewSet)
