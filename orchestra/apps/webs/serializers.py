from rest_framework import serializers

from .models import Web


class WebSerializer(serializers.ModelSerializer):
    class Meta:
        model = Web
