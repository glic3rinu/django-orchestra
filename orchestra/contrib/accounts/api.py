from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, exceptions

from orchestra.api import router, SetPasswordApiMixin, LogApiMixin

from .models import Account
from .serializers import AccountSerializer


class AccountApiMixin(object):
    def get_queryset(self):
        qs = super(AccountApiMixin, self).get_queryset()
        return qs.filter(account=self.request.user.pk)


class AccountViewSet(LogApiMixin, SetPasswordApiMixin, viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    singleton_pk = lambda _,request: request.user.pk
    
    def get_queryset(self):
        qs = super(AccountViewSet, self).get_queryset()
        return qs.filter(id=self.request.user.pk)
    
    def destroy(self, request, pk=None):
        # TODO reimplement in permissions
        if not request.user.is_superuser:
            raise exceptions.PermissionDenied(_("Accounts can not be deleted."))
        return super(AccountViewSet, self).destroy(request, pk=pk)


router.register(r'accounts', AccountViewSet)
