from functools import wraps, partial

from django.contrib import messages
from django.contrib.admin import helpers
from django.core.exceptions import ValidationError
from django.template.response import TemplateResponse
from django.utils.decorators import available_attrs
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _


def admin_field(method):
    """ Wraps a function to be used as a ModelAdmin method field """
    def admin_field_wrapper(*args, **kwargs):
        """ utility function for creating admin links """
        kwargs['field'] = args[0] if args else '__str__'
        kwargs['order'] = kwargs.get('order', kwargs['field'])
        kwargs['popup'] = kwargs.get('popup', False)
        # TODO get field verbose name
        kwargs['short_description'] = kwargs.get('short_description',
                kwargs['field'].split('__')[-1].replace('_', ' ').capitalize())
        admin_method = partial(method, **kwargs)
        admin_method.short_description = kwargs['short_description']
        admin_method.allow_tags = True
        admin_method.admin_order_field = kwargs['order']
        return admin_method
    return admin_field_wrapper


def format_display_objects(modeladmin, request, queryset):
    from .utils import change_url
    opts = modeladmin.model._meta
    objects = []
    for obj in queryset:
        objects.append(format_html('{0}: <a href="{1}">{2}</a>',
                capfirst(opts.verbose_name), change_url(obj), obj)
        )
    return objects


def action_with_confirmation(action_name=None, extra_context=None, validator=None,
                             template='admin/orchestra/generic_confirmation.html'):
    """ 
    Generic pattern for actions that needs confirmation step
    If custom template is provided the form must contain:
    <input type="hidden" name="post" value="generic_confirmation" />
    """
    
    def decorator(func, extra_context=extra_context, template=template, action_name=action_name, validatior=validator):
        @wraps(func, assigned=available_attrs(func))
        def inner(modeladmin, request, queryset, action_name=action_name, extra_context=extra_context, validator=validator):
            if validator is not None:
                try:
                    validator(queryset)
                except ValidationError as e:
                    messages.error(request, '<br>'.join(e))
                    return
            # The user has already confirmed the action.
            if request.POST.get('post') == 'generic_confirmation':
                stay = func(modeladmin, request, queryset)
                if not stay:
                    return
            
            opts = modeladmin.model._meta
            app_label = opts.app_label
            action_value = func.__name__
            
            if len(queryset) == 1:
                objects_name = force_text(opts.verbose_name)
                obj = queryset.get()
            else:
                objects_name = force_text(opts.verbose_name_plural)
                obj = None
            if not action_name:
                action_name = func.__name__
            context = {
                'title': _("Are you sure?"),
                'content_message': _("Are you sure you want to {action} the selected {item}?").format(
                    action=action_name, item=objects_name),
                'action_name': action_name.capitalize(),
                'action_value': action_value,
                'queryset': queryset,
                'opts': opts,
                'obj': obj,
                'app_label': app_label,
                'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
            }
            
            if callable(extra_context):
                extra_context = extra_context(modeladmin, request, queryset)
            context.update(extra_context or {})
            if 'display_objects' not in context:
                # Compute it only when necessary
                context['display_objects'] = format_display_objects(modeladmin, request, queryset)
            
            # Display the confirmation page
            return TemplateResponse(request, template, context)
        return inner
    return decorator
