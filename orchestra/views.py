from django.apps import apps
from django.http import Http404
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.views.static import serve


def serve_private_media(request, app_label, model_name, field_name, object_id, filename):
    model = apps.get_model(app_label, model_name)
    if model is None:
        raise Http404('')
    instance = get_object_or_404(model, pk=unquote(object_id))
    if not hasattr(instance, field_name):
        raise Http404('')
    field = getattr(instance, field_name)
    if field.condition(request, instance):
        return serve(request, field.name, document_root=field.storage.location)
    else:
        raise PermissionDenied()
