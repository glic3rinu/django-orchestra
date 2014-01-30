from __future__ import absolute_import

from django.contrib import admin
from django.conf import settings
from django.conf.urls import patterns, include, url

from . import api


admin.autodiscover()
api.autodiscover()

urlpatterns = patterns('',
    # Admin
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    # REST API
    url(r'^api/', include(api.router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )