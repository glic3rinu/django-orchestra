from rest_framework import viewsets

from orchestra.api import router

from .models import Entity, Contract
from .serializers import EntitySerializer, ContractSerializer


class EntityViewSet(viewsets.ModelViewSet):
    model = Entity
    serializer_class = EntitySerializer


class ContractViewSet(viewsets.ModelViewSet):
    model = Contract
    serializer_class = ContractSerializer


router.register(r'entities', EntityViewSet)
router.register(r'contracts', ContractViewSet)
