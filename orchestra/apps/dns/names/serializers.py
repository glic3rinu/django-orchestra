from rest_framework import serializers

from .models import Domain


class DomainSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Domain
