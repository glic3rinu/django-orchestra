from functools import update_wrapper

from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import importlib
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.models.utils import get_field_value
from orchestra.utils.time import timesince, timeuntil


def get_modeladmin(model, import_module=True):
    """ returns the modeladmin registred for model """
    for k,v in admin.site._registry.iteritems():
        if k is model:
            return type(v)
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
        modeladmin = get_modeladmin(model)
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
        inserted_attrs[name] = [ (attr, weights.get(attr, 0)) for attr in getattr(modeladmin, name) ]
    
    inserted_attrs[name].append((value, weight))
    inserted_attrs[name].sort(key=lambda a: a[1])
    setattr(modeladmin, name, [ attr[0] for attr in inserted_attrs[name] ])
    setattr(modeladmin, '__inserted_attrs__', inserted_attrs)


def wrap_admin_view(modeladmin, view):
    """ Add admin authentication to view """
    def wrapper(*args, **kwargs):
        return modeladmin.admin_site.admin_view(view)(*args, **kwargs)
    return update_wrapper(wrapper, view)


def set_default_filter(queryarg, request, value):
    """ set default filters for changelist_view """
    if queryarg not in request.GET:
        q = request.GET.copy()
        if callable(value):
            value = value(request)
        q[queryarg] = value
        request.GET = q
        request.META['QUERY_STRING'] = request.GET.urlencode()


def link(*args, **kwargs):
    """ utility function for creating admin links """
    field = args[0] if args else ''
    order = kwargs.pop('order', field)
    popup = kwargs.pop('popup', False)
    
    def display_link(self, instance):
        obj = getattr(instance, field, instance)
        if not getattr(obj, 'pk', False):
            return '---'
        opts = obj._meta
        view_name = 'admin:%s_%s_change' % (opts.app_label, opts.model_name)
        url = reverse(view_name, args=(obj.pk,))
        extra = ''
        if popup:
            extra = 'onclick="return showAddAnotherPopup(this);"'
        return '<a href="%s" %s>%s</a>' % (url, extra, obj)
    display_link.allow_tags = True
    display_link.short_description = _(field)
    display_link.admin_order_field = order
    return display_link


def colored(field_name, colours, description='', verbose=False, bold=True):
    """ returns a method that will render obj with colored html """
    def colored_field(obj, field=field_name, colors=colours, verbose=verbose):
        value = escape(get_field_value(obj, field))
        color = colors.get(value, "black")
        if verbose:
            # Get the human-readable value of a choice field
            value = getattr(obj, 'get_%s_display' % field)()
        colored_value = '<span style="color: %s;">%s</span>' % (color, value)
        if bold:
            colored_value = '<b>%s</b>' % colored_value
        return mark_safe(colored_value)
    if not description:
        description = field_name.split('__').pop().replace('_', ' ').capitalize()
    colored_field.short_description = description
    colored_field.allow_tags = True
    colored_field.admin_order_field = field_name
    return colored_field


def display_timesince(date, double=False):
    """ 
    Format date for messages create_on: show a relative time
    with contextual helper to show fulltime format.
    """
    if not date:
        return 'Never'
    date_rel = timesince(date)
    if not double:
        date_rel = date_rel.split(',')[0]  
    date_rel += ' ago'
    date_abs = date.strftime("%Y-%m-%d %H:%M:%S %Z")
    return mark_safe("<span title='%s'>%s</span>" % (date_abs, date_rel))


def display_timeuntil(date):
    date_rel = timeuntil(date) + ' left'
    date_abs = date.strftime("%Y-%m-%d %H:%M:%S %Z")
    return mark_safe("<span title='%s'>%s</span>" % (date_abs, date_rel))
