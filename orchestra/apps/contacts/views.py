from models import Contact
#from blog.serializers import CommentSerializer
from django.http import Http404
from djangorestframework.views import APIView
from djangorestframework.response import Response
from djangorestframework import status


class ContactSerializer(ModelSerializer):
    class Meta:
        model = Contact


class CommentRoot(generics.RootAPIView):
    model = Contact
    serializer_class = CommentSerializer

class CommentInstance(generics.InstanceAPIView):
    model = Contact
    serializer_class = CommentSerializer


