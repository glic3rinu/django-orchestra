from rest_framework import serializers

from orchestra.api import router

from .models import Database


class DatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Database
        fields = ('name', 'username', 'password', 'type')


router.insert(r'webs', 'databases', DatabaseSerializer)
