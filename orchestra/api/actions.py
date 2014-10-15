from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import SetPasswordSerializer


class SetPasswordApiMixin(object):
    @action(serializer_class=SetPasswordSerializer)
    def set_password(self, request, pk):
        obj = self.get_object()
        data = request.DATA
        if isinstance(data, basestring):
            data = {
                'password': data
            }
        serializer = SetPasswordSerializer(data=data)
        if serializer.is_valid():
            obj.set_password(serializer.data['password'])
            try:
                obj.save(update_fields=['password'])
            except ValueError:
                # Some services don't store the password on the database
                # update_fields=[] doesn't trigger post save!
                obj.save()
            return Response({
                'status': 'password changed'
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
