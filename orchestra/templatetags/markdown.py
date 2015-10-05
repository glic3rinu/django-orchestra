from django import template
from markdown import markdown


register = template.Library()


@register.filter(name='markdown')
def do_markdown(text):
    return markdown(text)
