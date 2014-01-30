from rest_framework import viewsets

from orchestra.api import router

from .models import Name
from .serializers import NameSerializer


class NameViewSet(viewsets.ModelViewSet):
    model = Name
    serializer_class = NameSerializer


router.register(r'names', NameViewSet)


