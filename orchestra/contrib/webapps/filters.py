from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from . import settings


class HasWebsiteListFilter(SimpleListFilter):
    title = _("Has website")
    parameter_name = 'has_website'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("True")),
            ('False', _("False")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(content__isnull=False)
        elif self.value() == 'False':
            return queryset.filter(content__isnull=True)
        return queryset


class PHPVersionListFilter(SimpleListFilter):
    title = _("PHP version")
    parameter_name = 'php_version'
    
    def lookups(self, request, model_admin):
        return settings.WEBAPPS_PHP_VERSIONS
    
    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(data__contains='"php_version":"%s"' % value)
        return queryset
