from django import template

from orchestra import get_version


register = template.Library()


@register.simple_tag(name="version")
def controller_version():
    return get_version()
