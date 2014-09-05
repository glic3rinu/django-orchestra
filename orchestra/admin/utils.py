from functools import wraps

from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.shortcuts import redirect
from django.utils import importlib
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.models.utils import get_field_value
from orchestra.utils.humanize import naturaldate

from .decorators import admin_field


def get_modeladmin(model, import_module=True):
    """ returns the modeladmin registred for model """
    for k,v in admin.site._registry.iteritems():
        if k is model:
            return v
    if import_module:
        # Sometimes the admin module is not yet imported
        app_label = model._meta.app_label
        for app in settings.INSTALLED_APPS:
            if app.endswith(app_label):
                app_label = app
        importlib.import_module('%s.%s' % (app_label, 'admin'))
        return get_modeladmin(model, import_module=False)


def insertattr(model, name, value, weight=0):
    """ Inserts attribute to a modeladmin """
    modeladmin = model
    if models.Model in model.__mro__:
        modeladmin = type(get_modeladmin(model))
    # Avoid inlines defined on parent class be shared between subclasses
    # Seems that if we use tuples they are lost in some conditions like changing
    # the tuple in modeladmin.__init__
    if not getattr(modeladmin, name):
        setattr(type(modeladmin), name, [])
    
    inserted_attrs = getattr(modeladmin, '__inserted_attrs__', {})
    if not name in inserted_attrs:
        weights = {}
        if hasattr(modeladmin, 'weights') and name in modeladmin.weights:
            weights = modeladmin.weights.get(name)
        inserted_attrs[name] = [
            (attr, weights.get(attr, 0)) for attr in getattr(modeladmin, name)
        ]
    
    inserted_attrs[name].append((value, weight))
    inserted_attrs[name].sort(key=lambda a: a[1])
    setattr(modeladmin, name, [ attr[0] for attr in inserted_attrs[name] ])
    setattr(modeladmin, '__inserted_attrs__', inserted_attrs)


def wrap_admin_view(modeladmin, view):
    """ Add admin authentication to view """
    @wraps(view)
    def wrapper(*args, **kwargs):
        return modeladmin.admin_site.admin_view(view)(*args, **kwargs)
    return wrapper


def set_url_query(request, key, value):
    """ set default filters for changelist_view """
    if key not in request.GET:
        request_copy = request.GET.copy()
        if callable(value):
            value = value(request)
        request_copy[key] = value
        request.GET = request_copy
        request.META['QUERY_STRING'] = request.GET.urlencode()


def action_to_view(action, modeladmin):
    """ Converts modeladmin action to view function """
    @wraps(action)
    def action_view(request, object_id=1, modeladmin=modeladmin, action=action):
        queryset = modeladmin.model.objects.filter(pk=object_id)
        response = action(modeladmin, request, queryset)
        if not response:
            opts = modeladmin.model._meta
            url = 'admin:%s_%s_change' % (opts.app_label, opts.module_name)
            return redirect(url, object_id)
        return response
    return action_view


@admin_field
def admin_link(*args, **kwargs):
    instance = args[-1]
    if kwargs['field'] in ['id', 'pk', '__unicode__']:
        obj = instance
    else:
        obj = get_field_value(instance, kwargs['field'])
    if not getattr(obj, 'pk', None):
        return '---'
    opts = obj._meta
    view_name = 'admin:%s_%s_change' % (opts.app_label, opts.model_name)
    url = reverse(view_name, args=(obj.pk,))
    extra = ''
    if kwargs['popup']:
        extra = 'onclick="return showAddAnotherPopup(this);"'
    return '<a href="%s" %s>%s</a>' % (url, extra, obj)


@admin_field
def admin_colored(*args, **kwargs):
    instance = args[-1]
    field = kwargs['field']
    value = escape(get_field_value(instance, field))
    color = kwargs.get('colors', {}).get(value, 'black')
    value = getattr(instance, 'get_%s_display' % field)().upper()
    colored_value = '<span style="color: %s;">%s</span>' % (color, value)
    if kwargs.get('bold', True):
        colored_value = '<b>%s</b>' % colored_value
    return mark_safe(colored_value)


@admin_field
def admin_date(*args, **kwargs):
    instance = args[-1]
    value = get_field_value(instance, kwargs['field'])
    if not value:
        return kwargs.get('default', '')
    return '<span title="{0}">{1}</span>'.format(
        escape(str(value)), escape(naturaldate(value)),
    )
