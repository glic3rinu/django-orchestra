from functools import update_wrapper

from django.contrib.admin import site

from .dashboard import *
from .options import *


# monkey-patch admin.site in order to porvide some extra admin urls

urls = []
def register_url(pattern, view, name=""):
    global urls
    urls.append((pattern, view, name))
site.register_url = register_url


site_get_urls = site.get_urls
def get_urls():
    def wrap(view, cacheable=False):
        def wrapper(*args, **kwargs):
            return site.admin_view(view, cacheable)(*args, **kwargs)
        wrapper.admin_site = site
        return update_wrapper(wrapper, view)
    global urls
    extra_patterns = []
    for pattern, view, name in urls:
        extra_patterns.append(
            url(pattern, wrap(view), name=name)
        )
    return site_get_urls() + extra_patterns
site.get_urls = get_urls
