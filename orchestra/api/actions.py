from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import SetPasswordSerializer


class SetPasswordApiMixin(object):
    @action(serializer_class=SetPasswordSerializer)
    def set_password(self, request, pk):
        obj = self.get_object()
        serializer = SetPasswordSerializer(data=request.DATA)
        if serializer.is_valid():
            obj.set_password(serializer.data['password'])
            obj.save()
            return Response({'status': 'password changed'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
