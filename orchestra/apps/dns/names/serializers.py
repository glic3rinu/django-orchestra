from rest_framework import serializers

from .models import Name


class NameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Name
