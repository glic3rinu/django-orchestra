import itertools
from collections import OrderedDict

from django.http import Http404
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import get_model
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.static import serve

from orchestra.contrib.accounts.models import Account

from .core import accounts, services
from .utils.python import OrderedSet


def serve_private_media(request, app_label, model_name, field_name, object_id, filename):
    model = get_model(app_label, model_name)
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


def search(request):
    query = request.GET.get('q', '')
    if query.endswith('!'):
        # Account direct access
        query = query.replace('!', '')
        try:
            account = Account.objects.get(username=query)
        except Account.DoesNotExist:
            pass
        else:
            account_url = reverse('admin:accounts_account_change', args=(account.pk,))
            return redirect(account_url)
    results = OrderedDict()
    models = set()
    for service in itertools.chain(services, accounts):
        if service.search:
            models.add(service.model)
    models = sorted(models, key=lambda m: m._meta.verbose_name_plural.lower())
    total = 0
    for model in models:
        try:
            modeladmin = admin.site._registry[model]
        except KeyError:
            pass
        else:
            qs = modeladmin.get_queryset(request)
            qs, search_use_distinct = modeladmin.get_search_results(request, qs, query)
            if search_use_distinct:
                qs = qs.distinct()
            num = len(qs)
            if num:
                total += num
                results[model._meta] = qs
    title = _("{total} search results for '<tt>{query}</tt>'").format(total=total, query=query)
    context = {
        'title': mark_safe(title),
        'total': total,
        'columns': min(int(total/17), 3),
        'query': query,
        'results': results,
        'search_autofocus': True,
    }
    return render(request, 'admin/orchestra/search.html', context)
