from rest_framework import viewsets

from orchestra.api import router

from .models import Entity, Contract


class EntityViewSet(viewsets.ReadOnlyModelViewSet):
    model = Entity


class ContractViewSet(viewsets.ReadOnlyModelViewSet):
    model = Contract


router.register(r'entities', EntityViewSet)
router.register(r'contracts', ContractViewSet)
