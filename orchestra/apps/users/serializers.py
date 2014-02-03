from django.contrib.auth.models import User
from rest_framework import serializers



class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            'url', 'id', 'username', 'is_superuser', 'first_name', 'last_name',
            'email', 'is_staff', 'is_active'
        ]
