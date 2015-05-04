from django.contrib import admin
from django.conf import settings
from django.conf.urls import patterns, include, url

from . import api
from .utils.apps import isinstalled


admin.autodiscover()
api.autodiscover()


urlpatterns = patterns('',
    # Admin
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    # REST API
    url(r'^api/', include(api.router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/',
        'rest_framework.authtoken.views.obtain_auth_token',
        name='api-token-auth'
    ),
    # TODO make this private
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
        'show_indexes': True
    })
)


if isinstalled('debug_toolbar'):
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
