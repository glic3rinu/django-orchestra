from rest_framework import viewsets

from orchestra.api import router

from .models import Account
from .serializers import AccountSerializer


class AccountApiMixin(object):
    def get_queryset(self):
        qs = super(AccountApiMixin, self).get_queryset()
        return qs.filter(account=self.request.user.pk)


class AccountViewSet(viewsets.ModelViewSet):
    model = Account
    serializer_class = AccountSerializer
    singleton_pk = lambda _,request: request.user.pk
    
    def get_queryset(self):
        qs = super(AccountViewSet, self).get_queryset()
        return qs.filter(id=self.request.user)


router.register(r'accounts', AccountViewSet)
