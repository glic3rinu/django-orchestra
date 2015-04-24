from rest_framework import viewsets

from orchestra.api import router, LogApiMixin
from orchestra.contrib.accounts.api import AccountApiMixin

from . import settings
from .models import WebApp
from .options import AppOption
from .serializers import WebAppSerializer
from .types import AppType


class WebAppViewSet(LogApiMixin, AccountApiMixin, viewsets.ModelViewSet):
    queryset = WebApp.objects.prefetch_related('options').all()
    serializer_class = WebAppSerializer
    filter_fields = ('name',)
    
    def options(self, request):
        metadata = super(WebAppViewSet, self).options(request)
        names = [
            'WEBAPPS_BASE_DIR', 'WEBAPPS_TYPES', 'WEBAPPS_WEBAPP_OPTIONS',
            'WEBAPPS_PHP_DISABLED_FUNCTIONS', 'WEBAPPS_DEFAULT_TYPE'
        ]
        metadata.data['settings'] = {
            name.lower(): getattr(settings, name, None) for name in names
        }
        # AppTypes
        meta = self.metadata_class()
        app_types = {}
        for app_type in AppType.get_plugins():
            if app_type.serializer:
                data = meta.get_serializer_info(app_type.serializer())
            else:
                data = {}
            data['option_groups'] = app_type.option_groups
            app_types[app_type.get_name()] = data
        metadata.data['actions']['types'] = app_types
        # Options
        options = {}
        for option in AppOption.get_plugins():
            options[option.get_name()] = {
                'verbose_name': option.get_verbose_name(),
                'help_text': option.help_text,
                'group': option.group,
            }
        metadata.data['actions']['options'] = options
        return metadata


router.register(r'webapps', WebAppViewSet)
