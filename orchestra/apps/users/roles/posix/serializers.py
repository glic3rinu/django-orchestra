from rest_framework import serializers

from orchestra.api import router

from .models import POSIX


class POSIXSerializer(serializers.ModelSerializer):
    class Meta:
        model = POSIX
        fields = ('home', 'shell')


router.insert('users', 'posix', POSIXSerializer, required=False)
