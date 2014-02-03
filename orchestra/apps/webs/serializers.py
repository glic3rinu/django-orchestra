from rest_framework import serializers

from .models import Web


class WebSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Web
