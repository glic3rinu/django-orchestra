from django.contrib import admin
from django.conf.urls import include, url
from rest_framework.authtoken.views import obtain_auth_token

from orchestra.views import serve_private_media

from . import api
from .utils.apps import isinstalled


admin.autodiscover()
api.autodiscover()


urlpatterns = [
    # Admin
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    # REST API
    url(r'^api/', include(api.router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', obtain_auth_token, name='api-token-auth'),
    url(r'^media/(.+)/(.+)/(.+)/(.+)/(.+)$', serve_private_media, name='private-media'),
#    url(r'search', 'orchestra.views.search', name='search'),
]


if isinstalled('debug_toolbar'):
    import debug_toolbar
    urlpatterns.append(
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
