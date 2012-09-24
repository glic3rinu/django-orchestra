from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'orchestra.views.home', name='home'),
    # url(r'^orchestra/', include('orchestra.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),

    # django-rest-framework browsable API
    url(r'^api-auth/', include('djangorestframework.urls', namespace='djangorestframework')),
    
    url(r'^contacts/', include('contacts.urls')),
)
