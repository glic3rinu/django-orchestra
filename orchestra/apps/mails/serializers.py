from rest_framework import serializers

from .models import MailDomain, MailAlias


class MailDomainSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MailDomain


class MailAliasSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MailAlias
