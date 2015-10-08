import itertools
from collections import OrderedDict
from functools import update_wrapper

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .dashboard import *
from .options import *
from ..core import accounts, services


# monkey-patch admin.site in order to porvide some extra admin urls

urls = []
def register_url(pattern, view, name=""):
    global urls
    urls.append((pattern, view, name))
admin.site.register_url = register_url


site_get_urls = admin.site.get_urls
def get_urls():
    def wrap(view, cacheable=False):
        def wrapper(*args, **kwargs):
            return admin.site.admin_view(view, cacheable)(*args, **kwargs)
        wrapper.admin_site = admin.site
        return update_wrapper(wrapper, view)
    global urls
    extra_patterns = []
    for pattern, view, name in urls:
        extra_patterns.append(
            url(pattern, wrap(view), name=name)
        )
    return site_get_urls() + extra_patterns
admin.site.get_urls = get_urls


def get_model(model_name, model_name_map):
    try:
        return model_name_map[model_name.lower()]
    except KeyError:
        return


def search(request):
    query = request.GET.get('q', '')
    search_term = query
    models = set()
    selected_models = set()
    model_name_map = {}
    for service in itertools.chain(services, accounts):
        if service.search:
            models.add(service.model)
            model_name_map[service.model._meta.model_name] = service.model
    
    # Account direct access
    if search_term.endswith('!'):
        from ..contrib.accounts.models import Account
        search_term = search_term.replace('!', '')
        try:
            account = Account.objects.get(username=search_term)
        except Account.DoesNotExist:
            pass
        else:
            account_url = reverse('admin:accounts_account_change', args=(account.pk,))
            return redirect(account_url)
    # Search for specific model
    elif ':' in search_term:
        new_search_term = []
        for part in search_term.split():
            if ':' in part:
                model_name, term = part.split(':')
                model = get_model(model_name, model_name_map)
                # Retry with singular version
                if model is None and model_name.endswith('s'):
                    model = get_model(model_name[:-1], model_name_map)
                if model is None:
                    new_search_term.append(':'.join((model_name, term)))
                else:
                    selected_models.add(model)
                    new_search_term.append(term)
            else:
                new_search_term.append(part)
        search_term = ' '.join(new_search_term)
    if selected_models:
        models = selected_models
    results = OrderedDict()
    models = sorted(models, key=lambda m: m._meta.verbose_name_plural.lower())
    total = 0
    for model in models:
        try:
            modeladmin = admin.site._registry[model]
        except KeyError:
            pass
        else:
            qs = modeladmin.get_queryset(request)
            qs, search_use_distinct = modeladmin.get_search_results(request, qs, search_term)
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
        'search_term': search_term,
        'results': results,
        'search_autofocus': True,
    }
    return render(request, 'admin/orchestra/search.html', context)


admin.site.register_url(r'^search/$', search, 'orchestra_search_view')
