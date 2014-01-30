from rest_framework import viewsets

from orchestra.api import router

from .models import MailDomain, Mailbox, MailAlias
from .serializers import MailDomainSerializer, MailAliasSerializer


class MailDomainViewSet(viewsets.ModelViewSet):
    model = MailDomain
    serializer_class = MailDomainSerializer


class MailboxViewSet(viewsets.ModelViewSet):
    model = Mailbox


class MailAliasViewSet(viewsets.ModelViewSet):
    model = MailAlias
    serializer_class = MailAliasSerializer


router.register(r'maildomains', MailDomainViewSet)
router.register(r'mailboxes', MailboxViewSet)
router.register(r'mailaliases', MailAliasViewSet)


