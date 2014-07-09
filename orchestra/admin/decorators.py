from functools import wraps

from django.contrib import messages
from django.contrib.admin import helpers
from django.template.response import TemplateResponse 
from django.utils.decorators import available_attrs
from django.utils.encoding import force_text


def action_with_confirmation(action_name, extra_context={},
                             template='admin/orchestra/generic_confirmation.html'):
    """ 
    Generic pattern for actions that needs confirmation step
    If custom template is provided the form must contain:
    <input type="hidden" name="post" value="generic_confirmation" />
    """

    def decorator(func, extra_context=extra_context, template=template):
        @wraps(func, assigned=available_attrs(func))
        def inner(modeladmin, request, queryset):
            # The user has already confirmed the action.
            if request.POST.get('post') == "generic_confirmation":
                stay = func(modeladmin, request, queryset)
                if not stay:
                    return

            opts = modeladmin.model._meta
            app_label = opts.app_label
            action_value = func.__name__

            if len(queryset) == 1:
                objects_name = force_text(opts.verbose_name)
            else:
                objects_name = force_text(opts.verbose_name_plural)

            context = {
                "title": "Are you sure?",
                "content_message": "Are you sure you want to %s the selected %s?" %
                                    (action_name, objects_name),
                "action_name": action_name.capitalize(),
                "action_value": action_value,
                "deletable_objects": queryset,
                'queryset': queryset,
                "opts": opts,
                "app_label": app_label,
                'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
            }

            context.update(extra_context)

            # Display the confirmation page
            return TemplateResponse(request, template,
                context, current_app=modeladmin.admin_site.name)
        return inner
    return decorator

