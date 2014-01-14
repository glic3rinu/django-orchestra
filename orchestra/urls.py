from __future__ import absolute_import

from django.contrib import admin
from django.conf.urls import patterns, include, url


admin.autodiscover()


urlpatterns = patterns('',
    # Admin
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
)
