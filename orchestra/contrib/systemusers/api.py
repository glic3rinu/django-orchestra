from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, exceptions

from orchestra.api import router, SetPasswordApiMixin, LogApiMixin
from orchestra.contrib.accounts.api import AccountApiMixin

from .models import SystemUser
from .serializers import SystemUserSerializer


class SystemUserViewSet(LogApiMixin, AccountApiMixin, SetPasswordApiMixin, viewsets.ModelViewSet):
    queryset = SystemUser.objects.all()
    serializer_class = SystemUserSerializer
    filter_fields = ('username',)
    
    def destroy(self, request, pk=None):
        user = self.get_object()
        if user.is_main:
            raise exceptions.PermissionDenied(_("Main system user can not be deleted."))
        return super(SystemUserViewSet, self).destroy(request, pk=pk)


router.register(r'systemusers', SystemUserViewSet)
