from rest_framework import serializers

from orchestra.api import router

from .models import WebDatabase


class WebDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebDatabase
        fields = ('name', 'username', 'password', 'type')


router.insert(r'webs', 'webdatabases', WebDatabaseSerializer)
