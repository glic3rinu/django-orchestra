from django import template
from django.core.urlresolvers import reverse, NoReverseMatch
from django.forms import CheckboxInput

from orchestra import get_version
from orchestra.admin.utils import change_url
from orchestra.utils.apps import isinstalled


register = template.Library()


@register.filter(name='isinstalled')
def app_is_installed(app_name):
    return isinstalled(app_name)


@register.simple_tag(name="version")
def orchestra_version():
    return get_version()


@register.simple_tag(name="admin_url", takes_context=True)
def rest_to_admin_url(context):
    """ returns the admin equivelent url of the current REST API view """
    view = context['view']
    queryset = getattr(view, 'queryset', None)
    model = queryset.model if queryset else None
    url = 'admin:index'
    args = []
    if model:
        opts = model._meta
        url = 'admin:%s_%s' % (opts.app_label, opts.model_name)
        pk = view.kwargs.get(view.lookup_field)
        if pk:
            url += '_change'
            args = [pk]
        else:
            url += '_changelist'
    try:
        return reverse(url, args=args)
    except NoReverseMatch:
        return reverse('admin:index')


@register.filter
def size(value, length):
    value = str(value)[:int(length)]
    num_spaces = int(length) - len(str(value))
    return str(value) + (' '*num_spaces)


@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, CheckboxInput)


@register.filter
def admin_url(obj):
    return change_url(obj)


@register.filter
def isactive(obj):
    return getattr(obj, 'is_active', True)
