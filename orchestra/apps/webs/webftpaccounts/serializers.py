from rest_framework import serializers

from orchestra.api import router

from .models import WebFTPAccount


class WebFTPAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebFTPAccount
        fields = ('username', 'password', 'directory')


router.insert(r'webs', 'webftpaccounts', WebFTPAccountSerializer, many=True)
