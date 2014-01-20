from rest_framework.routers import DefaultRouter

from .utils import autodiscover as module_autodiscover


# Create a router and register our viewsets with it.
router = DefaultRouter()

autodiscover = lambda: module_autodiscover('api')
