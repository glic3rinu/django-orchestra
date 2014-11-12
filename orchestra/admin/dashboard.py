from django.conf import settings

from orchestra.core import services


def generate_services_group():
    models = []
    for model, options in services.get().iteritems():
        if options.get('menu', True):
            models.append("%s.%s" % (model.__module__, model._meta.object_name))
    
    settings.FLUENT_DASHBOARD_APP_GROUPS += (
        ('Services', {
            'models': models,
            'collapsible': True,
        }),
    )


generate_services_group()
