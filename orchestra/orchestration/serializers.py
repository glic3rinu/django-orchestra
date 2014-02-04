from rest_framework import serializers

from .models import Server


class ServerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Server
