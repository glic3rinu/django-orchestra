import datetime
import json
import re

from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, NoReverseMatch
from django.forms import CheckboxInput
from django.template.base import Node
from django.template.defaultfilters import date
from django.utils.safestring import mark_safe

from orchestra import get_version
from orchestra.admin.utils import change_url, admin_link as utils_admin_link
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


class OneLinerNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        line = self.nodelist.render(context).replace('\n', ' ')
        return re.sub(r'\s\s+', '', line)


@register.tag
def oneliner(parser, token):
    nodelist = parser.parse(('endoneliner',))
    parser.delete_first_token()
    return OneLinerNode(nodelist)


@register.filter
def size(value, length):
    value = str(value)[:int(length)]
    num_spaces = int(length) - len(str(value))
    return str(value) + (' '*num_spaces)


@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, CheckboxInput)


@register.filter
def content_type_id(label):
    app_label, model = label.split('.')
    return ContentType.objects.filter(app_label=app_label, model=model).values_list('id', flat=True)[0]


@register.filter
def split(value, sep=' '):
    parts = value.split(sep)
    return (parts[0], sep.join(parts[1:]))


@register.filter
def admin_url(obj):
    return change_url(obj)


@register.filter
def admin_link(obj):
    try:
        url = change_url(obj)
    except NoReverseMatch:
        return str(obj)
    return mark_safe('<a href="%s">%s</a>' % (url, obj))


@register.filter
def isactive(obj):
    return getattr(obj, 'is_active', True)


@register.filter
def sub(value, arg):
    return value - arg


@register.filter
def mul(value, arg):
    return value * arg


@register.filter
def as_json(obj, *args):
    indent = args[0] if args else None
    def default(obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return date(obj)
        return obj
    return mark_safe(json.dumps(obj, indent=indent, default=default))
