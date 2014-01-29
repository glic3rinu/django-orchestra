from rest_framework import serializers

from orchestra.api import router

from .models import FTP


class FTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = FTP
        fields = ('username', 'password', 'directory')


router.insert(r'webs', 'ftps', FTPSerializer)
